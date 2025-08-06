from datetime import datetime
from typing import List, Optional

from server.utils.printer import Printer
from server.utils.pdf_reader import DocumentReader
from server.utils.image_reader import ImageReader
from server.utils.audio_reader import AudioReader

from server.db import session_context_sync
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

from server.ai.ai_interface import AIInterface, function_to_openai_schema
import os
import json
from server.utils.redis_cache import redis_client

printer = Printer("PROCESSOR")

audio_reader = AudioReader(model_name="base", include_timestamps=False)


def send_message_to_user(message: str, workflow_execution_id: str):
    redis_client.publish(
        "workflow_updates",
        json.dumps(
            {
                "workflow_execution_id": workflow_execution_id,
                "log": message,
                "status": "PROCESSING",
                "assets_ready": False,
            }
        ),
    )


def process_workflow_execution(workflow_execution_id: str):
    printer.info(f"Procesando ejecución de workflow {workflow_execution_id}")
    # Usar el context manager para obtener la sesión
    with session_context_sync() as session:
        w = (
            session.query(WorkflowExecution)
            .filter(WorkflowExecution.id == workflow_execution_id)
            .first()
        )
        if not w:
            printer.error(f"No se encontró la ejecución #{workflow_execution_id}")
            return

        log = w.generation_log
        if not log:
            log = f"<workflow_execution>{workflow_execution_id}</workflow_execution>"
            w.generation_log = log
            session.commit()

        assets = w.assets

        log += f"<instructions>{w.workflow.instructions}</instructions>"
        printer.info(log)

        w.status = WorkflowExecutionStatus.IN_PROGRESS
        w.started_at = datetime.now()
        session.commit()

        document_reader = DocumentReader()
        image_reader = ImageReader()

        for asset in assets:
            if asset.status == AssetStatus.DONE:
                continue
            log += f"<asset>{asset.name}</asset>"
            if asset.asset_type == AssetType.FILE:
                file_extension = os.path.splitext(asset.name)[1]
                file_path = (
                    f"uploads/{asset.workflow_execution_id}/{asset.id}{file_extension}"
                )
                ext = file_extension.lower()
                extracted_text = None
                printer.info(f"Procesando archivo {asset.name}")
                if ext in [".pdf", ".docx"]:
                    extracted_text = document_reader.read(file_path)
                    log += (
                        f"<document_extraction>{extracted_text}</document_extraction>"
                    )
                elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
                    extracted_text = image_reader.read(
                        file_path,
                        f"Nombre del archivo adjunto: {asset.name}. Se está realizando un flujo de trabajo que requiere de la información de la imagen. Las instrucciones del flujo de trabajo son: {w.workflow.instructions}. Extraer la información que pueda ser útil para el flujo de trabajo.",
                    )
                    log += f"<image_extraction>{extracted_text}</image_extraction>"
                elif ext in [".txt", ".xml", ".html", ".md", ".json", ".csv"]:
                    with open(file_path, "r", encoding="utf-8") as f:
                        extracted_text = f.read()
                    log += f"<text_extraction>{extracted_text}</text_extraction>"
                elif ext in [".mp3", ".wav", ".m4a", ".webm"]:
                    redis_client.publish(
                        "workflow_updates",
                        json.dumps(
                            {
                                "workflow_execution_id": workflow_execution_id,
                                "log": f"El agente IA está transcribiendo el audio {asset.name}.",
                                "status": "PROCESSING",
                                "assets_ready": False,
                            }
                        ),
                    )
                    extracted_text = audio_reader.read(file_path)
                    log += (
                        f"<audio_transcription>{extracted_text}</audio_transcription>"
                    )
                    redis_client.publish(
                        "workflow_updates",
                        json.dumps(
                            {
                                "workflow_execution_id": workflow_execution_id,
                                "log": f"Se extrajo el texto de **{asset.name}**.",
                                "status": "PROCESSING",
                                "assets_ready": False,
                            }
                        ),
                    )

                asset.extracted_text = extracted_text
                asset.content = extracted_text
                asset.status = AssetStatus.DONE
                w.generation_log = log
                session.commit()
                redis_client.publish(
                    "workflow_updates",
                    json.dumps(
                        {
                            "workflow_execution_id": workflow_execution_id,
                            "log": f"Se extrajo el texto de **{asset.name}**.",
                            "status": "PROCESSING",
                            "assets_ready": False,
                        }
                    ),
                )

        ai = AIInterface(
            provider=os.getenv("PROVIDER", "ollama"),
            api_key=os.getenv("PROVIDER_API_KEY", "asdasd"),
            base_url=os.getenv("PROVIDER_BASE_URL", None),
        )

        def on_message(message):
            print("New response received from agent")
            # printer.yellow(message, "MESSAGE")

        assets_text = "\n".join(
            [
                f"```{asset.name}\n{asset.content}\n\n> ASSET DESCRIPTION: {asset.brief or 'No description'}```"
                for asset in assets
                if asset.content
            ]
        )

        output_examples_text = "\n".join(
            [
                f"<EXAMPLE name={example.name} description={example.description}>{example.content}</EXAMPLE>"
                for example in w.workflow.output_examples
            ]
        )

        printer.cyan(
            "<OUTPUT EXAMPLES TEXT>", output_examples_text, "<OUTPUT EXAMPLES TEXT>"
        )

        messages = [
            {
                "role": "system",
                "content": f"You are a helpful agent that can execute workflows over files. For the current workflow, these are the instructions provided by the user: ```{w.workflow.instructions}```. The goal is to use the available tools until the workflow is completed. Interact with the user to let him know the progress of the workflow. Stop calling tools ONLY when the workflow is completed, if you don't call tools, your loop will stop and you can maybe not finish the workflow. You will receive the text of the uploaded files, and you will have to use the tools to craft new files based on the requirements. The new files will be in markdown format. Don't stop until all necessary assets are created. Keep in mind that you cannot interact with the user directly, you can only use the tools to interact with the user. You need to work only with the information available at the moment. The user will see the result later. If the user added examples to this workflow, these are the examples: {output_examples_text}",
            },
            {
                "role": "user",
                "content": f"The workflow is: {w.workflow.name}. The assets on this execution are: {assets_text}",
            },
        ]

        def emit_message(message):
            send_message_to_user(message, str(workflow_execution_id))
            m = Message(
                workflow_execution_id=workflow_execution_id,
                role="assistant",
                content=message,
            )
            w.generation_log += f"\n<ai_message>{message}</ai_message>"
            session.add(m)
            session.commit()
            return "Message sent successfully"

        def annotate_in_scratchpad(message: str):
            """
            This function is used to annotate the scratchpad.
            The scratchpad is a list of messages that the agent can use to remember things.
            """
            w.generation_log += f"\n<scratchpad>{message}</scratchpad>"
            session.commit()
            return "Scratchpad annotated successfully"

        def create_new_asset(name: str, content: str):
            printer.magenta(content, "CONTENT", name, "NAME")

            asset = Asset(
                name=name,
                content=content,
                extracted_text=content,
                asset_type=AssetType.TEXT,
                workflow_execution_id=workflow_execution_id,
                origin=AssetOrigin.AI,
            )
            session.add(asset)

            w.generation_log += f"\n<ai_message>Se creó el asset **{name}**. Con contenido:```markdown\n{content}\n```</ai_message>"
            redis_client.publish(
                "workflow_updates",
                json.dumps(
                    {
                        "workflow_execution_id": workflow_execution_id,
                        "log": f"Se creó el asset **{name}**. Con contenido: {content}",
                        "status": "PROCESSING",
                        "assets_ready": False,
                    }
                ),
            )
            session.commit()
            return "Asset created successfully"

        ai.agent_loop(
            messages,
            model=os.getenv("MODEL", "gemma3"),
            tools=[
                # function_to_openai_schema(emit_message),
                function_to_openai_schema(create_new_asset),
                function_to_openai_schema(annotate_in_scratchpad),
            ],
            tools_fn_map={
                "emit_message": emit_message,
                "create_new_asset": create_new_asset,
                "annotate_in_scratchpad": annotate_in_scratchpad,
            },
            on_message=on_message,
        )
        w.status = WorkflowExecutionStatus.DONE
        w.finished_at = datetime.now()
        session.commit()
        redis_client.publish(
            "workflow_updates",
            json.dumps(
                {
                    "workflow_execution_id": workflow_execution_id,
                    "log": "Workflow completed. The assets are ready to be used.",
                    "status": "DONE",
                    "assets_ready": True,
                }
            ),
        )


