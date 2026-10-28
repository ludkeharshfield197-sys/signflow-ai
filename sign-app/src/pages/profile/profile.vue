<template>
  <view class="sf-page sf-page--tab" :class="sfAccessibilityClass">
    <SfTopBar title="我的" />

    <view class="profile-card sf-surface">
      <view class="profile-card__avatar">{{ avatarLetter }}</view>
      <view class="profile-card__identity">
        <text class="profile-card__name">{{ user?.displayName || user?.username || 'SignFlow 用户' }}</text>
        <text class="profile-card__username">@{{ user?.username || 'unknown' }}</text>
      </view>
    </view>

    <view class="profile-section">
      <text class="sf-section-title">识别服务</text>
      <view class="server-card sf-surface">
        <label class="sf-label" for="profile-server-origin">服务地址</label>
        <input
          id="profile-server-origin"
          v-model.trim="serverOrigin"
          class="sf-input server-card__input"
          name="serverOrigin"
          type="text"
          placeholder="https://api.example.com"
          aria-label="识别服务地址"
        />
        <text class="server-card__help">
          正式微信小程序必须使用后台白名单内的 HTTPS/WSS 域名；同一 Wi-Fi 调试可使用电脑局域网 IP。
        </text>
        <button class="sf-button server-card__save" @tap="saveServer">保存服务地址</button>
      </view>
    </view>

    <view class="profile-section">
      <text class="sf-section-title">无障碍显示</text>
      <view class="accessibility-card sf-surface">
        <button
          class="accessibility-row"
          role="switch"
          :aria-checked="String(sfAccessibilityPreferences.largeText)"
          aria-label="切换大字模式"
          @tap="toggleAccessibility('largeText')"
        >
          <view>
            <text class="accessibility-row__title">大字模式</text>
            <text class="accessibility-row__help">放大说明文字和操作控件</text>
          </view>
          <text class="accessibility-row__state">
            {{ sfAccessibilityPreferences.largeText ? '已开启' : '已关闭' }}
          </text>
        </button>
        <button
          class="accessibility-row"
          role="switch"
          :aria-checked="String(sfAccessibilityPreferences.highContrast)"
          aria-label="切换高对比模式"
          @tap="toggleAccessibility('highContrast')"
        >
          <view>
            <text class="accessibility-row__title">高对比模式</text>
            <text class="accessibility-row__help">增强文字、边框与主操作对比度</text>
          </view>
          <text class="accessibility-row__state">
            {{ sfAccessibilityPreferences.highContrast ? '已开启' : '已关闭' }}
          </text>
        </button>
      </view>
    </view>

    <view class="profile-section">
      <text class="sf-section-title">隐私与数据</text>
      <view class="privacy-card sf-surface">
        <view class="privacy-row">
          <text class="privacy-row__title">用户素材</text>
          <text class="privacy-row__value">不进入训练集</text>
        </view>
        <view class="privacy-row">
          <text class="privacy-row__title">识别记录</text>
          <text class="privacy-row__value">仅账号本人可见，默认保留 30 天</text>
        </view>
        <view class="privacy-row">
          <text class="privacy-row__title">密码</text>
          <text class="privacy-row__value">不在手机保存</text>
        </view>
      </view>
    </view>

    <button class="sf-button sf-button--danger logout-button" :disabled="loggingOut" @tap="signOut">
      {{ loggingOut ? '正在退出…' : '退出登录' }}
    </button>
    <view v-if="errorMessage" class="sf-error">{{ errorMessage }}</view>
  </view>
</template>

<script>
import SfTopBar from '../../components/SfTopBar.vue'
import { enhanceH5Inputs } from '../../services/accessibility'
import { logout } from '../../services/auth'
import { getServerOrigin, normalizeServerOrigin, saveServerOrigin } from '../../services/config'
import { clearSession, getCurrentUser } from '../../services/session'

