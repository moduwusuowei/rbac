<template>
  <el-container class="app-layout">
    <el-aside :width="isCollapsed ? '64px' : '200px'" class="sidebar">
      <div class="logo">
        <img src="@/assets/logo.svg" alt="Logo" />
        <span v-show="!isCollapsed">RBAC 系统</span>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        
        <el-menu-item 
          v-if="userStore.hasPermission('user:read')" 
          index="/users"
        >
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        
        <el-menu-item 
          v-if="userStore.hasPermission('role:read')" 
          index="/roles"
        >
          <el-icon><Setting /></el-icon>
          <span>角色管理</span>
        </el-menu-item>
        
        <el-menu-item 
          v-if="userStore.hasPermission('permission:read')" 
          index="/permissions"
        >
          <el-icon><Key /></el-icon>
          <span>权限管理</span>
        </el-menu-item>
        
        <el-menu-item 
          v-if="userStore.hasPermission('product:read')" 
          index="/products"
        >
          <el-icon><Goods /></el-icon>
          <span>商品管理</span>
        </el-menu-item>
        
        <el-menu-item 
          v-if="userStore.hasPermission('mobile:read')" 
          index="/phones"
        >
          <el-icon><Cellphone /></el-icon>
          <span>手机管理</span>
        </el-menu-item>
        
        <el-menu-item 
          index="/customer-products"
        >
          <el-icon><View /></el-icon>
          <span>客户浏览预览</span>
        </el-menu-item>
        
        <el-menu-item 
          index="/tasks"
        >
          <el-icon><Timer /></el-icon>
          <span>任务管理</span>
        </el-menu-item>
        
        <el-menu-item 
          index="/groups"
        >
          <el-icon><Operation /></el-icon>
          <span>组管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon 
            class="collapse-btn"
            @click="isCollapsed = !isCollapsed"
          >
            <Fold v-if="!isCollapsed" />
            <Expand v-else />
          </el-icon>
        </div>
        
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar
                :size="36"
                :src="userStore.avatarUrl || defaultAvatar"
                class="user-avatar"
              >
                {{ userStore.username?.charAt(0).toUpperCase() }}
              </el-avatar>
              <span class="username">{{ userStore.username }}</span>
              <el-icon class="arrow-icon"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { HomeFilled, User, Setting, Key, Goods, Cellphone, Fold, Expand, ArrowDown, View, Timer, Operation } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

const isCollapsed = ref(false)

const activeMenu = computed(() => route.path)

const handleCommand = async (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        userStore.logout()
        router.push('/login')
      } catch {
        // 用户取消
      }
      break
  }
}
</script>

<style scoped>
.app-layout {
  height: 100vh;
}

.sidebar {
  background: #304156;
  transition: width 0.3s;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
}

.logo img {
  width: 32px;
  height: 32px;
  margin-right: 8px;
}

.sidebar-menu {
  border-right: none;
  background: transparent;
  --el-menu-text-color: #f5f7fa;
  --el-menu-active-text-color: #409eff;
  --el-menu-hover-text-color: #409eff;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 200px;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #303133;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.user-avatar {
  margin-right: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.username {
  font-size: 14px;
  margin-right: 6px;
}

.arrow-icon {
  font-size: 12px;
  color: #909399;
}

.main-content {
  background: #f5f7fa;
  padding: 20px;
}
</style>
