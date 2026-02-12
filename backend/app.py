from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_session import Session
from routes.connection import connection_bp
from routes.query import query_bp
from routes.compare import compare_bp
from config import DevelopmentConfig

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

# Enable CORS for React frontend
CORS(app, origins=['http://localhost:3000'], supports_credentials=True)

# Configure session for connection storage
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
Session(app)

# Register blueprints
app.register_blueprint(connection_bp)
app.register_blueprint(query_bp)
app.register_blueprint(compare_bp)

@app.route('/health', methods=['GET'])
def health_check():
    return {"status": "healthy"}

if __name__ == '__main__':
    app.run(debug=True, port=5000)
