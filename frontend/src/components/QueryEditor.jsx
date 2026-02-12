import React, { useState, useEffect } from 'react';
import { parseColumns } from '../api/queryApi';
import './styles/QueryEditor.css';

const QueryEditor = ({ label, placeholder, onQueryChange, onColumnsParsed }) => {
  const [query, setQuery] = useState('');
  const [columns, setColumns] = useState([]);
  const [parsing, setParsing] = useState(false);

  useEffect(() => {
    const timer = setTimeout(async () => {
      if (query.trim()) {
        setParsing(true);
        try {
          const result = await parseColumns(query);
          setColumns(result.columns || []);
          onColumnsParsed(result.columns || []);
        } catch (error) {
          console.error('Failed to parse columns:', error);
        }
        setParsing(false);
      }
    }, 1000);
    
    return () => clearTimeout(timer);
  }, [query, onColumnsParsed]);

  const handleChange = (e) => {
    setQuery(e.target.value);
    onQueryChange(e.target.value);
  };

  return (
    <div className="query-editor">
      <div className="query-header">
        <span className="query-label">{label}</span>
        {parsing && <span className="parsing-indicator">Parsing columns...</span>}
        {columns.length > 0 && (
          <span className="column-badge">
            {columns.length} column{columns.length !== 1 ? 's' : ''} detected
          </span>
        )}
      </div>
      
      <textarea
        value={query}
        onChange={handleChange}
        placeholder={placeholder}
        className="query-textarea"
        spellCheck="false"
      />
      
      {columns.length > 0 && (
        <div className="column-preview">
          <small>Detected columns:</small>
          <div className="column-tags">
            {columns.map((col, idx) => (
              <span key={idx} className="column-tag">{col}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default QueryEditor;
