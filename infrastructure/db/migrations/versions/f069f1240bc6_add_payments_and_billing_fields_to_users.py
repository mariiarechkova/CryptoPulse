"""add payments and billing fields to users

Revision ID: f069f1240bc6
Revises: 3f620f8bf967
Create Date: 2026-01-06 12:51:30.001316

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f069f1240bc6"
down_revision: Union[str, Sequence[str], None] = "3f620f8bf967"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------------------
    # 1. ENUM TYPES (CREATE ONCE, MANUALLY)
    # ---------------------------------------------------------------------
    payment_provider_enum = postgresql.ENUM(
        "cryptobot",
        name="payment_provider",
        create_type=False,
    )

    payment_status_enum = postgresql.ENUM(
        "pending",
        "paid",
        "expired",
        "failed",
        name="payment_status",
        create_type=False,
    )

    tariff_code_enum = postgresql.ENUM(
        "free",
        "paid_month",
        "paid_year",
        name="tariff_code",
        create_type=False,
    )

    bind = op.get_bind()

    payment_provider_enum.create(bind, checkfirst=True)
    payment_status_enum.create(bind, checkfirst=True)
    tariff_code_enum.create(bind, checkfirst=True)

    # ---------------------------------------------------------------------
    # 2. TARIFF PLANS
    # ---------------------------------------------------------------------
    op.create_table(
        "tariff_plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("price_amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("price_currency", sa.String(length=10), nullable=False),
        sa.Column("duration_days", sa.Integer(), nullable=False),
        sa.Column("max_symbols", sa.Integer(), nullable=False),
        sa.Column("demo_levels_requests_total", sa.Integer(), nullable=False),
        sa.Column("llm_enabled", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_tariff_plans_code"),
        "tariff_plans",
        ["code"],
        unique=True,
    )

    # ---------------------------------------------------------------------
    # 3. PAYMENTS
    # ---------------------------------------------------------------------
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "provider",
            payment_provider_enum,
            server_default="cryptobot",
            nullable=False,
        ),
        sa.Column("invoice_id", sa.String(length=128), nullable=False),
        sa.Column(
            "status",
            payment_status_enum,
            server_default="pending",
            nullable=False,
        ),
        sa.Column(
            "tariff_code",
            tariff_code_enum,
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("asset", sa.String(length=16), server_default="USDT", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_payload", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_payments_invoice_id"), "payments", ["invoice_id"], unique=True)
    op.create_index(op.f("ix_payments_provider"), "payments", ["provider"])
    op.create_index(op.f("ix_payments_status"), "payments", ["status"])
    op.create_index(op.f("ix_payments_user_id"), "payments", ["user_id"])

    # ---------------------------------------------------------------------
    # 4. USERS CHANGES
    # ---------------------------------------------------------------------
    op.add_column(
        "users",
        sa.Column("paid_until", sa.DateTime(timezone=True), nullable=True),
    )

    op.add_column(
        "users",
        sa.Column(
            "tariff_code",
            tariff_code_enum,
            server_default="free",
            nullable=False,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "levels_demo_remaining",
            sa.Integer(),
            server_default="3",
            nullable=False,
        ),
    )

    op.drop_column("users", "current_plan")
    op.drop_column("users", "is_subscription_active")


def downgrade() -> None:
    # ---------------------------------------------------------------------
    # USERS
    # ---------------------------------------------------------------------
    op.add_column(
        "users",
        sa.Column(
            "is_subscription_active",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "current_plan",
            postgresql.ENUM(
                "FREE",
                "PREMIUM",
                name="subscription_plan",
            ),
            server_default=sa.text("'FREE'::subscription_plan"),
            nullable=False,
        ),
    )

    op.drop_column("users", "levels_demo_remaining")
    op.drop_column("users", "tariff_code")
    op.drop_column("users", "paid_until")

    # ---------------------------------------------------------------------
    # PAYMENTS / TARIFF PLANS
    # ---------------------------------------------------------------------
    op.drop_index(op.f("ix_payments_user_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_status"), table_name="payments")
    op.drop_index(op.f("ix_payments_provider"), table_name="payments")
    op.drop_index(op.f("ix_payments_invoice_id"), table_name="payments")
    op.drop_table("payments")

    op.drop_index(op.f("ix_tariff_plans_code"), table_name="tariff_plans")
    op.drop_table("tariff_plans")

    # ---------------------------------------------------------------------
    # ENUM TYPES (DROP IF UNUSED)
    # ---------------------------------------------------------------------
    bind = op.get_bind()

    postgresql.ENUM(name="payment_provider").drop(bind, checkfirst=True)
    postgresql.ENUM(name="payment_status").drop(bind, checkfirst=True)
    postgresql.ENUM(name="tariff_code").drop(bind, checkfirst=True)
