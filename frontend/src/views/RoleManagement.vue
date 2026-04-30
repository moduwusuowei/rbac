<template>
  <div class="role-management">
    <h2 class="page-title">角色管理</h2>
    
    <el-card>
      <template #header>
        <div class="page-toolbar">
          <span>角色列表</span>
          <el-button 
            type="primary" 
            @click="showCreateDialog"
            v-if="userStore.hasPermission('role:manage')"
          >
            <el-icon><Plus /></el-icon>
            新增角色
          </el-button>
        </div>
      </template>
      
      <el-table :data="roles" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="角色名称" width="150" />
        <el-table-column prop="code" label="角色编码" width="120" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="permissions" label="权限" min-width="300">
          <template #default="{ row }">
            <el-tag 
              v-for="perm in row.permissions" 
              :key="perm"
              size="small"
              style="margin-right: 4px; margin-bottom: 4px;"
            >
              {{ perm }}
            </el-tag>
            <span v-if="!row.permissions || row.permissions.length === 0" style="color: #909399;">
              无权限
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="150" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              link
              size="small"
              @click="showEditDialog(row)"
              :disabled="row.code === 'admin'"
            >
              编辑
            </el-button>
            <el-button 
              type="danger" 
              link
              size="small"
              @click="handleDelete(row)"
              :disabled="row.code === 'admin'"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 新增/编辑角色对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input 
            v-model="formData.code" 
            :disabled="isEdit"
            placeholder="请输入角色编码" 
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="formData.description" 
            type="textarea"
            :rows="3"
            placeholder="请输入角色描述" 
          />
        </el-form-item>
        <el-form-item label="权限" prop="permission_ids">
          <el-checkbox-group v-model="formData.permission_ids">
            <el-checkbox 
              v-for="perm in allPermissions" 
              :key="perm.id"
              :label="perm.id"
            >
              {{ perm.name }} ({{ perm.code }})
            </el-checkbox>
          </el-checkbox-group>
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
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import apiClient from '@/utils/request'

const userStore = useUserStore()

const roles = ref([])
const permissions = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增角色')
const isEdit = ref(false)
const submitLoading = ref(false)

const formRef = ref(null)
const formData = reactive({
  id: null,
  name: '',
  code: '',
  description: '',
  permission_ids: []
})

const formRules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { max: 50, message: '角色名称最长50个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入角色编码', trigger: 'blur' },
    { max: 50, message: '角色编码最长50个字符', trigger: 'blur' }
  ]
}

const allPermissions = computed(() => permissions.value)

const fetchRoles = async () => {
  loading.value = true
  try {
    const response = await apiClient.get('/roles')
    roles.value = response.data
  } catch (error) {
    ElMessage.error('获取角色列表失败')
  } finally {
    loading.value = false
  }
}

const fetchPermissions = async () => {
  try {
    const response = await apiClient.get('/permissions')
    permissions.value = response.data
  } catch (error) {
    console.error('获取权限列表失败', error)
  }
}

const showCreateDialog = () => {
  dialogTitle.value = '新增角色'
  isEdit.value = false
  dialogVisible.value = true
}

const showEditDialog = async (role) => {
  dialogTitle.value = '编辑角色'
  isEdit.value = true
  formData.id = role.id
  formData.name = role.name
  formData.code = role.code
  formData.description = role.description || ''
  
  // 先更新权限列表，确保包含所有最新的权限
  await fetchPermissions()
  
  // 转换权限为ID列表
  formData.permission_ids = role.permissions?.map(p => {
    if (typeof p === 'object') {
      return p.id
    } else {
      const perm = permissions.value.find(perm => perm.code === p)
      return perm ? perm.id : null
    }
  }).filter(id => id !== null) || []
  
  dialogVisible.value = true
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
  Object.assign(formData, {
    id: null,
    name: '',
    code: '',
    description: '',
    permission_ids: []
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
      await apiClient.put(`/roles/${formData.id}`, formData)
      ElMessage.success('角色更新成功')
    } else {
      await apiClient.post('/roles', formData)
      ElMessage.success('角色创建成功')
    }
    dialogVisible.value = false
    fetchRoles()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async (role) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除角色 "${role.name}" 吗？`,
      '删除确认',
      { type: 'warning' }
    )
    
    await apiClient.delete(`/roles/${role.id}`)
    ElMessage.success('角色删除成功')
    fetchRoles()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchRoles()
  fetchPermissions()
})
</script>

<style scoped>
.role-management {
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
