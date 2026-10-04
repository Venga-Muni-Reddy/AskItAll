/// <reference types="vite/client" />
import axios from 'axios';

const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('askitall_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const api = {
  // Auth
  register: (data: any) => apiClient.post('/auth/register', data),
  login: (data: any) => apiClient.post('/auth/login', data),
  getMe: () => apiClient.get('/auth/me'),

  // Organizations & Workspaces
  getOrganizations: () => apiClient.get('/organizations'),
  createOrganization: (data: any) => apiClient.post('/organizations', data),
  getWorkspaces: (orgId: string) => apiClient.get(`/organizations/${orgId}/workspaces`),
  createWorkspace: (orgId: string, data: any) => apiClient.post(`/organizations/${orgId}/workspaces`, data),

  // Knowledge Bases
  getKnowledgeBases: (workspaceId: string) => apiClient.get(`/workspaces/${workspaceId}/knowledge-bases`),
  createKnowledgeBase: (workspaceId: string, data: any) => apiClient.post(`/workspaces/${workspaceId}/knowledge-bases`, data),

  // Documents
  getDocuments: (workspaceId: string) => apiClient.get(`/workspaces/${workspaceId}/documents`),
  uploadDocument: (workspaceId: string, formData: FormData) =>
    apiClient.post(`/workspaces/${workspaceId}/documents/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  getDocumentStatus: (docId: string) => apiClient.get(`/documents/${docId}/processing-status`),

  // Search & Chat
  search: (data: any) => apiClient.post('/search', data),
  chat: (data: any) => apiClient.post('/chat', data),

  // Conversations
  getConversations: (workspaceId: string) => apiClient.get(`/conversations?workspace_id=${workspaceId}`),
  createConversation: (data: any) => apiClient.post('/conversations', data),
  getMessages: (convId: string) => apiClient.get(`/conversations/${convId}/messages`),
};
