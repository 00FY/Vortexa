import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship

from core.database import Base


class ActorType(str):
    SYSTEM = "system"
    USER = "user"


actor_type_enum = Enum(
    ActorType.SYSTEM,
    ActorType.USER,
    name="actor_type",
    native_enum=True,
)


class PolicyCheckPath(str):
    RULES_ONLY = "RULES_ONLY"
    AI_ASSISTED = "AI_ASSISTED"


policy_check_path_enum = Enum(
    PolicyCheckPath.RULES_ONLY,
    PolicyCheckPath.AI_ASSISTED,
    name="policy_check_path",
    native_enum=True,
)


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id = Column(UUID(as_uuid=True), nullable=False)
    actor_type = Column(actor_type_enum, nullable=False)
    action = Column(String, nullable=False)
    resource = Column(String, nullable=False)
    resource_id = Column(UUID(as_uuid=True), nullable=False)
    before_state = Column(JSON, nullable=True)
    after_state = Column(JSON, nullable=True)
    request_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    policy_check_path = Column(
        policy_check_path_enum,
        nullable=False,
        default=PolicyCheckPath.RULES_ONLY,
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        CheckConstraint(
            "created_at IS NOT NULL",
            name="ck_activity_logs_created_at_not_null",
        ),
        CheckConstraint(
            "policy_check_path IN ('RULES_ONLY', 'AI_ASSISTED')",
            name="ck_activity_logs_policy_check_path",
        ),
        CheckConstraint(
            "actor_type IN ('system', 'user')",
            name="ck_activity_logs_actor_type",
        ),
    )

    def __repr__(self):
        return f"<ActivityLog(id={self.id}, action={self.action!r})>"