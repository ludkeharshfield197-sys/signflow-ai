<template>
  <view class="sf-page register-page" :class="sfAccessibilityClass">
    <SfTopBar title="创建账号" back />
    <text class="sf-heading">开始使用 SignFlow</text>
    <text class="sf-subheading">账号会与网页端共享结果和模型，无需重复配置。</text>

    <view class="register-card sf-surface">
      <view class="sf-field">
        <label class="sf-label" for="register-username">账号</label>
        <input
          id="register-username"
          v-model.trim="form.username"
          class="sf-input"
          name="username"
          maxlength="100"
          placeholder="2–100 个字符"
          aria-label="注册账号"
        />
      </view>
      <view class="sf-field">
        <label class="sf-label" for="register-email">邮箱（可选）</label>
        <input
          id="register-email"
          v-model.trim="form.email"
          class="sf-input"
          name="email"
          type="text"
          maxlength="254"
          placeholder="用于账号联系"
          aria-label="注册邮箱，可选"
        />
      </view>
      <view class="sf-field">
        <label class="sf-label" for="register-password">密码</label>
        <input
          id="register-password"
          v-model="form.password"
          class="sf-input"
          name="password"
          password
          maxlength="128"
          placeholder="至少 12 位"
          aria-label="注册密码"
        />
      </view>
      <view class="sf-field">
        <label class="sf-label" for="register-confirm-password">确认密码</label>
        <input
          id="register-confirm-password"
          v-model="form.confirmPassword"
          class="sf-input"
          name="confirmPassword"
          password
          maxlength="128"
          placeholder="再次输入密码"
          aria-label="确认注册密码"
          confirm-type="done"
          @confirm="submit"
        />
      </view>

      <view v-if="errorMessage" class="sf-error">{{ errorMessage }}</view>
      <button
        class="sf-button sf-button--primary register-card__submit"
        :disabled="loading"
        @tap="submit"
      >
        {{ loading ? '正在创建…' : '创建账号' }}
      </button>
    </view>
  </view>
</template>

<script>
import SfTopBar from '../../components/SfTopBar.vue'
import { enhanceH5Inputs } from '../../services/accessibility'
import { registerAccount } from '../../services/auth'

export default {
  components: { SfTopBar },
  data() {
    return {
      form: {
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
      },
      loading: false,
      errorMessage: '',
    }
  },
  onReady() {
    this.$nextTick(() => {
      enhanceH5Inputs([
        {
          id: 'register-username',
          name: 'username',
          label: '注册账号',
          placeholder: '2–100 个字符',
          autocomplete: 'username',
        },
        {
          id: 'register-email',
          name: 'email',
          label: '注册邮箱，可选',
          placeholder: '用于账号联系',
          autocomplete: 'email',
        },
        {
          id: 'register-password',
          name: 'password',
          label: '注册密码',
          placeholder: '至少 12 位',
          autocomplete: 'new-password',
        },
        {
          id: 'register-confirm-password',
          name: 'confirmPassword',
          label: '确认注册密码',
          placeholder: '再次输入密码',
          autocomplete: 'new-password',
        },
      ])
    })
  },
  methods: {
    async submit() {
      if (this.loading) return
      this.errorMessage = ''
      if (this.form.username.length < 2) {
        this.errorMessage = '账号至少需要 2 个字符。'
        return
      }
      if (this.form.password.length < 12) {
        this.errorMessage = '密码至少需要 12 位。'
        return
      }
      if (this.form.password !== this.form.confirmPassword) {
        this.errorMessage = '两次输入的密码不一致。'
        return
      }
      this.loading = true
      try {
        await registerAccount(this.form)
        this.form.password = ''
        this.form.confirmPassword = ''
        uni.showToast({ title: '账号已创建', icon: 'success' })
        setTimeout(() => uni.navigateBack(), 600)
      } catch (error) {
        this.errorMessage = error.message || '账号创建失败。'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.register-page {
  padding-bottom: calc(56rpx + env(safe-area-inset-bottom));
}

.register-card {
  margin-top: 40rpx;
  padding: 8rpx 30rpx 34rpx;
}

.register-card__submit {
  width: 100%;
  margin-top: 34rpx;
}
</style>
