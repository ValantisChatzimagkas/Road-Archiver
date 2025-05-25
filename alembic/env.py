import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from app.core.config import settings

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import Base  # adjust path as needed

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option("sqlalchemy.url", settings.DB_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Define tables to exclude - PostGIS and other system tables
def include_object(object, name, type_, reflected, compare_to):
    # Exclude PostGIS tables and schemas
    if type_ == "table":
        # Exclude tables from PostGIS and Tiger Geocoder
        postgis_tables = [
            "spatial_ref_sys",
            "geography_columns",
            "geometry_columns",
            "zip_lookup",
            "zip_lookup_base",
            "zip_lookup_all",
            "zip_state",
            "zip_state_loc",
            "county_lookup",
            "countysub_lookup",
            "cousub_lookup",
            "place_lookup",
            "secondary_unit_lookup",
            "street_type_lookup",
            "direction_lookup",
            "state_lookup",
            "geocode_settings",
            "geocode_settings_default",
            "loader_platform",
            "loader_variables",
            "loader_lookuptables",
            "pagc_gaz",
            "pagc_lex",
            "pagc_rules",
            "featnames",
            "faces",
            "edges",
            "addr",
            "addrfeat",
            "tabblock",
            "tract",
            "county",
            "topology",
            "zcta5",
            "place",
            "layer",
            "bg",
            "state",
            "tabblock20",
            "cousub",
        ]
        # Check if name exactly matches any postgis table
        if name in postgis_tables:
            return False
        # Check if name starts with any common prefixes
        for prefix in ["tiger_", "tiger.", "topology.", "layer_"]:
            if name.startswith(prefix):
                return False

    # Exclude specific schemas
    if hasattr(object, "schema") and object.schema in ("tiger", "topology", "postgis"):
        return False

    return True


# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,  # Add this line
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection withF the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,  # Add this line
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
