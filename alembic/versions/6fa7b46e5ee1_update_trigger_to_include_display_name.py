"""update trigger to include display name

Revision ID: 6fa7b46e5ee1
Revises: 11458fc6c41d
Create Date: 2025-11-09 16:47:21.691920

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6fa7b46e5ee1'
down_revision: Union[str, Sequence[str], None] = '11458fc6c41d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Recreate the trigger function to include full_name from auth.users metadata
    op.execute("""
    CREATE OR REPLACE FUNCTION public.handle_new_user()
    RETURNS TRIGGER
    LANGUAGE plpgsql
    SECURITY DEFINER
    AS $$
    BEGIN
      INSERT INTO public.profiles (id, email, full_name, created_at, updated_at)
      VALUES (
        NEW.id, 
        NEW.email, 
        NEW.raw_user_meta_data->>'name',  -- Extract display name from metadata
        now(), 
        now()
      )
      ON CONFLICT (id) DO NOTHING;
      RETURN NEW;
    END;
    $$;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Revert to the original trigger function (without full_name)
    op.execute("""
    CREATE OR REPLACE FUNCTION public.handle_new_user()
    RETURNS TRIGGER
    LANGUAGE plpgsql
    SECURITY DEFINER
    AS $$
    BEGIN
      INSERT INTO public.profiles (id, email, created_at, updated_at)
      VALUES (NEW.id, NEW.email, now(), now())
      ON CONFLICT (id) DO NOTHING;
      RETURN NEW;
    END;
    $$;
    """)
