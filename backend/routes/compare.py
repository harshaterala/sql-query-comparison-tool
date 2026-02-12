from flask import Blueprint, request, jsonify, session
from services.comparator import compare_queries

compare_bp = Blueprint('compare', __name__)

@compare_bp.route('/api/compare', methods=['POST'])
def compare_query_results():
    """Execute and compare two SQL queries"""
    data = request.json
    query1 = data.get('query1')
    query2 = data.get('query2')
    mappings = data.get('mappings', [])
    primary_keys = data.get('primary_keys', [])
    
    try:
        result = compare_queries(
            session.get('db_connection'),
            query1,
            query2,
            mappings,
            primary_keys
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
