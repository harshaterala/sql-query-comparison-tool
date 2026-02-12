import React, { useState, useEffect } from 'react';
import './styles/ColumnMapper.css';

const ColumnMapper = ({ columns1, columns2, onMappingsChange, onPrimaryKeysChange }) => {
  const [mappings, setMappings] = useState([]);
  const [primaryKeys, setPrimaryKeys] = useState([]);

  const addMapping = () => {
    if (columns1.length > 0 && columns2.length > 0) {
      setMappings([
        ...mappings,
        {
          id: Date.now(),
          left: columns1[0],
          right: columns2[0]
        }
      ]);
    }
  };

  const removeMapping = (id) => {
    setMappings(mappings.filter(m => m.id !== id));
    
    // Remove from primary keys if this mapping was a primary key
    const mapping = mappings.find(m => m.id === id);
    if (mapping) {
      setPrimaryKeys(primaryKeys.filter(pk => 
        !(pk.left === mapping.left && pk.right === mapping.right)
      ));
    }
  };

  const updateMapping = (id, field, value) => {
    const updatedMappings = mappings.map(m => {
      if (m.id === id) {
        return { ...m, [field]: value };
      }
      return m;
    });
    setMappings(updatedMappings);
  };

  const togglePrimaryKey = (mappingId) => {
    const mapping = mappings.find(m => m.id === mappingId);
    if (!mapping) return;
    
    const exists = primaryKeys.some(pk => 
      pk.left === mapping.left && pk.right === mapping.right
    );
    
    if (exists) {
      setPrimaryKeys(primaryKeys.filter(pk => 
        !(pk.left === mapping.left && pk.right === mapping.right)
      ));
    } else {
      setPrimaryKeys([...primaryKeys, { left: mapping.left, right: mapping.right }]);
    }
  };

  useEffect(() => {
    onMappingsChange(mappings);
  }, [mappings, onMappingsChange]);

  useEffect(() => {
    onPrimaryKeysChange(primaryKeys);
  }, [primaryKeys, onPrimaryKeysChange]);

  if (columns1.length === 0 || columns2.length === 0) {
    return (
      <div className="column-mapper-placeholder">
        <span className="icon">🔗</span>
        <p>Enter both queries to enable column mapping</p>
      </div>
    );
  }

  return (
    <div className="column-mapper">
      <div className="mapper-header">
        <h4>
          <span className="icon">🔗</span>
          Column Mapping
        </h4>
        <button onClick={addMapping} className="btn-add">
          + Add Mapping
        </button>
      </div>
      
      <div className="mapping-instructions">
        <small>Map columns between queries and select primary key(s) for row matching</small>
      </div>
      
      <div className="mappings-list">
        {mappings.map((mapping) => (
          <div key={mapping.id} className="mapping-row">
            <select
              value={mapping.left}
              onChange={(e) => updateMapping(mapping.id, 'left', e.target.value)}
              className="column-select"
            >
              {columns1.map(col => (
                <option key={col} value={col}>{col}</option>
              ))}
            </select>
            
            <span className="mapping-arrow">→</span>
            
            <select
              value={mapping.right}
              onChange={(e) => updateMapping(mapping.id, 'right', e.target.value)}
              className="column-select"
            >
              {columns2.map(col => (
                <option key={col} value={col}>{col}</option>
              ))}
            </select>
            
            <label className="primary-key-checkbox">
              <input
                type="checkbox"
                checked={primaryKeys.some(pk => 
                  pk.left === mapping.left && pk.right === mapping.right
                )}
                onChange={() => togglePrimaryKey(mapping.id)}
              />
              Primary Key
            </label>
            
            <button 
              onClick={() => removeMapping(mapping.id)}
              className="btn-remove"
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ColumnMapper;
