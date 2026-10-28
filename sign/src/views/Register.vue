<script setup>
import { Check, Lock, Message, User } from '@element-plus/icons-vue'
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import AuthShell from '@/components/auth/AuthShell.vue'
import { getApiError } from '@/services/api'
import { registerAccount } from '@/services/auth'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const errorMessage = ref('')

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  accepted: false,
})

function validateConfirmation(rule, value, callback) {
  if (value !== form.password) callback(new Error('两次输入的密码不一致'))
  else callback()
}

function validatePrivacy(rule, value, callback) {
  if (!value) callback(new Error('请阅读并同意隐私说明'))
  else callback()
}

const rules = {
  username: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { min: 3, max: 32, message: '账号需为 3–32 个字符', trigger: 'blur' },
    { pattern: /^[A-Za-z0-9_.-]+$/, message: '仅支持字母、数字、点、横线和下划线', trigger: 'blur' },
  ],
  email: [
    { type: 'email', message: '请输入有效邮箱', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请设置密码', trigger: 'blur' },
    { min: 10, message: '密码至少 10 个字符', trigger: 'blur' },
    { pattern: /^(?=.*[A-Za-z])(?=.*\d).+$/, message: '密码需同时包含字母和数字', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmation, trigger: ['blur', 'change'] },
  ],
  accepted: [{ validator: validatePrivacy, trigger: 'change' }],
}

async function submit() {
  errorMessage.value = ''
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await registerAccount({
      username: form.username.trim(),
      email: form.email.trim(),
      password: form.password,
      confirmPassword: form.confirmPassword,
    })
    await router.replace({ path: '/auth/login', query: { registered: '1' } })
  } catch (error) {
    errorMessage.value = getApiError(error, '创建账号失败，请检查信息后重试。')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthShell title="创建 SignFlow AI 账号" description="注册后可保存识别结果、管理模型版本并查看完整任务记录。">
    <el-alert
      v-if="errorMessage"
      class="sf-auth-alert"
      :title="errorMessage"
      type="error"
      :closable="false"
      show-icon
      role="alert"
    />

    <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="submit">
      <el-form-item prop="username">
        <template #label><label for="register-username">账号</label></template>
        <el-input id="register-username" v-model="form.username" autocomplete="username" placeholder="例如 signflow_user" size="large">
          <template #prefix><el-icon><User /></el-icon></template>
        </el-input>
      </el-form-item>

      <el-form-item prop="email">
        <template #label><label for="register-email">邮箱（选填）</label></template>
        <el-input id="register-email" v-model="form.email" autocomplete="email" inputmode="email" placeholder="用于接收重要安全通知" size="large">
          <template #prefix><el-icon><Message /></el-icon></template>
        </el-input>
      </el-form-item>

      <el-form-item prop="password">
        <template #label><label for="register-password">密码</label></template>
        <el-input id="register-password" v-model="form.password" autocomplete="new-password" placeholder="至少 10 位，包含字母和数字" show-password size="large" type="password">
          <template #prefix><el-icon><Lock /></el-icon></template>
        </el-input>
      </el-form-item>

      <el-form-item prop="confirmPassword">
        <template #label><label for="register-confirm-password">确认密码</label></template>
        <el-input id="register-confirm-password" v-model="form.confirmPassword" autocomplete="new-password" placeholder="再次输入密码" show-password size="large" type="password">
          <template #prefix><el-icon><Check /></el-icon></template>
        </el-input>
      </el-form-item>

      <el-form-item prop="accepted" class="sf-privacy-field">
        <el-checkbox v-model="form.accepted">
          我已阅读并同意
          <RouterLink to="/privacy" target="_blank">隐私与数据保留说明</RouterLink>
        </el-checkbox>
      </el-form-item>

      <el-button class="sf-auth-submit" type="primary" native-type="submit" size="large" :loading="loading">
        {{ loading ? '正在创建账号' : '创建账号' }}
      </el-button>
    </el-form>

    <p class="sf-login-entry">已有账号？<RouterLink to="/auth/login">返回登录</RouterLink></p>
  </AuthShell>
</template>

<style scoped>
.sf-auth-alert { margin-bottom: var(--sf-space-5); }
:deep(.el-form-item) { margin-bottom: var(--sf-space-4); }
:deep(.el-form-item__label) {
  padding: 0 0 var(--sf-space-2);
  color: var(--sf-color-text-secondary);
  font-size: var(--sf-text-sm);
  font-weight: 700;
}

.sf-privacy-field { margin-top: var(--sf-space-2); }
.sf-privacy-field a { color: var(--sf-color-primary); font-weight: 700; }
.sf-auth-submit { width: 100%; min-height: 48px; margin-top: var(--sf-space-2); font-size: var(--sf-text-sm); }
.sf-login-entry { margin: var(--sf-space-6) 0 0; color: var(--sf-color-text-muted); font-size: var(--sf-text-sm); text-align: center; }
.sf-login-entry a { color: var(--sf-color-primary); font-weight: 700; }

@media (max-width: 420px) {
  :deep(.el-checkbox__label) { white-space: normal; line-height: 1.6; }
}
</style>
