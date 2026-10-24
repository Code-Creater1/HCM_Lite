from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./hcm_lite.db"
    jwt_secret: str = "dev-secret-change-me"
    jwt_expires_minutes: int = 480
    admin_email: str = ""
    admin_password: str = ""
    admin_name: str = "System Admin"
    company_name_default: str = "HCM Lite Co."
    class Config: env_file = ".env"

settings = Settings()