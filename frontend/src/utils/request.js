import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'


const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})


// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 从本地存储获取Token
    const token = localStorage.getItem('token')
    console.log('请求拦截器 - 从localStorage获取token:', token ? '存在' : '不存在')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log('请求拦截器 - 添加Authorization头:', config.headers.Authorization)
    } else {
      console.log('请求拦截器 - 没有token，不添加Authorization头')
    }
    console.log('请求拦截器 - 完整配置:', config)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)


// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    const { response } = error
    
    if (response) {
      console.error('API错误:', response.status, response.data)
      switch (response.status) {
        case 401:
          // Token过期或无效，跳转登录页
          console.warn('Token验证失败，清除本地存储并跳转登录页')
          localStorage.removeItem('token')
          localStorage.removeItem('token_type')
          router.push('/login?redirect=' + router.currentRoute.value.fullPath)
          ElMessage.error('登录已过期，请重新登录')
          break
        case 403:
          // 无权限访问
          ElMessage.error('没有权限访问该资源')
          router.push('/403')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误，请稍后重试')
          break
        default:
          ElMessage.error(response.data?.detail || '请求失败')
      }
    } else {
      ElMessage.error('网络连接异常，请检查网络')
    }
    
    return Promise.reject(error)
  }
)


export default apiClient