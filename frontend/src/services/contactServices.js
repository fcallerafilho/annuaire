import api from './api';
import { fetchUsers } from './userService';

export const contactService = {
  getContacts: () => fetchUsers(),
  getContact: (id) => api.get(`/users/${id}`),
  createContact: (data) => api.post('/users', data),
  updateContact: (id, data) => api.put(`/users/${id}/profile`, data),
  deleteContact: (id) => api.delete(`/users/${id}`)
};