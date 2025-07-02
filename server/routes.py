import os
import tempfile
import subprocess
from typing import List
import shutil
import traceback

from fastapi import APIRouter, Form, File, UploadFile, Depends, HTTPException
from typing import List, Optional
from fastapi.responses import JSONResponse


from sqlalchemy.ext.asyncio import AsyncSession
from server.utils.printer import Printer
from server.utils.csv_logger import CSVLogger
from server.db import get_session
from server.models import Case, Attachment, CaseStatus, AttachmentStatus
from server.tasks import read_attachments
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from server.utils.pdf_reader import DocumentReader

csv_logger = CSVLogger()
printer = Printer("ROUTES")

UPLOADS_PATH = "uploads"

router = APIRouter(prefix="/api")


@router.post("/upload-files")
async def upload_files(
    files: List[UploadFile] = File(...),
    session: AsyncSession = Depends(get_session),
    resumen_del_caso: str = Form(...),
    selected_items: str = Form(...),
    juzgado: str = Form(...),
    abogados_asociados: str = Form(...),
):
    try:
        summary = f"Resumen del caso proporcionado por el usuario: {resumen_del_caso}\n\nTipos de demanda seleccionados por el usuario: {selected_items}\n\nAbogados asociados al caso: {abogados_asociados}\n\nJuzgado a cargo (en todos los documentos debe aparecer exactamente así): {juzgado}"

        case = Case(status=CaseStatus.PENDING, summary=summary)
        session.add(case)
        await session.flush()  # Para obtener el ID del caso

        # Crear directorio para el caso
        case_upload_path = f"{UPLOADS_PATH}/{case.id}"
        os.makedirs(case_upload_path, exist_ok=True)

        attachments = []

        for index, file in enumerate(files, 1):
            # Crear el attachment en la base de datos
            attachment = Attachment(
                case_id=case.id,
                name=file.filename,
                anexo=index,
                status=AttachmentStatus.PENDING,
            )
            session.add(attachment)
            await session.flush()

            file_extension = (
                os.path.splitext(file.filename)[1] if "." in file.filename else ""
            )
            file_path = f"{case_upload_path}/{attachment.id}{file_extension}"

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            attachments.append(attachment)

        # Commit de todos los cambios
        await session.commit()

        printer.info(f"Case {case.id} created with {len(attachments)} attachments")

        read_attachments.delay(case.id)

        return JSONResponse(
            content={
                "case_id": str(case.id),
                "attachments_count": len(attachments),
                "status": case.status.value,
            }
        )

    except Exception as e:
        await session.rollback()
        printer.error(f"Error uploading files: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Error uploading files", "details": str(e)},
        )


