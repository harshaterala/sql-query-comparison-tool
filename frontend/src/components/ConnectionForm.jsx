import React, { useState } from 'react';
import { testConnection } from '../api/connectionApi';
import './styles/ConnectionForm.css';

const ConnectionForm = ({ onConnectionSuccess }) => {
  const [connection, setConnection] = useState({
    server: '',
    database: '',
    username: '',
    password: '',
    trusted_connection: false
  });
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setConnection({
      ...connection,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleTestConnection = async () => {
    setLoading(true);
    setStatus({ type: 'info', message: 'Testing connection...' });
    
    const result = await testConnection(connection);
    
    if (result.status === 'success') {
      setStatus({ type: 'success', message: result.message });
      onConnectionSuccess(true);
    } else {
      setStatus({ type: 'error', message: result.message });
      onConnectionSuccess(false);
    }
    
    setLoading(false);
  };

  return (
    <div className="connection-form">
      <h3>
        <span className="icon">🗄️</span>
        Database Connection
      </h3>
      
      <div className="form-group">
        <label>Server</label>
        <input
          type="text"
          name="server"
          value={connection.server}
          onChange={handleChange}
          placeholder="localhost or server name"
        />
      </div>
      
      <div className="form-group">
        <label>Database</label>
        <input
          type="text"
          name="database"
          value={connection.database}
          onChange={handleChange}
          placeholder="Database name"
        />
      </div>
      
      <div className="form-check">
        <input
          type="checkbox"
          name="trusted_connection"
          id="trusted_connection"
          checked={connection.trusted_connection}
          onChange={handleChange}
        />
        <label htmlFor="trusted_connection">Windows Authentication</label>
      </div>
      
      {!connection.trusted_connection && (
        <>
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              name="username"
              value={connection.username}
              onChange={handleChange}
            />
          </div>
          
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={connection.password}
              onChange={handleChange}
            />
          </div>
        </>
      )}
      
      <button 
        onClick={handleTestConnection} 
        disabled={loading}
        className="btn-primary"
      >
        {loading ? 'Testing...' : 'Test Connection'}
      </button>
      
      {status && (
        <div className={`status-indicator ${status.type}`}>
          {status.type === 'success' && '✓'}
          {status.type === 'error' && '✗'}
          {status.type === 'info' && 'ℹ'}
          {status.message}
        </div>
      )}
    </div>
  );
};

export default ConnectionForm;
