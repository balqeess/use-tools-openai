from sqlalchemy import inspect
from sqlalchemy.sql import text
import pandas as pd

def get_metadata(engine):
    """
    Retrieves metadata about the database, including table names and their schemas.

    Parameters:
        engine (Engine): SQLAlchemy engine object.

    Returns:
        dict: A dictionary where keys are table names and values are lists of column details.
    """
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    metadata = {}
    for table in tables:
        columns = inspector.get_columns(table)
        metadata[table] = [{"name": col["name"], "type": col["type"]} for col in columns]
    return metadata


def list_tables(engine):
    """
    Lists all table names in the database.

    Parameters:
        engine (Engine): SQLAlchemy engine object.

    Returns:
        list: A list of table names present in the database.
    """
    inspector = inspect(engine)
    return inspector.get_table_names()


def check_query(engine, query):
    """
    Validates a SQL query without executing it and provides guidelines for best practices.

    Parameters:
    ----------
    engine : sqlalchemy.engine.base.Engine
        SQLAlchemy engine object.
    query : str
        The SQL query to validate.

    Returns:
    -------
    str
        A message indicating whether the query is valid or contains errors.

    Guidelines for Writing SQL Queries:
    -----------------------------------
    1. **Handling Numeric Columns:**
       - If numeric columns contain formatted values (e.g., commas as thousand separators),
         use `REPLACE()` to clean them before processing.
         Example: `CAST(REPLACE(column_name, ',', '') AS REAL)`

    2. **GROUP BY and ORDER BY:**
       - Ensure queries with `GROUP BY` include an `ORDER BY` clause for logical sorting.
         Example: `SELECT column_name FROM table GROUP BY column_name ORDER BY column_name`

    3. **Proper Quoting of Column Names:**
       - Enclose column names with spaces or special characters in backticks (`) or double quotes (").
         Example: `SELECT "column name" FROM table` or `SELECT `column name` FROM table`


    Example Usage:
    --------------
    >>> check_query(engine, "SELECT * FROM transactions WHERE amount > 1000;")
    "Valid SQL query."
    """
    try:
        with engine.connect() as conn:
            conn.execute(text(query))  # Validate query execution
        return "Valid SQL query."
    except Exception as e:
        return f"Invalid SQL query: {str(e)}"



def execute_query(engine, query):
    """
    Executes a SQL query and returns the results.

    Parameters:
        engine (Engine): SQLAlchemy engine object.
        query (str): The SQL query to execute.
                     Dates in the query must be formatted as `dd-MMM-yy` (e.g., if the question contains '2nd of January 2015', then the query will have '02-Jan-15' ).
                     Column Names: If column names contain spaces, special characters, or reserved keywords, 
                                    enclose them in backticks (`) or double quotes (") to avoid syntax errors.
                                    Example: 
                                    `SELECT MAX("column name") FROM table;` or 
                                    `SELECT MAX(`column name`) FROM table;`

    Returns:
        pandas.DataFrame: A DataFrame containing the query results.
    """
    with engine.connect() as conn:
        result = conn.execute(text(query))  # Wrap the query in `text`
        data = result.fetchall()
        columns = result.keys()
        return pd.DataFrame(data, columns=columns)
    

