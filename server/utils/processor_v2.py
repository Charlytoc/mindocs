from datetime import datetime
from typing import List, Optional
import uuid
import traceback
import os
import json

from sqlalchemy.orm import Session
from server.utils.printer import Printer
from server.utils.pdf_reader import DocumentReader, find_placeholders, generate_docx_from_template, docx_to_html
from server.utils.image_reader import ImageReader
from server.utils.audio_reader import AudioReader
from server.utils.redis_cache import redis_client

from server.models import (
    WorkflowExecution,
    AssetType,
    Asset,
    AssetOrigin,
    WorkflowExecutionStatus,
    Message,
    AssetStatus,
    Workflow,
    WorkflowOutputExample,
)

from server.utils.agent_v2 import WorkflowAgent, AgentTool
from server.services.openai_responses_service import ResponsesAPIService

printer = Printer("PROCESSOR_V2")

audio_reader = AudioReader(model_name="base", include_timestamps=False)


def send_message_to_user(message: str, workflow_execution_id: str):
    redis_client.publish(
        "workflow_updates",
        json.dumps(
            {
                "workflow_execution_id": workflow_execution_id,
                "log": f"<AI_MESSAGE>{message}</AI_MESSAGE>",
                "status": "PROCESSING",
                "assets_ready": False,
            }
        ),
    )


def create_workflow_example_text(workflow_example: WorkflowOutputExample):
    if workflow_example.is_template:
        return f"""
<TEMPLATE id={workflow_example.id} help_text="This is an template provided by the user to this workflow, use the use_template tool to fill the template with the information provided by the user">
<VARIABLES>
    {json.dumps(workflow_example.variables)}
</VARIABLES>
<CONTENT>
    {workflow_example.content}
</CONTENT>
</TEMPLATE>
        """
    else:
        return f"""
<EXAMPLE>
<CONTENT>
    {workflow_example.content}
</CONTENT>
</EXAMPLE>
        """


