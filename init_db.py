
"""
This sets up a budget database from scratch.
"""

from budget import DB_NAME
import sqlite3

if __name__ == "__main__":

    db_conn = sqlite3.connect(DB_NAME)
    db_cursor = db_conn.cursor()
    init_sql = """
    CREATE TABLE accounts (
    name NVARCHAR,
    balance DOUBLE);
    """

    try:
        print("Initializing accounts table...")
        db_cursor.execute(init_sql)
    except sqlite3.OperationalError:
        print("Skipping initialization of accounts table - already exists")

    init_sql = """
    CREATE TABLE history (
    id INTEGER PRIMARY KEY,
    account_from NVARCHAR,
    charge DOUBLE,
    date DATE,
    notes NVARCHAR,
    account_to NVARCHAR,
    file_name NVARCHAR,
    file_type NVARCHAR,
    file_size INTEGER,
    file_data IMAGE);
    """

    try:
        print("Initializing history table...")
        db_cursor.execute(init_sql)
    except sqlite3.OperationalError:
        print("Skipping initialization of history table - already exists")

    db_conn.commit()
    db_conn.close()