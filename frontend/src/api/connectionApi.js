import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

export const testConnection = async (connectionData) => {
  try {
    const response = await axios.post(`${API_BASE}/test-connection`, connectionData, {
      withCredentials: true
    });
    return response.data;
  } catch (error) {
    return {
      status: 'error',
      message: error.response?.data?.error || error.message
    };
  }
};