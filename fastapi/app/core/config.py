from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SUPABASE_JWKS_URL: str
    API_ALLOWED_ORIGINS: str
    JWT_EXPECTED_ISS: str
    JWT_EXPECTED_AUD: str

settings = Settings()
