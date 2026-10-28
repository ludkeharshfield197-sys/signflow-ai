<template>
  <view class="topbar">
    <button v-if="back" class="topbar__back" aria-label="返回上一页" @tap="goBack">返回</button>
    <text v-else class="topbar__brand">SignFlow AI</text>
    <text v-if="title" class="topbar__title">{{ title }}</text>
    <view class="topbar__spacer"></view>
  </view>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      default: '',
    },
    back: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    goBack() {
      const pages = getCurrentPages()
      if (pages.length > 1) {
        uni.navigateBack()
      } else {
        uni.switchTab({ url: '/pages/home/home' })
      }
    },
  },
}
</script>

<style scoped>
.topbar {
  min-height: 76rpx;
  display: flex;
  align-items: center;
  gap: 18rpx;
  margin-bottom: 28rpx;
}

.topbar__brand {
  color: #5b5bd6;
  font-size: 32rpx;
  line-height: 1;
  font-weight: 760;
}

.topbar__title {
  flex: 1;
  color: #182230;
  font-size: 32rpx;
  line-height: 1;
  font-weight: 720;
  text-align: center;
}

.topbar__back {
  min-width: 92rpx;
  min-height: 64rpx;
  padding: 0;
  background: transparent;
  color: #475467;
  font-size: 27rpx;
  line-height: 64rpx;
  text-align: left;
}

.topbar__spacer {
  min-width: 92rpx;
}
</style>
