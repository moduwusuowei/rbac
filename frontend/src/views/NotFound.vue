<template>
  <div class="not-found-page">
    <el-empty description="404">
      <template #image>
        <el-icon :size="120" color="#909399"><WarningFilled /></el-icon>
      </template>
      <template #description>
        <h3>抱歉，您访问的页面不存在</h3>
        <p>请检查 URL 地址是否正确</p>
      </template>
      <el-button type="primary" @click="goHome">返回首页</el-button>
    </el-empty>
  </div>
</template>

<script setup>
import { WarningFilled } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.not-found-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #f5f7fa;
}

.not-found-page h3 {
  margin: 16px 0 8px;
  color: #303133;
}

.not-found-page p {
  color: #909399;
  margin-bottom: 20px;
}
</style>