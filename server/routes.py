import os
import shutil
import subprocess
import tempfile

# import traceback
from typing import List, Optional
from sqlalchemy.orm import selectinload
from server.tasks import (
    async_process_workflow_execution,
    async_request_changes,
    async_process_example_files,
)

from fastapi import APIRouter, Form, File, UploadFile, Depends, HTTPException, Header
from fastapi.responses import JSONResponse, FileResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload


from server.db import get_session
from server.models import (
    User,
    Workflow,
    WorkflowExecution,
    Asset,
    WorkflowExecutionStatus,
    AssetOrigin,
    AssetType,
    AssetStatus,
)
from server.utils.printer import Printer
from server.utils.csv_logger import CSVLogger
from server.utils.pdf_reader import DocumentReader

csv_logger = CSVLogger()
printer = Printer("ROUTES")

UPLOADS_PATH = "uploads"


def get_media_type(export_type: str) -> str:
    """Get the appropriate media type for the export format"""
    media_types = {
        "html": "text/html",
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "txt": "text/plain",
        "md": "text/markdown",
        "rtf": "application/rtf",
        "odt": "application/vnd.oasis.opendocument.text",
        "epub": "application/epub+zip",
    }
    return media_types.get(export_type, "application/octet-stream")


router = APIRouter(prefix="/api")

# --- AUTH ------------------------------------------------


@router.post("/signup")
async def signup(
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(None),
    session: AsyncSession = Depends(get_session),
):
    existing = await session.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already exists")
    user = User(email=email, name=name, password=password)
    session.add(user)
    await session.commit()
    return {"message": "Signup successful"}


@router.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": str(user.id)}