@router.post("/upload-files-two")
async def upload_files_two(
    juzgado: str = Form(...),
    acta_de_matrimonio: UploadFile = File(...),
    solicitante_adjuntos: UploadFile = File(...),
    propuesta_convenio: str = Form(...),
    propuesta_convenio_file: Optional[UploadFile] = File(None),
    hijos: str = Form(...),
    hijos_files: Optional[List[UploadFile]] = File(None),
    convenio: Optional[UploadFile] = File(None),
    otros_anexos: Optional[List[UploadFile]] = File(None),
    session: "AsyncSession" = Depends(get_session),
):
    # print(hijos, "hijos")
    # print(hijos_files, "hijos_files")
    # print(propuesta_convenio, "propuesta_convenio")
    # print(propuesta_convenio_file, "propuesta_convenio_file")
    # print(convenio, "convenio")
    # print(otros_anexos, "otros_anexos")
    # print(juzgado, "juzgado")
    # print(solicitante_adjuntos, "solicitante_adjuntos")
    # print(acta_de_matrimonio, "acta_de_matrimonio")

    try:
        summary = f"""        p
Juzgado a cargo (en todos los documentos debe aparecer exactamente así): {juzgado}
"""

        summary += f"\nActa de Matrimonio: {acta_de_matrimonio.filename}"
        summary += (
            f"\nAdjunto del solicitante (Acta, INE): {solicitante_adjuntos.filename}"
        )

        if hijos:
            for idx, hijo_file in enumerate(hijos_files):
                summary += f"\nActa de nacimiento de hijo {idx+1}: {hijo_file.filename}"

        if convenio:
            summary += f"\nConvenio: {convenio.filename}"

        if otros_anexos:
            for idx, anexo in enumerate(otros_anexos):
                summary += f"\nOtro anexo {idx+1}: {anexo.filename}"

        # --- Guardado de archivos y base de datos ---
        case = Case(status=CaseStatus.PENDING, summary=summary)
        session.add(case)
        await session.flush()  # Para obtener el ID del caso

        case_upload_path = f"{UPLOADS_PATH}/{case.id}"
        os.makedirs(case_upload_path, exist_ok=True)

        attachments = []
        idx = 1

        def save_and_attach(file: UploadFile, anexo: int, name: str):
            attachment = Attachment(
                case_id=case.id,
                name=name,
                anexo=anexo,
                status=AttachmentStatus.PENDING,
            )
            session.add(attachment)
            return attachment

        all_files = [
            acta_de_matrimonio,
            solicitante_adjuntos,
            convenio,
            propuesta_convenio_file,
            *(hijos_files or []),
            *(otros_anexos or []),
        ]
        for file in all_files:
            if file:
                attachment = save_and_attach(file, idx, file.filename)
                await session.flush()
                ext = os.path.splitext(file.filename)[1]
                file_path = f"{case_upload_path}/{attachment.id}{ext}"
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                attachments.append(attachment)
                idx += 1

        await session.commit()

        printer.info(f"Case {case.id} created with {len(attachments)} attachments")
        read_attachments.delay(case.id)

        return JSONResponse(
            content={
                "case_id": str(case.id),
                "attachments_count": len(attachments),
                "status": case.status.value,
                "summary": summary,
            }
        )

    except Exception as e:
        await session.rollback()
        # print all the traceback
        traceback.print_exc()
        printer.error(f"Error uploading files: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Error uploading files", "details": str(e)},
        )


@router.get("/case/{case_id}/results")
async def get_case_results(case_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Case)
        .options(
            selectinload(Case.demands),
            selectinload(Case.agreements),
        )
        .where(Case.id == case_id)
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Get the latest demand and agreement
    demand = case.demands[-1] if case.demands else None
    agreement = case.agreements[-1] if case.agreements else None

    return JSONResponse(
        content={
            "demand": demand.html if demand else None,
            "agreement": agreement.html if agreement else None,
            "summary": case.summary,
            "status": case.status.value,
        }
    )


# get /case/{case_id}/status
# Returns the status of the case


@router.get("/case/{case_id}/status")
async def get_case_status(case_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Case)
        .options(
            selectinload(Case.demands),
            selectinload(Case.agreements),
        )
        .where(Case.id == case_id)
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    return JSONResponse(
        content={
            "status": case.status.value,
            "has_demands": len(case.demands) > 0,
            "has_agreements": len(case.agreements) > 0,
        }
    )


@router.put("/case/{case_id}/demand")
async def update_demand(
    case_id: str,
    session: AsyncSession = Depends(get_session),
    html_content: str = Form(...),
):
    try:
        result = await session.execute(
            select(Case).options(selectinload(Case.demands)).where(Case.id == case_id)
        )
        case = result.scalar_one_or_none()

        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        # Get the latest demand or create a new one
        latest_demand = case.demands[-1] if case.demands else None

        if latest_demand:
            # Update existing demand
            latest_demand.html = html_content
            latest_demand.version += 1
        else:
            # Create new demand
            from server.models import Demand

            new_demand = Demand(case_id=case.id, html=html_content, version=1)
            session.add(new_demand)

        await session.commit()

        return JSONResponse(
            content={"message": "Demand updated successfully", "case_id": str(case.id)}
        )
    except Exception as e:
        await session.rollback()
        printer.error(f"Error updating demand: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating demand: {str(e)}")


