"""create profiles and auth trigger

Revision ID: 11458fc6c41d
Revises: 
Create Date: 2025-11-09 15:45:21.795779

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '11458fc6c41d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1) Create profiles table (in public schema)
    op.create_table(
        "profiles",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        # sa.Column("avatar_url", sa.String(length=2048), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["id"], ["auth.users.id"], ondelete="CASCADE"),
        schema="public",
    )
    op.create_index("ix_profiles_email", "profiles", ["email"], unique=False, schema="public")

    # 2) Create trigger function in public schema
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

    # 3) Attach trigger to auth.users (fires after each row insert)
    op.execute("""
    DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
    CREATE TRIGGER on_auth_user_created
      AFTER INSERT ON auth.users
      FOR EACH ROW
      EXECUTE FUNCTION public.handle_new_user();
    """)

    # (Optional) RLS enable and policies for public.profiles
    op.execute("ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;")

    # Allow authenticated users to read/write their own profile by default:
    # Adjust to your needs or manage in Supabase UI.
    op.execute("""
    CREATE POLICY "Allow select own profile"
    ON public.profiles
    FOR SELECT
    TO authenticated
    USING (auth.uid() = id);
    """)
    op.execute("""
    CREATE POLICY "Allow update own profile"
    ON public.profiles
    FOR UPDATE
    TO authenticated
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);
    """)



def downgrade() -> None:
    """Downgrade schema."""
    # Drop trigger and function first
    op.execute("DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;")
    op.execute("DROP FUNCTION IF EXISTS public.handle_new_user();")
    # Drop table and index
    op.drop_index("ix_profiles_email", table_name="profiles", schema="public")
    op.drop_table("profiles", schema="public")
