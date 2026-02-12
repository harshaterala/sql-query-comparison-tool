from flask import Blueprint, request, jsonify, session
from database.db import get_db_connection
from services.query_parser import extract_columns
from utils.validator import validate_sql

query_bp = Blueprint('query', __name__)

@query_bp.route('/api/execute-query', methods=['POST'])
def execute_query():
    """Execute SQL query and return results"""
    data = request.json
    query = data.get('query')
    
    # Validate SQL syntax
    is_valid, error = validate_sql(query)
    if not is_valid:
        return jsonify({"error": error}), 400
    
    try:
        conn = get_db_connection(session.get('db_connection'))
        cursor = conn.cursor()
        cursor.execute(query)
        
        # Get column names
        columns = [column[0] for column in cursor.description]
        
        # Fetch results (limit rows)
        rows = cursor.fetchmany(1000)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "columns": columns,
            "rows": rows,
            "row_count": len(rows)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@query_bp.route('/api/parse-columns', methods=['POST'])
def parse_query_columns():
    """Extract column names from SQL query without executing"""
    data = request.json
    query = data.get('query')
    
    columns = extract_columns(query)
    return jsonify({"columns": columns})
