<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

onMounted(() => {
  // 初始化时检查登录状态
  const token = localStorage.getItem('token')
  if (token && !userStore.userInfo) {
    userStore.fetchUserInfo().catch(() => {
      // 获取用户信息失败，清除Token
      userStore.logout()
    })
  }
})
</script>

<style>
#app {
  margin: 0;
  padding: 0;
}
</style>