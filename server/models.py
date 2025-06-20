import uuid
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    Integer,
    ForeignKey,
    Enum,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from server.db import Base
import enum


class CaseStatus(str, enum.Enum):
    PENDING = "PENDING"
    ERROR = "ERROR"
    DONE = "DONE"
    APPROVED = "APPROVED"
    DELIVERED = "DELIVERED"


class AttachmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    ERROR = "ERROR"
    DONE = "DONE"


class Case(Base):
    __tablename__ = "cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    finished_at = Column(DateTime(timezone=True), nullable=True)  # <-- Campo agregado
    status = Column(Enum(CaseStatus), default=CaseStatus.PENDING, nullable=False)
    delivered = Column(Boolean, default=False, nullable=False)
    summary = Column(Text, nullable=True)

    # Relaciones
    attachments = relationship(
        "Attachment", back_populates="case", cascade="all, delete-orphan"
    )
    demands = relationship(
        "Demand", back_populates="case", cascade="all, delete-orphan"
    )
    agreements = relationship(
        "Agreement", back_populates="case", cascade="all, delete-orphan"
    )


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(
        UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(255), nullable=False)
    anexo = Column(Integer, nullable=False)
    status = Column(
        Enum(AttachmentStatus), default=AttachmentStatus.PENDING, nullable=False
    )
    extracted_text = Column(Text, nullable=True)
    brief = Column(Text, nullable=True)
    findings = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    case = relationship("Case", back_populates="attachments")


class Demand(Base):
    __tablename__ = "demands"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(
        UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    version = Column(Integer, default=1, nullable=False)
    html = Column(Text, nullable=False)
    feedback = Column(Text, default="", nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    case = relationship("Case", back_populates="demands")


class Agreement(Base):
    __tablename__ = "agreements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(
        UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    version = Column(Integer, default=1, nullable=False)
    html = Column(Text, nullable=False)
    feedback = Column(Text, default="", nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    case = relationship("Case", back_populates="agreements")
