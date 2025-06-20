#!/usr/bin/env python3
"""
Script de prueba para verificar la generación de demanda inicial y convenio.
Este script simula el proceso completo desde la subida de archivos hasta la generación de ambos documentos.
"""

# import os
import sys

# import uuid
# import json
# from datetime import datetime

# Agregar el directorio del servidor al path
sys.path.append("server")

from server.db import session_context_sync
from server.models import (
    Case,
    Attachment,
    # Demand,
    # Agreement,
    CaseStatus,
    AttachmentStatus,
)
from server.generator.generate_initial_demand import generate_initial_demand
from server.generator.generate_initial_agreement import generate_initial_agreement
from server.utils.printer import Printer

printer = Printer("TEST_BOTH_DOCUMENTS_GENERATION")


def create_test_case():
    """Crea un caso de prueba con attachments simulados."""
    with session_context_sync() as session:
        # Crear caso de prueba
        case = Case(
            status=CaseStatus.PENDING, summary="Caso de prueba para divorcio incausado"
        )
        session.add(case)
        session.flush()

        # Crear attachments de prueba con datos simulados
        test_attachments = [
            {
                "name": "acta_matrimonio.pdf",
                "anexo": 1,
                "extracted_text": """
                ACTA DE MATRIMONIO
                Número: 12345
                Fecha: 15 de febrero de 2010
                Lugar: Registro Civil de Toluca
                
                CONTRATANTES:
                Promovente: JUAN PÉREZ MARTÍNEZ
                Demandado: LAURA MARTÍNEZ GARCÍA
                
                RÉGIMEN CONYUGAL: Sociedad conyugal
                
                DOMICILIO CONYUGAL: Av. Principal 456, Toluca, Estado de México
                """,
                "brief": "Acta de matrimonio entre Juan Pérez y Laura Martínez",
                "findings": "Fecha matrimonio: 15 de febrero de 2010, Régimen: sociedad conyugal, Domicilio: Av. Principal 456, Toluca",
            },
            {
                "name": "actas_nacimiento.pdf",
                "anexo": 2,
                "extracted_text": """
                ACTAS DE NACIMIENTO
                
                HIJO 1:
                Nombre: María Pérez Martínez
                Fecha de nacimiento: 10 de marzo de 2012
                Edad actual: 12 años
                
                HIJO 2:
                Nombre: José Pérez Martínez
                Fecha de nacimiento: 5 de julio de 2015
                Edad actual: 9 años
                
                Ambos menores han estado bajo el cuidado de JUAN PÉREZ MARTÍNEZ desde el 1 de enero de 2020.
                """,
                "brief": "Actas de nacimiento de dos hijos menores",
                "findings": "Hijos: María Pérez (12 años), José Pérez (9 años), Cuidado desde: 1 de enero de 2020",
            },
            {
                "name": "documentos_bienes.pdf",
                "anexo": 3,
                "extracted_text": """
                DOCUMENTOS DE BIENES INMUEBLES
                
                CASA HABITACIÓN:
                Dirección: Av. Reforma 123, Col. Centro, CDMX
                Tipo de adquisición: Compraventa
                Fecha de adquisición: 20 de marzo de 2015
                Valor: $2,500,000 MXN
                Crédito hipotecario: $1,800,000 MXN
                
                DEPARTAMENTO:
                Dirección: Calle Falsa 456, Col. Norte, Toluca
                Tipo de adquisición: Herencia
                Fecha de adquisición: 10 de octubre de 2018
                Valor: $800,000 MXN
                """,
                "brief": "Documentos de bienes inmuebles del matrimonio",
                "findings": "Casa en Av. Reforma 123 CDMX (compraventa), Departamento en Calle Falsa 456 Toluca (herencia)",
            },
        ]

        attachments = []
        for att_data in test_attachments:
            attachment = Attachment(
                case_id=case.id,
                name=att_data["name"],
                anexo=att_data["anexo"],
                status=AttachmentStatus.DONE,
                extracted_text=att_data["extracted_text"],
                brief=att_data["brief"],
                findings=att_data["findings"],
            )
            session.add(attachment)
            attachments.append(attachment)

        session.commit()

        printer.green(f"Caso de prueba creado: {case.id}")
        printer.green(f"Attachments creados: {len(attachments)}")

        return str(case.id)