class WorkflowProcessorV2:
    """V2 processor using OpenAI Responses API and class-based architecture"""
    
    def __init__(
        self,
        workflow_execution_id: str,
        session: Session,
    ):
        self.workflow_execution_id = workflow_execution_id
        self.session = session
        self.workflow_execution: Optional[WorkflowExecution] = None
        self.agent: Optional[WorkflowAgent] = None
        self.document_reader = DocumentReader()
        self.image_reader = ImageReader()
    
    def process(self) -> bool:
        """Main processing method"""
        try:
            # 1. Load workflow execution
            if not self._load_workflow_execution():
                return False
            
            # 2. Process assets (extract text from files)
            self._process_assets()
            
            # 3. Build system instructions
            system_instructions = self._build_system_instructions()
            
            # 4. Create tools
            tools, tools_fn_map = self._create_tools()
            
            # 5. Execute agent
            self._execute_agent(system_instructions, tools, tools_fn_map)
            
            # 6. Update status
            self._update_status()
            
            return True
        except Exception as e:
            printer.error(f"Error in workflow processing: {e}")
            traceback.print_exc()
            self._set_error_status(str(e))
            return False
    
    def _load_workflow_execution(self) -> bool:
        """Load workflow execution from database"""
        self.workflow_execution = (
            self.session.query(WorkflowExecution)
            .filter(WorkflowExecution.id == self.workflow_execution_id)
            .first()
        )
        
        if not self.workflow_execution:
            printer.error(f"No se encontró la ejecución #{self.workflow_execution_id}")
            return False
        
        # Initialize log if needed
        if not self.workflow_execution.generation_log:
            self.workflow_execution.generation_log = "Ejecución iniciada.\n"
            self.session.commit()
        
        # Update status
        self.workflow_execution.status = WorkflowExecutionStatus.IN_PROGRESS
        self.workflow_execution.started_at = datetime.now()
        self.session.commit()
        
        return True
    
    def _process_assets(self):
        """Extract text from uploaded files"""
        assets = self.workflow_execution.assets
        log = self.workflow_execution.generation_log
        
        for asset in assets:
            if asset.status == AssetStatus.DONE:
                continue
                
            log += f"Procesando archivo: {asset.name}\n"
            
            if asset.asset_type == AssetType.FILE:
                file_extension = os.path.splitext(asset.name)[1]
                file_path = f"uploads/{asset.workflow_execution_id}/{asset.id}{file_extension}"
                ext = file_extension.lower()
                extracted_text = None
                
                if ext in [".pdf", ".docx"]:
                    extracted_text = self.document_reader.read(file_path)
                    log += f"Contenido del archivo {asset.name} extraído con exito.\n"
                elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
                    extracted_text = self.image_reader.read(
                        file_path,
                        f"Nombre del archivo adjunto: {asset.name}. Se está realizando un flujo de trabajo que requiere de la información de la imagen. Esta es una descripción del flujo de trabajo para que puedas entender mejor el tipo de información que se requiere extraer de la imagen: {self.workflow_execution.workflow.description}. Extrae la información que pueda ser útil para el flujo de trabajo en la imagen. {'\nEsta descripción puede ser útil: ' + asset.brief if asset.brief else ''}",
                    )
                    log += f"Contenido de la imagen {asset.name} extraído con exito.\n"
                elif ext in [".txt", ".xml", ".html", ".md", ".json", ".csv"]:
                    with open(file_path, "r", encoding="utf-8") as f:
                        extracted_text = f.read()
                    log += f"Contenido del archivo {asset.name} extraído con exito.\n"
                elif ext in [".mp3", ".wav", ".m4a", ".webm"]:
                    redis_client.publish(
                        "workflow_updates",
                        json.dumps(
                            {
                                "workflow_execution_id": self.workflow_execution_id,
                                "log": f"El agente IA está transcribiendo el audio {asset.name}.",
                                "status": "PROCESSING",
                                "assets_ready": False,
                            }
                        ),
                    )
                    extracted_text = audio_reader.read(file_path)
                    log += f"Se realizó la transcripción del audio {asset.name} con exito.\n"
                
                redis_client.publish(
                    "workflow_updates",
                    json.dumps(
                        {
                            "workflow_execution_id": self.workflow_execution_id,
                            "log": f"Se extrajo el texto de **{asset.name}**.",
                            "status": "PROCESSING",
                            "assets_ready": False,
                        }
                    ),
                )
                
                asset.extracted_text = extracted_text
                asset.content = extracted_text
                asset.status = AssetStatus.DONE
                self.workflow_execution.generation_log = log
                self.session.commit()
                
                redis_client.publish(
                    "workflow_updates",
                    json.dumps(
                        {
                            "workflow_execution_id": self.workflow_execution_id,
                            "log": f"Se extrajo el texto de **{asset.name}**.",
                            "status": "PROCESSING",
                            "assets_ready": False,
                        }
                    ),
                )
        
        self.workflow_execution.generation_log = log
        self.session.commit()
    
    def _build_system_instructions(self) -> str:
        """Build system prompt from workflow configuration"""
        assets_text = "\n".join(
            [
                f'<ASSET name="{asset.name}" description="{asset.brief or "No description"}">{asset.content}</ASSET>'
                for asset in self.workflow_execution.assets
                if asset.content
            ]
        )
        
        output_examples_text = "\n".join(
            [
                create_workflow_example_text(example)
                for example in self.workflow_execution.workflow.output_examples
            ]
        )
        
        system_instructions = f"""
ROLE: You are a helpful agent that can use different tools to execute workflows. 

TASK DESCRIPTION:                
- The goal is to use the available tools until the workflow is completed and you have generated all the required files. 
- Interact with the user to let him know the progress of the workflow. 
- Stop calling tools ONLY when the workflow is completed, if you don't call tools, your loop will stop and you can maybe not finish the workflow. You will receive the text of the uploaded files, and you will have to use the tools to craft new files based on the requirements. The new files will be in markdown format unless you're working with templates. Don't stop until all necessary assets are created. Keep in mind that you cannot interact with the user directly, you can only use the tools to interact with the user. You need to work only with the information available at the moment. The user will see the result later. 

CURRENT WORKFLOW: 
NAME: {self.workflow_execution.workflow.name}
```instructions
{self.workflow_execution.workflow.instructions}
```

EXAMPLES or TEMPLATES (if provided):

{output_examples_text}
"""
        return system_instructions
    
    def _build_user_message(self) -> str:
        """Build user message with assets content"""
        assets_text = "\n".join(
            [
                f'<ASSET name="{asset.name}" description="{asset.brief or "No description"}">{asset.content}</ASSET>'
                for asset in self.workflow_execution.assets
                if asset.content
            ]
        )
        return f"Use the following information to execute the workflow and craft the new files: {assets_text}"
    
    def _create_tools(self) -> tuple[List[AgentTool], dict]:
        """Create tools available to the agent"""
        tools = [
            AgentTool(
                name="create_new_markdown_asset",
                description="Create a new markdown asset. Use it only when there is not a template to use. The name and content needs to match the criteria of the workflow.",
                parameters={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "content": {"type": "string"},
                    },
                    "required": ["name", "content"],
                }
            ),
            AgentTool(
                name="use_template",
                description="Use a template to generate a new file. The template to use will be provided in the template_id parameter. The variables parameter must be a json string with the variables to use like this: {'variable_name': 'variable_value', ...}. The document_name parameter is the name of the document to create. It must not contain spaces or special characters.",
                parameters={
                    "type": "object",
                    "properties": {
                        "template_id": {"type": "string"},
                        "variables": {"type": "string"},
                        "document_name": {"type": "string"},
                    },
                    "required": ["template_id", "variables", "document_name"],
                }
            ),
            AgentTool(
                name="annotate_in_scratchpad",
                description="Annotate the scratchpad. The scratchpad is a list of messages that the agent can use to remember things.",
                parameters={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"},
                    },
                    "required": ["message"],
                }
            ),
        ]
        
        tools_fn_map = {
            "create_new_markdown_asset": self._create_markdown_asset,
            "use_template": self._use_template,
            "annotate_in_scratchpad": self._annotate_scratchpad,
        }
        
        return tools, tools_fn_map
    
    def _execute_agent(self, system_instructions: str, tools: List[AgentTool], tools_fn_map: dict):
        """Execute the agent loop"""
        # Initialize OpenAI service
        api_key = os.getenv("PROVIDER_API_KEY", "")
        if not api_key:
            raise ValueError("PROVIDER_API_KEY environment variable not set")
        
        openai_service = ResponsesAPIService(api_key=api_key)
        model = os.getenv("MODEL", "gpt-4o-mini")
        max_iterations = int(os.getenv("RESPONSES_API_MAX_ITERATIONS", "20"))
        
        # Create agent
        self.agent = WorkflowAgent(
            openai_service=openai_service,
            model=model,
            max_iterations=max_iterations,
        )
        
        # Execute agent
        user_message = self._build_user_message()
        
        def on_message(message):
            printer.info(f"New response from agent: {message}")
        
        result = self.agent.execute(
            system_instructions=system_instructions,
            user_message=user_message,
            tools=tools,
            tools_fn_map=tools_fn_map,
            on_message_callback=on_message,
        )
        
        # Process result
        if result.error:
            printer.error(f"Agent execution error: {result.error}")
            self.workflow_execution.generation_log += f"\n<error>{result.error}</error>"
        
        # Save messages
        for msg in result.messages:
            message = Message(
                workflow_execution_id=self.workflow_execution_id,
                role=msg.get("role", "assistant"),
                content=msg.get("content", ""),
            )
            self.session.add(message)
        
        self.session.commit()
    
    def _update_status(self):
        """Update workflow execution status to done"""
        self.workflow_execution.status = WorkflowExecutionStatus.DONE
        self.workflow_execution.finished_at = datetime.now()
        self.session.commit()
        
        redis_client.publish(
            "workflow_updates",
            json.dumps(
                {
                    "workflow_execution_id": self.workflow_execution_id,
                    "log": "Workflow completed. The assets are ready to be used.",
                    "status": "DONE",
                    "assets_ready": True,
                }
            ),
        )
    
    def _set_error_status(self, error_message: str):
        """Set workflow execution status to error"""
        if self.workflow_execution:
            self.workflow_execution.status = WorkflowExecutionStatus.FAILED
            self.workflow_execution.finished_at = datetime.now()
            if self.workflow_execution.generation_log:
                self.workflow_execution.generation_log += f"\n<error>{error_message}</error>"
            self.session.commit()
    
    # Tool implementations
    def _create_markdown_asset(self, name: str, content: str) -> str:
        """Tool: Create markdown asset"""
        printer.magenta(content, "CONTENT", name, "NAME")
        
        asset = Asset(
            name=name,
            content=content,
            extracted_text=content,
            format="markdown",
            asset_type=AssetType.TEXT,
            workflow_execution_id=self.workflow_execution_id,
            origin=AssetOrigin.AI,
        )
        self.session.add(asset)
        
        self.workflow_execution.generation_log += (
            f"\n<ai_message>Se creó el asset **{name}**.</ai_message>"
        )
        redis_client.publish(
            "workflow_updates",
            json.dumps(
                {
                    "workflow_execution_id": self.workflow_execution_id,
                    "log": f"Se creó el asset **{name}**.",
                    "status": "PROCESSING",
                    "assets_ready": False,
                }
            ),
        )
        self.session.commit()
        return "Asset created successfully"
    
    def _use_template(self, template_id: str, variables: str, document_name: str) -> str:
        """Tool: Fill template with variables"""
        printer.green(f"Using template {template_id} with variables {variables}")
        
        template = next(
            (t for t in self.workflow_execution.workflow.output_examples if str(t.id) == template_id),
            None
        )
        
        if not template:
            return "The template was not found, please check the template id"
        
        try:
            variables_dict = json.loads(variables)
            random_id = str(uuid.uuid4())
            output_path = os.path.join("uploads", str(self.workflow_execution_id), f"{random_id}.docx")
            absolute_output_path = os.path.join(os.getcwd(), output_path)
            printer.green(f"Generating docx file at {absolute_output_path}")
            
            generate_docx_from_template(template.internal_path, variables_dict, output_path)
            printer.green(f"Generated docx file at {absolute_output_path}")
            
            html_content = docx_to_html(absolute_output_path)
            
            if not document_name.endswith(".docx"):
                document_name += ".docx"
            
            asset = Asset(
                name=document_name,
                content=html_content,
                asset_type=AssetType.FILE,
                format="docx",
                workflow_execution_id=self.workflow_execution_id,
                origin=AssetOrigin.AI,
                internal_path=output_path,
            )
            self.session.add(asset)
            self.session.commit()
            
            return "The template was used successfully and the file was created successfully"
            
        except Exception as e:
            traceback.print_exc()
            printer.error(f"Error using template {template_id}: {e}")
            return f"Error using template {template_id}: {e}. The file was not created."
    
    def _annotate_scratchpad(self, message: str) -> str:
        """Tool: Add note to scratchpad"""
        self.workflow_execution.generation_log += f"\n<scratchpad>{message}</scratchpad>"
        self.session.commit()
        return "Scratchpad annotated successfully"


# Entry function for compatibility
def process_workflow_execution_v2(workflow_execution_id: str):
    """Entry point for V2 processor"""
    from server.db import session_context_sync
    
    with session_context_sync() as session:
        processor = WorkflowProcessorV2(workflow_execution_id, session)
        return processor.process()
