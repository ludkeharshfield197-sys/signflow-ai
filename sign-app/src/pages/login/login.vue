<template>
  <view class="login-page" :class="sfAccessibilityClass">
    <view class="login-page__glow"></view>
    <view class="login-page__content">
      <text class="login-page__brand">SignFlow AI</text>
      <text class="login-page__title">欢迎回来</text>
      <text class="login-page__lead">登录后可在手机上完成真实图片、视频与实时手语识别。</text>

      <view class="login-card">
        <view class="sf-field">
          <label class="sf-label" for="login-username">账号</label>
          <input
            id="login-username"
            v-model.trim="form.username"
            class="sf-input"
            name="username"
            type="text"
            maxlength="100"
            autocomplete="username"
            placeholder="请输入账号"
            aria-label="登录账号"
          />
        </view>
        <view class="sf-field">
          <label class="sf-label" for="login-password">密码</label>
          <input
            id="login-password"
            v-model="form.password"
            class="sf-input"
            name="password"
            password
            maxlength="128"
            autocomplete="current-password"
            placeholder="请输入密码"
            aria-label="登录密码"
            confirm-type="done"
            @confirm="handleLogin"
          />
        </view>

        <view v-if="errorMessage" class="sf-error">{{ errorMessage }}</view>

        <button
          class="sf-button sf-button--primary login-card__submit"
          :disabled="loading"
          @tap="handleLogin"
        >
          {{ loading ? '正在安全登录…' : '登录 SignFlow' }}
        </button>

        <button class="login-card__link" @tap="goRegister">创建新账号</button>

        <button class="server-toggle" @tap="toggleServerSettings">
          {{ showServer ? '收起服务设置' : '识别服务设置' }}
        </button>
        <view v-if="showServer" class="server-panel">
          <label class="sf-label" for="login-server-origin">服务地址</label>
          <input
            id="login-server-origin"
            v-model.trim="serverOrigin"
            class="sf-input server-panel__input"
            name="serverOrigin"
            type="text"
            placeholder="http://电脑局域网IP:8001"
            aria-label="识别服务地址"
          />
          <text class="server-panel__help">
            真机不能使用 127.0.0.1。本地调试环境可填写电脑 IP；正式部署必须使用微信后台白名单内的 HTTPS 域名。
          </text>
        </view>
      </view>

      <text class="login-page__privacy">密码不会保存在手机本地，也不会进入 URL 或日志。</text>
    </view>
  </view>
</template>

<script>
import { login } from '../../services/auth'
import { enhanceH5Inputs } from '../../services/accessibility'
import {
  getServerOrigin,
  normalizeServerOrigin,
  saveServerOrigin,
} from '../../services/config'

export default {
  data() {
    return {
      form: {
        username: '',
        password: '',
      },
      serverOrigin: getServerOrigin(),
      showServer: false,
      loading: false,
      errorMessage: '',
    }
  },
  onReady() {
    this.applyInputAccessibility()
  },
  methods: {
    applyInputAccessibility() {
      this.$nextTick(() => {
        enhanceH5Inputs([
          {
            id: 'login-username',
            name: 'username',
            label: '登录账号',
            placeholder: '请输入账号',
            autocomplete: 'username',
          },
          {
            id: 'login-password',
            name: 'password',
            label: '登录密码',
            placeholder: '请输入密码',
            autocomplete: 'current-password',
          },
          {
            id: 'login-server-origin',
            name: 'serverOrigin',
            label: '识别服务地址',
            placeholder: 'http://电脑局域网IP:8001',
          },
        ])
      })
    },
    toggleServerSettings() {
      this.showServer = !this.showServer
      this.applyInputAccessibility()
    },
    async handleLogin() {
      if (this.loading) return
      this.errorMessage = ''
      if (!this.form.username || !this.form.password) {
        this.errorMessage = '请输入账号和密码。'
        return
      }
      try {
        this.serverOrigin = normalizeServerOrigin(this.serverOrigin)
        saveServerOrigin(this.serverOrigin)
      } catch (error) {
        this.showServer = true
        this.errorMessage = error.message
        return
      }

      this.loading = true
      try {
        await login(this.form)
        this.form.password = ''
        uni.switchTab({ url: '/pages/home/home' })
      } catch (error) {
        this.errorMessage = error.message || '登录失败，请检查账号和服务地址。'
      } finally {
        this.loading = false
      }
    },
    goRegister() {
      uni.navigateTo({ url: '/pages/register/register' })
    },
  },
}
</script>

<style scoped>
.login-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  background: #f7f9fc;
}

.login-page__glow {
  position: absolute;
  top: -260rpx;
  right: -220rpx;
  width: 640rpx;
  height: 640rpx;
  border-radius: 50%;
  background: rgba(91, 91, 214, 0.1);
}

.login-page__content {
  position: relative;
  z-index: 1;
  padding: calc(var(--status-bar-height) + 96rpx) 36rpx 52rpx;
}

.login-page__brand {
  display: block;
  color: #5b5bd6;
  font-size: 32rpx;
  font-weight: 760;
}

.login-page__title {
  display: block;
  margin-top: 52rpx;
  color: #182230;
  font-size: 56rpx;
  line-height: 1.15;
  font-weight: 780;
}

.login-page__lead {
  display: block;
  max-width: 610rpx;
  margin-top: 18rpx;
  color: #667085;
  font-size: 28rpx;
  line-height: 1.65;
}

.login-card {
  margin-top: 56rpx;
  padding: 8rpx 34rpx 34rpx;
  border: 1rpx solid #e6eaf2;
  border-radius: 30rpx;
  background: #ffffff;
  box-shadow: 0 18rpx 60rpx rgba(15, 23, 42, 0.07);
}

.login-card__submit {
  width: 100%;
  margin-top: 34rpx;
}

.login-card__link,
.server-toggle {
  width: 100%;
  min-height: 72rpx;
  background: transparent;
  color: #5b5bd6;
  font-size: 27rpx;
  line-height: 72rpx;
}

.server-toggle {
  margin-top: 4rpx;
  color: #667085;
  border-top: 1rpx solid #eaecf0;
}

.server-panel {
  padding-top: 14rpx;
}

.server-panel__input {
  min-height: 80rpx;
  font-size: 24rpx;
}

.server-panel__help {
  display: block;
  margin-top: 12rpx;
  color: #667085;
  font-size: 22rpx;
  line-height: 1.55;
}

.login-page__privacy {
  display: block;
  margin-top: 28rpx;
  color: #98a2b3;
  font-size: 23rpx;
  line-height: 1.55;
  text-align: center;
}
</style>