export default {
  components: { SfTopBar },
  data() {
    return {
      user: getCurrentUser(),
      serverOrigin: getServerOrigin(),
      loggingOut: false,
      errorMessage: '',
    }
  },
  computed: {
    avatarLetter() {
      return String(this.user?.displayName || this.user?.username || 'S')
        .slice(0, 1)
        .toUpperCase()
    },
  },
  onShow() {
    this.user = getCurrentUser()
    this.serverOrigin = getServerOrigin()
    this.applyInputAccessibility()
  },
  onReady() {
    this.applyInputAccessibility()
  },
  methods: {
    applyInputAccessibility() {
      this.$nextTick(() => {
        enhanceH5Inputs([
          {
            id: 'profile-server-origin',
            name: 'serverOrigin',
            label: '识别服务地址',
            placeholder: 'https://api.example.com',
          },
        ])
      })
    },
    toggleAccessibility(key) {
      this.sfSetAccessibilityPreferences({
        ...this.sfAccessibilityPreferences,
        [key]: !this.sfAccessibilityPreferences[key],
      })
    },
    saveServer() {
      this.errorMessage = ''
      try {
        const normalized = normalizeServerOrigin(this.serverOrigin)
        const changed = normalized !== getServerOrigin()
        this.serverOrigin = saveServerOrigin(normalized)
        if (changed) {
          clearSession()
          uni.showModal({
            title: '服务地址已更新',
            content: '为避免账号连接到错误的服务，需要重新登录。',
            showCancel: false,
            success: () => uni.reLaunch({ url: '/pages/login/login' }),
          })
        } else {
          uni.showToast({ title: '设置已保存', icon: 'success' })
        }
      } catch (error) {
        this.errorMessage = error.message
      }
    },
    async signOut() {
      if (this.loggingOut) return
      this.loggingOut = true
      try {
        await logout()
      } finally {
        this.loggingOut = false
        uni.reLaunch({ url: '/pages/login/login' })
      }
    },
  },
}
</script>

<style scoped>
.profile-card {
  padding: 30rpx;
  display: flex;
  align-items: center;
  gap: 24rpx;
}

.profile-card__avatar {
  width: 92rpx;
  height: 92rpx;
  border-radius: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #5b5bd6;
  color: #ffffff;
  font-size: 38rpx;
  font-weight: 760;
}

.profile-card__identity {
  flex: 1;
  min-width: 0;
}

.profile-card__name,
.profile-card__username {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.profile-card__name {
  color: #182230;
  font-size: 32rpx;
  font-weight: 720;
}

.profile-card__username {
  margin-top: 8rpx;
  color: #667085;
  font-size: 23rpx;
}

.profile-section {
  margin-top: 36rpx;
}

.server-card {
  padding: 28rpx;
}

.server-card__input {
  min-height: 82rpx;
  font-size: 24rpx;
}

.server-card__help {
  display: block;
  margin-top: 14rpx;
  color: #667085;
  font-size: 22rpx;
  line-height: 1.6;
}

.server-card__save {
  width: 100%;
  margin-top: 24rpx;
}

.privacy-card {
  overflow: hidden;
}

.accessibility-card {
  overflow: hidden;
}

.accessibility-row {
  width: 100%;
  min-height: 108rpx;
  padding: 20rpx 24rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
  border-bottom: 1rpx solid #eaecf0;
  border-radius: 0;
  background: #ffffff;
  text-align: left;
}

.accessibility-row:last-child {
  border-bottom: 0;
}

.accessibility-row__title,
.accessibility-row__help {
  display: block;
}

.accessibility-row__title {
  color: #344054;
  font-size: 26rpx;
  font-weight: 680;
}

.accessibility-row__help {
  margin-top: 6rpx;
  color: #667085;
  font-size: 22rpx;
}

.accessibility-row__state {
  flex: 0 0 auto;
  color: #5b5bd6;
  font-size: 23rpx;
  font-weight: 680;
}

.privacy-row {
  min-height: 84rpx;
  padding: 0 24rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
  border-bottom: 1rpx solid #eaecf0;
}

.privacy-row:last-child {
  border-bottom: 0;
}

.privacy-row__title {
  color: #344054;
  font-size: 25rpx;
}

.privacy-row__value {
  max-width: 62%;
  color: #0e9384;
  font-size: 23rpx;
  line-height: 1.45;
  text-align: right;
}

.logout-button {
  width: 100%;
  margin-top: 40rpx;
}
</style>
