<template>
  <div class="dashboard">
    <h2 class="page-title">仪表盘</h2>
    
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="stat-card">
          <template #header>
            <div class="stat-header">
              <el-icon class="stat-icon user"><User /></el-icon>
              <span>用户总数</span>
            </div>
          </template>
          <div class="stat-value">{{ userCount }}</div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="stat-card">
          <template #header>
            <div class="stat-header">
              <el-icon class="stat-icon role"><Setting /></el-icon>
              <span>角色总数</span>
            </div>
          </template>
          <div class="stat-value">{{ roleCount }}</div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="stat-card">
          <template #header>
            <div class="stat-header">
              <el-icon class="stat-icon permission"><Lock /></el-icon>
              <span>权限总数</span>
            </div>
          </template>
          <div class="stat-value">{{ permissionCount }}</div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card class="info-card" style="margin-top: 20px;">
      <template #header>
        <span>欢迎使用 RBAC 系统</span>
      </template>
      <div class="welcome-content">
        <p v-if="userStore.isSuperuser">
          您好，超级管理员！您拥有系统的所有权限，可以进行用户管理、角色分配等操作。
        </p>
        <p v-else>
          您好，{{ userStore.username }}！您的角色是：{{ userStore.roles.join(', ') }}。
        </p>
        <div class="permissions-list">
          <h4>您拥有的权限：</h4>
          <el-tag 
            v-for="perm in userStore.permissions" 
            :key="perm"
            type="info"
            size="small"
            style="margin: 4px;"
          >
            {{ perm }}
          </el-tag>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { User, Setting, Lock } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import apiClient from '@/utils/request'

const userStore = useUserStore()
const userCount = ref(0)
const roleCount = ref(0)
const permissionCount = ref(0)

const fetchStats = async () => {
  try {
    const response = await apiClient.get('/auth/stats')
    userCount.value = response.data.user_count
    roleCount.value = response.data.role_count
    permissionCount.value = response.data.permission_count
  } catch (error) {
    console.error('获取统计数据失败', error)
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stat-card {
  border-radius: 4px;
}

.stat-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.stat-icon {
  font-size: 24px;
}

.stat-icon.user {
  color: #409EFF;
}

.stat-icon.role {
  color: #67C23A;
}

.stat-icon.permission {
  color: #E6A23C;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.welcome-content p {
  margin-bottom: 16px;
  line-height: 1.6;
}

.permissions-list {
  margin-top: 16px;
}

.permissions-list h4 {
  margin-bottom: 8px;
  color: #606266;
}
</style>