@router.put("/case/{case_id}/agreement")
async def update_agreement(
    case_id: str,
    session: AsyncSession = Depends(get_session),
    html_content: str = Form(...),
):
    try:
        result = await session.execute(
            select(Case)
            .options(selectinload(Case.agreements))
            .where(Case.id == case_id)
        )
        case = result.scalar_one_or_none()

        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        # Get the latest agreement or create a new one
        latest_agreement = case.agreements[-1] if case.agreements else None

        if latest_agreement:
            # Update existing agreement
            latest_agreement.html = html_content
            latest_agreement.version += 1
        else:
            # Create new agreement
            from server.models import Agreement

            new_agreement = Agreement(case_id=case.id, html=html_content, version=1)
            session.add(new_agreement)

        await session.commit()

        return JSONResponse(
            content={
                "message": "Agreement updated successfully",
                "case_id": str(case.id),
            }
        )
    except Exception as e:
        await session.rollback()
        printer.error(f"Error updating agreement: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error updating agreement: {str(e)}"
        )


@router.post("/case/{case_id}/request-ai-changes")
async def request_ai_changes(
    case_id: str,
    session: AsyncSession = Depends(get_session),
    document_type: str = Form(...),  # "demand" or "agreement"
    user_feedback: str = Form(...),
):
    try:
        result = await session.execute(
            select(Case)
            .options(selectinload(Case.demands), selectinload(Case.agreements))
            .where(Case.id == case_id)
        )
        case = result.scalar_one_or_none()

        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        # Log the user feedback for now (in the future this will trigger AI processing)
        printer.info(f"AI change request for case {case_id}:")
        printer.info(f"Document type: {document_type}")
        printer.info(f"User feedback: {user_feedback}")

        # Store feedback in the appropriate document
        if document_type == "demand" and case.demands:
            latest_demand = case.demands[-1]
            latest_demand.feedback = user_feedback
        elif document_type == "agreement" and case.agreements:
            latest_agreement = case.agreements[-1]
            latest_agreement.feedback = user_feedback

        await session.commit()

        return JSONResponse(
            content={
                "message": "AI change request received successfully",
                "case_id": str(case.id),
                "document_type": document_type,
                "feedback": user_feedback,
            }
        )
    except Exception as e:
        await session.rollback()
        printer.error(f"Error processing AI change request: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing AI change request: {str(e)}"
        )


@router.post("/case/{case_id}/approve")
async def approve_case(case_id: str, session: AsyncSession = Depends(get_session)):
    try:
        # Cargar el caso con demandas y acuerdos
        result = await session.execute(
            select(Case)
            .options(selectinload(Case.demands), selectinload(Case.agreements))
            .where(Case.id == case_id)
        )
        case = result.scalar_one_or_none()

        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        # Obtener la última demanda y acuerdo
        last_demand = max(
            case.demands, key=lambda d: (d.version, d.created_at), default=None
        )
        last_agreement = max(
            case.agreements, key=lambda a: (a.version, a.created_at), default=None
        )

        if not last_demand or not last_agreement:
            raise HTTPException(
                status_code=400, detail="No demand or agreement found for this case"
            )

        # Directorio de salida
        output_dir = os.path.join("outputs", str(case_id))
        os.makedirs(output_dir, exist_ok=True)

        # Instead of generating two PDFs, we need to merge the two HTML files into one
        # and then convert it to a PDF
        merged_html = last_demand.html + "<hr/>" + last_agreement.html

        final_document_path = os.path.join(output_dir, "document.pdf")

        # Guardar HTMLs temporales y convertirlos a PDF
        with tempfile.NamedTemporaryFile(
            suffix=".html", delete=False, mode="w", encoding="utf-8"
        ) as tmp_document:
            tmp_document.write(merged_html)
            tmp_document_path = tmp_document.name

        try:
            subprocess.run(
                ["pandoc", tmp_document_path, "-o", final_document_path], check=True
            )
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"Pandoc error: {e}")
        finally:
            os.remove(tmp_document_path)

        # Actualizar estado del caso
        case.status = CaseStatus.APPROVED
        await session.commit()

        return JSONResponse(
            content={
                "message": "Case approved and PDFs generated successfully",
                "case_id": str(case.id),
                "status": case.status.value,
            }
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error approving case: {str(e)}")