def request_changes(
    workflow_execution_id: str, asset_id: str, changes: str, not_id: str
):
    with session_context_sync() as session:
        w = (
            session.query(WorkflowExecution)
            .filter(WorkflowExecution.id == workflow_execution_id)
            .first()
        )
        if not w:
            printer.error(f"No se encontró la ejecución #{workflow_execution_id}")
            return
        asset = session.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            printer.error(f"No se encontró el asset {asset_id}")
            return
        asset.status = AssetStatus.PENDING
        session.commit()

        redis_client.publish(
            "notifications",
            json.dumps(
                {
                    "not_id": not_id,
                    "message": "Solicitud de cambios recibida. El agente IA está procesando la solicitud.",
                    "status": "PROCESSING",
                }
            ),
        )

        ai = AIInterface(
            provider=os.getenv("PROVIDER", "ollama"),
            api_key=os.getenv("PROVIDER_API_KEY", "asdasd"),
            base_url=os.getenv("PROVIDER_BASE_URL", None),
        )

        def replace_asset_content(new_content: str):
            """
            This function is used to replace the content of the asset.
            The new content will be provided in the new_content parameter.
            The asset will be updated with the new content.
            The asset status will be set to DONE.
            """
            redis_client.publish(
                "notifications",
                json.dumps(
                    {
                        "not_id": not_id,
                        "message": "El agente IA está reemplazando el contenido del asset.",
                        "status": "PROCESSING",
                    }
                ),
            )
            asset.content = new_content
            asset.status = AssetStatus.DONE
            session.commit()
            return "The asset content was replaced successfully"

        def replace_string_in_asset(search_string: str, replacement: str):
            """
            Reemplaza todas las ocurrencias exactas de search_string por replacement en el asset.content.
            No utiliza expresiones regulares: es un reemplazo literal.
            """
            printer.bold(f"SEARCH_STRING: {search_string!r}")
            printer.bold(f"REPLACEMENT: {replacement!r}")

            if not search_string:
                printer.error("The search string is empty")
                return "The search string cannot be empty"

            if asset.content is None:
                printer.error("Asset content is empty")
                return "Asset content is empty"

            if search_string not in asset.content:
                printer.error(
                    f"The search string {search_string!r} was not found in the asset content"
                )
                return "The search string was not found in the asset content"
            else:
                printer.success("Replacement string found in the asset content")

            asset.content = asset.content.replace(search_string, replacement)
            asset.status = AssetStatus.DONE
            session.commit()
            redis_client.publish(
                "notifications",
                json.dumps(
                    {
                        "not_id": not_id,
                        "message": "El agente IA ha reemplazado el contenido del asset.",
                        "status": "PROCESSING",
                    }
                ),
            )
            return "The search string was found and replaced successfully"

        ai.agent_loop(
            messages=[
                {
                    "role": "system",
                    "content": f"""You are a document assistant. You already generated some documents over a workflow, but now the user is requesting some changes over one of the documents. THis is the information about the document that the user wants to change: <DOCUMENT name={asset.name}>{asset.content}</DOCUMENT>. Stop calling tools ONLY when the requested changes are complete, if you don't call tools, your loop will stop and you can maybe not finish the workflow. You are processing in the background, so you can't interact with the user directly, you can only use the tools to accomplish your task. The user will see the result later.""",
                },
                {
                    "role": "user",
                    "content": f"The changes requested by the user are: ```{changes}```.",
                },
            ],
            model=os.getenv("MODEL", "gemma3"),
            tools=[
                function_to_openai_schema(replace_asset_content),
                function_to_openai_schema(replace_string_in_asset),
            ],
            tools_fn_map={
                "replace_asset_content": replace_asset_content,
                "replace_string_in_asset": replace_string_in_asset,
            },
        )
        asset.status = AssetStatus.DONE
        session.commit()
        printer.success("Agent request changes process completed")
        redis_client.publish(
            "notifications",
            json.dumps(
                {
                    "not_id": not_id,
                    "message": "El agente IA ha completado el proceso de solicitud de cambios.",
                    "status": "DONE",
                }
            ),
        )
    return "Agent request changes process completed"


