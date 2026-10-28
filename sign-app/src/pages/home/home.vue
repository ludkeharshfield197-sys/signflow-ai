<template>
  <view class="sf-page sf-page--tab" :class="sfAccessibilityClass">
    <SfTopBar />

    <view class="home-hero">
      <text class="sf-heading">今天想识别什么？</text>
      <text class="sf-subheading">拍照、选择视频或开启实时模式，结果会同步到同一账号。</text>
      <button class="sf-button sf-button--primary home-hero__action" @tap="openMode('image')">
        开始识别
      </button>
    </view>

    <view class="service sf-surface">
      <view class="service__state">
        <view class="sf-status-dot" :class="{ 'sf-status-dot--ready': serviceReady }"></view>
        <view>
          <text class="service__title">识别服务</text>
          <text class="service__detail">{{ serviceText }}</text>
        </view>
      </view>
      <button class="service__refresh" :disabled="loading" @tap="loadData">刷新</button>
    </view>

    <view class="home-section">
      <text class="sf-section-title">选择输入方式</text>
      <view class="mode-grid">
        <button class="mode-card" @tap="openMode('image')">
          <text class="mode-card__mark">01</text>
          <text class="mode-card__title">拍照</text>
          <text class="mode-card__desc">图片快速识别</text>
        </button>
        <button class="mode-card" @tap="openMode('video')">
          <text class="mode-card__mark">02</text>
          <text class="mode-card__title">视频</text>
          <text class="mode-card__desc">上传连续片段</text>
        </button>
        <button class="mode-card" @tap="openMode('live')">
          <text class="mode-card__mark">03</text>
          <text class="mode-card__title">实时</text>
          <text class="mode-card__desc">微信摄像头识别</text>
        </button>
      </view>
    </view>

    <view class="home-section">
      <view class="section-row">
        <text class="sf-section-title section-row__title">今日真实任务</text>
        <text class="section-row__source">来源：识别任务</text>
      </view>
      <view class="metrics sf-surface">
        <view class="metric">
          <text class="metric__value">{{ metrics.completed }}</text>
          <text class="metric__label">已完成</text>
        </view>
        <view class="metric metrics__middle">
          <text class="metric__value">{{ metrics.pending }}</text>
          <text class="metric__label">处理中</text>
        </view>
        <view class="metric">
          <text class="metric__value">{{ successRateText }}</text>
          <text class="metric__label">任务成功率</text>
        </view>
      </view>
    </view>

    <view class="home-section">
      <view class="section-row">
        <text class="sf-section-title section-row__title">最近结果</text>
        <button class="section-row__action" @tap="openResults">查看全部</button>
      </view>
      <view v-if="recentResults.length" class="recent-list sf-surface">
        <button
          v-for="item in recentResults"
          :key="item.id"
          class="recent-row"
          @tap="openResult(item.id)"
        >
          <view class="recent-row__mode">{{ modeLabel(item.mode) }}</view>
          <view class="recent-row__content">
            <text class="recent-row__title">{{ item.sentence || '未生成文本' }}</text>
            <text class="recent-row__meta">{{ item.model?.name || '识别模型' }} · {{ dateText(item.createdAt) }}</text>
          </view>
          <text class="recent-row__status">已完成</text>
        </button>
      </view>
      <view v-else class="empty sf-surface">
        <text class="empty__title">还没有真实识别结果</text>
        <text class="empty__desc">完成第一次拍照、视频或实时识别后会显示在这里。</text>
      </view>
    </view>

    <view v-if="errorMessage" class="sf-error">{{ errorMessage }}</view>
  </view>
</template>

<script>
import SfTopBar from '../../components/SfTopBar.vue'
import { getHealth, getOverview } from '../../services/product'

export default {
  components: { SfTopBar },
  data() {
    return {
      loading: false,
      serviceReady: false,
      serviceText: '正在检查',
      metrics: {
        completed: 0,
        pending: 0,
        successRate: 0,
      },
      recentResults: [],
      errorMessage: '',
    }
  },
  computed: {
    successRateText() {
      return `${Number(this.metrics.successRate || 0).toFixed(0)}%`
    },
  },
  onShow() {
    this.loadData()
  },
  onPullDownRefresh() {
    this.loadData().finally(() => uni.stopPullDownRefresh())
  },
  methods: {
    async loadData() {
      if (this.loading) return
      this.loading = true
      this.errorMessage = ''
      const healthPromise = getHealth()
        .then((health) => {
          this.serviceReady = health?.status === 'ready'
          this.serviceText = this.serviceReady ? '运行正常' : '部分依赖不可用'
        })
        .catch(() => {
          this.serviceReady = false
          this.serviceText = '当前无法连接'
        })
      try {
        const overview = await getOverview()
        this.metrics = overview.metrics || this.metrics
        this.recentResults = overview.recentResults || []
      } catch (error) {
        if (error.status === 401) {
          uni.reLaunch({ url: '/pages/login/login' })
          return
        }
        this.errorMessage = error.message || '暂时无法读取真实任务数据。'
      } finally {
        await healthPromise
        this.loading = false
      }
    },
    openMode(mode) {
      uni.setStorageSync('signflow.nextMode', mode)
      uni.switchTab({ url: '/pages/workbench/workbench' })
    },
    openResults() {
      uni.switchTab({ url: '/pages/results/results' })
    },
    openResult(id) {
      uni.navigateTo({ url: `/pages/result-detail/result-detail?id=${encodeURIComponent(id)}` })
    },
    modeLabel(mode) {
      return { image: '图片', video: '视频', live: '实时' }[mode] || '任务'
    },
    dateText(value) {
      if (!value) return '刚刚'
      const date = new Date(value)
      return `${String(date.getMonth() + 1).padStart(2, '0')}-${String(
        date.getDate(),
      ).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(
        date.getMinutes(),
      ).padStart(2, '0')}`
    },
  },
}
</script>

