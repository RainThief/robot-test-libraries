"""sql database module"""
from sqlalchemy import orm, MetaData, Table, engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from sqlalchemy.engine import create_engine
from sqlalchemy.engine.url import make_url
from robot_support.errors import ServiceNotReadyError
from robot_support.logger import Logger
from .sql_assertions import SQLAssertions


LOGGER = Logger.get_instance()


class SQLDatabase(SQLAssertions):
    """SQL database class

    Provides methods for working with SQL databases

    Attributes:
        _engine: SqlAlchemy engine
        _connection: SqlAlchemy connection
        _database_url: Database url string
        _meta: Database table schema meta
        _name: Database name

    Args:
        name: Database url string
    """


    def __init__(self, database_url: str):
        self._engine: engine.Engine = None
        self._connection: engine.base.Connection = None
        self._database_url: str = database_url
        self._meta: MetaData = None
        self._name: str = make_url(database_url).database


    def connect(self) -> None:
        """Connect to database"""
        try:
            self._engine = create_engine(self._database_url)
            self._connection = self._engine.connect()
            LOGGER.info(f"connected to database {self._database_url}")
        except OperationalError as error:
            LOGGER.debug(error, False)
            raise ServiceNotReadyError(f"failed connection to database  {self._database_url}", error) from error


    def close_connection(self) -> None:
        """Close database connection"""
        LOGGER.info(f"closing connection to database {self._database_url}")
        if self._connection is not None:
            self._connection.close()


    def reflect(self):
        """Reflect database, load tables in meta object"""
        self._meta = MetaData(bind=self._engine, reflect=True)
        return self


    def list_tables(self) -> None:
        """List all tables in database"""
        return self._meta.tables.keys()


    def load_table(self, table_name: str) -> Table:
        """Load table from database

        Returns:
            SQLAlchemy tables
        """
        return Table(table_name, self._meta, autoload=True, autoload_with=self._engine)

    @property
    def engine(self) -> engine:
        """Gets database engine

        Returns:
            SQLAlchemy engine
        """
        return self._engine


    def create_session(self) -> orm.session.Session:
        """create a session for transactions"""
        return Session(self._engine)


    @property
    def name(self) -> str:
        """Gets database name

        Returns:
            Database name
        """
        return self._name
