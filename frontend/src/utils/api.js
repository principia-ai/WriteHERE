import axios from 'axios';

// Base URL for API requests - adjust as needed for production/development
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : 'http://localhost:5002/api';

// Create an axios instance with CORS headers
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: 30000 // 30 seconds timeout
});

/**
 * Test the API connection
 * @returns {Promise} - Promise that resolves with ping result
 */
export const pingAPI = async () => {
  try {
    const response = await apiClient.get('/ping');
    return response.data;
  } catch (error) {
    console.error('API ping failed:', error);
    throw error;
  }
};

/**
 * Generates a story using the heterogeneous recursive planning engine
 * @param {Object} params - Generation parameters
 * @param {string} params.prompt - The story prompt
 * @param {string} params.model - The model to use (e.g., 'gpt-4o', 'claude-3-5-sonnet-20241022')
 * @param {string} [params.language='english'] - The language for prompts ('english' or 'chinese')
 * @param {Object} params.apiKeys - API keys for different services
 * @param {string} params.apiKeys.openai - OpenAI API key
 * @param {string} params.apiKeys.claude - Claude API key
 * @returns {Promise} - Promise that resolves with generation result
 */
export const generateStory = async (params) => {
  try {
    console.log('Sending story generation request to:', `${API_BASE_URL}/generate-story`);
    const requestParams = {
      ...params,
      language: params.language || 'english'
    };
    const response = await apiClient.post('/generate-story', requestParams);
    return response.data;
  } catch (error) {
    console.error('Error generating story:', error);
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('Error response data:', error.response.data);
      console.error('Error response status:', error.response.status);
      throw new Error(`Server error: ${error.response.data.error || error.response.statusText}`);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('Error request:', error.request);
      throw new Error('No response from server. Please make sure the backend is running.');
    } else {
      // Something happened in setting up the request that triggered an Error
      throw error;
    }
  }
};

/**
 * Generates a report using the heterogeneous recursive planning engine
 * @param {Object} params - Generation parameters
 * @param {string} params.prompt - The report prompt
 * @param {string} params.model - The model to use
 * @param {boolean} params.enableSearch - Whether to enable search
 * @param {string} params.searchEngine - Search engine to use ('google' or 'bing')
 * @param {string} [params.language='english'] - The language for output ('english' or 'chinese')
 * @param {Object} params.apiKeys - API keys for different services
 * @param {string} params.apiKeys.openai - OpenAI API key
 * @param {string} params.apiKeys.claude - Claude API key
 * @param {string} params.apiKeys.serpapi - SerpAPI key for search
 * @returns {Promise} - Promise that resolves with generation result
 */
export const generateReport = async (params) => {
  try {
    console.log('Sending report generation request to:', `${API_BASE_URL}/generate-report`);
    const requestParams = {
      ...params,
      language: params.language || 'english'
    };
    const response = await apiClient.post('/generate-report', requestParams);
    return response.data;
  } catch (error) {
    console.error('Error generating report:', error);
    if (error.response) {
      console.error('Error response data:', error.response.data);
      console.error('Error response status:', error.response.status);
      throw new Error(`Server error: ${error.response.data.error || error.response.statusText}`);
    } else if (error.request) {
      console.error('Error request:', error.request);
      throw new Error('No response from server. Please make sure the backend is running.');
    } else {
      throw error;
    }
  }
};

/**
 * Fetches the status of a generation task
 * @param {string} taskId - ID of the generation task
 * @returns {Promise} - Promise that resolves with task status
 */
export const getGenerationStatus = async (taskId) => {
  try {
    const response = await apiClient.get(`/status/${taskId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching generation status:', error);
    if (error.response && error.response.status === 404) {
      throw new Error('Task not found. It may have been removed or expired.');
    }
    throw error;
  }
};

/**
 * Fetches the result of a completed generation task
 * @param {string} taskId - ID of the generation task
 * @returns {Promise} - Promise that resolves with task result
 */
export const getGenerationResult = async (taskId) => {
  try {
    const response = await apiClient.get(`/result/${taskId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching generation result:', error);
    if (error.response && error.response.status === 404) {
      throw new Error('Result not found. The task may have been removed or expired.');
    }
    throw error;
  }
};

/**
 * Fetches the task graph data for a completed generation task
 * @param {string} taskId - ID of the generation task
 * @returns {Promise} - Promise that resolves with task graph data
 */
export const getTaskGraph = async (taskId) => {
  try {
    const response = await apiClient.get(`/task-graph/${taskId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching task graph data:', error);
    if (error.response && error.response.status === 404) {
      throw new Error('Task graph not found. It may not be available for this task.');
    }
    throw error;
  }
};

/**
 * Fetches the history of previously generated tasks
 * @returns {Promise} - Promise that resolves with history data
 */
export const getHistory = async () => {
  try {
    const response = await apiClient.get('/history');
    return response.data;
  } catch (error) {
    console.error('Error fetching generation history:', error);
    throw error;
  }
};

/**
 * Reloads all tasks from the filesystem
 * @returns {Promise} - Promise that resolves with reload status
 */
export const reloadTasks = async () => {
  try {
    const response = await apiClient.post('/reload');
    return response.data;
  } catch (error) {
    console.error('Error reloading tasks:', error);
    throw error;
  }
};

/**
 * Deletes a task and its associated files
 * @param {string} taskId - ID of the task to delete
 * @returns {Promise} - Promise that resolves with delete status
 */
export const deleteTask = async (taskId) => {
  try {
    const response = await apiClient.delete(`/delete-task/${taskId}`);
    return response.data;
  } catch (error) {
    console.error(`Error deleting task ${taskId}:`, error);
    if (error.response && error.response.status === 404) {
      throw new Error('Task not found. It may have already been deleted.');
    }
    throw error;
  }
};