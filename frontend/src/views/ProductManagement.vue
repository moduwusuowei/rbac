<template>
  <div class="product-management">
    <h2 class="page-title">商品管理</h2>
    
    <el-card>
      <template #header>
        <div class="page-toolbar">
          <span>商品列表</span>
          <el-button 
            type="primary" 
            @click="showCreateDialog"
            v-if="userStore.hasPermission('product:create')"
          >
            <el-icon><Plus /></el-icon>
            新增商品
          </el-button>
        </div>
      </template>
      
      <el-table :data="products" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="image_url" label="商品图片" width="120">
          <template #default="{ row }">
            <el-image 
              v-if="row.image_url"
              :src="row.image_url" 
              fit="cover" 
              style="width: 60px; height: 60px"
            />
            <span v-else>无图片</span>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="商品名称" width="150" />
        <el-table-column prop="code" label="商品编码" width="120" />
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
              v-if="userStore.hasPermission('product:update')"
            >
              编辑
            </el-button>
            <el-button 
              type="danger" 
              link
              size="small"
              @click="handleDelete(row)"
              v-if="userStore.hasPermission('product:delete')"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 新增/编辑商品对话框 -->
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
        <el-form-item label="商品名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入商品名称" />
        </el-form-item>
        <el-form-item label="商品编码" prop="code">
          <el-input 
            v-model="formData.code" 
            :disabled="isEdit"
            placeholder="请输入商品编码" 
          />
        </el-form-item>
        <el-form-item label="商品图片">
          <el-upload
            class="avatar-uploader"
            action="/api/v1/uploads/image"
            :headers="{ Authorization: `Bearer ${userStore.token}` }"
            :show-file-list="false"
            :on-success="handleImageUploadSuccess"
            :on-error="handleImageUploadError"
            :before-upload="beforeImageUpload"
          >
            <img v-if="formData.image_url" :src="formData.image_url" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <div class="upload-tip">支持 JPG、PNG、WEBP 格式，大小不超过 5MB，分辨率不低于 800×800 像素</div>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="formData.description" 
            type="textarea"
            :rows="3"
            placeholder="请输入商品描述" 
          />
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number 
            v-model="formData.price" 
            :min="0" 
            :step="0.01"
            placeholder="请输入商品价格"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="库存" prop="stock">
          <el-input-number 
            v-model="formData.stock" 
            :min="0" 
            placeholder="请输入商品库存"
            style="width: 100%"
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

const products = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增商品')
const isEdit = ref(false)
const submitLoading = ref(false)

const formRef = ref(null)
const formData = reactive({
  id: null,
  name: '',
  code: '',
  description: '',
  price: 0,
  stock: 0,
  is_active: true,
  image_url: '',
  image_path: '',
  image_id: ''
})

const formRules = {
  name: [
    { required: true, message: '请输入商品名称', trigger: 'blur' },
    { max: 100, message: '商品名称最长100个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入商品编码', trigger: 'blur' },
    { max: 50, message: '商品编码最长50个字符', trigger: 'blur' }
  ],
  price: [
    { required: true, message: '请输入商品价格', trigger: 'blur' },
    { type: 'number', min: 0, message: '价格不能为负数', trigger: 'blur' }
  ],
  stock: [
    { required: true, message: '请输入商品库存', trigger: 'blur' },
    { type: 'number', min: 0, message: '库存不能为负数', trigger: 'blur' }
  ]
}

const fetchProducts = async () => {
  loading.value = true
  try {
    const response = await apiClient.get('/products')
    products.value = response.data
  } catch (error) {
    ElMessage.error('获取商品列表失败')
  } finally {
    loading.value = false
  }
}

const showCreateDialog = () => {
  dialogTitle.value = '新增商品'
  isEdit.value = false
  formData.id = null
  formData.name = ''
  formData.code = ''
  formData.description = ''
  formData.price = 0
  formData.stock = 0
  formData.is_active = true
  formData.image_url = ''
  formData.image_path = ''
  formData.image_id = ''
  dialogVisible.value = true
}

const showEditDialog = (product) => {
  dialogTitle.value = '编辑商品'
  isEdit.value = true
  formData.id = product.id
  formData.name = product.name
  formData.code = product.code
  formData.description = product.description || ''
  formData.price = product.price
  formData.stock = product.stock
  formData.is_active = product.is_active
  formData.image_url = product.image_url || ''
  formData.image_path = product.image_path || ''
  formData.image_id = product.image_id || ''
  dialogVisible.value = true
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
}

const handleImageUploadSuccess = (response) => {
  formData.image_url = response.image_url
  formData.image_path = response.image_path
  formData.image_id = response.image_id
  ElMessage.success('图片上传成功')
}

const handleImageUploadError = (error) => {
  ElMessage.error('图片上传失败，请重试')
  console.error('图片上传失败:', error)
}

const beforeImageUpload = (file) => {
  const isJpgOrPngOrWebp = file.type === 'image/jpeg' || file.type === 'image/png' || file.type === 'image/webp'
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isJpgOrPngOrWebp) {
    ElMessage.error('只支持 JPG、PNG、WEBP 格式的图片')
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB')
  }

  return isJpgOrPngOrWebp && isLt5M
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
      await apiClient.put(`/products/${formData.id}`, formData)
      ElMessage.success('商品更新成功')
    } else {
      await apiClient.post('/products', formData)
      ElMessage.success('商品创建成功')
    }
    dialogVisible.value = false
    fetchProducts()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async (product) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除商品 "${product.name}" 吗？`,
      '删除确认',
      { type: 'warning' }
    )
    
    await apiClient.delete(`/products/${product.id}`)
    ElMessage.success('商品删除成功')
    fetchProducts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.product-management {
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

.avatar-uploader {
  display: flex;
  align-items: center;
}

.avatar-uploader .avatar {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #909399;
  width: 120px;
  height: 120px;
  line-height: 120px;
  text-align: center;
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.avatar-uploader-icon:hover {
  border-color: #409eff;
  color: #409eff;
}

.upload-tip {
  margin-top: 10px;
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}
</style>
