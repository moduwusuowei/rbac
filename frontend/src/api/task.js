import apiClient from '@/utils/request'


// 任务管理 API 调用
export const getTasksApi = (params) => {
  return apiClient.get('/tasks/', { params })
}

export const createTaskApi = (data) => {
  return apiClient.post('/tasks/', data)
}

export const getTaskApi = (taskId) => {
  return apiClient.get(`/tasks/${taskId}`)
}

export const updateTaskApi = (taskId, data) => {
  return apiClient.put(`/tasks/${taskId}`, data)
}

export const deleteTaskApi = (taskId) => {
  return apiClient.delete(`/tasks/${taskId}`)
}


// 组管理 API 调用
export const getGroupsApi = () => {
  return apiClient.get('/groups/')
}

export const createGroupApi = (data) => {
  return apiClient.post('/groups/', data)
}

export const getGroupApi = (groupId) => {
  return apiClient.get(`/groups/${groupId}`)
}

export const updateGroupApi = (groupId, data) => {
  return apiClient.put(`/groups/${groupId}`, data)
}

export const addMemberApi = (groupId, data) => {
  return apiClient.post(`/groups/${groupId}/members`, data)
}

export const removeMemberApi = (groupId, userId) => {
  return apiClient.delete(`/groups/${groupId}/members/${userId}`)
}

export const transferLeadershipApi = (groupId, data) => {
  return apiClient.post(`/groups/${groupId}/transfer-leadership`, data)
}
