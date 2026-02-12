import sqlparse
import re

def extract_columns(query):
    """Extract column names from SELECT query"""
    parsed = sqlparse.parse(query)[0]
    
    columns = []
    in_select = False
    
    for token in parsed.tokens:
        if token.ttype is sqlparse.tokens.Keyword.DML and token.value.upper() == 'SELECT':
            in_select = True
        elif in_select and token.ttype is sqlparse.tokens.Keyword:
            if token.value.upper() in ('FROM', 'WHERE', 'GROUP BY', 'ORDER BY'):
                break
        elif in_select and token.ttype is None:
            # This likely contains the column list
            column_text = token.value
            # Split by commas and clean up
            raw_columns = column_text.split(',')
            for col in raw_columns:
                # Remove aliases and whitespace
                col = col.strip()
                if ' as ' in col.lower():
                    col = col.split(' as ')[0].strip()
                elif ' ' in col:
                    parts = col.split()
                    if len(parts) > 1 and parts[0] != '*':
                        col = parts[0]
                if col and col != '*':
                    columns.append(col)
            break
    
    return columns[:20]  # Limit columns
