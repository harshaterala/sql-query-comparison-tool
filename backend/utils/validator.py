import sqlparse

def validate_sql(query):
    """Validate SQL query syntax"""
    try:
        parsed = sqlparse.parse(query)
        if not parsed:
            return False, "Empty query"
        
        # Check if it's a SELECT query
        first_token = parsed[0].token_first()
        if not first_token or first_token.value.upper() != 'SELECT':
            return False, "Only SELECT queries are supported"
            
        return True, None
    except Exception as e:
        return False, str(e)
