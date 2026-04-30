<template>
  <div class="permission-management">
    <h2 class="page-title">权限管理</h2>
    
    <el-card>
      <template #header>
        <div class="page-toolbar">
          <span>权限列表</span>
          <el-button 
            type="primary" 
            @click="showCreateDialog"
            v-if="userStore.hasPermission('permission:manage')"
          >
            <el-icon><Plus /></el-icon>
            新增权限
          </el-button>
        </div>
      </template>
      
      <el-table :data="permissions" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="权限名称" width="150" />
        <el-table-column prop="code" label="权限编码" width="150" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="操作" min-width="150" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              link
              size="small"
              @click="showEditDialog(row)"
              v-if="userStore.hasPermission('permission:manage')"
            >
              编辑
            </el-button>
            <el-button 
              type="danger" 
              link
              size="small"
              @click="handleDelete(row)"
              v-if="userStore.hasPermission('permission:manage')"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 新增/编辑权限对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="500px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="80px"
      >
        <el-form-item label="权限名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入权限名称" />
        </el-form-item>
        <el-form-item label="权限编码" prop="code">
          <el-input v-model="formData.code" placeholder="请输入权限编码" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="formData.description" placeholder="请输入权限描述" type="textarea" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import apiClient from '@/utils/request'

const userStore = useUserStore()

const permissions = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增权限')
const isEdit = ref(false)
const submitLoading = ref(false)

const formRef = ref(null)
const formData = reactive({
  id: null,
  name: '',
  code: '',
  description: ''
})

const formRules = {
  name: [
    { required: true, message: '请输入权限名称', trigger: 'blur' },
    { min: 2, max: 50, message: '权限名称长度在2-50个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入权限编码', trigger: 'blur' },
    { min: 2, max: 50, message: '权限编码长度在2-50个字符', trigger: 'blur' }
  ]
}

const fetchPermissions = async () => {
  loading.value = true
  try {
    const response = await apiClient.get('/permissions')
    permissions.value = response.data
  } catch (error) {
    ElMessage.error('获取权限列表失败')
  } finally {
    loading.value = false
  }
}

const showCreateDialog = () => {
  dialogTitle.value = '新增权限'
  isEdit.value = false
  dialogVisible.value = true
}

const showEditDialog = (permission) => {
  dialogTitle.value = '编辑权限'
  isEdit.value = true
  formData.id = permission.id
  formData.name = permission.name
  formData.code = permission.code
  formData.description = permission.description || ''
  dialogVisible.value = true
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
  Object.assign(formData, {
    id: null,
    name: '',
    code: '',
    description: ''
  })
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
  } catch (error) {
    return
  }
  
  submitLoading.value = true
  try {
    if (isEdit.value) {
      await apiClient.put(`/permissions/${formData.id}`, formData)
      ElMessage.success('权限更新成功')
    } else {
      await apiClient.post('/permissions', formData)
      ElMessage.success('权限创建成功')
    }
    dialogVisible.value = false
    fetchPermissions()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async (permission) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除权限 "${permission.name}" 吗？`,
      '删除确认',
      { type: 'warning' }
    )
    
    await apiClient.delete(`/permissions/${permission.id}`)
    ElMessage.success('权限删除成功')
    fetchPermissions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchPermissions()
})
</script>

<style scoped>
.permission-management {
  padding: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #303133;
}

.page-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
