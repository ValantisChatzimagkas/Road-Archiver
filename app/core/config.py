from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=["settings.toml", ".env"],
    environments=True,
    load_dotenv=True,
)

# Compose the DB URL manually
settings.DB_URL = (
    f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)