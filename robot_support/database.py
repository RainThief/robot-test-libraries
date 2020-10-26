"""docker wrapper module"""
from .database_lib import sql_database, sql_assertions

SQLDatabase = sql_database.SQLDatabase
check_table_exists = sql_assertions.check_table_exists
check_table_not_exists = sql_assertions.check_table_not_exists
check_record_by_position = sql_assertions.check_record_by_position
check_record_count = sql_assertions.check_record_count
check_column_names = sql_assertions.check_column_names
