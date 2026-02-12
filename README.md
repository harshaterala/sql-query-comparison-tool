🚀 Setup & Running Instructions
Backend Setup:
bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
Frontend Setup:
bash
cd frontend
npm install
npm start
SQL Server ODBC Driver:
Download and install "ODBC Driver 17 for SQL Server" from Microsoft

Ensure SQL Server is configured for TCP/IP connections

✅ Features Implemented
Database Connection - Test and establish SQL Server connection

Query Input - SQL editor with column auto-detection

Column Mapping - Visual interface for column mapping with primary key selection

Comparison Engine - Row-by-row comparison based on mapped keys

Results Display - Color-coded results with summary statistics

Export Options - JSON and CSV export

Error Handling - User-friendly error messages

🔮 Future Enhancements
Query history

Saved comparisons

Advanced comparison options (case sensitivity, null handling)

Pagination for large result sets

WebSocket for real-time comparison progress

Authentication & user management

Scheduled comparisons

This implementation provides a solid foundation for your SQL query comparison tool with a clean, professional UI and robust backend processing.
