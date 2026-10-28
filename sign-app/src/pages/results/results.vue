<template>
  <view class="sf-page sf-page--tab" :class="sfAccessibilityClass">
    <SfTopBar title="结果中心" />

    <view class="filter-row">
      <button
        v-for="item in filters"
        :key="item.value"
        class="filter"
        :class="{ 'filter--active': mode === item.value }"
        @tap="changeMode(item.value)"
      >
        {{ item.label }}
      </button>
    </view>

    <view v-if="loading && !items.length" class="loading-state sf-surface">
      <view class="loading-state__bar"></view>
      <view class="loading-state__bar loading-state__bar--short"></view>
      <text class="loading-state__text">正在读取真实任务记录</text>
    </view>

    <view v-else-if="items.length" class="result-list">
      <button
        v-for="item in items"
        :key="item.id"
        class="result-row sf-surface"
        @tap="openResult(item.id)"
      >
        <view class="result-row__top">
          <text class="result-row__mode">{{ modeLabel(item.mode) }}</text>
          <text class="result-row__status" :class="`result-row__status--${item.status}`">
            {{ statusLabel(item.status) }}
          </text>
        </view>
        <text class="result-row__sentence">{{ item.sentence || '未生成识别文本' }}</text>
        <view class="result-row__meta">
          <text>{{ item.model?.name || '识别模型' }} · {{ item.model?.version || '—' }}</text>
          <text>{{ dateText(item.createdAt) }}</text>
        </view>
        <view v-if="item.status === 'succeeded'" class="result-row__confidence">
          <text>任务置信度</text>
          <text>{{ confidenceText(item.confidence) }}</text>
        </view>
      </button>
    </view>

    <view v-else class="empty sf-surface">
      <text class="empty__title">暂无{{ selectedFilterLabel }}记录</text>
      <text class="empty__desc">识别完成后，真实任务会按账号安全地保存在这里。</text>
      <button class="sf-button sf-button--primary empty__action" @tap="startRecognition">
        开始识别
      </button>
    </view>

    <view v-if="errorMessage" class="sf-error">{{ errorMessage }}</view>
  </view>
</template>

<script>
import SfTopBar from '../../components/SfTopBar.vue'
import { confidencePercent } from '../../services/detections'
import { getResults } from '../../services/product'

export default {
  components: { SfTopBar },
  data() {
    return {
      filters: [
        { value: 'all', label: '全部' },
        { value: 'image', label: '图片' },
        { value: 'video', label: '视频' },
        { value: 'live', label: '实时' },
      ],
      mode: 'all',
      items: [],
      loading: false,
      errorMessage: '',
    }
  },
  computed: {
    selectedFilterLabel() {
      return this.filters.find((item) => item.value === this.mode)?.label || ''
    },
  },
  onShow() {
    this.loadResults()
  },
  onPullDownRefresh() {
    this.loadResults().finally(() => uni.stopPullDownRefresh())
  },
  methods: {
    async loadResults() {
      if (this.loading) return
      this.loading = true
      this.errorMessage = ''
      try {
        const data = await getResults({ mode: this.mode, pageSize: 50 })
        this.items = data.items || []
      } catch (error) {
        if (error.status === 401) {
          uni.reLaunch({ url: '/pages/login/login' })
          return
        }
        this.errorMessage = error.message || '无法读取结果记录。'
      } finally {
        this.loading = false
      }
    },
    changeMode(mode) {
      if (this.mode === mode) return
      this.mode = mode
      this.loadResults()
    },
    openResult(id) {
      uni.navigateTo({ url: `/pages/result-detail/result-detail?id=${encodeURIComponent(id)}` })
    },
    startRecognition() {
      uni.switchTab({ url: '/pages/workbench/workbench' })
    },
    modeLabel(mode) {
      return { image: '图片', video: '视频', live: '实时' }[mode] || '任务'
    },
    statusLabel(status) {
      return {
        queued: '排队中',
        running: '处理中',
        succeeded: '已完成',
        failed: '失败',
        timed_out: '超时',
        cancelled: '已取消',
        cancel_requested: '取消中',
      }[status] || status
    },
    confidenceText(value) {
      return confidencePercent(value)
    },
    dateText(value) {
      if (!value) return '—'
      const date = new Date(value)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(
        date.getDate(),
      ).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(
        date.getMinutes(),
      ).padStart(2, '0')}`
    },
  },
}
</script>

<style scoped>
.filter-row {
  padding: 8rpx;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 6rpx;
  border: 1rpx solid #e6eaf2;
  border-radius: 20rpx;
  background: #ffffff;
}

.filter {
  min-height: 66rpx;
  border-radius: 14rpx;
  background: transparent;
  color: #667085;
  font-size: 24rpx;
  line-height: 66rpx;
}

.filter--active {
  background: #f0f0ff;
  color: #4f4fc9;
  font-weight: 680;
}

.result-list {
  margin-top: 22rpx;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.result-row {
  width: 100%;
  padding: 24rpx;
  background: #ffffff;
  text-align: left;
}

.result-row__top,
.result-row__meta,
.result-row__confidence {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
}

.result-row__mode {
  padding: 7rpx 12rpx;
  border-radius: 12rpx;
  background: #f0f0ff;
  color: #5b5bd6;
  font-size: 21rpx;
}

.result-row__status {
  color: #667085;
  font-size: 22rpx;
}

.result-row__status--succeeded {
  color: #067647;
}

.result-row__status--failed,
.result-row__status--timed_out {
  color: #b42318;
}

.result-row__sentence {
  display: block;
  margin-top: 22rpx;
  overflow: hidden;
  color: #182230;
  font-size: 33rpx;
  line-height: 1.35;
  font-weight: 710;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-row__meta {
  margin-top: 16rpx;
  color: #667085;
  font-size: 21rpx;
}

.result-row__confidence {
  margin-top: 20rpx;
  padding-top: 18rpx;
  border-top: 1rpx solid #eaecf0;
  color: #667085;
  font-size: 22rpx;
}

.result-row__confidence text:last-child {
  color: #0e9384;
  font-weight: 700;
}

.loading-state,
.empty {
  margin-top: 24rpx;
  padding: 48rpx 30rpx;
  text-align: center;
}

.loading-state__bar {
  height: 22rpx;
  border-radius: 999rpx;
  background: #eaecf0;
}

.loading-state__bar--short {
  width: 62%;
  margin-top: 16rpx;
}

.loading-state__text {
  display: block;
  margin-top: 28rpx;
  color: #667085;
  font-size: 24rpx;
}

.empty__title,
.empty__desc {
  display: block;
}

.empty__title {
  color: #344054;
  font-size: 31rpx;
  font-weight: 700;
}

.empty__desc {
  margin-top: 14rpx;
  color: #667085;
  font-size: 24rpx;
  line-height: 1.6;
}

.empty__action {
  margin-top: 30rpx;
}
</style>
