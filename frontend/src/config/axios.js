// frontend/src/config/axios.js
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8001',
  withCredentials: true,
  timeout: 30000,
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Log request for debugging - FIXED syntax error
    console.log(`🚀 ${config.method?.toUpperCase()} ${config.url}`, {
      headers: config.headers,
      data: config.data
    });
    
    return config;
  },
  (error) => {
    console.error('❌ Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => {
    console.log(`✅ ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ Response error:', {
      url: error.config?.url,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    });
    
    if (error.response?.status === 401) {
      console.log('🛑 401 Unauthorized - Removing token');
      localStorage.removeItem('auth_token');
      delete api.defaults.headers.common['Authorization'];
      window.location.href = '/login';
    }
    
    if (error.response?.status === 404) {
      console.log('🔍 404 Not Found - Check endpoint URL');
    }
    
    // Handle network errors
    if (!error.response) {
      console.error('🌐 Network error - Backend might be down');
    }
    
    return Promise.reject(error);
  }
);

export default api;