"""sql database assertions"""
from typing import Union, List
from abc import ABC
from robot_support.logger import Logger
from robot_support.errors import NotExpectedError


LOGGER = Logger.get_instance()


class SQLAssertions(ABC):
    # disable errors not relevant when passthrough args
    # pylint: disable=unused-argument, no-self-use
    """SQL utility abstract class

    Allows sql utility functions to be used as class methods in subclass"""


    def check_table_exists(self, table_name: str) -> None:
        """wraps sql_assertions.check_table_exists"""
        check_table_exists(*locals().values())


    def check_table_not_exists(self, table_name: str) -> None:
        """wraps sql_assertions.check_table_not_exists"""
        check_table_not_exists(*locals().values())


    def check_record_by_position(
        self,
        position: Union[str,int],
        table_name: str,
        col_name: str,
        expected_val: str
    ):
        """wraps sql_assertions.check_record_by_position"""
        check_record_by_position(*locals().values())


    def check_record_count(self, table_name: str, expected_records: int) -> None:
        """wraps sql_assertions.check_record_count"""
        check_record_count(*locals().values())


    def check_column_names(self, table_name: str, expected_columns: List[str]) -> None:
        """wraps sql_assertions.check_column_names"""
        check_column_names(*locals().values())



def check_table_exists(database: object, table_name: str) -> None:
    """Checks a if a table exists in database

    Args:
        database: robot support database object
        table_name: the table to query
    """
    LOGGER.info(f"checking table {table_name} exists in database {database.name}")
    if table_name not in database.reflect().list_tables():
        raise NotExpectedError(f"table {table_name} does not exist in database {database.name}")


def check_table_not_exists(database: object, table_name: str) -> None:
    """Checks a if a table does NOT exist in database

    Args:
        database: robot support database object
        table_name: the table to query
    """
    LOGGER.info(f"checking table {table_name} NOT exists in database {database.name}")
    if table_name in database.reflect().list_tables():
        raise NotExpectedError(f"table {table_name} exists in database {database.name}")


def check_record_by_position(
    database: object,
    position: Union[str,int],
    table_name: str,
    col_name: str,
    expected_val: str
) -> None:
    """Checks a record in database table by human readable or numerical position

    Compares a referenced column in given position against an expect value

    Args:
        database: robot support database object
        position: position identifier
        table_name: the table to query
        col_name: the column to extract value
        expected_val: the expected value retrieved from database
    """
    LOGGER.info(
        f"checking table {table_name} in database {database.name}, "
        + f"{position} record in col {col_name} has value {expected_val}"
    )

    def pos(index):
        switcher={
            'first': 0,
            'second': 1,
            'third': 2,
            'forth': 3,
            'fifth': 4,
        }
        return switcher.get(index, 0)

    result = getattr(
        database.create_session().query(database.load_table(table_name)).offset(pos(position)).limit(1)[0],
        col_name
    )
    if result != expected_val:
        raise NotExpectedError(
            f"database {database.name}, "
            + f"{table_name} table {position} record in col {col_name} has value {result}; expected {expected_val}"
        )


def check_record_count(database, table_name: str, expected_records: int) -> None:
    """Checks a count of records in a table

    Compares a table count against an expected value

    Args:
        database: robot support database object
        table_name: the table to query
        expected_records: the number of records expected in table
    """
    LOGGER.info(f"checking table {table_name} in database {database.name} has {expected_records} records")
    rows = database.create_session().query(database.load_table(table_name)).count()
    if rows != int(expected_records):
        raise NotExpectedError(
            f"database {database.name} {table_name} table has {rows} records; expected {expected_records}"
        )


def check_column_names(database, table_name: str, expected_columns: List[str]) -> None:
    """Checks a list of table column names

    Compares a list of table column names against an expect list

    Args:
        database: robot support database object
        table_name: the table to query
        expected_columns: the list of column names expected in table
    """
    LOGGER.info(f"checking table {table_name} in database {database.name} has columns {expected_columns}")
    cols_found = [c.name for c in database.load_table(table_name).c]
    if expected_columns != cols_found:
        raise NotExpectedError(
            f"database {database.name}, "
            + f"{table_name} table columns expected {expected_columns} does not match found columns {cols_found}"
        )
