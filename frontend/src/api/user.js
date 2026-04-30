import apiClient from '@/utils/request'

// 用户管理 API 调用
export const getUsersApi = () => {
  return apiClient.get('/users')
}
