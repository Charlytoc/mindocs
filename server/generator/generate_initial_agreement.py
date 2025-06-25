from server.utils.printer import Printer
from server.utils.redis_cache import redis_client
from server.ai.ai_interface import AIInterface
from server.models import Case, Attachment, Agreement
from server.db import session_context_sync
from sqlalchemy import select
import json
import os
from datetime import datetime

printer = Printer("GENERATE_INITIAL_AGREEMENT")


def read_machote_template(template_name: str = "convenio") -> str:
    """Lee el template HTML del machote especificado."""
    template_path = f"server/machotes/{template_name}.html"
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        printer.error(f"No se encontró el template: {template_path}")
        return ""


def get_attachments_data(case_id: str) -> str:
    """Obtiene todos los attachments analizados para un caso."""
    with session_context_sync() as session:
        attachments = (
            session.execute(
                select(Attachment).where(
                    Attachment.case_id == case_id, Attachment.status == "DONE"
                )
            )
            .scalars()
            .all()
        )

        attachments_data = []
        for attachment in attachments:
            attachments_data.append(
                {
                    "name": attachment.name,
                    "anexo": attachment.anexo,
                    "brief": attachment.brief,
                    "findings": attachment.findings,
                }
            )

        return json.dumps(attachments_data, indent=2, ensure_ascii=False)


def get_case_summary(case_id: str) -> str:
    """Obtiene el summary del caso."""
    with session_context_sync() as session:
        case = session.execute(
            select(Case).where(Case.id == case_id)
        ).scalar_one_or_none()
        return case.summary if case else ""


def save_html_as_temp_file(html_content: str, case_id: str) -> str:
    """Guarda el HTML generado como archivo temporal y retorna la ruta."""
    try:
        # Crear directorio temporal si no existe
        temp_dir = "temp_agreements"
        os.makedirs(temp_dir, exist_ok=True)

        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"convenio_inicial_{case_id}_{timestamp}.html"
        file_path = os.path.join(temp_dir, filename)

        # Guardar el archivo
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        printer.green(f"HTML guardado como archivo temporal: {file_path}")
        return file_path

    except Exception as e:
        printer.error(f"Error guardando archivo temporal: {e}")
        return ""


def generate_initial_agreement(case_id: str):
    printer.info(f"Generando convenio inicial para el caso {case_id}")
    redis_client.publish(
        "case_updates",
        json.dumps({"case_id": case_id, "log": "Generando convenio inicial."}),
    )

    try:
        # Leer el template HTML
        html_template = read_machote_template("convenio")
        if not html_template:
            raise Exception("No se pudo leer el template HTML del convenio")

        # Obtener datos de los attachments
        attachments_data = get_attachments_data(case_id)
        if not attachments_data:
            raise Exception("No se encontraron attachments analizados para este caso")

        # Obtener el summary del caso
        case_summary = get_case_summary(case_id)

        # Generar HTML usando IA
        ai_interface = AIInterface(
            provider=os.getenv("PROVIDER", "ollama"),
            api_key=os.getenv("PROVIDER_API_KEY", "asdasd"),
            base_url=os.getenv("PROVIDER_BASE_URL", None),
        )

        # Crear el contexto con el summary del caso
        summary_context = ""
        if case_summary:
            summary_context = f"\n\nCONTEXTO DEL CASO (Resumen proporcionado por el abogado, usalo para generar el convenio):\n{case_summary}\n\n"

        current_date = datetime.now().strftime("%d/%m/%Y")

        system_prompt = (
            "Eres un asistente legal especializado en la generación de convenios de divorcio. "
            "Tu tarea es generar un convenio de divorcio incausado basándote en el análisis de los documentos proporcionados. "
            "Debes generar el HTML del convenio reemplazando las variables del template con la información extraída de los documentos. "
            "IMPORTANTE: Considera el contexto del caso proporcionado por el abogado al generar el convenio. "
            "Asegúrate de que el convenio refleje los hechos y circunstancias descritas en el resumen del caso. "
            "El documento producido no debe tener nada que no sea útil para el caso. "
            f"La fecha actual es {current_date}." + summary_context
        )

        user_prompt = f"""
Template HTML del Convenio:
{html_template}

Datos de los attachments analizados:
{attachments_data}

Genera el HTML completo del convenio inicial reemplazando todas las variables con la información extraída de los attachments.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        redis_client.publish(
            "case_updates",
            json.dumps(
                {"case_id": case_id, "log": "Generando HTML del convenio con IA..."}
            ),
        )

        response = ai_interface.chat(
            messages=messages, model=os.getenv("MODEL", "gemma3")
        )

        # Limpiar la respuesta (remover markdown si existe)
        html_content = response.strip()
        if html_content.startswith("```html"):
            html_content = html_content[7:]
        if html_content.endswith("```"):
            html_content = html_content[:-3]
        html_content = html_content.strip()

        # Guardar en la base de datos
        with session_context_sync() as session:
            case = session.get(Case, case_id)
            if not case:
                raise Exception(f"No se encontró el caso {case_id}")

            # Crear nuevo convenio
            agreement = Agreement(
                case_id=case_id, version=1, html=html_content, feedback=""
            )
            session.add(agreement)
            session.commit()

            printer.green(
                f"Convenio inicial generado y guardado para el caso {case_id}"
            )

        # Notificar éxito
        redis_client.publish(
            "case_updates",
            json.dumps(
                {
                    "case_id": case_id,
                    "log": "Convenio inicial generado exitosamente.",
                    "agreement_id": str(agreement.id),
                    "agreement_completed": True,
                }
            ),
        )

        return f"Convenio inicial generado para el caso {case_id}"

    except Exception as e:
        error_msg = f"Error generando convenio inicial: {str(e)}"
        printer.error(error_msg)
        redis_client.publish(
            "case_updates",
            json.dumps({"case_id": case_id, "log": error_msg, "error": True}),
        )
        raise e
