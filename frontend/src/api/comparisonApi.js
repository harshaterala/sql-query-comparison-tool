import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

export const runComparison = async (query1, query2, mappings, primaryKeys) => {
  const response = await axios.post(`${API_BASE}/compare`, {
    query1,
    query2,
    mappings,
    primary_keys: primaryKeys
  }, {
    withCredentials: true
  });
  return response.data;
};
