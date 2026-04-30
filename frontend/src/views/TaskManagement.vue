<template>
  <div class="task-management">
    <el-card class="task-card">
      <template #header>
        <div class="card-header">
          <h2>任务管理</h2>
          <el-button type="primary" @click="handleCreateTask">
            <el-icon><Plus /></el-icon> 创建任务
          </el-button>
        </div>
      </template>

      <div class="task-filter">
        <el-radio-group v-model="taskType" @change="loadTasks">
          <el-radio label="all">全部任务</el-radio>
          <el-radio label="personal">个人创建</el-radio>
          <el-radio label="group">组内任务</el-radio>
        </el-radio-group>

        <el-select v-model="selectedGroupId" placeholder="选择组" v-if="taskType === 'group'" @change="loadTasks">
          <el-option
            v-for="group in groups"
            :key="group.id"
            :label="group.name"
            :value="group.id"
          />
        </el-select>
      </div>

      <el-table :data="tasks" style="width: 100%" v-loading="loading">
        <el-table-column prop="title" label="任务标题" min-width="200" />
        <el-table-column prop="description" label="任务描述" min-width="250">
          <template #default="scope">
            <span :title="scope.row.description">{{ scope.row.description || '无' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="scope">
            <el-tag :type="getPriorityType(scope.row.priority)">
              {{ getPriorityText(scope.row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="creator_name" label="创建人" width="120" />
        <el-table-column prop="group_name" label="所属组" width="120" />
        <el-table-column prop="due_date" label="截止日期" width="150">
          <template #default="scope">
            {{ scope.row.due_date ? formatDate(scope.row.due_date) : '无' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220">
          <template #default="scope">
            <div style="display: flex; gap: 8px;">
              <el-button
                type="primary"
                size="small"
                @click="handleEditTask(scope.row)"
                v-if="scope.row.permissions.can_edit"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="handleDeleteTask(scope.row.id)"
                v-if="scope.row.permissions.can_delete"
              >
                删除
              </el-button>
              <el-button
                type="info"
                size="small"
                @click="handleViewTask(scope.row)"
              >
                查看
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑任务对话框 -->
    <el-dialog
      v-model="showTaskDialog"
      :title="isEditing ? '编辑任务' : '创建任务'"
      width="600px"
    >
      <el-form
        ref="taskFormRef"
        :model="taskForm"
        :rules="taskRules"
        label-width="100px"
      >
        <el-form-item label="任务标题" prop="title">
          <el-input v-model="taskForm.title" placeholder="请输入任务标题" />
        </el-form-item>

        <el-form-item label="任务描述" prop="description">
          <el-input
            v-model="taskForm.description"
            type="textarea"
            rows="3"
            placeholder="请输入任务描述"
          />
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-select v-model="taskForm.status" placeholder="请选择状态">
            <el-option label="待处理" value="pending" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>

        <el-form-item label="优先级" prop="priority">
          <el-select v-model="taskForm.priority" placeholder="请选择优先级">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
          </el-select>
        </el-form-item>

        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker
            v-model="taskForm.start_date"
            type="datetime"
            placeholder="选择开始日期"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="截止日期" prop="due_date">
          <el-date-picker
            v-model="taskForm.due_date"
            type="datetime"
            placeholder="选择截止日期"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="所属组" prop="group_id">
          <el-select v-model="taskForm.group_id" placeholder="选择所属组" @change="handleGroupChange">
            <el-option label="个人任务" value="" />
            <el-option
              v-for="group in groups"
              :key="group.id"
              :label="group.name"
              :value="group.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="指派给" prop="assigned_to">
          <el-select v-model="taskForm.assigned_to" placeholder="选择指派用户">
            <el-option label="未指派" value="" />
            <el-option
              v-for="user in groupMembers"
              :key="user.id"
              :label="user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="handleCancelTask">取 消</el-button>
        <el-button type="primary" @click="handleSaveTask" :loading="saving">
          {{ saving ? '保存中...' : '确 定' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看任务对话框 -->
    <el-dialog
      v-model="showViewDialog"
      title="任务详情"
      width="600px"
    >
      <div class="task-detail">
        <div class="detail-item">
          <span class="label">任务标题：</span>
          <span class="value">{{ viewTask.title }}</span>
        </div>
        <div class="detail-item">
          <span class="label">任务描述：</span>
          <span class="value">{{ viewTask.description || '无' }}</span>
        </div>
        <div class="detail-item">
          <span class="label">状态：</span>
          <el-tag :type="getStatusType(viewTask.status)">
            {{ getStatusText(viewTask.status) }}
          </el-tag>
        </div>
        <div class="detail-item">
          <span class="label">优先级：</span>
          <el-tag :type="getPriorityType(viewTask.priority)">
            {{ getPriorityText(viewTask.priority) }}
          </el-tag>
        </div>
        <div class="detail-item">
          <span class="label">创建人：</span>
          <span class="value">{{ viewTask.creator_name }}</span>
        </div>
        <div class="detail-item">
          <span class="label">所属组：</span>
          <span class="value">{{ viewTask.group_name || '个人任务' }}</span>
        </div>
        <div class="detail-item">
          <span class="label">指派给：</span>
          <span class="value">{{ viewTask.assignee_name || '未指派' }}</span>
        </div>
        <div class="detail-item">
          <span class="label">截止日期：</span>
          <span class="value">{{ viewTask.due_date ? formatDate(viewTask.due_date) : '无' }}</span>
        </div>
        <div class="detail-item">
          <span class="label">创建时间：</span>
          <span class="value">{{ formatDate(viewTask.created_at) }}</span>
        </div>
        <div class="detail-item">
          <span class="label">更新时间：</span>
          <span class="value">{{ formatDate(viewTask.updated_at) }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getTasksApi, createTaskApi, getTaskApi, updateTaskApi, deleteTaskApi, getGroupsApi, getGroupApi } from '@/api/task'

const tasks = ref([])
const groups = ref([])
const users = ref([])
const groupMembers = ref([])
const loading = ref(false)
const saving = ref(false)
const taskType = ref('all')
const selectedGroupId = ref('')

const showCreateTaskDialog = ref(false)
const showTaskDialog = ref(false)
const showViewDialog = ref(false)
const taskFormRef = ref(null)
const isEditing = ref(false)
const currentTaskId = ref(null)

const taskForm = reactive({
  title: '',
  description: '',
  status: 'pending',
  priority: 'medium',
  start_date: '',
  due_date: '',
  group_id: '',
  assigned_to: ''
})

const viewTask = reactive({
  title: '',
  description: '',
  status: '',
  priority: '',
  creator_name: '',
  group_name: '',
  assignee_name: '',
  due_date: '',
  created_at: '',
  updated_at: ''
})

const taskRules = {
  title: [
    { required: true, message: '请输入任务标题', trigger: 'blur' },
    { min: 1, max: 100, message: '标题长度1-100字符', trigger: 'blur' }
  ]
}

const loadGroups = async () => {
  try {
    const response = await getGroupsApi()
    groups.value = response.data
  } catch (error) {
    console.error('获取组列表失败:', error)
  }
}

const loadTasks = async () => {
  loading.value = true
  try {
    const params = {
      type: taskType.value
    }
    if (taskType.value === 'group' && selectedGroupId.value) {
      params.group_id = selectedGroupId.value
    }
    const response = await getTasksApi(params)
    tasks.value = response.data
  } catch (error) {
    console.error('获取任务列表失败:', error)
    ElMessage.error('获取任务列表失败')
  } finally {
    loading.value = false
  }
}

const handleCreateTask = () => {
  isEditing.value = false
  currentTaskId.value = null
  Object.assign(taskForm, {
    title: '',
    description: '',
    status: 'pending',
    priority: 'medium',
    start_date: '',
    due_date: '',
    group_id: '',
    assigned_to: ''
  })
  groupMembers.value = []
  showTaskDialog.value = true
}

const handleGroupChange = async (groupId) => {
  taskForm.assigned_to = ''
  groupMembers.value = []
  
  if (groupId) {
    try {
      const response = await getGroupApi(groupId)
      const groupData = response.data
      if (groupData.members) {
        groupMembers.value = groupData.members.map(member => ({
          id: member.id,
          username: member.username
        }))
      }
    } catch (error) {
      console.error('获取组成员失败:', error)
      ElMessage.error('获取组成员失败')
    }
  }
}

const handleEditTask = async (task) => {
  isEditing.value = true
  currentTaskId.value = task.id
  try {
    const response = await getTaskApi(task.id)
    const taskData = response.data
    Object.assign(taskForm, {
      title: taskData.title,
      description: taskData.description,
      status: taskData.status,
      priority: taskData.priority,
      start_date: taskData.start_date,
      due_date: taskData.due_date,
      group_id: taskData.group_id || '',
      assigned_to: taskData.assigned_to || ''
    })
    
    // 如果任务有组，加载组成员
    if (taskData.group_id) {
      await handleGroupChange(taskData.group_id)
    } else {
      groupMembers.value = []
    }
    
    showTaskDialog.value = true
  } catch (error) {
    console.error('获取任务详情失败:', error)
    ElMessage.error('获取任务详情失败')
  }
}

const handleViewTask = async (task) => {
  try {
    const response = await getTaskApi(task.id)
    const taskData = response.data
    Object.assign(viewTask, taskData)
    showViewDialog.value = true
  } catch (error) {
    console.error('获取任务详情失败:', error)
    ElMessage.error('获取任务详情失败')
  }
}

const handleSaveTask = async () => {
  if (!taskFormRef.value) return

  try {
    const valid = await taskFormRef.value.validate()
    if (!valid) return

    saving.value = true

    const taskData = {
      title: taskForm.title,
      description: taskForm.description,
      status: taskForm.status,
      priority: taskForm.priority,
      due_date: taskForm.due_date,
      group_id: taskForm.group_id || null,
      assigned_to: taskForm.assigned_to || null
    }

    if (isEditing.value) {
      await updateTaskApi(currentTaskId.value, taskData)
      ElMessage.success('任务更新成功')
    } else {
      await createTaskApi(taskData)
      ElMessage.success('任务创建成功')
    }

    showTaskDialog.value = false
    loadTasks()
  } catch (error) {
    console.error('保存任务失败:', error)
    const errorMessage = error.response?.data?.detail || '保存任务失败'
    ElMessage.error(errorMessage)
  } finally {
    saving.value = false
  }
}

const handleCancelTask = () => {
  showTaskDialog.value = false
  if (taskFormRef.value) {
    taskFormRef.value.clearValidate()
  }
}

const handleDeleteTask = async (taskId) => {
  try {
    await ElMessageBox.confirm('确定要删除该任务吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteTaskApi(taskId)
    ElMessage.success('任务删除成功')
    loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除任务失败:', error)
      const errorMessage = error.response?.data?.detail || '删除任务失败'
      ElMessage.error(errorMessage)
    }
  }
}

const getStatusType = (status) => {
  const typeMap = {
    pending: 'info',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    pending: '待处理',
    in_progress: '进行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return textMap[status] || status
}

const getPriorityType = (priority) => {
  const typeMap = {
    low: 'info',
    medium: 'warning',
    high: 'danger'
  }
  return typeMap[priority] || 'info'
}

const getPriorityText = (priority) => {
  const textMap = {
    low: '低',
    medium: '中',
    high: '高'
  }
  return textMap[priority] || priority
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString()
}

onMounted(() => {
  loadGroups()
  loadTasks()
})
</script>

<style scoped>
.task-management {
  padding: 20px;
}

.task-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-filter {
  margin-bottom: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
}

.task-detail {
  line-height: 2;
}

.detail-item {
  margin-bottom: 10px;
}

.label {
  font-weight: bold;
  margin-right: 10px;
  display: inline-block;
  width: 80px;
}

.value {
  display: inline-block;
  vertical-align: top;
}
</style>
