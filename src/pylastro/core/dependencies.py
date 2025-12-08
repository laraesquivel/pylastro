from .config import DB_PATH
from ..db.duckdb import DuckDBManager


def get_db_manager():
    dudck_db_mamnager = DuckDBManager(DB_PATH)
    return dudck_db_mamnager