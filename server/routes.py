import os
import shutil

# import traceback
from typing import List, Optional
from sqlalchemy.orm import selectinload
from server.tasks import async_process_workflow_execution

from fastapi import APIRouter, Form, File, UploadFile, Depends, HTTPException, Header
from fastapi.responses import JSONResponse

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

csv_logger = CSVLogger()
printer = Printer("ROUTES")

UPLOADS_PATH = "uploads"

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
            selectinload(Workflow.example_assets),
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
        # "examples": [
        #     {"id": str(a.id), "name": a.name, "type": a.asset_type, "brief": a.brief}
        #     for a in workflow.example_assets
        # ],
    }


@router.post("/workflow")
async def create_workflow(
    name: str = Form(...),
    description: str = Form(...),
    instructions: str = Form(...),
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


# --- WORKFLOW EXECUTION ----------------------------------


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


@router.get("/workflow-execution/{execution_id}")
async def get_execution(
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
                "content": a.extracted_text,
            }
            for a in assets_upload
        ],
        "generated": [
            {
                "id": str(a.id),
                "name": a.name,
                "type": a.asset_type,
                "description": a.brief,
                "content": a.extracted_text,
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
