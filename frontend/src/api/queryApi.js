import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

export const executeQuery = async (query) => {
  const response = await axios.post(`${API_BASE}/execute-query`, { query }, {
    withCredentials: true
  });
  return response.data;
};

export const parseColumns = async (query) => {
  const response = await axios.post(`${API_BASE}/parse-columns`, { query }, {
    withCredentials: true
  });
  return response.data;
};
