import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getUserInfoApi } from '@/api/auth'


export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)
  const permissions = ref([])
  const roles = ref([])
  const avatarUrl = ref('')
  
  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  const isSuperuser = computed(() => userInfo.value?.is_superuser || false)
  const username = computed(() => userInfo.value?.username || '')
  
  // 方法
  function setToken(newToken) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }
  
  function setUserInfo(info) {
    userInfo.value = info
    roles.value = info?.roles || []
    permissions.value = info?.permissions || []
    if (info?.avatar_url) {
      avatarUrl.value = info.avatar_url
    }
  }
  
  function setAvatarUrl(url) {
    avatarUrl.value = url
    if (userInfo.value) {
      userInfo.value.avatar_url = url
    }
  }
  
  async function fetchUserInfo() {
    try {
      const response = await getUserInfoApi()
      setUserInfo(response.data)
      return response.data
    } catch (error) {
      logout()
      throw error
    }
  }
  
  function hasPermission(permissionCode) {
    // 超级管理员拥有所有权限
    if (isSuperuser.value) {
      return true
    }
    return permissions.value.includes(permissionCode)
  }
  
  function hasRole(roleCode) {
    return roles.value.includes(roleCode)
  }
  
  function logout() {
    token.value = ''
    userInfo.value = null
    permissions.value = []
    roles.value = []
    localStorage.removeItem('token')
    localStorage.removeItem('token_type')
  }
  
  // 初始化时获取用户信息
  if (token.value && !userInfo.value) {
    fetchUserInfo()
  }
  
  return {
    token,
    userInfo,
    permissions,
    roles,
    avatarUrl,
    isLoggedIn,
    isSuperuser,
    username,
    setToken,
    setUserInfo,
    setAvatarUrl,
    fetchUserInfo,
    hasPermission,
    hasRole,
    logout
  }
})