"""
Result Formatter Service
Handles formatting of comparison results for different output formats
Supports JSON, CSV, Excel, and HTML report generation
"""

import json
import csv
import io
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import html


class ResultFormatter:
    """Format comparison results for various output formats"""
    
    @staticmethod
    def format_for_display(comparison_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format raw comparison results for frontend display
        Handles data type serialization and null values
        """
        formatted = {
            "summary": comparison_result.get("summary", {}),
            "matches": [],
            "only_in_query1": [],
            "only_in_query2": [],
            "mismatches": [],
            "columns": comparison_result.get("columns", {})
        }
        
        # Format matches - convert non-serializable types
        for match in comparison_result.get("matches", []):
            formatted_match = {}
            for key, value in match.items():
                formatted_match[key] = ResultFormatter._serialize_value(value)
            formatted["matches"].append(formatted_match)
        
        # Format only_in_query1
        for row in comparison_result.get("only_in_query1", []):
            formatted_row = {}
            for key, value in row.items():
                formatted_row[key] = ResultFormatter._serialize_value(value)
            formatted["only_in_query1"].append(formatted_row)
        
        # Format only_in_query2
        for row in comparison_result.get("only_in_query2", []):
            formatted_row = {}
            for key, value in row.items():
                formatted_row[key] = ResultFormatter._serialize_value(value)
            formatted["only_in_query2"].append(formatted_row)
        
        # Format mismatches with detailed differences
        for mismatch in comparison_result.get("mismatches", []):
            formatted_mismatch = {
                "key": {},
                "differences": {}
            }
            
            # Format key values
            for key, value in mismatch.get("key", {}).items():
                formatted_mismatch["key"][key] = ResultFormatter._serialize_value(value)
            
            # Format differences
            for col, diff in mismatch.get("differences", {}).items():
                formatted_mismatch["differences"][col] = {
                    "query1": ResultFormatter._serialize_value(diff.get("query1")),
                    "query2": ResultFormatter._serialize_value(diff.get("query2"))
                }
            
            formatted["mismatches"].append(formatted_mismatch)
        
        return formatted
    
    @staticmethod
    def _serialize_value(value: Any) -> Any:
        """Convert non-serializable types to JSON-compatible formats"""
        if value is None:
            return None
        elif isinstance(value, (datetime, pd.Timestamp)):
            return value.isoformat()
        elif isinstance(value, (pd.Int64Dtype, pd.Float64Dtype)):
            return float(value) if hasattr(value, 'item') else value
        elif hasattr(value, 'item'):  # numpy/pandas types
            return value.item()
        elif isinstance(value, (bytes, bytearray)):
            return value.hex() if len(value) < 1000 else "[BINARY DATA]"
        elif isinstance(value, dict):
            return {k: ResultFormatter._serialize_value(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [ResultFormatter._serialize_value(v) for v in value]
        else:
            return str(value) if not isinstance(value, (str, int, float, bool)) else value

    @staticmethod
    def to_json(comparison_result: Dict[str, Any], pretty: bool = True) -> str:
        """Export comparison results as JSON"""
        formatted = ResultFormatter.format_for_display(comparison_result)
        
        # Add metadata
        output = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "1.0.0",
                "type": "sql_comparison_result"
            },
            "data": formatted
        }
        
        indent = 2 if pretty else None
        return json.dumps(output, indent=indent, default=str)
    
    @staticmethod
    def to_csv(comparison_result: Dict[str, Any]) -> Dict[str, str]:
        """
        Export comparison results as CSV files
        Returns dictionary with CSV content for each category
        """
        formatted = ResultFormatter.format_for_display(comparison_result)
        csv_outputs = {}
        
        # Export matches to CSV
        if formatted["matches"]:
            csv_outputs["matches"] = ResultFormatter._dicts_to_csv(
                formatted["matches"], 
                "matches.csv"
            )
        
        # Export only_in_query1 to CSV
        if formatted["only_in_query1"]:
            csv_outputs["only_query1"] = ResultFormatter._dicts_to_csv(
                formatted["only_in_query1"],
                "only_query1.csv"
            )
        
        # Export only_in_query2 to CSV
        if formatted["only_in_query2"]:
            csv_outputs["only_query2"] = ResultFormatter._dicts_to_csv(
                formatted["only_in_query2"],
                "only_query2.csv"
            )
        
        # Export mismatches summary to CSV
        if formatted["mismatches"]:
            mismatch_rows = []
            for mismatch in formatted["mismatches"]:
                key_str = ", ".join([f"{k}={v}" for k, v in mismatch["key"].items()])
                for col, diff in mismatch["differences"].items():
                    mismatch_rows.append({
                        "key": key_str,
                        "column": col,
                        "query1_value": diff["query1"],
                        "query2_value": diff["query2"],
                        "match_status": "MISMATCH"
                    })
            
            if mismatch_rows:
                csv_outputs["mismatches"] = ResultFormatter._dicts_to_csv(
                    mismatch_rows,
                    "mismatches.csv"
                )
        
        # Export summary statistics
        summary_rows = [{
            "metric": k.replace("_", " ").title(),
            "value": v
        } for k, v in formatted["summary"].items()]
        
        csv_outputs["summary"] = ResultFormatter._dicts_to_csv(
            summary_rows,
            "summary.csv"
        )
        
        return csv_outputs
    
    @staticmethod
    def _dicts_to_csv(data: List[Dict], filename: str) -> Dict[str, str]:
        """Convert list of dictionaries to CSV string"""
        if not data:
            return {"filename": filename, "content": ""}
        
        output = io.StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        return {
            "filename": filename,
            "content": output.getvalue()
        }
    
    @staticmethod
    def to_excel(comparison_result: Dict[str, Any]) -> io.BytesIO:
        """Export comparison results as Excel file with multiple sheets"""
        formatted = ResultFormatter.format_for_display(comparison_result)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Summary sheet
            summary_df = pd.DataFrame([
                {"Metric": k.replace("_", " ").title(), "Value": v}
                for k, v in formatted["summary"].items()
            ])
            summary_df.to_excel(writer, sheet_name="Summary", index=False)
            
            # Matches sheet
            if formatted["matches"]:
                matches_df = pd.DataFrame(formatted["matches"])
                matches_df.to_excel(writer, sheet_name="Matches", index=False)
            
            # Only Query 1 sheet
            if formatted["only_in_query1"]:
                only1_df = pd.DataFrame(formatted["only_in_query1"])
                only1_df.to_excel(writer, sheet_name="Only in Query 1", index=False)
            
            # Only Query 2 sheet
            if formatted["only_in_query2"]:
                only2_df = pd.DataFrame(formatted["only_in_query2"])
                only2_df.to_excel(writer, sheet_name="Only in Query 2", index=False)
            
            # Mismatches sheet
            if formatted["mismatches"]:
                mismatch_rows = []
                for mismatch in formatted["mismatches"]:
                    key_str = ", ".join([f"{k}={v}" for k, v in mismatch["key"].items()])
                    for col, diff in mismatch["differences"].items():
                        mismatch_rows.append({
                            "Key": key_str,
                            "Column": col,
                            "Query 1 Value": diff["query1"],
                            "Query 2 Value": diff["query2"]
                        })
                
                if mismatch_rows:
                    mismatches_df = pd.DataFrame(mismatch_rows)
                    mismatches_df.to_excel(writer, sheet_name="Mismatches", index=False)
        
        output.seek(0)
        return output
    
    @staticmethod
    def to_html_report(comparison_result: Dict[str, Any]) -> str:
        """Generate HTML report for comparison results"""
        formatted = ResultFormatter.format_for_display(comparison_result)
        summary = formatted["summary"]
        
        # Color coding based on match percentage
        total_rows = summary.get("total_rows_query1", 0) + summary.get("total_rows_query2", 0)
        match_count = summary.get("matches", 0)
        match_percentage = (match_count / total_rows * 100) if total_rows > 0 else 0
        
        if match_percentage >= 95:
            status_color = "#28a745"  # Green
            status_text = "Excellent"
        elif match_percentage >= 80:
            status_color = "#ffc107"  # Yellow
            status_text = "Good"
        else:
            status_color = "#dc3545"  # Red
            status_text = "Needs Review"
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>SQL Comparison Report - {datetime.now().strftime('%Y-%m-%d')}</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f7fa;
                }}
                .report-header {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 30px;
                }}
                h1 {{
                    color: #1a2b3c;
                    margin: 0 0 10px 0;
                    border-bottom: 3px solid #28a745;
                    padding-bottom: 10px;
                    display: inline-block;
                }}
                .report-meta {{
                    color: #6c757d;
                    font-size: 14px;
                    margin-top: 10px;
                }}
                .status-badge {{
                    display: inline-block;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-weight: 600;
                    background-color: {status_color};
                    color: white;
                    margin-left: 20px;
                }}
                .summary-cards {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .card {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    border-left: 4px solid #28a745;
                }}
                .card.match {{ border-left-color: #28a745; }}
                .card.mismatch {{ border-left-color: #dc3545; }}
                .card.only1 {{ border-left-color: #fd7e14; }}
                .card.only2 {{ border-left-color: #17a2b8; }}
                .card-value {{
                    font-size: 32px;
                    font-weight: 700;
                    margin: 5px 0;
                }}
                .card-label {{
                    color: #6c757d;
                    font-size: 14px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                .section {{
                    background: white;
                    padding: 25px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 30px;
                }}
                h2 {{
                    color: #1a2b3c;
                    margin-top: 0;
                    margin-bottom: 20px;
                    font-size: 20px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 14px;
                }}
                th {{
                    background-color: #f8f9fa;
                    padding: 12px;
                    text-align: left;
                    font-weight: 600;
                    color: #495057;
                    border-bottom: 2px solid #dee2e6;
                }}
                td {{
                    padding: 10px 12px;
                    border-bottom: 1px solid #e9ecef;
                    font-family: 'SF Mono', 'Menlo', monospace;
                }}
                tr:hover {{
                    background-color: #f8f9fa;
                }}
                .mismatch-row {{
                    background-color: #fff3e0;
                }}
                .match-highlight {{
                    background-color: #e8f5e9;
                }}
                .footer {{
                    text-align: center;
                    color: #6c757d;
                    font-size: 12px;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #dee2e6;
                }}
                .progress-bar {{
                    width: 100%;
                    height: 20px;
                    background-color: #e9ecef;
                    border-radius: 10px;
                    margin: 15px 0;
                    overflow: hidden;
                }}
                .progress-fill {{
                    height: 100%;
                    background-color: {status_color};
                    width: {match_percentage}%;
                    border-radius: 10px;
                    transition: width 0.3s ease;
                }}
                @media print {{
                    body {{
                        background-color: white;
                    }}
                    .card, .section {{
                        box-shadow: none;
                        border: 1px solid #dee2e6;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="report-header">
                <h1>SQL Query Comparison Report</h1>
                <span class="status-badge">{status_text}</span>
                <div class="report-meta">
                    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
                    Execution Time: {summary.get('execution_time', 0)}s
                </div>
                <div class="progress-bar">
                    <div class="progress-fill"></div>
                </div>
                <div style="text-align: right; font-size: 13px; margin-top: 5px;">
                    Match Rate: {match_percentage:.1f}% ({match_count}/{total_rows})
                </div>
            </div>
            
            <div class="summary-cards">
                <div class="card match">
                    <div class="card-label">Matching Rows</div>
                    <div class="card-value">{summary.get('matches', 0)}</div>
                    <div style="color: #28a745;">✓ Perfect matches</div>
                </div>
                <div class="card mismatch">
                    <div class="card-label">Mismatches</div>
                    <div class="card-value">{summary.get('mismatches', 0)}</div>
                    <div style="color: #dc3545;">⚠ Value differences</div>
                </div>
                <div class="card only1">
                    <div class="card-label">Only in Query 1</div>
                    <div class="card-value">{summary.get('only_in_query1', 0)}</div>
                    <div style="color: #fd7e14;">→ Missing from Query 2</div>
                </div>
                <div class="card only2">
                    <div class="card-label">Only in Query 2</div>
                    <div class="card-value">{summary.get('only_in_query2', 0)}</div>
                    <div style="color: #17a2b8;">← Missing from Query 1</div>
                </div>
            </div>
            
            <div class="section">
                <h2>📊 Detailed Comparison Results</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Count</th>
                            <th>Percentage</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr class="match-highlight">
                            <td><strong>Matches</strong></td>
                            <td>{summary.get('matches', 0)}</td>
                            <td>{match_percentage:.1f}%</td>
                            <td style="color: #28a745;">✓ Match</td>
                        </tr>
                        <tr>
                            <td>Mismatches</td>
                            <td>{summary.get('mismatches', 0)}</td>
                            <td>{(summary.get('mismatches', 0) / total_rows * 100) if total_rows > 0 else 0:.1f}%</td>
                            <td style="color: #dc3545;">⚠ Review</td>
                        </tr>
                        <tr>
                            <td>Only in Query 1</td>
                            <td>{summary.get('only_in_query1', 0)}</td>
                            <td>{(summary.get('only_in_query1', 0) / total_rows * 100) if total_rows > 0 else 0:.1f}%</td>
                            <td style="color: #fd7e14;">→ Missing</td>
                        </tr>
                        <tr>
                            <td>Only in Query 2</td>
                            <td>{summary.get('only_in_query2', 0)}</td>
                            <td>{(summary.get('only_in_query2', 0) / total_rows * 100) if total_rows > 0 else 0:.1f}%</td>
                            <td style="color: #17a2b8;">← Missing</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        """
        
        # Add mismatches section if any exist
        if formatted["mismatches"]:
            html_template += """
            <div class="section">
                <h2>⚠ Value Mismatches</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Key</th>
                            <th>Column</th>
                            <th>Query 1 Value</th>
                            <th>Query 2 Value</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for mismatch in formatted["mismatches"][:50]:  # Limit to first 50 mismatches
                key_str = ", ".join([f"{k}={v}" for k, v in mismatch["key"].items()])
                for col, diff in mismatch["differences"].items():
                    html_template += f"""
                        <tr class="mismatch-row">
                            <td><code>{html.escape(key_str)}</code></td>
                            <td><strong>{html.escape(col)}</strong></td>
                            <td style="color: #dc3545;"><code>{html.escape(str(diff['query1']))}</code></td>
                            <td style="color: #28a745;"><code>{html.escape(str(diff['query2']))}</code></td>
                        </tr>
                    """
            
            html_template += """
                    </tbody>
                </table>
            """
            
            if len(formatted["mismatches"]) > 50:
                html_template += f"""
                <p style="color: #6c757d; margin-top: 15px;">
                    * Showing first 50 of {len(formatted['mismatches'])} mismatches
                </p>
                """
            
            html_template += "</div>"
        
        # Add matches preview if any exist
        if formatted["matches"]:
            html_template += """
            <div class="section">
                <h2>✓ Matching Rows Preview</h2>
                <table>
                    <thead>
                        <tr>
            """
            
            # Add table headers
            if formatted["matches"]:
                for col in formatted["matches"][0].keys():
                    html_template += f"<th>{html.escape(str(col))}</th>"
            
            html_template += """
                        </tr>
                    </thead>
                    <tbody>
            """
            
            # Add first 20 matches
            for match in formatted["matches"][:20]:
                html_template += "<tr>"
                for value in match.values():
                    html_template += f"<td><code>{html.escape(str(value))}</code></td>"
                html_template += "</tr>"
            
            html_template += """
                    </tbody>
                </table>
            """
            
            if len(formatted["matches"]) > 20:
                html_template += f"""
                <p style="color: #6c757d; margin-top: 15px;">
                    * Showing first 20 of {len(formatted['matches'])} matching rows
                </p>
                """
            
            html_template += "</div>"
        
        # Close HTML
        html_template += """
            <div class="footer">
                <p>Generated by SQL Query Comparison Tool v1.0.0</p>
                <p>Report includes all comparison results and detailed mismatch analysis</p>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    @staticmethod
    def to_markdown(comparison_result: Dict[str, Any]) -> str:
        """Generate Markdown report for documentation"""
        formatted = ResultFormatter.format_for_display(comparison_result)
        summary = formatted["summary"]
        
        total_rows = summary.get("total_rows_query1", 0) + summary.get("total_rows_query2", 0)
        match_percentage = (summary.get("matches", 0) / total_rows * 100) if total_rows > 0 else 0
        
        md = []
        md.append("# SQL Query Comparison Report")
        md.append("")
        md.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md.append(f"**Execution Time:** {summary.get('execution_time', 0)}s")
        md.append(f"**Match Rate:** {match_percentage:.1f}%")
        md.append("")
        
        # Summary table
        md.append("## Summary Statistics")
        md.append("")
        md.append("| Metric | Value |")
        md.append("|--------|-------|")
        md.append(f"| Total Rows (Query 1) | {summary.get('total_rows_query1', 0)} |")
        md.append(f"| Total Rows (Query 2) | {summary.get('total_rows_query2', 0)} |")
        md.append(f"| ✅ Matches | {summary.get('matches', 0)} |")
        md.append(f"| ⚠ Mismatches | {summary.get('mismatches', 0)} |")
        md.append(f"| → Only in Query 1 | {summary.get('only_in_query1', 0)} |")
        md.append(f"| ← Only in Query 2 | {summary.get('only_in_query2', 0)} |")
        md.append("")
        
        # Mismatches
        if formatted["mismatches"]:
            md.append("## ⚠ Mismatch Details")
            md.append("")
            
            for i, mismatch in enumerate(formatted["mismatches"][:20], 1):
                key_str = ", ".join([f"**{k}**={v}" for k, v in mismatch["key"].items()])
                md.append(f"### Mismatch {i}: {key_str}")
                md.append("")
                md.append("| Column | Query 1 Value | Query 2 Value |")
                md.append("|--------|---------------|---------------|")
                
                for col, diff in mismatch["differences"].items():
                    md.append(f"| {col} | `{diff['query1']}` | `{diff['query2']}` |")
                
                md.append("")
            
            if len(formatted["mismatches"]) > 20:
                md.append(f"*... and {len(formatted['mismatches']) - 20} more mismatches*")
                md.append("")
        
        # Column mappings
        md.append("## Column Mappings")
        md.append("")
        md.append("| Query 1 Column | Query 2 Column |")
        md.append("|----------------|----------------|")
        
        columns = formatted.get("columns", {})
        query1_cols = columns.get("query1", [])
        query2_cols = columns.get("query2", [])
        mapped_cols = columns.get("mapped", [])
        
        for col in mapped_cols:
            md.append(f"| {col} | {col} |")
        
        # Add unmapped columns
        unmapped1 = [c for c in query1_cols if c not in mapped_cols]
        unmapped2 = [c for c in query2_cols if c not in mapped_cols]
        
        if unmapped1:
            md.append(f"| *{', '.join(unmapped1)}* | *(unmapped)* |")
        if unmapped2:
            md.append(f"| *(unmapped)* | *{', '.join(unmapped2)}* |")
        
        md.append("")
        
        return "\n".join(md)


class ComparisonReportGenerator:
    """Generate comprehensive comparison reports"""
    
    def __init__(self, comparison_result: Dict[str, Any]):
        self.result = comparison_result
        self.formatter = ResultFormatter
    
    def generate_report_package(self) -> Dict[str, Any]:
        """Generate all report formats in one package"""
        return {
            "json": self.formatter.to_json(self.result),
            "csv": self.formatter.to_csv(self.result),
            "excel": self.formatter.to_excel(self.result),
            "html": self.formatter.to_html_report(self.result),
            "markdown": self.formatter.to_markdown(self.result),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "row_count": {
                    "matches": len(self.result.get("matches", [])),
                    "mismatches": len(self.result.get("mismatches", [])),
                    "only_query1": len(self.result.get("only_in_query1", [])),
                    "only_query2": len(self.result.get("only_in_query2", []))
                }
            }
        }
    
    def save_report(self, output_dir: str, formats: List[str] = None) -> Dict[str, str]:
        """Save reports to files"""
        import os
        
        if formats is None:
            formats = ["json", "csv", "html", "markdown"]
        
        os.makedirs(output_dir, exist_ok=True)
        saved_files = {}
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if "json" in formats:
            json_content = self.formatter.to_json(self.result)
            filename = f"comparison_report_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w") as f:
                f.write(json_content)
            saved_files["json"] = filepath
        
        if "csv" in formats:
            csv_files = self.formatter.to_csv(self.result)
            for key, csv_data in csv_files.items():
                if csv_data.get("content"):
                    filename = f"{key}_{timestamp}.csv"
                    filepath = os.path.join(output_dir, filename)
                    with open(filepath, "w", newline="") as f:
                        f.write(csv_data["content"])
                    saved_files[f"csv_{key}"] = filepath
        
        if "excel" in formats:
            excel_content = self.formatter.to_excel(self.result)
            filename = f"comparison_report_{timestamp}.xlsx"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "wb") as f:
                f.write(excel_content.getvalue())
            saved_files["excel"] = filepath
        
        if "html" in formats:
            html_content = self.formatter.to_html_report(self.result)
            filename = f"comparison_report_{timestamp}.html"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w") as f:
                f.write(html_content)
            saved_files["html"] = filepath
        
        if "markdown" in formats:
            md_content = self.formatter.to_markdown(self.result)
            filename = f"comparison_report_{timestamp}.md"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w") as f:
                f.write(md_content)
            saved_files["markdown"] = filepath
        
        return saved_files