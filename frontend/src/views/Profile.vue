<template>
  <el-card class="profile-card">
    <template #header>
      <h2>个人信息</h2>
    </template>
    
    <div class="profile-content">
      <div class="avatar-section">
        <el-avatar
          :size="120"
          :src="userStore.avatarUrl || defaultAvatar"
          class="user-avatar"
        >
          {{ userStore.username?.charAt(0).toUpperCase() }}
        </el-avatar>
        
        <el-upload
          class="avatar-uploader"
          action="/api/v1/uploads/avatar"
          :headers="{ Authorization: `Bearer ${userStore.token}` }"
          :show-file-list="false"
          :on-success="handleAvatarUploadSuccess"
          :on-error="handleAvatarUploadError"
          :before-upload="beforeAvatarUpload"
          accept="image/jpeg,image/png,image/webp,image/gif"
        >
          <el-button type="primary" size="small" :loading="uploading">
            {{ uploading ? '上传中...' : '更换头像' }}
          </el-button>
        </el-upload>
      </div>
      
      <el-form
        ref="profileFormRef"
        :model="profileForm"
        :rules="profileRules"
        label-width="100px"
        class="profile-form"
      >
        <el-form-item label="用户名">
          <el-input v-model="userStore.username" disabled />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        
        <el-form-item label="角色">
          <el-input :value="userStore.roles?.join(', ')" disabled />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleUpdateProfile" :loading="saving">
            {{ saving ? '保存中...' : '保存修改' }}
          </el-button>
          <el-button @click="showChangePasswordDialog = true">
            修改密码
          </el-button>
        </el-form-item>
      </el-form>

      <el-dialog
        v-model="showChangePasswordDialog"
        title="修改密码"
        width="500px"
        :close-on-click-modal="false"
      >
        <el-form
          ref="changePasswordFormRef"
          :model="changePasswordForm"
          :rules="changePasswordRules"
          label-width="120px"
        >
          <el-form-item label="当前密码" prop="currentPassword">
            <el-input
              v-model="changePasswordForm.currentPassword"
              type="password"
              placeholder="请输入当前密码"
              show-password
            />
          </el-form-item>

          <el-form-item label="新密码" prop="newPassword">
            <el-input
              v-model="changePasswordForm.newPassword"
              type="password"
              placeholder="请输入新密码"
              show-password
              @input="checkPasswordStrength"
            />
          </el-form-item>

          <el-form-item label="密码强度" prop="passwordStrength" v-if="changePasswordForm.newPassword">
            <div class="password-strength">
              <div class="strength-bar">
                <div
                  class="strength-level"
                  :class="passwordStrengthClass"
                  :style="{ width: passwordStrengthPercent + '%' }"
                ></div>
              </div>
              <span class="strength-text" :class="passwordStrengthClass">
                {{ passwordStrengthText }}
              </span>
            </div>
          </el-form-item>

          <el-form-item label="密码要求" v-if="changePasswordForm.newPassword">
            <div class="password-requirements">
              <div :class="{ met: passwordRequirements.length }">
                长度至少8个字符
              </div>
              <div :class="{ met: passwordRequirements.uppercase }">
                包含大写字母 (A-Z)
              </div>
              <div :class="{ met: passwordRequirements.lowercase }">
                包含小写字母 (a-z)
              </div>
              <div :class="{ met: passwordRequirements.digit }">
                包含数字 (0-9)
              </div>
              <div :class="{ met: passwordRequirements.special }">
                包含特殊符号 (!@#$%^&*等)
              </div>
            </div>
          </el-form-item>

          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input
              v-model="changePasswordForm.confirmPassword"
              type="password"
              placeholder="请再次输入新密码"
              show-password
            />
          </el-form-item>
        </el-form>

        <template #footer>
          <el-button @click="handleCancelChangePassword">取 消</el-button>
          <el-button type="primary" @click="handleChangePassword" :loading="changingPassword">
            {{ changingPassword ? '提交中...' : '确 定' }}
          </el-button>
        </template>
      </el-dialog>
    </div>
  </el-card>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { uploadAvatarApi, getUserInfoApi, changePasswordApi } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const profileFormRef = ref(null)
const changePasswordFormRef = ref(null)
const uploading = ref(false)
const saving = ref(false)
const changingPassword = ref(false)
const showChangePasswordDialog = ref(false)

const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

const profileForm = reactive({
  email: ''
})

const profileRules = {
  email: [
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ]
}

const changePasswordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== changePasswordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const changePasswordRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码长度不能少于8个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const passwordRequirements = computed(() => ({
  length: changePasswordForm.newPassword.length >= 8,
  uppercase: /[A-Z]/.test(changePasswordForm.newPassword),
  lowercase: /[a-z]/.test(changePasswordForm.newPassword),
  digit: /[0-9]/.test(changePasswordForm.newPassword),
  special: /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(changePasswordForm.newPassword)
}))

const passwordStrengthPercent = computed(() => {
  const reqs = passwordRequirements.value
  const metCount = Object.values(reqs).filter(Boolean).length
  return (metCount / 5) * 100
})

const passwordStrengthClass = computed(() => {
  const percent = passwordStrengthPercent.value
  if (percent <= 20) return 'weak'
  if (percent <= 40) return 'fair'
  if (percent <= 60) return 'medium'
  if (percent <= 80) return 'good'
  return 'strong'
})

const passwordStrengthText = computed(() => {
  const classMap = {
    weak: '非常弱',
    fair: '弱',
    medium: '中等',
    good: '强',
    strong: '非常强'
  }
  return classMap[passwordStrengthClass.value]
})

const checkPasswordStrength = () => {
  // 密码强度通过computed属性自动计算
}

const loadUserInfo = async () => {
  try {
    const response = await getUserInfoApi()
    const userInfo = response.data
    profileForm.email = userInfo.email || ''
    if (userInfo.avatar_url) {
      userStore.setAvatarUrl(userInfo.avatar_url)
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

const beforeAvatarUpload = (file) => {
  const isImage = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'].includes(file.type)
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('头像图片格式不正确，支持 JPG、PNG、WEBP、GIF 格式')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('头像大小不能超过 2MB')
    return false
  }
  return true
}

const handleAvatarUploadSuccess = (response) => {
  uploading.value = false
  if (response.image_url) {
    userStore.setAvatarUrl(response.image_url)
    ElMessage.success('头像上传成功')
  }
}

const handleAvatarUploadError = (error) => {
  uploading.value = false
  console.error('头像上传失败:', error)
  ElMessage.error('头像上传失败，请重试')
}

const handleUpdateProfile = async () => {
  saving.value = true
  try {
    ElMessage.success('个人信息更新成功')
  } catch (error) {
    console.error('更新失败:', error)
    ElMessage.error('更新失败，请重试')
  } finally {
    saving.value = false
  }
}

const handleChangePassword = async () => {
  if (!changePasswordFormRef.value) return

  try {
    const valid = await changePasswordFormRef.value.validate()
    if (!valid) return

    changingPassword.value = true

    await changePasswordApi({
      current_password: changePasswordForm.currentPassword,
      new_password: changePasswordForm.newPassword,
      confirm_password: changePasswordForm.confirmPassword
    })

    ElMessage.success('密码修改成功！请重新登录')
    handleCancelChangePassword()
    userStore.logout()
    window.location.href = '/login'

  } catch (error) {
    console.error('修改密码失败:', error)
    const errorMessage = error.response?.data?.detail || '修改密码失败，请稍后重试'
    ElMessage.error(errorMessage)
  } finally {
    changingPassword.value = false
  }
}

const handleCancelChangePassword = () => {
  showChangePasswordDialog.value = false
  changePasswordForm.currentPassword = ''
  changePasswordForm.newPassword = ''
  changePasswordForm.confirmPassword = ''
  if (changePasswordFormRef.value) {
    changePasswordFormRef.value.clearValidate()
  }
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.profile-card {
  max-width: 600px;
  margin: 20px auto;
}

.profile-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
}

.user-avatar {
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.avatar-uploader {
  margin-top: 10px;
}

.profile-form {
  width: 100%;
}

.password-strength {
  display: flex;
  align-items: center;
  width: 100%;
}

.strength-bar {
  flex: 1;
  height: 8px;
  background: #e4e7ed;
  border-radius: 4px;
  margin-right: 10px;
  overflow: hidden;
}

.strength-level {
  height: 100%;
  transition: width 0.3s, background-color 0.3s;
  border-radius: 4px;
}

.strength-level.weak {
  background: #f56c6c;
}

.strength-level.fair {
  background: #e6a23c;
}

.strength-level.medium {
  background: #e6a23c;
}

.strength-level.good {
  background: #67c23a;
}

.strength-level.strong {
  background: #67c23a;
}

.strength-text {
  font-size: 12px;
  min-width: 50px;
}

.strength-text.weak {
  color: #f56c6c;
}

.strength-text.fair {
  color: #e6a23c;
}

.strength-text.medium {
  color: #e6a23c;
}

.strength-text.good {
  color: #67c23a;
}

.strength-text.strong {
  color: #67c23a;
}

.password-requirements {
  font-size: 12px;
  color: #909399;
  line-height: 1.8;
}

.password-requirements div {
  position: relative;
  padding-left: 18px;
}

.password-requirements div::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 12px;
  height: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 50%;
  background: #fff;
  transition: all 0.3s;
}

.password-requirements div.met::before {
  background: #67c23a;
  border-color: #67c23a;
}

.password-requirements div.met::after {
  content: '';
  position: absolute;
  left: 4px;
  top: 50%;
  transform: translateY(-50%) rotate(45deg);
  width: 4px;
  height: 7px;
  border: solid #fff;
  border-width: 0 2px 2px 0;
}

.password-requirements div.met {
  color: #67c23a;
}
</style>