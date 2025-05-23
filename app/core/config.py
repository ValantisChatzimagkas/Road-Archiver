from dynaconf import Dynaconf
import os

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "roadnetworks")

settings = Dynaconf(
    settings_files=["settings.toml", ".env"],
    environments=True,
    load_dotenv=True,
)

settings.DB_HOST = DB_HOST
settings.DB_PORT = DB_PORT
settings.DB_USER = DB_USER
settings.DB_PASSWORD = DB_PASSWORD
settings.DB_NAME = DB_NAME

settings.DB_URL = (
    f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)
