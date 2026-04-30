<template>
  <div class="phone-management">
    <h2 class="page-title">手机管理</h2>
    
    <el-card>
      <template #header>
        <div class="page-toolbar">
          <span>手机列表</span>
          <el-button 
            type="primary" 
            @click="showCreateDialog"
            v-if="userStore.hasPermission('mobile:create')"
          >
            <el-icon><Plus /></el-icon>
            新增手机
          </el-button>
        </div>
      </template>
      
      <el-table :data="phones" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="手机名称" width="150" />
        <el-table-column prop="brand" label="品牌" width="120" />
        <el-table-column prop="model" label="型号" width="120" />
        <el-table-column prop="price" label="价格" width="100">
          <template #default="{ row }">
            ¥{{ row.price.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="100" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="150" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              link
              size="small"
              @click="showEditDialog(row)"
              v-if="userStore.hasPermission('mobile:update')"
            >
              编辑
            </el-button>
            <el-button 
              type="danger" 
              link
              size="small"
              @click="handleDelete(row)"
              v-if="userStore.hasPermission('mobile:delete')"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 新增/编辑手机对话框 -->
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
        <el-form-item label="手机名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入手机名称" />
        </el-form-item>
        <el-form-item label="品牌" prop="brand">
          <el-input v-model="formData.brand" placeholder="请输入品牌" />
        </el-form-item>
        <el-form-item label="型号" prop="model">
          <el-input v-model="formData.model" placeholder="请输入型号" />
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number 
            v-model="formData.price" 
            :min="0" 
            :step="0.01"
            placeholder="请输入价格"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="库存" prop="stock">
          <el-input-number 
            v-model="formData.stock" 
            :min="0" 
            placeholder="请输入库存"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="formData.description" 
            type="textarea"
            :rows="3"
            placeholder="请输入描述" 
          />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="formData.is_active" />
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

const phones = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增手机')
const isEdit = ref(false)
const submitLoading = ref(false)

const formRef = ref(null)
const formData = reactive({
  id: null,
  name: '',
  brand: '',
  model: '',
  price: 0,
  stock: 0,
  description: '',
  is_active: true
})

const formRules = {
  name: [
    { required: true, message: '请输入手机名称', trigger: 'blur' },
    { max: 100, message: '手机名称最长100个字符', trigger: 'blur' }
  ],
  brand: [
    { required: true, message: '请输入品牌', trigger: 'blur' },
    { max: 50, message: '品牌最长50个字符', trigger: 'blur' }
  ],
  model: [
    { required: true, message: '请输入型号', trigger: 'blur' },
    { max: 50, message: '型号最长50个字符', trigger: 'blur' }
  ],
  price: [
    { required: true, message: '请输入价格', trigger: 'blur' },
    { type: 'number', min: 0, message: '价格不能为负数', trigger: 'blur' }
  ],
  stock: [
    { required: true, message: '请输入库存', trigger: 'blur' },
    { type: 'number', min: 0, message: '库存不能为负数', trigger: 'blur' }
  ]
}

const fetchPhones = async () => {
  loading.value = true
  try {
    const response = await apiClient.get('/phones')
    phones.value = response.data
  } catch (error) {
    ElMessage.error('获取手机列表失败')
  } finally {
    loading.value = false
  }
}

const showCreateDialog = () => {
  dialogTitle.value = '新增手机'
  isEdit.value = false
  formData.id = null
  formData.name = ''
  formData.brand = ''
  formData.model = ''
  formData.price = 0
  formData.stock = 0
  formData.description = ''
  formData.is_active = true
  dialogVisible.value = true
}

const showEditDialog = (phone) => {
  dialogTitle.value = '编辑手机'
  isEdit.value = true
  formData.id = phone.id
  formData.name = phone.name
  formData.brand = phone.brand
  formData.model = phone.model
  formData.price = phone.price
  formData.stock = phone.stock
  formData.description = phone.description || ''
  formData.is_active = phone.is_active
  dialogVisible.value = true
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
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
      await apiClient.put(`/phones/${formData.id}`, formData)
      ElMessage.success('手机更新成功')
    } else {
      await apiClient.post('/phones', formData)
      ElMessage.success('手机创建成功')
    }
    dialogVisible.value = false
    fetchPhones()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async (phone) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除手机 "${phone.name}" 吗？`,
      '删除确认',
      { type: 'warning' }
    )
    
    await apiClient.delete(`/phones/${phone.id}`)
    ElMessage.success('手机删除成功')
    fetchPhones()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchPhones()
})
</script>

<style scoped>
.phone-management {
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
