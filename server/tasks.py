from server.generator.read_attachments import extract_and_update_attachments_text
from server.generator.analize_attachment import analyze_text_with_ai
from server.generator.generate_initial_demand import generate_initial_demand
from server.generator.generate_initial_agreement import generate_initial_agreement
from server.celery_app import celery
from celery import chord
from server.db import session_context_sync
from server.utils.printer import Printer
from server.models import Case, CaseStatus
from sqlalchemy import select

printer = Printer("TASKS")


@celery.task(
    name="read_attachments",
    autoretry_for=(Exception,),
    retry_kwargs={"countdown": 10},
    retry_backoff=True,
    bind=True,
    max_retries=5,
)
def read_attachments(self, case_id: str):
    try:
        printer.info(f"Leyendo archivos del caso {case_id}")
        return extract_and_update_attachments_text(case_id)
    except Exception as e:
        printer.error(f"Error al leer los archivos: {e}")
        raise e


@celery.task(
    name="analyze_attachment",
    autoretry_for=(Exception,),
    retry_kwargs={"countdown": 10},
    retry_backoff=True,
    bind=True,
    max_retries=5,
)
def analyze_attachment(self, attachment_id: str, case_id: str):
    try:
        printer.info(f"Analizando attachment {attachment_id} del caso {case_id}")
        return analyze_text_with_ai(attachment_id, case_id)
    except Exception as e:
        printer.error(f"Error al analizar el attachment: {e}")
        raise e


@celery.task(
    name="on_all_analyses_done",
    autoretry_for=(Exception,),
    retry_kwargs={"countdown": 10},
    retry_backoff=True,
    bind=True,
    max_retries=5,
)
def on_all_analyses_done(self, results, case_id: str):
    printer.info(
        f"Todas las analisis de los attachments del caso {case_id} han terminado"
    )

    # Import task objects, not results
    from .tasks import (
        generate_initial_demand_task,
        generate_initial_agreement_task,
        on_both_documents_generated,
    )

    # Pass signatures, not results
    chord(
        [
            generate_initial_demand_task.s(case_id),
            generate_initial_agreement_task.s(case_id),
        ]
    )(on_both_documents_generated.s(case_id))

    return f"Generación de documentos iniciada para el caso {case_id}"


@celery.task(
    name="generate_initial_demand_task",
    autoretry_for=(Exception,),
    retry_kwargs={"countdown": 10},
    retry_backoff=True,
    bind=True,
    max_retries=5,
)
def generate_initial_demand_task(self, case_id: str):
    try:
        printer.info(f"Generando demanda inicial para el caso {case_id}")
        return generate_initial_demand(case_id)
    except Exception as e:
        printer.error(f"Error al generar la demanda inicial: {e}")
        raise e


@celery.task(
    name="generate_initial_agreement_task",
    autoretry_for=(Exception,),
    retry_kwargs={"countdown": 10},
    retry_backoff=True,
    bind=True,
    max_retries=5,
)
def generate_initial_agreement_task(self, case_id: str):
    try:
        printer.info(f"Generando convenio inicial para el caso {case_id}")
        return generate_initial_agreement(case_id)
    except Exception as e:
        printer.error(f"Error al generar el convenio inicial: {e}")
        raise e


@celery.task(
    name="on_both_documents_generated",
    autoretry_for=(Exception,),
    retry_kwargs={"countdown": 10},
    retry_backoff=True,
    bind=True,
    max_retries=5,
)
def on_both_documents_generated(self, results, case_id: str):
    printer.info(
        f"Ambos documentos (demanda y convenio) han sido generados para el caso {case_id}"
    )

    from server.utils.redis_cache import redis_client
    import json

    redis_client.publish(
        "case_updates",
        json.dumps(
            {
                "case_id": case_id,
                "log": "¡Proceso completado! Demanda inicial y convenio generados exitosamente.",
                "status": "COMPLETED",
                "both_documents_ready": True,
            }
        ),
    )

    # Update the case status to COMPLETED
    with session_context_sync() as session:
        case = session.execute(select(Case).where(Case.id == case_id))
        case.status = CaseStatus.DONE
        session.commit()

    return f"Proceso completado para el caso {case_id}"