def process_example_files(
    workflow_id: str,
    file_paths: List[str],
    output_examples_description: List[str],
):
    with session_context_sync() as session:
        w = session.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not w:
            printer.error(f"No se encontró el workflow {workflow_id}")
            return

        for file_path, description in zip(file_paths, output_examples_description):
            file_extension = os.path.splitext(file_path)[1]
            ext = file_extension.lower()
            if ext in [".pdf", ".docx"]:
                document_reader = DocumentReader()
                extracted_text = document_reader.read(file_path)
                print(extracted_text)
                session.add(
                    WorkflowOutputExample(
                        workflow_id=workflow_id,
                        name=os.path.basename(file_path),
                        content=extracted_text,
                        description=description,
                    )
                )
            elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
                image_reader = ImageReader()
                extracted_text = image_reader.read(
                    file_path,
                    f"Nombre del archivo adjunto: {file_path}. Se está realizando un flujo de trabajo que requiere de la información de la imagen. Las instrucciones del flujo de trabajo son: {w.workflow.instructions}. Extraer la información que pueda ser útil para el flujo de trabajo.",
                )
                print(extracted_text)
                session.add(
                    WorkflowOutputExample(
                        workflow_id=workflow_id,
                        name=os.path.basename(file_path),
                        content=extracted_text,
                        description=description,
                    )
                )
            elif ext in [".txt", ".xml", ".html", ".md", ".json", ".csv"]:
                with open(file_path, "r", encoding="utf-8") as f:
                    extracted_text = f.read()
                print(extracted_text)
                session.add(
                    WorkflowOutputExample(
                        workflow_id=workflow_id,
                        name=os.path.basename(file_path),
                        content=extracted_text,
                        description=description,
                    )
                )
            elif ext in [".mp3", ".wav", ".m4a", ".webm"]:
                audio_reader = AudioReader(model_name="base", include_timestamps=False)
                extracted_text = audio_reader.read(file_path)
                print(extracted_text)
                session.add(
                    WorkflowOutputExample(
                        workflow_id=workflow_id,
                        name=os.path.basename(file_path),
                        content=extracted_text,
                        description=description,
                    )
                )
            else:
                printer.error(f"No se puede procesar el archivo {file_path}")

        session.commit()

    return "Output examples created successfully"