def test_demand_generation(case_id: str):
    """Prueba la generación de demanda inicial."""
    try:
        printer.info(f"Iniciando prueba de generación de demanda para caso: {case_id}")

        # Generar demanda inicial
        result = generate_initial_demand(case_id)
        printer.green(f"Resultado demanda: {result}")

        # Verificar que se creó la demanda en la base de datos
        with session_context_sync() as session:
            demands = session.execute(
                f"SELECT * FROM demands WHERE case_id = '{case_id}'"
            ).fetchall()

            if demands:
                printer.green(f"Demanda creada exitosamente. ID: {demands[0][0]}")
                printer.green(f"Versión: {demands[0][2]}")
                printer.green(f"HTML generado: {len(demands[0][3])} caracteres")

                # Mostrar las primeras 300 caracteres del HTML
                html_preview = (
                    demands[0][3][:300] + "..."
                    if len(demands[0][3]) > 300
                    else demands[0][3]
                )
                printer.blue(f"Vista previa del HTML de la demanda:\n{html_preview}")

                return True
            else:
                printer.error("No se encontró la demanda en la base de datos")
                return False

    except Exception as e:
        printer.error(f"Error en la prueba de demanda: {e}")
        return False


def test_agreement_generation(case_id: str):
    """Prueba la generación de convenio inicial."""
    try:
        printer.info(f"Iniciando prueba de generación de convenio para caso: {case_id}")

        # Generar convenio inicial
        result = generate_initial_agreement(case_id)
        printer.green(f"Resultado convenio: {result}")

        # Verificar que se creó el convenio en la base de datos
        with session_context_sync() as session:
            agreements = session.execute(
                f"SELECT * FROM agreements WHERE case_id = '{case_id}'"
            ).fetchall()

            if agreements:
                printer.green(f"Convenio creado exitosamente. ID: {agreements[0][0]}")
                printer.green(f"Versión: {agreements[0][2]}")
                printer.green(f"HTML generado: {len(agreements[0][3])} caracteres")

                # Mostrar las primeras 300 caracteres del HTML
                html_preview = (
                    agreements[0][3][:300] + "..."
                    if len(agreements[0][3]) > 300
                    else agreements[0][3]
                )
                printer.blue(f"Vista previa del HTML del convenio:\n{html_preview}")

                return True
            else:
                printer.error("No se encontró el convenio en la base de datos")
                return False

    except Exception as e:
        printer.error(f"Error en la prueba de convenio: {e}")
        return False


def test_both_documents(case_id: str):
    """Prueba la generación de ambos documentos."""
    try:
        printer.info(
            f"Iniciando prueba de generación de ambos documentos para caso: {case_id}"
        )

        # Generar ambos documentos
        demand_success = test_demand_generation(case_id)
        agreement_success = test_agreement_generation(case_id)

        if demand_success and agreement_success:
            printer.green("✅ AMBOS DOCUMENTOS GENERADOS EXITOSAMENTE")

            # Verificar que ambos están en la base de datos
            with session_context_sync() as session:
                demands_count = session.execute(
                    f"SELECT COUNT(*) FROM demands WHERE case_id = '{case_id}'"
                ).scalar()

                agreements_count = session.execute(
                    f"SELECT COUNT(*) FROM agreements WHERE case_id = '{case_id}'"
                ).scalar()

                printer.green(f"Demandas en BD: {demands_count}")
                printer.green(f"Convenios en BD: {agreements_count}")

                if demands_count > 0 and agreements_count > 0:
                    return True
                else:
                    printer.error(
                        "No se encontraron ambos documentos en la base de datos"
                    )
                    return False
        else:
            printer.error("❌ FALLO EN LA GENERACIÓN DE DOCUMENTOS")
            return False

    except Exception as e:
        printer.error(f"Error en la prueba de ambos documentos: {e}")
        return False


def cleanup_test_data(case_id: str):
    """Limpia los datos de prueba."""
    try:
        with session_context_sync() as session:
            # Eliminar convenios
            session.execute(f"DELETE FROM agreements WHERE case_id = '{case_id}'")

            # Eliminar demandas
            session.execute(f"DELETE FROM demands WHERE case_id = '{case_id}'")

            # Eliminar attachments
            session.execute(f"DELETE FROM attachments WHERE case_id = '{case_id}'")

            # Eliminar caso
            session.execute(f"DELETE FROM cases WHERE id = '{case_id}'")

            session.commit()
            printer.green("Datos de prueba limpiados exitosamente")

    except Exception as e:
        printer.error(f"Error limpiando datos de prueba: {e}")


def main():
    """Función principal del script de prueba."""
    printer.info("=== INICIANDO PRUEBA DE GENERACIÓN DE DEMANDA Y CONVENIO ===")

    try:
        # Crear caso de prueba
        case_id = create_test_case()

        # Probar generación de ambos documentos
        success = test_both_documents(case_id)

        if success:
            printer.green(
                "✅ PRUEBA EXITOSA: La generación de demanda y convenio funciona correctamente"
            )
        else:
            printer.error(
                "❌ PRUEBA FALLIDA: Hubo errores en la generación de documentos"
            )

        # Limpiar datos de prueba
        cleanup_test_data(case_id)

    except Exception as e:
        printer.error(f"Error general en la prueba: {e}")
        return False

    printer.info("=== PRUEBA COMPLETADA ===")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
