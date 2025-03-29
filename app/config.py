from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "postgresql://user:password@localhost:port/db_name"

    FIRST_ADMIN_EMAIL: str = "admin@example.com"
    FIRST_ADMIN_PASSWORD: str = "changeme123"
    FIRST_ADMIN_FULLNAME: str = "System Administrator"
    FIRST_ADMIN_ROLE_ID: int = 1  
    FIRST_ADMIN_ORG_ID: int = 1  

    class Config:
        env_file = ".env"


settings = Settings()
