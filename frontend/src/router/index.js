import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'


const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue')
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('@/views/UserManagement.vue'),
        meta: { permission: 'user:read' }
      },
      {
        path: 'roles',
        name: 'RoleManagement',
        component: () => import('@/views/RoleManagement.vue'),
        meta: { permission: 'role:read' }
      },
      {
          path: 'permissions',
          name: 'PermissionManagement',
          component: () => import('@/views/PermissionManagement.vue'),
          meta: { permission: 'permission:read' }
        },
        {
          path: 'products',
          name: 'ProductManagement',
          component: () => import('@/views/ProductManagement.vue'),
          meta: { permission: 'product:read' }
        },
        {
          path: 'phones',
          name: 'PhoneManagement',
          component: () => import('@/views/PhoneManagement.vue'),
          meta: { permission: 'mobile:read' }
        },
        {
          path: 'profile',
          name: 'Profile',
          component: () => import('@/views/Profile.vue')
        },
        {
          path: 'tasks',
          name: 'TaskManagement',
          component: () => import('@/views/TaskManagement.vue')
        },
        {
          path: 'groups',
          name: 'GroupManagement',
          component: () => import('@/views/GroupManagement.vue')
        }
    ]
  },
  {
    path: '/customer-products',
    name: 'CustomerProducts',
    component: () => import('@/views/CustomerProducts.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/Forbidden.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]


const router = createRouter({
  history: createWebHistory(),
  routes
})


// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  const token = localStorage.getItem('token')
  
  // 需要登录
  if (to.meta.requiresAuth) {
    if (!token) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
    
    // 确保用户信息已加载
    if (!userStore.userInfo) {
      try {
        await userStore.fetchUserInfo()
      } catch (error) {
        next({ name: 'Login', query: { redirect: to.fullPath } })
        return
      }
    }
    
    // 检查权限
    if (to.meta.permission) {
      const hasPermission = userStore.hasPermission(to.meta.permission)
      if (!hasPermission) {
        next({ name: 'Forbidden' })
        return
      }
    }
  }
  
  // 已登录访问登录页或注册页，跳转首页
  if ((to.name === 'Login' || to.name === 'Register') && token) {
    next({ name: 'Dashboard' })
    return
  }
  
  next()
})


export default router
