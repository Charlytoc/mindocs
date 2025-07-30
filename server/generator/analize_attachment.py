# import re
# import os
# import json
# from server.utils.printer import Printer
# from server.utils.redis_cache import redis_client
# from server.ai.ai_interface import AIInterface
# from server.models import Asset, WorkflowExecution
# from server.db import session_context_sync
# from sqlalchemy import select

# printer = Printer("ANALYZE_ATTACHMENT")


# def get_variables_from_html() -> dict:
#     variables = {
#         "detalle_bienes_inmuebles": "[enumerar brevemente con incisos, los bienes comunes a repartir, si los hay, o indicar que no existen bienes sujetos a liquidación] Se destaca, que dicho bien inmueble fue adquirido a través de [Tipo de contrato de adquisición, ejemplo: compraventa, donación, etc.] ",
#         "detalle_hijos": "Nombres y edades de todos los hijos, si los hay",
#         "detalles_abogados": "[NOMBRE COMPLETO DE LA PERSONA ABOGADA QUE REPRESENTARA EN JUICIO A LA PERSONA PROMOVENTE], con número de cédula profesional [número de cédula profesional de la persona abogada], de todos los abogados que intervienen en el proceso, señalar el nombre de la persona abogada que tiene acceso al sistema",
#         "domicilio_conyugal": "Direccion de domicilio conyugal",
#         "domicilio_del_demandado": "DOMICILIO DEL DEMANDADO",
#         "domicilio_del_promovente": "DOMICILIO DEL PROMOVENTE",
#         "fecha_de_cuidado": "FECHA DE CUMPLIMIENTO DE LA OBLIGACION DE CUIDADO",
#         "fecha_matrimonio": "FECHA DE MATRIMONIO",
#         "nombre_completo_del_demandado": "[NOMBRE COMPLETO DE LA PERSONA QUE ES DEMANDADA]",
#         "nombre_del_promovente": "[NOMBRE COMPLETO DE LA PERSONA QUE PROMUEVE EL DIVORCIO]",
#         "nombre_promovente": "[NOMBRE DE LA PERSONA QUE PROMUEVE EL DIVORCIO]",
#         "persona_abogada_acceso_al_sistema": "[NOMBRE COMPLETO DE LA PERSONA QUE TIENE ACCESO AL SISTEMA]",
#         "persona_autorizada_notificaciones": "[NOMBRE COMPLETO DE LA PERSONA QUE TIENE AUTORIZACION PARA RECIBIR NOTIFICACIONES]",
#         "tipo_regimen_conyugal": "sociedad conyugal / separación de bienes",
#     }
#     return json.dumps(variables)


# def extract_brief_and_findings(text: str) -> dict:
#     """
#     Extrae el contenido entre las etiquetas <brief> y <findings> de un texto.
#     Retorna un diccionario con las claves 'brief' y 'findings'.
#     """
#     brief_match = re.search(r"<brief>(.*?)</brief>", text, re.DOTALL | re.IGNORECASE)
#     findings_match = re.search(
#         r"<findings>(.*?)</findings>", text, re.DOTALL | re.IGNORECASE
#     )
#     return {
#         "brief": brief_match.group(1).strip() if brief_match else "",
#         "findings": findings_match.group(1).strip() if findings_match else "",
#     }


# # completion = client.chat.completions.create(
# #     model="gpt-4.1",
# #     messages=[
# #         {
# #             "role": "user",
# #             "content": [
# #                 { "type": "text", "text": "what's in this image?" },
# #                 {
# #                     "type": "image_url",
# #                     "image_url": {
# #                         "url": f"data:image/jpeg;base64,{base64_image}",
# #                     },
# #                 },
# #             ],
# #         }
# #     ],
# # )


# def analyze_text_with_ai(attachment_id: str, workflow_execution_id: str):
#     with session_context_sync() as session:
#         attachment = session.get(Asset, attachment_id)
#         if not attachment:
#             printer.error(f"No se encontró el attachment {attachment_id}")
#             return None
#         if not attachment.extracted_text:
#             printer.error(f"No hay texto extraído para el attachment {attachment.name}")
#             return None
#         text = attachment.extracted_text

#         # Obtener el summary del caso
#         workflow_execution = session.execute(
#             select(WorkflowExecution).where(
#                 WorkflowExecution.id == workflow_execution_id
#             )
#         ).scalar_one_or_none()
#         workflow_execution_summary = (
#             workflow_execution.summary if workflow_execution else ""
#         )

#     ai_interface = AIInterface(
#         provider=os.getenv("PROVIDER", "ollama"),
#         api_key=os.getenv("PROVIDER_API_KEY", "asdasd"),
#         base_url=os.getenv("PROVIDER_BASE_URL", None),
#     )

#     # Incluir el summary del caso en el prompt
#     summary_context = ""
#     if workflow_execution_summary:
#         summary_context = f"\n\nCONTEXTO DEL CASO (Resumen proporcionado por el abogado):\n{workflow_execution_summary}\n\n"

#     system_prompt = (
#         "Eres un asistente legal. Extrae la información relevante del siguiente documento. "
#         "Que pueda ser útil para la generación de la demanda inicial del caso en cuestión. "
#         "Debes returnar tu respuesta en un formato XML de la siguiente manera: "
#         "<brief> Resumen del documento </brief><findings> Puntos relevantes del documento que puedan ser útiles para la generación de la demanda inicial, datos, nombres, fechas, montos, etc. </findings>. Durante el proceso de extracción, debes tener en cuenta las variables que se encuentran en el siguiente diccionario, extrae todas las que sean posibles dentro de <findings> y <brief>."
#         + summary_context
#         + "IMPORTANTE: Considera el contexto del caso proporcionado por el abogado al analizar este documento. "
#         "Relaciona la información del documento con los hechos descritos en el resumen del caso."
#     )

#     messages = [
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": text},
#     ]
#     redis_client.publish(
#         "case_updates",
#         json.dumps(
#             {
#                 "workflow_execution_id": workflow_execution_id,
#                 "attachment_id": attachment_id,
#                 "log": f"Iniciando análisis IA para {attachment_id}",
#             }
#         ),
#     )

#     response = ai_interface.chat(messages=messages, model=os.getenv("MODEL", "gemma3"))
#     printer.green(f"Respuesta IA para attachment {attachment_id}: {response[:200]}...")

#     # Guardar en la base de datos
#     with session_context_sync() as session:
#         attachment = session.get(Asset, attachment_id)
#         if not attachment:
#             printer.error(f"No se encontró el attachment {attachment_id} (al guardar)")
#             return None

#         result = extract_brief_and_findings(response)
#         attachment.brief = result["brief"]
#         attachment.findings = result["findings"]
#         attachment.status = "DONE"
#         session.commit()
#         printer.green(f"Análisis IA guardado en DB para attachment {attachment_id}")

#     # Publicar en Redis para notificación
#     redis_client.publish(
#         "case_updates",
#         json.dumps(
#             {
#                 "workflow_execution_id": workflow_execution_id,
#                 "attachment_id": attachment_id,
#                 "ai_analysis": result,
#                 "response": response,
#                 "log": f"Análisis IA guardado para {attachment_id}",
#             }
#         ),
#     )

#     return f"Archivo {attachment_id} analizado"
