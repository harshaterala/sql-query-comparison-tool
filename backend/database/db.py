import pyodbc
from flask import current_app, g

def get_db_connection(connection_params):
    """Create database connection with provided parameters"""
    try:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={connection_params['server']};"
            f"DATABASE={connection_params['database']};"
            f"UID={connection_params['username']};"
            f"PWD={connection_params['password']}"
        )
        
        if connection_params.get('trusted_connection'):
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={connection_params['server']};"
                f"DATABASE={connection_params['database']};"
                f"Trusted_Connection=yes;"
            )
            
        conn = pyodbc.connect(conn_str, timeout=10)
        return conn
    except Exception as e:
        raise Exception(f"Connection failed: {str(e)}")

def test_connection(connection_params):
    """Test database connection"""
    try:
        conn = get_db_connection(connection_params)
        conn.close()
        return {"status": "success", "message": "Connected successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
