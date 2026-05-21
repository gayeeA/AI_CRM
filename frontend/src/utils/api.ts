import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API Services
export const interactionAPI = {
  // Get all interactions
  getAll: async (skip = 0, limit = 100) => {
    const response = await apiClient.get('/api/interactions', {
      params: { skip, limit },
    });
    return response.data;
  },

  // Get single interaction
  getById: async (id: number) => {
    const response = await apiClient.get(`/api/interactions/${id}`);
    return response.data;
  },

  // Create interaction
  create: async (data: any) => {
    const response = await apiClient.post('/api/interactions', data);
    return response.data;
  },

  // Update interaction
  update: async (id: number, data: any) => {
    const response = await apiClient.put(`/api/interactions/${id}`, data);
    return response.data;
  },

  // Delete interaction
  delete: async (id: number) => {
    const response = await apiClient.delete(`/api/interactions/${id}`);
    return response.data;
  },
};

export const chatAPI = {
  // Send AI message
  sendMessage: async (
    message: string,
    interactionId?: number,
    includeCurrentState = false,
    currentInteraction?: any
  ) => {
    const response = await apiClient.post('/api/chat', {
      message,
      interaction_id: interactionId,
      include_current_state: includeCurrentState,
      current_interaction: currentInteraction,
    });
    return response.data;
  },

  // Get conversation history
  getHistory: async (interactionId: number) => {
    const response = await apiClient.get(`/api/conversation-history/${interactionId}`);
    return response.data;
  },
};

export const toolAPI = {
  // List available tools
  listTools: async () => {
    const response = await apiClient.get('/api/tools/list');
    return response.data;
  },

  // Execute tool directly
  executeTool: async (toolName: string, interactionData: any, userInput: string) => {
    const response = await apiClient.post('/api/tools/execute', {
      tool_name: toolName,
      interaction_data: interactionData,
      user_input: userInput,
    });
    return response.data;
  },
};

export const configAPI = {
  // Get configuration
  getConfig: async () => {
    const response = await apiClient.get('/api/config');
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },
};

export default apiClient;
