"""add referral_code and referred_by_id to users

Revision ID: 0014_add_referral
Revises: 0013_add_testimonial
Create Date: 2026-09-15
"""
import secrets
import string
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0014_add_referral"
down_revision: Union[str, Sequence[str], None] = "0013_add_testimonial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

REFERRAL_CODE_ALPHABET = "".join(c for c in string.ascii_uppercase + string.digits if c not in "0O1I")


def _generate_code() -> str:
    return "".join(secrets.choice(REFERRAL_CODE_ALPHABET) for _ in range(8))


def upgrade() -> None:
    op.add_column("users", sa.Column("referral_code", sa.String(length=12), nullable=True))
    op.add_column(
        "users",
        sa.Column("referred_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )

    connection = op.get_bind()
    user_ids = [row[0] for row in connection.execute(sa.text("SELECT id FROM users")).fetchall()]
    used_codes: set[str] = set()
    for user_id in user_ids:
        code = _generate_code()
        while code in used_codes:
            code = _generate_code()
        used_codes.add(code)
        connection.execute(
            sa.text("UPDATE users SET referral_code = :code WHERE id = :id"),
            {"code": code, "id": user_id},
        )

    op.alter_column("users", "referral_code", nullable=False)
    op.create_unique_constraint("uq_users_referral_code", "users", ["referral_code"])
    op.create_index("ix_users_referral_code", "users", ["referral_code"])


def downgrade() -> None:
    op.drop_index("ix_users_referral_code", table_name="users")
    op.drop_constraint("uq_users_referral_code", "users", type_="unique")
    op.drop_column("users", "referred_by_id")
    op.drop_column("users", "referral_code")
