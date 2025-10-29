from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from server.models import (
    User,
    CreditBalance,
    CreditTransaction,
    CreditTransactionType,
    WorkflowExecution,
)
from server.utils.printer import Printer

printer = Printer("CREDIT_SERVICE")


class CreditService:
    """Servicio para gestionar créditos de usuarios"""

    @staticmethod
    async def get_user_balance(
        session: AsyncSession, user_id: str
    ) -> CreditBalance:
        """Obtiene el balance de créditos del usuario. Crea uno si no existe."""
        result = await session.execute(
            select(CreditBalance).where(CreditBalance.user_id == user_id)
        )
        balance = result.scalar_one_or_none()

        if not balance:
            # Crear balance inicial
            balance = CreditBalance(user_id=user_id, balance=0)
            session.add(balance)
            await session.commit()
            printer.green(f"Created initial credit balance for user {user_id}")

        return balance

    @staticmethod
    async def add_credits(
        session: AsyncSession,
        user_id: str,
        credits: int,
        transaction_type: CreditTransactionType,
        description: str = None,
        metadata: dict = None,
        subscription_id: str = None,
    ) -> CreditTransaction:
        """Añade créditos al usuario"""
        if credits <= 0:
            raise ValueError("Credits must be positive")

        # Obtener balance actual
        balance = await CreditService.get_user_balance(session, user_id)
        balance_before = balance.balance

        # Actualizar balance
        balance.balance += credits
        balance.last_credited_at = datetime.now()
        balance.updated_at = datetime.now()

        # Crear transacción
        transaction = CreditTransaction(
            user_id=user_id,
            credits=credits,
            transaction_type=transaction_type,
            description=description or f"Added {credits} credits",
            metadata=metadata,
            balance_before=balance_before,
            balance_after=balance.balance,
            subscription_id=subscription_id,
        )

        session.add(transaction)
        await session.commit()

        printer.green(
            f"Added {credits} credits to user {user_id}. New balance: {balance.balance}"
        )

        return transaction

    @staticmethod
    async def consume_credits(
        session: AsyncSession,
        user_id: str,
        credits: int,
        transaction_type: CreditTransactionType,
        execution_id: str = None,
        description: str = None,
        metadata: dict = None,
    ) -> CreditTransaction:
        """Consume créditos del usuario. Valida que tenga suficientes."""
        if credits <= 0:
            raise ValueError("Credits to consume must be positive")

        # Obtener balance
        balance = await CreditService.get_user_balance(session, user_id)

        # Verificar que tenga suficientes créditos
        if balance.balance < credits:
            raise HTTPException(
                status_code=402,
                detail=f"Insufficient credits. You have {balance.balance} credits, need {credits}",
            )

        balance_before = balance.balance

        # Descontar créditos
        balance.balance -= credits
        balance.last_debited_at = datetime.now()
        balance.updated_at = datetime.now()

        # Crear transacción
        transaction = CreditTransaction(
            user_id=user_id,
            credits=-credits,  # Negativo para consumo
            transaction_type=transaction_type,
            execution_id=execution_id,
            description=description or f"Consumed {credits} credits",
            metadata=metadata,
            balance_before=balance_before,
            balance_after=balance.balance,
        )

        session.add(transaction)
        await session.commit()

        printer.yellow(
            f"Consumed {credits} credits from user {user_id}. New balance: {balance.balance}"
        )

        return transaction

    @staticmethod
    async def get_transaction_history(
        session: AsyncSession, user_id: str, limit: int = 50
    ) -> List[CreditTransaction]:
        """Obtiene el historial de transacciones del usuario"""
        result = await session.execute(
            select(CreditTransaction)
            .where(CreditTransaction.user_id == user_id)
            .order_by(CreditTransaction.created_at.desc())
            .limit(limit)
        )

        transactions = result.scalars().all()
        return list(transactions)

    @staticmethod
    async def has_sufficient_credits(
        session: AsyncSession, user_id: str, required_credits: int
    ) -> bool:
        """Verifica si el usuario tiene suficientes créditos"""
        balance = await CreditService.get_user_balance(session, user_id)
        return balance.balance >= required_credits
