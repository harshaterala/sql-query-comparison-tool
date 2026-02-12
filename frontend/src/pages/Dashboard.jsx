import React, { useState } from 'react';
import ConnectionForm from '../components/ConnectionForm';
import QueryEditor from '../components/QueryEditor';
import ColumnMapper from '../components/ColumnMapper';
import ResultView from '../components/ResultView';
import { runComparison } from '../api/comparisonApi';
import './styles/Dashboard.css';

const Dashboard = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [query1, setQuery1] = useState('');
  const [query2, setQuery2] = useState('');
  const [columns1, setColumns1] = useState([]);
  const [columns2, setColumns2] = useState([]);
  const [mappings, setMappings] = useState([]);
  const [primaryKeys, setPrimaryKeys] = useState([]);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleConnectionSuccess = (connected) => {
    setIsConnected(connected);
  };

  const handleRunComparison = async () => {
    if (!query1.trim() || !query2.trim()) {
      setError('Please enter both SQL queries');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const result = await runComparison(query1, query2, mappings, primaryKeys);
      setComparisonResult(result);
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Comparison failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRestart = () => {
    setQuery1('');
    setQuery2('');
    setColumns1([]);
    setColumns2([]);
    setMappings([]);
    setPrimaryKeys([]);
    setComparisonResult(null);
    setError(null);
    setIsConnected(false);
  };

  return (
    <div className="dashboard">
      <div className="sidebar">
        <ConnectionForm onConnectionSuccess={handleConnectionSuccess} />
        
        <div className="action-buttons">
          <button 
            className="btn-run"
            onClick={handleRunComparison}
            disabled={!isConnected || !query1 || !query2 || loading}
          >
            {loading ? 'Running...' : '▶ Run Comparison'}
          </button>
          
          <button 
            className="btn-restart"
            onClick={handleRestart}
          >
            ↻ Restart
          </button>
        </div>
      </div>
      
      <div className="main-content">
        <h1>SQL Query Comparison Tool</h1>
        
        {!isConnected && (
          <div className="connection-prompt">
            <p>Please connect to a database to begin</p>
          </div>
        )}
        
        <div className="query-section">
          <div className="query-column">
            <QueryEditor
              label="Query 1"
              placeholder="SELECT name, id FROM employees"
              onQueryChange={setQuery1}
              onColumnsParsed={setColumns1}
            />
          </div>
          
          <div className="query-column">
            <QueryEditor
              label="Query 2"
              placeholder="SELECT full_name, employee_id FROM staff"
              onQueryChange={setQuery2}
              onColumnsParsed={setColumns2}
            />
          </div>
        </div>
        
        <div className="mapping-section">
          <ColumnMapper
            columns1={columns1}
            columns2={columns2}
            onMappingsChange={setMappings}
            onPrimaryKeysChange={setPrimaryKeys}
          />
        </div>
        
        {error && (
          <div className="error-message">
            <span className="icon">⚠️</span>
            {error}
          </div>
        )}
        
        {comparisonResult && (
          <div className="results-section">
            <ResultView results={comparisonResult} />
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
