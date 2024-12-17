from sqlalchemy import create_engine

def create_db_connection(connection_string):
    """
    Creates and returns a SQLAlchemy engine for the database connection.

    Args:
        connection_string (str): The connection string to the SQL database.

    Returns:
        Engine: SQLAlchemy engine object.
    """
    try:
        engine = create_engine(connection_string)
        # Test the connection
        with engine.connect():
            print("Database connection established.")
        return engine
    except Exception as e:
        raise ConnectionError(f"Failed to connect to the database: {e}")
