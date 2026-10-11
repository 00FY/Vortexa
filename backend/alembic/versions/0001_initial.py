"""Initial database migration: all tables, enums, indexes, and constraints.

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-11 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Enums
    user_role_enum = postgresql.ENUM(
        "employee", "manager", "admin", name="user_role"
    )
    user_role_enum.create(op.get_bind(), checkfirst=True)

    dept_enum = postgresql.ENUM(
        "Engineering",
        "Finance",
        "Risk_Compliance",
        "Operations",
        "HR",
        name="department",
    )
    dept_enum.create(op.get_bind(), checkfirst=True)

    leave_type_enum = postgresql.ENUM(
        "casual", "sick", "annual", "unpaid", name="leave_type"
    )
    leave_type_enum.create(op.get_bind(), checkfirst=True)

    leave_status_enum = postgresql.ENUM(
        "pending", "approved", "rejected", "cancelled", name="leave_status"
    )
    leave_status_enum.create(op.get_bind(), checkfirst=True)

    expense_category_enum = postgresql.ENUM(
        "travel",
        "food",
        "equipment",
        "accommodation",
        "other",
        name="expense_category",
    )
    expense_category_enum.create(op.get_bind(), checkfirst=True)

    expense_status_enum = postgresql.ENUM(
        "pending", "approved", "rejected", "paid", name="expense_status"
    )
    expense_status_enum.create(op.get_bind(), checkfirst=True)

    actor_type_enum = postgresql.ENUM(
        "system", "user", name="actor_type"
    )
    actor_type_enum.create(op.get_bind(), checkfirst=True)

    policy_check_path_enum = postgresql.ENUM(
        "RULES_ONLY", "AI_ASSISTED", name="policy_check_path"
    )
    policy_check_path_enum.create(op.get_bind(), checkfirst=True)

    # 2. Users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column(
            "role",
            postgresql.ENUM(name="user_role", create_type=False),
            nullable=False,
            server_default="employee",
        ),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default="true"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # 3. Employees table
    op.create_table(
        "employees",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column(
            "department",
            postgresql.ENUM(name="department", create_type=False),
            nullable=False,
        ),
        sa.Column("designation", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column(
            "manager_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("employees.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("employee_code", sa.String(), nullable=False),
        sa.Column("date_of_joining", sa.Date(), nullable=False),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default="true"
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_employees_employee_code",
        "employees",
        ["employee_code"],
        unique=True,
    )

    # 4. Leave requests table
    op.create_table(
        "leave_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "requester_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("employees.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "reviewed_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("employees.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "leave_type",
            postgresql.ENUM(name="leave_type", create_type=False),
            nullable=False,
        ),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(name="leave_status", create_type=False),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column(
            "request_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_leave_requests_request_id", "leave_requests", ["request_id"]
    )

    # 5. Expense claims table
    op.create_table(
        "expense_claims",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "requester_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("employees.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "reviewed_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("employees.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "amount", sa.Numeric(precision=12, scale=2), nullable=False
        ),
        sa.Column(
            "category",
            postgresql.ENUM(name="expense_category", create_type=False),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(name="expense_status", create_type=False),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column(
            "payment_reference_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("payment_date", sa.Date(), nullable=True),
        sa.Column(
            "request_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_expense_claims_request_id", "expense_claims", ["request_id"]
    )

    # 6. Activity logs table (append-only)
    op.create_table(
        "activity_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "actor_type",
            postgresql.ENUM(name="actor_type", create_type=False),
            nullable=False,
        ),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("resource", sa.String(), nullable=False),
        sa.Column(
            "resource_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("before_state", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("after_state", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "request_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column(
            "policy_check_path",
            postgresql.ENUM(name="policy_check_path", create_type=False),
            nullable=False,
            server_default="RULES_ONLY",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "created_at IS NOT NULL",
            name="ck_activity_logs_created_at_not_null",
        ),
        sa.CheckConstraint(
            "policy_check_path IN ('RULES_ONLY', 'AI_ASSISTED')",
            name="ck_activity_logs_policy_check_path",
        ),
        sa.CheckConstraint(
            "actor_type IN ('system', 'user')",
            name="ck_activity_logs_actor_type",
        ),
    )
    op.create_index(
        "ix_activity_logs_request_id", "activity_logs", ["request_id"]
    )


def downgrade() -> None:
    op.drop_table("activity_logs")
    op.drop_table("expense_claims")
    op.drop_table("leave_requests")
    op.drop_table("employees")
    op.drop_table("users")

    # Drop enums
    postgresql.ENUM(name="policy_check_path").drop(
        op.get_bind(), checkfirst=True
    )
    postgresql.ENUM(name="actor_type").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="expense_status").drop(
        op.get_bind(), checkfirst=True
    )
    postgresql.ENUM(name="expense_category").drop(
        op.get_bind(), checkfirst=True
    )
    postgresql.ENUM(name="leave_status").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="leave_type").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="department").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="user_role").drop(op.get_bind(), checkfirst=True)