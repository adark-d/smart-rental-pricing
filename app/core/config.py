from src.utils.settings import settings

database_url = (
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@localhost:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)
