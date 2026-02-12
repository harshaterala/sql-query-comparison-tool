from database.db import get_db_connection
import pandas as pd
from datetime import datetime

def compare_queries(connection_params, query1, query2, mappings, primary_keys):
    """Compare results of two SQL queries"""
    start_time = datetime.now()
    
    # Execute queries
    conn = get_db_connection(connection_params)
    
    df1 = pd.read_sql(query1, conn)
    df2 = pd.read_sql(query2, conn)
    
    conn.close()
    
    # Prepare mapping dictionary
    mapping_dict = {}
    for m in mappings:
        mapping_dict[m['left']] = m['right']
    
    # Reverse mapping for result display
    reverse_map = {v: k for k, v in mapping_dict.items()}
    
    # Rename columns in df2 to match df1
    df2_renamed = df2.rename(columns=mapping_dict)
    
    # Identify common columns for comparison
    common_columns = [col for col in df1.columns if col in df2_renamed.columns]
    
    # Determine join keys (primary keys)
    join_keys = primary_keys if primary_keys else common_columns[:1]
    
    # Perform comparison
    merged = pd.merge(
        df1, 
        df2_renamed, 
        on=join_keys, 
        how='outer', 
        suffixes=('_query1', '_query2'),
        indicator=True
    )
    
    # Categorize results
    matches = merged[merged['_merge'] == 'both']
    only_query1 = merged[merged['_merge'] == 'left_only']
    only_query2 = merged[merged['_merge'] == 'right_only']
    
    # Compare values in matches
    mismatches = []
    for idx, row in matches.iterrows():
        row_mismatches = {}
        for col in common_columns:
            if col not in join_keys:
                val1 = row[f"{col}_query1"]
                val2 = row[f"{col}_query2"]
                if str(val1) != str(val2):
                    row_mismatches[col] = {
                        "query1": val1,
                        "query2": val2
                    }
        if row_mismatches:
            mismatches.append({
                "key": {k: row[k] for k in join_keys},
                "differences": row_mismatches
            })
    
    execution_time = (datetime.now() - start_time).total_seconds()
    
    # Format results
    return {
        "summary": {
            "total_rows_query1": len(df1),
            "total_rows_query2": len(df2),
            "matches": len(matches),
            "only_in_query1": len(only_query1),
            "only_in_query2": len(only_query2),
            "mismatches": len(mismatches),
            "execution_time": round(execution_time, 2)
        },
        "matches": matches.head(100).to_dict('records') if not matches.empty else [],
        "only_in_query1": only_query1.head(100).to_dict('records') if not only_query1.empty else [],
        "only_in_query2": only_query2.head(100).to_dict('records') if not only_query2.empty else [],
        "mismatches": mismatches[:100],
        "columns": {
            "query1": df1.columns.tolist(),
            "query2": df2.columns.tolist(),
            "mapped": common_columns
        }
    }