<style scoped>
.home-hero {
  padding: 12rpx 4rpx 4rpx;
}

.home-hero__action {
  width: 100%;
  margin-top: 34rpx;
}

.service {
  margin-top: 26rpx;
  padding: 22rpx 24rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
}

.service__state {
  display: flex;
  align-items: center;
  gap: 18rpx;
}

.service__title,
.service__detail {
  display: block;
}

.service__title {
  color: #344054;
  font-size: 27rpx;
  font-weight: 700;
}

.service__detail {
  margin-top: 4rpx;
  color: #667085;
  font-size: 23rpx;
}

.service__refresh,
.section-row__action {
  min-height: 60rpx;
  padding: 0 10rpx;
  background: transparent;
  color: #5b5bd6;
  font-size: 24rpx;
  line-height: 60rpx;
}

.home-section {
  margin-top: 38rpx;
}

.mode-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14rpx;
}

.mode-card {
  min-width: 0;
  min-height: 180rpx;
  padding: 22rpx 16rpx;
  border: 1rpx solid #e6eaf2;
  border-radius: 24rpx;
  background: #ffffff;
  text-align: left;
}

.mode-card:active {
  border-color: #a4a7ef;
  background: #f5f5ff;
}

.mode-card__mark,
.mode-card__title,
.mode-card__desc {
  display: block;
}

.mode-card__mark {
  color: #5b5bd6;
  font-size: 22rpx;
  font-weight: 750;
}

.mode-card__title {
  margin-top: 22rpx;
  color: #182230;
  font-size: 29rpx;
  font-weight: 720;
}

.mode-card__desc {
  margin-top: 6rpx;
  color: #667085;
  font-size: 21rpx;
  line-height: 1.35;
}

.section-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
}

.section-row__title {
  margin-bottom: 0;
}

.section-row__source {
  color: #98a2b3;
  font-size: 21rpx;
}

.metrics {
  margin-top: 18rpx;
  padding: 28rpx 12rpx;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.metric {
  min-width: 0;
  text-align: center;
}

.metrics__middle {
  border-right: 1rpx solid #eaecf0;
  border-left: 1rpx solid #eaecf0;
}

.metric__value,
.metric__label {
  display: block;
}

.metric__value {
  color: #182230;
  font-size: 38rpx;
  font-weight: 760;
}

.metric__label {
  margin-top: 8rpx;
  color: #667085;
  font-size: 22rpx;
}

.recent-list {
  margin-top: 18rpx;
  overflow: hidden;
}

.recent-row {
  width: 100%;
  min-height: 112rpx;
  padding: 20rpx 22rpx;
  display: flex;
  align-items: center;
  gap: 18rpx;
  border-bottom: 1rpx solid #eaecf0;
  border-radius: 0;
  background: #ffffff;
  text-align: left;
}

.recent-row:last-child {
  border-bottom: 0;
}

.recent-row__mode {
  min-width: 72rpx;
  padding: 8rpx 10rpx;
  border-radius: 12rpx;
  background: #f0f0ff;
  color: #5b5bd6;
  font-size: 21rpx;
  text-align: center;
}

.recent-row__content {
  flex: 1;
  min-width: 0;
}

.recent-row__title,
.recent-row__meta {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recent-row__title {
  color: #182230;
  font-size: 27rpx;
  font-weight: 650;
}

.recent-row__meta {
  margin-top: 7rpx;
  color: #667085;
  font-size: 21rpx;
}

.recent-row__status {
  color: #0e9384;
  font-size: 22rpx;
}

.empty {
  margin-top: 18rpx;
  padding: 46rpx 28rpx;
  text-align: center;
}

.empty__title,
.empty__desc {
  display: block;
}

.empty__title {
  color: #344054;
  font-size: 28rpx;
  font-weight: 680;
}

.empty__desc {
  margin-top: 12rpx;
  color: #667085;
  font-size: 23rpx;
  line-height: 1.55;
}
</style>
