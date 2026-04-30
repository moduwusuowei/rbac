import apiClient from '@/utils/request'


export const loginApi = (data) => {
  return apiClient.post('/auth/login', data)
}


export const getUserInfoApi = () => {
  return apiClient.get('/auth/me/')
}


export const logoutApi = () => {
  return apiClient.post('/auth/logout/')
}


export const registerApi = (data) => {
  return apiClient.post('/auth/register/', data)
}


export const uploadAvatarApi = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return apiClient.post('/uploads/avatar/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}


export const changePasswordApi = (data) => {
  return apiClient.post('/auth/change-password/', data)
}