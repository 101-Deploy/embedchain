import os

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import scoped_session, sessionmaker
from google.cloud import spanner
from google.cloud.spanner_dbapi import connect
from .models import Base


class DatabaseManager:
    def __init__(self, echo: bool = False):
        # self.database_uri = os.environ.get("EMBEDCHAIN_DB_URI")
        # self.echo = echo
        # self.engine: Engine = None
        # self._session_factory = None
        self.instance_id = os.environ.get("EMBEDCHAIN_INSTANCE_ID")
        self.database_id = os.environ.get("EMBEDCHAIN_DATABASE_ID")
        self.spanner_client = spanner.Client()
        self.instance = None
        self.database = None

    def setup_engine(self) -> None:
        """Initializes the database engine and session factory."""
        if not self.instance_id or not self.database_id:
            raise RuntimeError("Instance ID and Database ID must be set in the environment variables.")
        # connect_args = {"client": spanner.Client(project="classyclass-dev")}
        # if self.database_uri.startswith("sqlite"):
        # connect_args["check_same_thread"] = False
        # self.engine = create_engine(self.database_uri, echo=self.echo, connect_args=connect_args)
        # self._session_factory = scoped_session(sessionmaker(bind=self.engine))
        # Base.metadata.bind = self.engine

        # Get a Cloud Spanner instance by ID.
        self.instance = self.spanner_client.instance(self.instance_id)

        # Get a Cloud Spanner database by ID.
        self.database = self.instance.database(self.database_id)

    def init_db(self) -> None:
        """Creates all tables defined in the Base metadata."""
        if not self.database or not self.instance:
            raise RuntimeError("Database instance and database must be set. Call setup_engine() first.")
        # Base.metadata.create_all(self.engine)
        ddl_statements = [
            """CREATE TABLE IF NOT EXISTS ec_data_sources (
                id VARCHAR(36) PRIMARY KEY NOT NULL,
                app_id TEXT,
                hash TEXT,
                type TEXT,
                value TEXT,
                metadata TEXT,
                is_uploaded INT DEFAULT 0
            );
            
            CREATE INDEX IF NOT EXISTS idx_app_id ON ec_data_sources (app_id);
            CREATE INDEX IF NOT EXISTS idx_hash ON ec_data_sources (hash);
            CREATE INDEX IF NOT EXISTS idx_type ON ec_data_sources (type);
            """,
            """CREATE TABLE IF NOT EXISTS ec_chat_history (
                app_id VARCHAR(255) NOT NULL,
                id VARCHAR(255) NOT NULL,
                session_id VARCHAR(255) NOT NULL,
                question TEXT,
                answer TEXT,
                metadata TEXT,
                created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (app_id, id, session_id)
            );

            CREATE INDEX IF NOT EXISTS idx_session_id ON ec_chat_history (session_id);
            CREATE INDEX IF NOT EXISTS idx_created_at ON ec_chat_history (created_at);""",
        ]

        # create the tables in the database if they do not exist
        operation = self.database.update_ddl(ddl_statements)

    def get_session(self) -> spanner.Database:
        # """Provides a session for database operations."""
        # if not self._session_factory:
        #     raise RuntimeError("Session factory is not initialized. Call setup_engine() first.")
        # return self._session_factory()
        return None

    def close_session(self) -> None:
        # """Closes the current session."""
        # if self._session_factory:
        #     self._session_factory.remove()
        return None

    def execute_transaction(self, transaction_block):
        #     """Executes a block of code within a database transaction."""
        #     self.database.run_in

        #     try:
        #     except Exception as e:
        #         raise e
        #     finally:
        #         cursor.close()
        #         conn.close()
        return None

    def execute_sql(self, sql: str):
        """Executes a raw SQL statement."""
        try:
            with self.database.snapshot() as snapshot:
                results = snapshot.execute_sql(sql)
                if results:
                    return results
        except Exception as e:
            raise e


# Singleton pattern to use throughout the application
database_manager = DatabaseManager()


# Convenience functions for backward compatibility and ease of use
def setup_engine(database_uri: str, echo: bool = False) -> None:
    # database_manager.database_uri = database_uri
    # database_manager.echo = echo
    database_manager.setup_engine()


def alembic_upgrade() -> None:
    """Upgrades the database to the latest version."""
    alembic_config_path = os.path.join(os.path.dirname(__file__), "..", "..", "alembic.ini")
    alembic_cfg = Config(alembic_config_path)
    command.upgrade(alembic_cfg, "head")


def init_db() -> None:
    alembic_upgrade()

    # def get_session() -> SQLAlchemySession:
    return database_manager.get_session()


def get_session():
    return None


def execute_sql(sql: str) -> None:
    database_manager.execute_sql(sql)


def execute_transaction(transaction_block):
    database_manager.execute_transaction(transaction_block)
