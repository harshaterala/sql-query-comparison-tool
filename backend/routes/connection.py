from flask import Blueprint, request, jsonify, session
from database.db import test_connection

connection_bp = Blueprint('connection', __name__)

@connection_bp.route('/api/test-connection', methods=['POST'])
def test_database_connection():
    """Test database connection"""
    data = request.json
    
    # Store in session temporarily (encrypt in production)
    session['db_connection'] = data
    
    result = test_connection(data)
    return jsonify(result)
