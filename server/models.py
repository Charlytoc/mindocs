import uuid
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Enum,
    Text,
    JSON,
    func,
    Integer,
    Numeric,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from server.db import Base
import enum


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    workflows = relationship(
        "Workflow", back_populates="user", cascade="all, delete-orphan"
    )
    subscription = relationship(
        "UserSubscription", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    credit_balance = relationship(
        "CreditBalance", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    credit_transactions = relationship(
        "CreditTransaction", back_populates="user", cascade="all, delete-orphan"
    )


class AssetStatus(str, enum.Enum):
    PENDING = "PENDING"
    ERROR = "ERROR"
    DONE = "DONE"


class AssetOrigin(str, enum.Enum):
    UPLOAD = "UPLOAD"
    AI = "AI"


class AssetType(str, enum.Enum):
    FILE = "FILE"
    URL = "URL"
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    instructions = Column(Text, nullable=True)
    user = relationship("User", back_populates="workflows")

    workflow_executions = relationship(
        "WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan"
    )

    output_examples = relationship(
        "WorkflowOutputExample", back_populates="workflow", cascade="all, delete-orphan"
    )


class WorkflowExecutionStatus(str, enum.Enum):
    PENDING = "PENDING"
    ERROR = "ERROR"
    DONE = "DONE"
    IN_PROGRESS = "IN_PROGRESS"


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(
        Enum(WorkflowExecutionStatus),
        default=WorkflowExecutionStatus.PENDING,
        nullable=False,
    )
    delivered = Column(Boolean, default=False, nullable=False)
    summary = Column(Text, nullable=True)
    status_message = Column(Text, nullable=True)

    generation_log = Column(Text, nullable=True)

    workflow = relationship("Workflow", back_populates="workflow_executions")

    assets = relationship(
        "Asset",
        back_populates="workflow_execution",
        primaryjoin="and_(WorkflowExecution.id==Asset.workflow_execution_id)",
        cascade="all, delete-orphan",
    )
    messages = relationship(
        "Message", back_populates="workflow_execution", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_execution_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflow_executions.id", ondelete="CASCADE"),
        nullable=False,
    )
    role = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    workflow_execution = relationship("WorkflowExecution", back_populates="messages")


class Asset(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    workflow_execution_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflow_executions.id", ondelete="CASCADE"),
        nullable=True,
    )

    name = Column(String(255), nullable=False)
    internal_path = Column(String(255), nullable=True)
    asset_type = Column(Enum(AssetType), nullable=False)
    origin = Column(Enum(AssetOrigin), nullable=False, default=AssetOrigin.UPLOAD)
    status = Column(Enum(AssetStatus), default=AssetStatus.PENDING, nullable=False)
    extracted_text = Column(Text, nullable=True)
    brief = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    format = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    workflow_execution = relationship("WorkflowExecution", back_populates="assets")


class WorkflowOutputExample(Base):
    __tablename__ = "workflow_output_examples"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    internal_path = Column(String(255), nullable=True)
    format = Column(String(255), nullable=True)
    variables = Column(JSON, nullable=True)
    is_template = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    description = Column(Text, nullable=True)

    workflow = relationship("Workflow", back_populates="output_examples")


class SubscriptionPlanType(str, enum.Enum):
    FREE = "FREE"
    BASIC = "BASIC"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    PAST_DUE = "PAST_DUE"
    TRIALING = "TRIALING"


class CreditTransactionType(str, enum.Enum):
    SUBSCRIPTION_RENEWAL = "SUBSCRIPTION_RENEWAL"
    PURCHASE_PACKAGE = "PURCHASE_PACKAGE"
    ADMIN_ADJUSTMENT = "ADMIN_ADJUSTMENT"
    REFUND = "REFUND"
    WORKFLOW_EXECUTION = "WORKFLOW_EXECUTION"
    FAILED_OPERATION = "FAILED_OPERATION"


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Tipo y nombre
    plan_type = Column(Enum(SubscriptionPlanType), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Precio y valor
    price_usd = Column(Numeric(10, 2), nullable=False)
    monthly_credits = Column(Integer, nullable=False)
    stripe_price_id = Column(String(255), nullable=True)

    # Costos internos (para calcular margen)
    estimated_cost_usd = Column(Numeric(10, 2), nullable=False)
    margin_percentage = Column(Numeric(5, 2), nullable=False)

    # Metadata
    is_active = Column(Boolean, default=True)
    features = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user_subscriptions = relationship("UserSubscription", back_populates="plan")


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=False)

    # Stripe
    stripe_subscription_id = Column(String(255), unique=True, nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_price_id = Column(String(255), nullable=True)

    # Estado
    status = Column(Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE)

    # Períodos
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="subscription")
    plan = relationship("SubscriptionPlan", back_populates="user_subscriptions")
    credit_transactions = relationship("CreditTransaction", back_populates="subscription")


class CreditBalance(Base):
    __tablename__ = "credit_balances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)

    # Balance actual
    balance = Column(Integer, default=0, nullable=False)  # En créditos (1 crédito = $0.01)

    # Tracking
    last_credited_at = Column(DateTime(timezone=True), nullable=True)
    last_debited_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="credit_balance")


class CreditTransaction(Base):
    __tablename__ = "credit_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Tipo y cantidad
    transaction_type = Column(Enum(CreditTransactionType), nullable=False)
    credits = Column(Integer, nullable=False)  # Positivo = suma, Negativo = resta

    # Referencias
    execution_id = Column(UUID(as_uuid=True), ForeignKey("workflow_executions.id"), nullable=True)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("user_subscriptions.id"), nullable=True)

    # Detalles
    description = Column(Text, nullable=True)
    transaction_metadata = Column(JSON, nullable=True)

    # Balance antes y después
    balance_before = Column(Integer, nullable=True)
    balance_after = Column(Integer, nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="credit_transactions")
    execution = relationship("WorkflowExecution")
    subscription = relationship("UserSubscription", back_populates="credit_transactions")
