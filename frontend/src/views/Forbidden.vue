<template>
  <div class="forbidden-page">
    <el-empty description="403">
      <template #image>
        <el-icon :size="120" color="#909399"><Lock /></el-icon>
      </template>
      <template #description>
        <h3>抱歉，您没有权限访问此页面</h3>
        <p>请联系管理员获取相应权限</p>
      </template>
      <el-button type="primary" @click="goHome">返回首页</el-button>
    </el-empty>
  </div>
</template>

<script setup>
import { Lock } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.forbidden-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #f5f7fa;
}

.forbidden-page h3 {
  margin: 16px 0 8px;
  color: #303133;
}

.forbidden-page p {
  color: #909399;
  margin-bottom: 20px;
}
</style>