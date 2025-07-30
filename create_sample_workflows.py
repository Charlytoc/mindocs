#!/usr/bin/env python3
"""
Script to create sample workflows for testing the new multi-workflow UI
"""

import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from server.db import get_session
from server.models import User, Workflow


async def create_sample_workflows():
    """Create sample workflows for testing"""

    # Get a database session
    session = await get_session().__anext__()

    try:
        # Create a test user if it doesn't exist
        test_email = "test@example.com"
        user_result = await session.execute(
            select(User).where(User.email == test_email)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            user = User(email=test_email, name="Test User", password="test123")
            session.add(user)
            await session.flush()
            print(f"Created test user: {test_email}")
        else:
            print(f"Using existing user: {test_email}")

        # Create sample workflows
        sample_workflows = [
            {
                "name": "Generación de Demandas",
                "description": "Proceso para generar demandas iniciales basadas en documentos legales",
                "instructions": "Sube los documentos legales relevantes y el sistema generará una demanda inicial",
            },
            {
                "name": "Creación de Convenios",
                "description": "Genera convenios legales basados en acuerdos entre partes",
                "instructions": "Proporciona los términos del acuerdo y el sistema creará un convenio formal",
            },
            {
                "name": "Análisis de Contratos",
                "description": "Analiza contratos y genera resúmenes y recomendaciones",
                "instructions": "Sube el contrato y el sistema analizará sus términos y condiciones",
            },
            {
                "name": "Generación de Recursos",
                "description": "Crea recursos legales como amparos y recursos administrativos",
                "instructions": "Proporciona la información del caso y el sistema generará el recurso correspondiente",
            },
        ]

        for workflow_data in sample_workflows:
            # Check if workflow already exists for this user
            existing = await session.execute(
                select(Workflow).where(
                    Workflow.user_id == user.id, Workflow.name == workflow_data["name"]
                )
            )

            if not existing.scalar_one_or_none():
                workflow = Workflow(
                    user_id=user.id,
                    name=workflow_data["name"],
                    description=workflow_data["description"],
                    instructions=workflow_data["instructions"],
                )
                session.add(workflow)
                print(f"Created workflow: {workflow_data['name']}")
            else:
                print(f"Workflow already exists: {workflow_data['name']}")

        await session.commit()
        print("\n✅ Sample workflows created successfully!")
        print(f"Test user: {test_email}")
        print("Password: test123")

    except Exception as e:
        print(f"Error creating sample workflows: {e}")
        await session.rollback()
    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(create_sample_workflows())
