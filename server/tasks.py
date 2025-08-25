# from server.generator.read_attachments import extract_and_update_attachments_text
# from server.generator.analize_attachment import analyze_text_with_ai
# from server.generator.generate_initial_demand import generate_initial_demand
# from server.generator.generate_initial_agreement import generate_initial_agreement
from server.celery_app import celery
import time
import json
from server.utils.redis_cache import redis_client
from typing import List

from server.utils.printer import Printer


from server.utils.processor import (
    process_workflow_execution,
    request_changes,
    process_example_files,
    process_template_file,
)

printer = Printer("TASKS")


@celery.task(
    name="process_workflow_execution",
    autoretry_for=(Exception,),
    retry_kwargs={"countdown": 10},
    retry_backoff=True,
    bind=True,
    max_retries=5,
)
def async_process_workflow_execution(self, workflow_execution_id: str):
    try:
        printer.info(f"Procesando ejecución de workflow {workflow_execution_id}")
        redis_client.publish(
            "workflow_updates",
            json.dumps(
                {
                    "workflow_execution_id": str(
                        workflow_execution_id
                    ),  # <-- fuerza a str
                    "log": "¡Proceso iniciado! Procesando archivos.",
                    "status": "PROCESSING",
                    "assets_ready": False,
                }
            ),
        )
        printer.green(
            f"Message sent to socketio to room: workflow_{workflow_execution_id}"
        )

        return process_workflow_execution(str(workflow_execution_id))
    except Exception as e:
        printer.error(f"Error al leer los archivos: {e}")
        raise e


@celery.task(
    name="request_changes",
    autoretry_for=(Exception,),
    retry_kwargs={"countdown": 10},
    retry_backoff=True,
    bind=True,
    max_retries=5,
)
def async_request_changes(
    self, workflow_execution_id: str, asset_id: str, changes: str, not_id: str
):
    try:
        printer.info(f"Solicitando cambios para el asset {asset_id}")
        return request_changes(
            str(workflow_execution_id), str(asset_id), changes, not_id
        )
    except Exception as e:
        printer.error(f"Error al solicitar cambios: {e}")
        raise e


@celery.task(
    name="process_example_files",
    autoretry_for=(Exception,),
    retry_kwargs={"countdown": 10},
    retry_backoff=True,
    bind=True,
    max_retries=5,
)
def async_process_example_files(
    self,
    workflow_id: str,
    file_paths: List[str],
    output_examples_description: List[str],
):
    try:
        printer.info(f"Procesando archivos de ejemplo para el workflow {workflow_id}")
        return process_example_files(
            workflow_id, file_paths, output_examples_description
        )
    except Exception as e:
        printer.error(f"Error al procesar archivos de ejemplo: {e}")
        raise e


@celery.task(
    name="process_template_file",
    autoretry_for=(Exception,),
    retry_kwargs={"countdown": 10},
    retry_backoff=True,
    bind=True,
    max_retries=5,
)
def async_process_template_file(self, workflow_id: str, file_path: str):
    try:
        printer.info(f"Procesando plantilla para el workflow {workflow_id}")
        return process_template_file(workflow_id, file_path)
    except Exception as e:
        printer.error(f"Error al procesar plantilla: {e}")
        raise e
