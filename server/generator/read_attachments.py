from server.db import session_context_sync
from server.models import Attachment  # Ajusta el import según tu estructura
import traceback
from celery import chord
from server.utils.printer import Printer
from server.utils.pdf_reader import DocumentReader
from server.utils.image_reader import ImageReader
import os
import json
from sqlalchemy import select
from server.utils.redis_cache import RedisCache

printer = Printer("READ_ATTACHMENTS")


def extract_and_update_attachments_text(case_id: str):
    from server.tasks import analyze_attachment, on_all_analyses_done

    redis_cache = RedisCache()
    with session_context_sync() as session:
        try:
            attachments = session.execute(
                select(Attachment).where(Attachment.case_id == case_id)
            )
            attachments = attachments.scalars().all()
            if not attachments:
                printer.yellow(f"No se encontraron attachments para el caso {case_id}")
                return

            document_reader = DocumentReader()
            image_reader = ImageReader()

            for attachment in attachments:
                file_extension = os.path.splitext(attachment.name)[1]
                file_path = (
                    f"uploads/{attachment.case_id}/{attachment.id}{file_extension}"
                )
                ext = file_extension.lower()
                extracted_text = None

                try:
                    if ext in [".pdf", ".docx"]:
                        extracted_text = document_reader.read(file_path)
                    elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
                        extracted_text = image_reader.read(file_path)
                    elif ext in [".txt", ".xml", ".html", ".md", ".json", ".csv"]:
                        with open(file_path, "r", encoding="utf-8") as f:
                            extracted_text = f.read()
                    else:
                        printer.yellow(f"Extensión no soportada: {ext} en {file_path}")
                        continue

                    attachment.extracted_text = extracted_text
                    printer.green(f"Texto extraído y actualizado para: {file_path}")

                    redis_cache.publish(
                        "case_updates",
                        json.dumps(
                            {
                                "case_id": str(case_id),
                                "attachment_id": str(attachment.id),
                                "attachment_name": attachment.name,
                                "extracted_text": extracted_text,
                                "log": f"Se extrajo el texto de {attachment.name}.",
                            }
                        ),
                    )
                except Exception as e:
                    printer.error(f"Error al procesar {file_path}: {e}")

            session.commit()

            header = [
                analyze_attachment.s(str(attachment.id), str(case_id))
                for attachment in attachments
            ]
            # Dispara el chord: cuando todas las tareas terminen, ejecuta la callback
            chord(header)(on_all_analyses_done.s(str(case_id)))
            printer.green("Todos los attachments procesados y actualizados.")
            return "Attachments processed and updated."
        except Exception as e:
            printer.error(f"Error general: {e}")
            traceback.print_exc()
            session.rollback()