@router.delete("/delete-account")
async def delete_account(
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    await session.delete(user)
    await session.commit()
    return {"message": "Account deleted"}


# --- WORKFLOW MANAGEMENT ---------------------------------


@router.get("/workflows")
async def list_workflows(
    session: AsyncSession = Depends(get_session), x_user_email: str = Header(...)
):
    result = await session.execute(
        select(Workflow).join(User).where(User.email == x_user_email)
    )
    workflows = result.scalars().all()
    return [
        {"id": str(w.id), "name": w.name, "description": w.description}
        for w in workflows
    ]


@router.get("/workflow/{workflow_id}")
async def get_workflow(
    workflow_id: str,
    session: AsyncSession = Depends(get_session),
    x_user_email: str = Header(...),
):
    result = await session.execute(
        select(Workflow)
        .where(Workflow.id == workflow_id)
        .options(
            selectinload(Workflow.output_examples),
            selectinload(Workflow.user),  # <-- ¡Esto es lo que faltaba!
        )
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if not workflow.user:
        raise HTTPException(status_code=404, detail="Workflow.user not found")
    if workflow.user.email != x_user_email:
        raise HTTPException(status_code=403, detail="Not allowed")

    # Obtener las últimas 20 ejecuciones del workflow
    executions_result = await session.execute(
        select(WorkflowExecution)
        .where(WorkflowExecution.workflow_id == workflow_id)
        .order_by(WorkflowExecution.created_at.desc())
        .limit(20)
    )
    executions = executions_result.scalars().all()

    return {
        "id": str(workflow.id),
        "name": workflow.name,
        "description": workflow.description,
        "instructions": workflow.instructions,
        "executions": [
            {
                "id": str(execution.id),
                "status": execution.status,
                "created_at": (
                    execution.created_at.isoformat() if execution.created_at else None
                ),
                "started_at": (
                    execution.started_at.isoformat() if execution.started_at else None
                ),
                "finished_at": (
                    execution.finished_at.isoformat() if execution.finished_at else None
                ),
                "summary": execution.summary,
                "status_message": execution.status_message,
                "delivered": execution.delivered,
            }
            for execution in executions
        ],
        "examples": [
            {
                "id": str(a.id),
                "name": a.name,
                "description": a.description,
                "content": a.content,
            }
            for a in workflow.output_examples
        ],
    }


@router.post("/workflow")
async def create_workflow(
    name: str = Form(...),
    description: str = Form(...),
    instructions: str = Form(...),
    output_examples: List[UploadFile] = File(None),
    output_examples_description: List[str] = Form(...),
    session: AsyncSession = Depends(get_session),
    x_user_email: str = Header(...),
):
    # Obtén el resultado de la consulta
    result = await session.execute(select(User).where(User.email == x_user_email))
    user = result.scalar_one_or_none()  # <-- Extrae el objeto User real

    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    workflow = Workflow(
        name=name,
        description=description,
        instructions=instructions,
        user_id=user.id,  # <-- Ahora sí existe user.id
    )
    session.add(workflow)
    await session.commit()
    if output_examples:
        file_paths = [
            f"{UPLOADS_PATH}/{output_example.filename}"
            for output_example in output_examples
        ]
        # Store the files in the uploads path
        for output_example in output_examples:
            file_path = f"{UPLOADS_PATH}/{output_example.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(output_example.file, buffer)
            file_paths.append(file_path)

        async_process_example_files.delay(
            workflow.id, file_paths, output_examples_description
        )
    return {"message": "Workflow created", "workflow_id": str(workflow.id)}


@router.put("/workflow/{workflow_id}")
async def update_workflow(
    workflow_id: str,
    name: str = Form(...),
    description: str = Form(None),
    instructions: str = Form(None),
    session: AsyncSession = Depends(get_session),
    x_user_email: str = Header(...),
):
    # Precargar la relación user
    result = await session.execute(
        select(Workflow)
        .options(selectinload(Workflow.user))
        .where(Workflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.user.email != x_user_email:
        raise HTTPException(status_code=403, detail="Not allowed")

    # Actualizar los campos del workflow
    workflow.name = name
    workflow.description = description
    workflow.instructions = instructions

    await session.commit()
    return {
        "message": "Workflow updated",
        "workflow": {
            "id": str(workflow.id),
            "name": workflow.name,
            "description": workflow.description,
            "instructions": workflow.instructions,
        },
    }


@router.delete("/workflow/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    session: AsyncSession = Depends(get_session),
    x_user_email: str = Header(...),
):
    # Precargar la relación user
    result = await session.execute(
        select(Workflow)
        .options(selectinload(Workflow.user))
        .where(Workflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.user.email != x_user_email:
        raise HTTPException(status_code=403, detail="Not allowed")
    await session.delete(workflow)
    await session.commit()
    return {"message": "Workflow deleted"}


@router.delete("/workflow-execution/{execution_id}")
async def delete_workflow_execution(
    execution_id: str,
    session: AsyncSession = Depends(get_session),
    x_user_email: str = Header(...),
):
    result = await session.execute(
        select(WorkflowExecution)
        .options(selectinload(WorkflowExecution.workflow).selectinload(Workflow.user))
        .where(WorkflowExecution.id == execution_id)
    )
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    if execution.workflow.user.email != x_user_email:
        raise HTTPException(status_code=403, detail="Not allowed")
    await session.delete(execution)
    await session.commit()
    return {"message": "Execution deleted"}


# --- WORKFLOW EXECUTION ----------------------------------


def get_asset_type_from_extension(filename: str) -> AssetType:
    extension = os.path.splitext(filename)[1]
    if extension in [".pdf", ".docx", ".doc", ".txt", ".jpg", ".png"]:
        return AssetType.FILE

    elif extension in [".mp3", ".wav", ".m4a"]:
        return AssetType.AUDIO
    else:
        return AssetType.FILE


@router.post("/start/{workflow_id}")
async def start_workflow(
    workflow_id: str,
    input_files: List[UploadFile] = File(...),
    input_descriptions: Optional[List[str]] = Form(None),
    input_text: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_session),
    x_user_email: str = Header(...),
):
    # Busca el usuario
    result = await session.execute(select(User).where(User.email == x_user_email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    # Busca el workflow
    result = await session.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    # Crea la ejecución
    execution = WorkflowExecution(
        workflow_id=workflow_id,
        status=WorkflowExecutionStatus.PENDING,
    )
    session.add(execution)
    await session.flush()

    # Guardar archivos como assets
    upload_path = f"{UPLOADS_PATH}/{execution.id}"
    os.makedirs(upload_path, exist_ok=True)
    assets = []

    if input_text:
        printer.yellow(input_text, "INPUT TEXT")
        asset = Asset(
            workflow_execution_id=execution.id,
            name="input_text",
            asset_type=AssetType.TEXT,
            origin=AssetOrigin.UPLOAD,
            content=input_text,
            extracted_text=input_text,
            status=AssetStatus.DONE,
            brief="Texto complementario, información adicional, etc.",
        )
        session.add(asset)
        await session.flush()
    for idx, file in enumerate(input_files):
        desc = (
            input_descriptions[idx]
            if input_descriptions and idx < len(input_descriptions)
            else None
        )
        asset = Asset(
            workflow_execution_id=execution.id,
            name=file.filename,
            asset_type=AssetType.FILE,
            origin=AssetOrigin.UPLOAD,
            status=AssetStatus.PENDING,
            brief=desc,
        )
        session.add(asset)
        await session.flush()
        ext = os.path.splitext(file.filename)[1]
        file_path = f"{upload_path}/{asset.id}{ext}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        assets.append(asset)
    await session.commit()
    # Aquí podrías lanzar tarea async de procesamiento
    async_process_workflow_execution.delay(execution.id)
    return JSONResponse(
        {
            "workflow_execution_id": str(execution.id),
            "uploaded_files": [a.name for a in assets],
        }
    )


@router.post("/workflow-execution/{execution_id}/rerun")
async def rerun_workflow_execution(
    execution_id: str,
    session: AsyncSession = Depends(get_session),
    x_user_email: str = Header(...),
):
    result = await session.execute(
        select(WorkflowExecution)
        .options(selectinload(WorkflowExecution.workflow).selectinload(Workflow.user))
        .where(WorkflowExecution.id == execution_id)
    )
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    if execution.workflow.user.email != x_user_email:
        raise HTTPException(status_code=403, detail="Not allowed")
    execution.status = WorkflowExecutionStatus.PENDING
    await session.commit()
    async_process_workflow_execution.delay(execution.id)
    return JSONResponse(
        {
            "message": "Execution rerunned",
            "workflow_execution_id": str(execution.id),
        }
    )


@router.get("/workflow-execution/{execution_id}")
async def get_execution(
    execution_id: str,
    session: AsyncSession = Depends(get_session),
    x_user_email: str = Header(...),
):
    result = await session.execute(
        select(WorkflowExecution)
        .options(
            selectinload(WorkflowExecution.workflow).selectinload(Workflow.user),
            selectinload(WorkflowExecution.messages),
        )
        .where(WorkflowExecution.id == execution_id)
    )
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    if not execution.workflow or not execution.workflow.user:
        raise HTTPException(status_code=404, detail="Workflow or user not found")
    if execution.workflow.user.email != x_user_email:
        raise HTTPException(status_code=403, detail="Not allowed")
    return {
        "id": str(execution.id),
        "workflow": {"id": str(execution.workflow_id), "name": execution.workflow.name},
        "status": execution.status.value,
        "created_at": execution.created_at.isoformat(),
        "started_at": (
            execution.started_at.isoformat() if execution.started_at else None
        ),
        "log": execution.generation_log,
        "messages": [
            {
                "role": m.role,
                "content": m.content,
            }
            for m in execution.messages
        ],
        "finished_at": (
            execution.finished_at.isoformat() if execution.finished_at else None
        ),
    }


@router.get("/workflow-execution/{execution_id}/assets")
async def get_execution_assets(
    execution_id: str,
    session: AsyncSession = Depends(get_session),
    x_user_email: str = Header(...),
):
    result = await session.execute(
        select(WorkflowExecution)
        .options(
            selectinload(WorkflowExecution.assets),
            selectinload(WorkflowExecution.workflow).selectinload(
                Workflow.user
            ),  # Precarga user
        )
        .where(WorkflowExecution.id == execution_id)
    )
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    if execution.workflow.user.email != x_user_email:
        raise HTTPException(status_code=403, detail="Not allowed")

    assets_upload = [a for a in execution.assets if a.origin == AssetOrigin.UPLOAD]
    assets_generated = [a for a in execution.assets if a.origin == AssetOrigin.AI]
    return {
        "uploaded": [
            {
                "id": str(a.id),
                "name": a.name,
                "description": a.brief,
                "content": a.content,
            }
            for a in assets_upload
        ],
        "generated": [
            {
                "id": str(a.id),
                "name": a.name,
                "type": a.asset_type,
                "description": a.brief,
                "content": a.content,
            }
            for a in assets_generated
        ],
    }


@router.get("/workflow-executions")
async def list_workflow_executions(
    session: AsyncSession = Depends(get_session), x_user_email: str = Header(...)
):
    # Busca usuario
    result = await session.execute(select(User).where(User.email == x_user_email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    # Busca ejecuciones de todos sus workflows
    result = await session.execute(
        select(WorkflowExecution).join(Workflow).where(Workflow.user_id == user.id)
    )
    executions = result.scalars().all()
    return [
        {
            "id": str(e.id),
            "workflow": {"id": str(e.workflow_id)},
            "status": e.status.value,
            "created_at": e.created_at.isoformat(),
        }
        for e in executions
    ]


@router.post("/convert/asset/{asset_id}")
async def convert_asset(
    asset_id: str,
    session: AsyncSession = Depends(get_session),
    x_user_email: str = Header(...),
    export_type: str = Form(...),
):
    # Get asset with proper relationships loaded
    result = await session.execute(
        select(Asset)
        .options(
            selectinload(Asset.workflow_execution)
            .selectinload(WorkflowExecution.workflow)
            .selectinload(Workflow.user)
        )
        .where(Asset.id == asset_id)
    )
    asset = result.scalar_one_or_none()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if (
        not asset.workflow_execution
        or not asset.workflow_execution.workflow
        or not asset.workflow_execution.workflow.user
    ):
        raise HTTPException(status_code=404, detail="Asset relationships not found")

    if asset.workflow_execution.workflow.user.email != x_user_email:
        raise HTTPException(status_code=403, detail="Not allowed")

    printer.yellow(export_type, "EXPORT TYPE")
    # Default export type if not provided
    if not export_type:
        export_type = "docx"

    try:
        # Get the content to convert
        content_to_convert = None

        content_to_convert = asset.content or asset.extracted_text or ""

        if not content_to_convert:
            raise HTTPException(status_code=400, detail="No content found in asset")

        # Create a temporary markdown file with the content
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as temp_md:
            temp_md.write(content_to_convert)
            temp_md_path = temp_md.name

        # Create output file path
        output_filename = f"converted_asset_{asset.id}.{export_type}"
        printer.yellow(output_filename, "OUTPUT FILENAME")
        output_path = f"{UPLOADS_PATH}/converted/{output_filename}"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Convert using pandoc
        try:
            # Build pandoc command based on export type
            pandoc_cmd = ["pandoc", temp_md_path, "-o", output_path]

            # Add format-specific options
            if export_type == "pdf":
                pandoc_cmd.extend(["--pdf-engine=xelatex"])
            elif export_type == "docx":
                pandoc_cmd.extend(
                    ["--reference-doc=template.docx"]
                    if os.path.exists("template.docx")
                    else []
                )
            elif export_type == "html":
                pandoc_cmd.extend(
                    ["--standalone", "--css=style.css"]
                    if os.path.exists("style.css")
                    else []
                )

            result = subprocess.run(
                pandoc_cmd, capture_output=True, text=True, check=True
            )
        except subprocess.CalledProcessError as e:
            os.unlink(temp_md_path)  # Clean up temp file
            raise HTTPException(
                status_code=500, detail=f"Error converting file: {e.stderr}"
            )
        except FileNotFoundError:
            os.unlink(temp_md_path)  # Clean up temp file
            raise HTTPException(
                status_code=500,
                detail="Pandoc not found. Please install pandoc to use this feature.",
            )

        # Clean up temporary file
        os.unlink(temp_md_path)

        res = {
            "retrieve_url": f"/api/download-converted/{output_filename}",
            "filename": output_filename,
        }
        return JSONResponse(res)

    except HTTPException:
        raise
    except Exception as e:
        printer.red(f"Error converting asset {asset_id}: {str(e)}", "CONVERT_ASSET")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/convert/supported-types")
async def get_supported_export_types():
    """Get list of supported export types for asset conversion"""
    supported_types = [
        # Document formats
        {"type": "html", "name": "HTML", "description": "Web page format"},
        {"type": "pdf", "name": "PDF", "description": "Portable Document Format"},
        {
            "type": "docx",
            "name": "Word Document",
            "description": "Microsoft Word format",
        },
        {
            "type": "odt",
            "name": "OpenDocument",
            "description": "OpenDocument Text format",
        },
        {"type": "rtf", "name": "Rich Text", "description": "Rich Text Format"},
        {"type": "txt", "name": "Plain Text", "description": "Simple text format"},
        # Markup formats
        {"type": "md", "name": "Markdown", "description": "Markdown format"},
        {
            "type": "gfm",
            "name": "GitHub Flavored Markdown",
            "description": "GitHub Flavored Markdown",
        },
        {
            "type": "commonmark",
            "name": "CommonMark",
            "description": "CommonMark format",
        },
        # {"type": "asciidoc", "name": "AsciiDoc", "description": "AsciiDoc format"},
        # {
        #     "type": "rst",
        #     "name": "reStructuredText",
        #     "description": "reStructuredText format",
        # },
        # {"type": "org", "name": "Org Mode", "description": "Emacs Org mode format"},
        # Presentation formats
        {
            "type": "pptx",
            "name": "PowerPoint",
            "description": "Microsoft PowerPoint format",
        },
        {
            "type": "odp",
            "name": "OpenDocument Presentation",
            "description": "OpenDocument presentation format",
        },
        # {
        #     "type": "beamer",
        #     "name": "Beamer",
        #     "description": "LaTeX Beamer presentation",
        # },
        # {
        #     "type": "revealjs",
        #     "name": "RevealJS",
        #     "description": "RevealJS presentation format",
        # },
        # Publishing formats
        {"type": "epub", "name": "EPUB", "description": "E-book format"},
        {"type": "latex", "name": "LaTeX", "description": "LaTeX document format"},
        # {"type": "tex", "name": "TeX", "description": "TeX document format"},
        # Data formats
        {"type": "json", "name": "JSON", "description": "JavaScript Object Notation"},
        {"type": "yaml", "name": "YAML", "description": "YAML format"},
        {"type": "xml", "name": "XML", "description": "Extensible Markup Language"},
        # Wiki formats
        # {
        #     "type": "mediawiki",
        #     "name": "MediaWiki",
        #     "description": "MediaWiki markup format",
        # },
        {"type": "jira", "name": "Jira", "description": "Jira markup format"},
        # {"type": "zimwiki", "name": "ZimWiki", "description": "ZimWiki format"},
        # {"type": "vimwiki", "name": "VimWiki", "description": "VimWiki format"},
        # {"type": "xwiki", "name": "XWiki", "description": "XWiki format"},
        # Documentation formats
        {"type": "man", "name": "Man Page", "description": "Unix manual page format"},
        # {"type": "docbook4", "name": "DocBook 4", "description": "DocBook 4 format"},
        # {"type": "docbook5", "name": "DocBook 5", "description": "DocBook 5 format"},
        # # Academic formats
        # {"type": "jats", "name": "JATS", "description": "Journal Article Tag Suite"},
        # {
        #     "type": "jats_archiving",
        #     "name": "JATS Archiving",
        #     "description": "JATS Archiving format",
        # },
        # {
        #     "type": "jats_publishing",
        #     "name": "JATS Publishing",
        #     "description": "JATS Publishing format",
        # },
        # {
        #     "type": "jats_articleauthoring",
        #     "name": "JATS Article Authoring",
        #     "description": "JATS Article Authoring format",
        # },
        # Other formats
        # {
        #     "type": "opml",
        #     "name": "OPML",
        #     "description": "Outline Processor Markup Language",
        # },
        # {"type": "native", "name": "Native", "description": "Pandoc native format"},
        # {"type": "icml", "name": "InCopy", "description": "Adobe InCopy format"},
        # {
        #     "type": "tei",
        #     "name": "TEI",
        #     "description": "Text Encoding Initiative format",
        # },
        # {"type": "t2t", "name": "txt2tags", "description": "txt2tags format"},
    ]
    return {"supported_types": supported_types}


@router.get("/download-converted/{filename}")
async def download_file(filename: str):
    # Get the file, reutnr the content bu also deleteds the file
    file_path = f"{UPLOADS_PATH}/converted/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, filename=filename)


@router.post("/request-changes/{asset_id}")
async def request_changes_route(
    asset_id: str,
    changes: str = Form(...),
    not_id: str = Form(...),
    session: AsyncSession = Depends(get_session),
    x_user_email: str = Header(...),
):

    # Verify exists and the workflow execution is owned by the user
    result = await session.execute(
        select(Asset)
        .options(
            selectinload(Asset.workflow_execution)
            .selectinload(WorkflowExecution.workflow)
            .selectinload(Workflow.user)
        )
        .where(Asset.id == asset_id)
    )
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if (
        not asset.workflow_execution
        or not asset.workflow_execution.workflow
        or not asset.workflow_execution.workflow.user
    ):
        raise HTTPException(status_code=404, detail="Asset relationships not found")

    if asset.workflow_execution.workflow.user.email != x_user_email:
        raise HTTPException(status_code=403, detail="Not allowed")

    printer.yellow(changes, "CHANGES")
    workflow_execution_id = asset.workflow_execution.id
    async_request_changes.delay(workflow_execution_id, asset_id, changes, not_id)
    return {"message": "Changes requested"}
