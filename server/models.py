import uuid
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Enum,
    Text,
    func,
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
    format = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    description = Column(Text, nullable=True)

    workflow = relationship("Workflow", back_populates="output_examples")
