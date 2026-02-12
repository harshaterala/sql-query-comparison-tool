import React, { useState } from 'react';
import './styles/ResultView.css';

const ResultView = ({ results }) => {
  const [activeTab, setActiveTab] = useState('summary');
  const [expandedMismatches, setExpandedMismatches] = useState([]);

  if (!results) return null;

  const { summary, matches, only_in_query1, only_in_query2, mismatches } = results;

  const toggleMismatchDetails = (index) => {
    if (expandedMismatches.includes(index)) {
      setExpandedMismatches(expandedMismatches.filter(i => i !== index));
    } else {
      setExpandedMismatches([...expandedMismatches, index]);
    }
  };

  const exportResults = (format) => {
    let data;
    let filename;
    let content;
    
    if (format === 'json') {
      data = results;
      content = JSON.stringify(data, null, 2);
      filename = 'comparison_results.json';
    } else {
      // CSV export
      // Implementation for CSV export
      filename = 'comparison_results.csv';
    }
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
  };

  return (
    <div className="result-view">
      <div className="result-header">
        <div className="summary-stats">
          <div className="stat-card match">
            <span className="stat-value">{summary.matches}</span>
            <span className="stat-label">Matches</span>
          </div>
          <div className="stat-card mismatch">
            <span className="stat-value">{summary.mismatches}</span>
            <span className="stat-label">Mismatches</span>
          </div>
          <div className="stat-card only1">
            <span className="stat-value">{summary.only_in_query1}</span>
            <span className="stat-label">Only in Query 1</span>
          </div>
          <div className="stat-card only2">
            <span className="stat-value">{summary.only_in_query2}</span>
            <span className="stat-label">Only in Query 2</span>
          </div>
          <div className="stat-card time">
            <span className="stat-value">{summary.execution_time}s</span>
            <span className="stat-label">Execution Time</span>
          </div>
        </div>
        
        <div className="export-buttons">
          <button onClick={() => exportResults('json')} className="btn-export">
            📄 JSON
          </button>
          <button onClick={() => exportResults('csv')} className="btn-export">
            📊 CSV
          </button>
        </div>
      </div>
      
      <div className="result-tabs">
        <button 
          className={activeTab === 'summary' ? 'active' : ''}
          onClick={() => setActiveTab('summary')}
        >
          Summary
        </button>
        <button 
          className={activeTab === 'matches' ? 'active' : ''}
          onClick={() => setActiveTab('matches')}
        >
          Matches ({matches.length})
        </button>
        <button 
          className={activeTab === 'mismatches' ? 'active' : ''}
          onClick={() => setActiveTab('mismatches')}
        >
          Mismatches ({mismatches.length})
        </button>
        <button 
          className={activeTab === 'only1' ? 'active' : ''}
          onClick={() => setActiveTab('only1')}
        >
          Only Query 1 ({only_in_query1.length})
        </button>
        <button 
          className={activeTab === 'only2' ? 'active' : ''}
          onClick={() => setActiveTab('only2')}
        >
          Only Query 2 ({only_in_query2.length})
        </button>
      </div>
      
      <div className="result-content">
        {activeTab === 'summary' && (
          <div className="summary-view">
            <h4>Comparison Summary</h4>
            <table className="summary-table">
              <tbody>
                <tr>
                  <td>Query 1 rows:</td>
                  <td><strong>{summary.total_rows_query1}</strong></td>
                </tr>
                <tr>
                  <td>Query 2 rows:</td>
                  <td><strong>{summary.total_rows_query2}</strong></td>
                </tr>
                <tr>
                  <td>Matching rows:</td>
                  <td><strong className="match-text">{summary.matches}</strong></td>
                </tr>
                <tr>
                  <td>Rows with value mismatches:</td>
                  <td><strong className="mismatch-text">{summary.mismatches}</strong></td>
                </tr>
                <tr>
                  <td>Rows only in Query 1:</td>
                  <td><strong className="only1-text">{summary.only_in_query1}</strong></td>
                </tr>
                <tr>
                  <td>Rows only in Query 2:</td>
                  <td><strong className="only2-text">{summary.only_in_query2}</strong></td>
                </tr>
              </tbody>
            </table>
          </div>
        )}
        
        {activeTab === 'mismatches' && (
          <div className="mismatches-view">
            <h4>Value Mismatches</h4>
            {mismatches.length === 0 ? (
              <p className="no-data">No value mismatches found</p>
            ) : (
              <div className="mismatch-list">
                {mismatches.map((mismatch, idx) => (
                  <div key={idx} className="mismatch-item">
                    <div 
                      className="mismatch-header"
                      onClick={() => toggleMismatchDetails(idx)}
                    >
                      <span className="expand-icon">
                        {expandedMismatches.includes(idx) ? '▼' : '▶'}
                      </span>
                      <span className="key-info">
                        Key: {Object.entries(mismatch.key).map(([k, v]) => `${k}=${v}`).join(', ')}
                      </span>
                      <span className="diff-count">
                        {Object.keys(mismatch.differences).length} differences
                      </span>
                    </div>
                    
                    {expandedMismatches.includes(idx) && (
                      <div className="mismatch-details">
                        <table>
                          <thead>
                            <tr>
                              <th>Column</th>
                              <th>Query 1 Value</th>
                              <th>Query 2 Value</th>
                              <th>Status</th>
                            </tr>
                          </thead>
                          <tbody>
                            {Object.entries(mismatch.differences).map(([col, vals]) => (
                              <tr key={col}>
                                <td><strong>{col}</strong></td>
                                <td className="value-query1">{String(vals.query1)}</td>
                                <td className="value-query2">{String(vals.query2)}</td>
                                <td>
                                  <span className="badge mismatch">Mismatch</span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
        
        {(activeTab === 'matches' || activeTab === 'only1' || activeTab === 'only2') && (
          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  {activeTab === 'matches' && matches.length > 0 && 
                    Object.keys(matches[0]).map(key => (
                      <th key={key}>{key}</th>
                    ))
                  }
                  {activeTab === 'only1' && only_in_query1.length > 0 && 
                    Object.keys(only_in_query1[0]).map(key => (
                      <th key={key}>{key}</th>
                    ))
                  }
                  {activeTab === 'only2' && only_in_query2.length > 0 && 
                    Object.keys(only_in_query2[0]).map(key => (
                      <th key={key}>{key}</th>
                    ))
                  }
                </tr>
              </thead>
              <tbody>
                {activeTab === 'matches' && matches.map((row, idx) => (
                  <tr key={idx}>
                    {Object.values(row).map((val, i) => (
                      <td key={i}>{String(val)}</td>
                    ))}
                  </tr>
                ))}
                {activeTab === 'only1' && only_in_query1.map((row, idx) => (
                  <tr key={idx} className="row-only1">
                    {Object.values(row).map((val, i) => (
                      <td key={i}>{String(val)}</td>
                    ))}
                  </tr>
                ))}
                {activeTab === 'only2' && only_in_query2.map((row, idx) => (
                  <tr key={idx} className="row-only2">
                    {Object.values(row).map((val, i) => (
                      <td key={i}>{String(val)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            
            {((activeTab === 'matches' && matches.length === 0) ||
              (activeTab === 'only1' && only_in_query1.length === 0) ||
              (activeTab === 'only2' && only_in_query2.length === 0)) && (
              <p className="no-data">No rows to display</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultView;
