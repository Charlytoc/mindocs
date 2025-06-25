import json
import os
from datetime import datetime

from server.utils.printer import Printer
from server.utils.redis_cache import redis_client
from server.ai.ai_interface import AIInterface
from server.models import Case, Attachment, Demand
from server.db import session_context_sync
from sqlalchemy import select
import json
import os
from datetime import datetime

printer = Printer("GENERATE_INITIAL_DEMAND")


def read_machote_template(template_name: str = "demanda") -> str:
    """Lee el template HTML del machote especificado."""
    template_path = f"server/machotes/{template_name}.html"
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        printer.error(f"No se encontró el template: {template_path}")
        return ""


# def extract_variables_from_template(html_template: str) -> dict:
#     """Extrae las variables del template HTML usando regex."""
#     variables = {}
#     # Buscar patrones como {{ variable_name }}
#     pattern = r"\{\{\s*(\w+)\s*\}\}"
#     matches = re.findall(pattern, html_template)

#     for match in matches:
#         variables[match] = f"[{match.upper().replace('_', ' ')}]"

#     return variables


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


def generate_initial_demand(case_id: str):
    printer.info(f"Generando demanda inicial para el caso {case_id}")
    redis_client.publish(
        "case_updates",
        json.dumps({"case_id": case_id, "log": "Generando demanda inicial."}),
    )

    try:
        # Leer el template HTML
        html_template = read_machote_template("demanda")
        if not html_template:
            raise Exception("No se pudo leer el template HTML")

        attachments_data = get_attachments_data(case_id)
        if not attachments_data:
            raise Exception("No se encontraron attachments analizados para este caso")

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
            summary_context = f"\n\nCONTEXTO DEL CASO (Resumen proporcionado por el abogado):\n{case_summary}\n\n"

        current_date = datetime.now().strftime("%d/%m/%Y")

        system_prompt = (
            "Eres un asistente legal especializado en la generación de demandas iniciales. "
            "Tu tarea es generar una demanda inicial para un caso basándote en el análisis de los documentos proporcionados. Y los tipos de demanda seleccionados por el usuario."
            "Debes generar el HTML de la demanda inicial, reemplazando las variables que correspondan del ejemplo proporcionado, eliminando las partes innecesarias para el caso cuando sea menester, y agregando las partes necesarias para el caso."
            "Asegúrate de que la demanda refleje los hechos y circunstancias descritas en el resumen del caso."
            f"La fecha actual es {current_date}."
            "Este es el template de la demanda inicial:"
            f"{html_template}"
        )

        user_prompt = f"""
Datos de los anexos analizados:
---
{attachments_data}
---

Resumen del caso:
---
{summary_context}
---

Genera el HTML completo de la demanda inicial reemplazando todas las variables con la información extraída de los anexos y el resumen del caso. 


Si falta algún dato o documento necesario según el tipo de demanda: Por ejemplo: Si se requiere separación de bienes, deben haber anexos que hagan referencia a los bienes. O si hay guardia y custodia de menores, deben haber anexos que hagan referencia a los menores. En casos donde algún documento haga falta, díceilo al usuario en un warning al final de la demanda.


El documento producido no debe tener nada que no sea útil para el caso.

"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        redis_client.publish(
            "case_updates",
            json.dumps({"case_id": case_id, "log": "Generando HTML con IA..."}),
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

            # Crear nueva demanda
            demand = Demand(case_id=case_id, version=1, html=html_content, feedback="")
            session.add(demand)
            session.commit()

            printer.green(f"Demanda inicial generada y guardada para el caso {case_id}")

        # Notificar éxito
        redis_client.publish(
            "case_updates",
            json.dumps(
                {
                    "case_id": case_id,
                    "log": "Demanda inicial generada exitosamente.",
                    # "demand_id": str(demand.id),
                    # "temp_file_path": temp_file_path,
                    "status": "DONE",
                }
            ),
        )

        return f"Demanda inicial generada para el caso {case_id}"

    except Exception as e:
        error_msg = f"Error generando demanda inicial: {str(e)}"
        printer.error(error_msg)
        redis_client.publish(
            "case_updates",
            json.dumps({"case_id": case_id, "log": error_msg, "error": True}),
        )
        raise e
