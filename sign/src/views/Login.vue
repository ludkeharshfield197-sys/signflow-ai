<script setup>
import { Lock, User } from '@element-plus/icons-vue'
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AuthShell from '@/components/auth/AuthShell.vue'
import { getApiError } from '@/services/api'
import { login } from '@/services/auth'
import { safeRedirectPath } from '@/services/navigation'

const route = useRoute()
const router = useRouter()
const formRef = ref()
const loading = ref(false)
const capsLock = ref(false)
const errorMessage = ref('')
const rememberedUsername = window.localStorage.getItem('signflow.rememberedUsername') || ''

const form = reactive({
  username: rememberedUsername,
  password: '',
  rememberUsername: Boolean(rememberedUsername),
})

const rules = {
  username: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { min: 3, message: '账号至少 3 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
  ],
}

function updateCapsLock(event) {
  capsLock.value = event.getModifierState?.('CapsLock') || false
}

async function submit() {
  errorMessage.value = ''
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await login({ username: form.username.trim(), password: form.password })
    if (form.rememberUsername) {
      window.localStorage.setItem('signflow.rememberedUsername', form.username.trim())
    } else {
      window.localStorage.removeItem('signflow.rememberedUsername')
    }
    await router.replace(safeRedirectPath(route.query.redirect))
  } catch (error) {
    errorMessage.value = error.message === 'INVALID_AUTH_RESPONSE'
      ? '登录服务返回了无效数据，请联系管理员。'
      : getApiError(error, '账号或密码错误，请检查后重试。')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthShell title="登录 SignFlow AI" description="进入识别工作台，继续管理任务、结果与模型。">
    <el-alert
      v-if="route.query.registered"
      class="sf-auth-alert"
      title="账号创建成功，请登录"
      type="success"
      :closable="false"
      show-icon
    />
    <el-alert
      v-if="route.query.loggedOut"
      class="sf-auth-alert"
      title="你已安全退出"
      type="info"
      :closable="false"
      show-icon
    />
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
        <template #label><label for="login-username">账号</label></template>
        <el-input
          id="login-username"
          v-model="form.username"
          autocomplete="username"
          inputmode="text"
          placeholder="请输入账号"
          size="large"
        >
          <template #prefix><el-icon><User /></el-icon></template>
        </el-input>
      </el-form-item>

      <el-form-item prop="password">
        <template #label><label for="login-password">密码</label></template>
        <el-input
          id="login-password"
          v-model="form.password"
          autocomplete="current-password"
          placeholder="请输入密码"
          show-password
          size="large"
          type="password"
          @keydown="updateCapsLock"
          @keyup="updateCapsLock"
        >
          <template #prefix><el-icon><Lock /></el-icon></template>
        </el-input>
        <p v-if="capsLock" class="sf-caps-warning" role="status">大写锁定已开启</p>
      </el-form-item>

      <div class="sf-login-options">
        <el-checkbox v-model="form.rememberUsername">记住账号</el-checkbox>
        <RouterLink to="/auth/register">创建账号</RouterLink>
      </div>

      <el-button class="sf-auth-submit" type="primary" native-type="submit" size="large" :loading="loading">
        {{ loading ? '正在安全登录' : '登录' }}
      </el-button>
    </el-form>

    <div class="sf-auth-divider"><span>或</span></div>
    <RouterLink class="sf-demo-entry" to="/product-tour">无需账号，体验官方样例</RouterLink>
  </AuthShell>
</template>

<style scoped>
.sf-auth-alert { margin-bottom: var(--sf-space-5); }

:deep(.el-form-item) { margin-bottom: var(--sf-space-5); }
:deep(.el-form-item__label) {
  padding: 0 0 var(--sf-space-2);
  color: var(--sf-color-text-secondary);
  font-size: var(--sf-text-sm);
  font-weight: 700;
}

.sf-caps-warning {
  width: 100%;
  margin: var(--sf-space-2) 0 0;
  color: var(--sf-color-warning);
  font-size: var(--sf-text-xs);
}

.sf-login-options {
  display: flex;
  margin: var(--sf-space-1) 0 var(--sf-space-6);
  align-items: center;
  justify-content: space-between;
  gap: var(--sf-space-4);
  font-size: var(--sf-text-sm);
}

.sf-login-options a { color: var(--sf-color-primary); font-weight: 700; }
.sf-auth-submit { width: 100%; min-height: 48px; font-size: var(--sf-text-sm); }

.sf-auth-divider {
  display: flex;
  margin: var(--sf-space-8) 0 var(--sf-space-5);
  align-items: center;
  gap: var(--sf-space-3);
  color: var(--sf-color-text-disabled);
  font-size: var(--sf-text-xs);
}

.sf-auth-divider::before,
.sf-auth-divider::after { content: ""; height: 1px; flex: 1; background: var(--sf-color-border); }

.sf-demo-entry {
  display: flex;
  min-height: 44px;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--sf-color-border);
  border-radius: var(--sf-radius-control);
  color: var(--sf-color-text-secondary);
  font-size: var(--sf-text-sm);
  font-weight: 700;
}

.sf-demo-entry:hover { border-color: var(--sf-color-primary); color: var(--sf-color-primary); }
</style>
