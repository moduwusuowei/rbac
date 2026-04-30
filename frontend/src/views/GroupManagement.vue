<template>
  <div class="group-management">
    <el-card class="group-card">
      <template #header>
        <div class="card-header">
          <h2>组管理</h2>
          <el-button type="primary" @click="handleCreateGroup">
            <el-icon><Plus /></el-icon> 创建组
          </el-button>
        </div>
      </template>

      <el-table :data="groups" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="组名称" min-width="150" />
        <el-table-column prop="code" label="组编码" width="120" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="member_count" label="成员数" width="80" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="handleViewGroup(scope.row)"
            >
              查看
            </el-button>
            <el-button
              type="info"
              size="small"
              @click="handleEditGroup(scope.row)"
              v-if="scope.row.is_leader"
            >
              编辑
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑组对话框 -->
    <el-dialog
      v-model="showGroupDialog"
      :title="isEditing ? '编辑组' : '创建组'"
      width="500px"
    >
      <el-form
        ref="groupFormRef"
        :model="groupForm"
        :rules="groupRules"
        label-width="80px"
      >
        <el-form-item label="组名称" prop="name">
          <el-input v-model="groupForm.name" placeholder="请输入组名称" />
        </el-form-item>

        <el-form-item label="组编码" prop="code">
          <el-input v-model="groupForm.code" placeholder="请输入组编码" />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="groupForm.description"
            type="textarea"
            rows="3"
            placeholder="请输入组描述"
          />
        </el-form-item>

        <el-form-item label="状态" prop="is_active" v-if="isEditing">
          <el-switch v-model="groupForm.is_active" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="handleCancelGroup">取 消</el-button>
        <el-button type="primary" @click="handleSaveGroup" :loading="saving">
          {{ saving ? '保存中...' : '确 定' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 组详情对话框 -->
    <el-dialog
      v-model="showGroupDetailDialog"
      :title="`${currentGroup.name || ''} - 组详情`"
      width="800px"
    >
      <div class="group-detail">
        <div class="detail-section">
          <h3>基本信息</h3>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="label">组名称：</span>
              <span class="value">{{ currentGroup.name }}</span>
            </div>
            <div class="detail-item">
              <span class="label">组编码：</span>
              <span class="value">{{ currentGroup.code }}</span>
            </div>
            <div class="detail-item">
              <span class="label">描述：</span>
              <span class="value">{{ currentGroup.description || '无' }}</span>
            </div>
            <div class="detail-item">
              <span class="label">状态：</span>
              <el-tag :type="currentGroup.is_active ? 'success' : 'danger'">
                {{ currentGroup.is_active ? '激活' : '禁用' }}
              </el-tag>
            </div>
            <div class="detail-item">
              <span class="label">创建时间：</span>
              <span class="value">{{ formatDate(currentGroup.created_at) }}</span>
            </div>
            <div class="detail-item">
              <span class="label">更新时间：</span>
              <span class="value">{{ formatDate(currentGroup.updated_at) }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <div class="section-header">
            <h3>成员管理</h3>
            <el-button type="primary" size="small" @click="showAddMemberDialog = true" v-if="currentGroup.is_leader">
              添加成员
            </el-button>
          </div>
          
          <el-table :data="currentGroup.members" style="width: 100%">
            <el-table-column prop="username" label="用户名" width="150" />
            <el-table-column prop="email" label="邮箱" min-width="200" />
            <el-table-column label="角色" width="100">
              <template #default="scope">
                <el-tag type="success" v-if="scope.row.is_leader">
                  组长
                </el-tag>
                <el-tag v-else>
                  组员
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="scope">
                <div style="display: flex; gap: 8px;">
                  <el-button
                    type="danger"
                    size="small"
                    @click="handleRemoveMember(scope.row.id)"
                    v-if="currentGroup.is_leader && !scope.row.is_leader"
                  >
                    移除
                  </el-button>
                  <el-button
                    type="warning"
                    size="small"
                    @click="handleTransferLeadership(scope.row)"
                    v-if="currentGroup.is_leader && !scope.row.is_leader"
                  >
                    设为组长
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>

    <!-- 添加成员对话框 -->
    <el-dialog
      v-model="showAddMemberDialog"
      title="添加成员"
      width="500px"
    >
      <el-form
        ref="memberFormRef"
        :model="memberForm"
        :rules="memberRules"
        label-width="80px"
      >
        <el-form-item label="选择用户" prop="userId">
          <el-select
            v-model="memberForm.userId"
            placeholder="请选择或搜索用户"
            filterable
            allow-create
            :filter-method="filterUsers"
            style="width: 100%"
          >
            <el-option
              v-for="user in sortedUsers"
              :key="user.id"
              :label="user.username"
              :value="user.id"
            />
          </el-select>
          <div class="select-hint">提示：可直接输入用户名搜索，或从下拉列表中选择</div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="handleCancelAddMember">取 消</el-button>
        <el-button type="primary" @click="handleAddMember" :loading="addingMember">
          {{ addingMember ? '添加中...' : '确 定' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 交接组长权限对话框 -->
    <el-dialog
      v-model="showTransferDialog"
      title="交接组长权限"
      width="400px"
    >
      <div class="transfer-info">
        <p>当前组长：{{ currentGroup.members?.find(m => m.is_leader)?.username }}</p>
        <p>新组长：{{ transferMember?.username }}</p>
        <p class="warning">确定要将组长权限交接给 {{ transferMember?.username }} 吗？</p>
      </div>

      <template #footer>
        <el-button @click="handleCancelTransfer">取 消</el-button>
        <el-button type="primary" @click="handleConfirmTransfer" :loading="transferring">
          {{ transferring ? '交接中...' : '确 定' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getGroupsApi, createGroupApi, getGroupApi, updateGroupApi, addMemberApi, removeMemberApi, transferLeadershipApi } from '@/api/task'
import { getUsersApi } from '@/api/user'

const groups = ref([])
const loading = ref(false)
const saving = ref(false)
const addingMember = ref(false)
const transferring = ref(false)

const showCreateGroupDialog = ref(false)
const showGroupDialog = ref(false)
const showGroupDetailDialog = ref(false)
const showAddMemberDialog = ref(false)
const showTransferDialog = ref(false)

const groupFormRef = ref(null)
const memberFormRef = ref(null)
const isEditing = ref(false)
const currentGroupId = ref(null)

const groupForm = reactive({
  name: '',
  code: '',
  description: '',
  is_active: true
})

const memberForm = reactive({
  userId: ''
})

const currentGroup = reactive({
  id: '',
  name: '',
  code: '',
  description: '',
  is_active: true,
  created_at: '',
  updated_at: '',
  is_leader: false,
  member_count: 0,
  members: []
})

const transferMember = ref(null)

const groupRules = {
  name: [
    { required: true, message: '请输入组名称', trigger: 'blur' },
    { min: 1, max: 50, message: '名称长度1-50字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入组编码', trigger: 'blur' },
    { min: 1, max: 50, message: '编码长度1-50字符', trigger: 'blur' }
  ]
}

const memberRules = {
  userId: [
    { required: true, message: '请选择或输入用户', trigger: 'blur' }
  ]
}

const allUsers = ref([])

const filterUsers = (query) => {
  if (!query) return true
  return (user) => user.username.toLowerCase().includes(query.toLowerCase())
}

const sortedUsers = computed(() => {
  return [...allUsers.value].sort((a, b) => {
    return a.username.localeCompare(b.username, 'zh-CN')
  })
})

const loadUsers = async () => {
  try {
    const response = await getUsersApi()
    allUsers.value = response.data
  } catch (error) {
    console.error('获取用户列表失败:', error)
  }
}

const loadGroups = async () => {
  loading.value = true
  try {
    const response = await getGroupsApi()
    groups.value = response.data
  } catch (error) {
    console.error('获取组列表失败:', error)
    ElMessage.error('获取组列表失败')
  } finally {
    loading.value = false
  }
}

const handleCreateGroup = () => {
  isEditing.value = false
  currentGroupId.value = null
  Object.assign(groupForm, {
    name: '',
    code: '',
    description: '',
    is_active: true
  })
  showGroupDialog.value = true
}

const handleEditGroup = async (group) => {
  isEditing.value = true
  currentGroupId.value = group.id
  try {
    const response = await getGroupApi(group.id)
    const groupData = response.data
    Object.assign(groupForm, {
      name: groupData.name,
      code: groupData.code,
      description: groupData.description,
      is_active: groupData.is_active
    })
    showGroupDialog.value = true
  } catch (error) {
    console.error('获取组详情失败:', error)
    ElMessage.error('获取组详情失败')
  }
}

const handleViewGroup = async (group) => {
  try {
    const response = await getGroupApi(group.id)
    const groupData = response.data
    Object.assign(currentGroup, groupData)
    showGroupDetailDialog.value = true
  } catch (error) {
    console.error('获取组详情失败:', error)
    ElMessage.error('获取组详情失败')
  }
}

const handleSaveGroup = async () => {
  if (!groupFormRef.value) return

  try {
    const valid = await groupFormRef.value.validate()
    if (!valid) return

    saving.value = true

    const groupData = {
      name: groupForm.name,
      code: groupForm.code,
      description: groupForm.description
    }

    if (isEditing.value) {
      groupData.is_active = groupForm.is_active
      await updateGroupApi(currentGroupId.value, groupData)
      ElMessage.success('组信息更新成功')
    } else {
      await createGroupApi(groupData)
      ElMessage.success('组创建成功')
    }

    showGroupDialog.value = false
    loadGroups()
  } catch (error) {
    console.error('保存组信息失败:', error)
    const errorMessage = error.response?.data?.detail || '保存组信息失败'
    ElMessage.error(errorMessage)
  } finally {
    saving.value = false
  }
}

const handleCancelGroup = () => {
  showGroupDialog.value = false
  if (groupFormRef.value) {
    groupFormRef.value.clearValidate()
  }
}

const handleAddMember = async () => {
  if (!memberFormRef.value) return

  try {
    const valid = await memberFormRef.value.validate()
    if (!valid) return

    addingMember.value = true

    await addMemberApi(currentGroup.id, {
      user_id: memberForm.userId
    })

    ElMessage.success('成员添加成功')
    showAddMemberDialog.value = false
    handleViewGroup(currentGroup)
  } catch (error) {
    console.error('添加成员失败:', error)
    const errorMessage = error.response?.data?.detail || '添加成员失败'
    ElMessage.error(errorMessage)
  } finally {
    addingMember.value = false
  }
}

const handleCancelAddMember = () => {
  showAddMemberDialog.value = false
  if (memberFormRef.value) {
    memberFormRef.value.clearValidate()
  }
  memberForm.userId = ''
}

const handleRemoveMember = async (userId) => {
  try {
    await ElMessageBox.confirm('确定要移除该成员吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await removeMemberApi(currentGroup.id, userId)
    ElMessage.success('成员移除成功')
    handleViewGroup(currentGroup)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('移除成员失败:', error)
      const errorMessage = error.response?.data?.detail || '移除成员失败'
      ElMessage.error(errorMessage)
    }
  }
}

const handleTransferLeadership = (member) => {
  transferMember.value = member
  showTransferDialog.value = true
}

const handleConfirmTransfer = async () => {
  if (!transferMember.value) return

  try {
    transferring.value = true

    await transferLeadershipApi(currentGroup.id, {
      username: transferMember.value.username
    })

    ElMessage.success('组长权限交接成功')
    showTransferDialog.value = false
    await handleViewGroup({ id: currentGroup.id })
  } catch (error) {
    console.error('交接组长权限失败:', error)
    const errorMessage = error.response?.data?.detail || '交接组长权限失败'
    ElMessage.error(errorMessage)
  } finally {
    transferring.value = false
  }
}

const handleCancelTransfer = () => {
  showTransferDialog.value = false
  transferMember.value = null
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString()
}

onMounted(() => {
  loadGroups()
  loadUsers()
})
</script>

<style scoped>
.group-management {
  padding: 20px;
}

.group-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.group-detail {
  line-height: 1.8;
}

.detail-section {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.detail-section:last-child {
  border-bottom: none;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h3 {
  margin: 0;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.detail-item {
  display: flex;
  align-items: center;
}

.label {
  font-weight: bold;
  margin-right: 10px;
  min-width: 80px;
}

.value {
  flex: 1;
}

.transfer-info {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}

.transfer-info p {
  margin: 10px 0;
}

.transfer-info .warning {
  color: #e6a23c;
  font-weight: bold;
}
</style>
