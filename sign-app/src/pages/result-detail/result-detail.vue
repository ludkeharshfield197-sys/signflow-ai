<template>
  <view class="sf-page detail-page" :class="sfAccessibilityClass">
    <SfTopBar title="识别结果" back />

    <view v-if="loading" class="detail-loading sf-surface">
      <text>正在读取真实识别结果…</text>
    </view>

    <template v-else-if="result">
      <view class="detail-hero sf-surface">
        <view class="detail-hero__status">
          <view class="detail-hero__check"></view>
          <text>识别完成</text>
        </view>
        <text class="detail-hero__source">真实识别任务</text>
        <text class="detail-hero__sentence">{{ result.sentence || '未识别到标签' }}</text>
        <view class="detail-hero__confidence">
          <text>任务置信度</text>
          <text>{{ confidenceText(result.confidence) }}</text>
        </view>
      </view>

      <view class="detail-section">
        <text class="sf-section-title">授权原始媒体</text>
        <view class="media-card sf-surface">
          <video
            v-if="mediaPath && isVideo"
            class="media-card__content"
            :src="mediaPath"
            controls
            playsinline
            aria-label="任务所有者授权的原始手语视频"
          />
          <image
            v-else-if="mediaPath"
            class="media-card__content"
            :src="mediaPath"
            mode="aspectFit"
            alt="任务所有者授权的原始手语图片"
          />
          <view v-else class="media-card__empty">
            <text>{{ mediaLoading ? '正在安全读取媒体…' : '原始媒体已清理或当前不可读取' }}</text>
            <text>媒体仅向任务所有者提供，不会使用样例替代。</text>
          </view>
        </view>
      </view>

      <view class="detail-section">
        <text class="sf-section-title">识别标签</text>
        <view v-if="labels.length" class="label-list sf-surface">
          <view v-for="(label, index) in labels" :key="`${label.text}-${index}`" class="label-row">
            <view class="label-row__index">{{ String(index + 1).padStart(2, '0') }}</view>
            <text class="label-row__text">{{ label.text }}</text>
            <text class="label-row__confidence">{{ confidenceText(label.confidence) }}</text>
          </view>
        </view>
        <view v-else class="detail-empty sf-surface">本次任务没有返回可展示的标签。</view>
      </view>

      <view class="detail-section">
        <text class="sf-section-title">任务信息</text>
        <view class="metadata sf-surface">
          <view class="metadata__row">
            <text>输入类型</text>
            <text>{{ modeLabel(result.mode) }}</text>
          </view>
          <view class="metadata__row">
            <text>模型</text>
            <text>{{ result.model?.name || '—' }}</text>
          </view>
          <view class="metadata__row">
            <text>模型版本</text>
            <text>{{ result.model?.version || '—' }}</text>
          </view>
          <view class="metadata__row">
            <text>任务编号</text>
            <text class="metadata__id">{{ result.id }}</text>
          </view>
          <view class="metadata__row">
            <text>创建时间</text>
            <text>{{ dateText(result.createdAt) }}</text>
          </view>
          <view class="metadata__row">
            <text>数据性质</text>
            <text class="metadata__real">真实任务</text>
          </view>
          <view class="metadata__row">
            <text>结果版本</text>
            <text>第 {{ result.revision || 1 }} 版</text>
          </view>
          <view class="metadata__row">
            <text>确认状态</text>
            <text class="metadata__real">{{ result.confirmation?.label || '待确认' }}</text>
          </view>
          <view class="metadata__row metadata__row--stack">
            <text>文件 SHA-256</text>
            <text class="metadata__hash">{{ result.trace?.fileSha256 || '历史任务未记录' }}</text>
          </view>
          <view class="metadata__row">
            <text>识别参数</text>
            <text>conf {{ result.trace?.parameters?.confidence ?? '—' }} / IoU {{ result.trace?.parameters?.iou ?? '—' }}</text>
          </view>
        </view>
      </view>

      <view v-if="versions.length" class="detail-section">
        <text class="sf-section-title">结果版本对比</text>
        <view class="version-list sf-surface">
          <button
            v-for="version in versions"
            :key="version.id"
            class="version-row"
            :class="{ 'version-row--active': version.id === result.id }"
            :aria-label="`查看第 ${version.revision || 1} 版识别结果`"
            @tap="openVersion(version.id)"
          >
            <text class="version-row__number">第 {{ version.revision || 1 }} 版</text>
            <text class="version-row__sentence">{{ version.sentence || statusText(version.status) }}</text>
            <text class="version-row__meta">{{ version.model?.version || '—' }} · {{ confidenceText(version.confidence) }}</text>
          </button>
        </view>
      </view>

      <view class="detail-actions">
        <button class="sf-button" @tap="copySummary">复制识别文本</button>
        <button
          class="sf-button"
          :disabled="confirming || isConfirmed || result.status !== 'succeeded'"
          @tap="confirmRecognition"
        >
          {{ isConfirmed ? '双方已确认' : confirming ? '正在确认…' : '确认结果' }}
        </button>
        <button
          class="sf-button"
          :disabled="rerunning || result.status !== 'succeeded'"
          @tap="createRevision"
        >
          {{ rerunning ? '正在创建…' : '重新识别' }}
        </button>
        <button class="sf-button sf-button--primary" @tap="saveResult">保存结果</button>
      </view>
    </template>

    <view v-if="errorMessage" class="sf-error">{{ errorMessage }}</view>
  </view>
</template>

<script>
import SfTopBar from '../../components/SfTopBar.vue'
import { confidencePercent, saveDetectionJob } from '../../services/detections'
import {
  confirmResult,
  getResult,
  getResultMedia,
  getResultVersions,
  rerunResult,
} from '../../services/product'

export default {
  components: { SfTopBar },
  data() {
    return {
      resultId: '',
      result: null,
      loading: true,
      errorMessage: '',
      mediaPath: '',
      mediaLoading: false,
      versions: [],
      confirming: false,
      rerunning: false,
    }
  },
  computed: {
    labels() {
      return (this.result?.labels || []).map((item) =>
        typeof item === 'string'
          ? { text: item, confidence: this.result?.confidence }
          : item,
      )
    },
    isVideo() {
      return this.result?.media?.contentType?.startsWith('video/')
    },
    isConfirmed() {
      return this.result?.confirmation?.status === 'both_confirmed'
    },
  },
  onLoad(options) {
    this.resultId = options.id || ''
    this.loadResult()
  },
  methods: {
    async loadResult() {
      if (!this.resultId) {
        this.loading = false
        this.errorMessage = '识别结果编号无效。'
        return
      }
      try {
        this.result = await getResult(this.resultId)
        await Promise.all([this.loadMedia(), this.loadVersions()])
      } catch (error) {
        if (error.status === 401) {
          uni.reLaunch({ url: '/pages/login/login' })
          return
        }
        this.errorMessage = error.message || '无法读取识别结果。'
      } finally {
        this.loading = false
      }
    },
    async loadMedia() {
      if (!this.result?.media?.available) return
      this.mediaLoading = true
      try {
        this.mediaPath = await getResultMedia(this.resultId)
      } catch {
        this.mediaPath = ''
      } finally {
        this.mediaLoading = false
      }
    },
    async loadVersions() {
      try {
        const payload = await getResultVersions(this.resultId)
        this.versions = payload?.items || []
      } catch {
        this.versions = this.result ? [this.result] : []
      }
    },
    async confirmRecognition() {
      if (this.confirming || this.isConfirmed) return
      this.confirming = true
      try {
        this.result = await confirmResult(this.resultId)
        await this.loadVersions()
        uni.showToast({ title: '双方已确认', icon: 'success' })
      } catch (error) {
        this.errorMessage = error.message || '确认状态保存失败。'
      } finally {
        this.confirming = false
      }
    },
    async createRevision() {
      if (this.rerunning) return
      this.rerunning = true
      try {
        const replacement = await rerunResult(this.resultId)
        uni.redirectTo({
          url: `/pages/result-detail/result-detail?id=${encodeURIComponent(replacement.id)}`,
        })
      } catch (error) {
        this.errorMessage = error.message || '无法使用原始媒体重新识别。'
      } finally {
        this.rerunning = false
      }
    },
    openVersion(resultId) {
      if (resultId === this.resultId) return
      uni.redirectTo({
        url: `/pages/result-detail/result-detail?id=${encodeURIComponent(resultId)}`,
      })
    },
    async saveResult() {
      try {
        await saveDetectionJob(this.resultId)
        uni.showToast({ title: '结果已保存', icon: 'success' })
      } catch (error) {
        this.errorMessage = error.message || '保存结果失败。'
      }
    },
    copySummary() {
      const text = this.result?.sentence || this.labels.map((item) => item.text).join(' ')
      if (!text) return
      uni.setClipboardData({
        data: text,
        success: () => uni.showToast({ title: '已复制', icon: 'success' }),
      })
    },
    confidenceText(value) {
      return confidencePercent(value)
    },
    modeLabel(mode) {
      return { image: '图片', video: '视频', live: '实时摄像头' }[mode] || mode
    },
    statusText(status) {
      return {
        queued: '等待识别',
        running: '正在识别',
        failed: '识别失败',
        timed_out: '识别超时',
      }[status] || '暂无识别文本'
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
.detail-page {
  padding-bottom: calc(56rpx + env(safe-area-inset-bottom));
}

.detail-loading {
  padding: 80rpx 28rpx;
  color: #667085;
  text-align: center;
}

.detail-hero {
  padding: 32rpx 30rpx;
}

.detail-hero__status {
  display: flex;
  align-items: center;
  gap: 14rpx;
  color: #067647;
  font-size: 27rpx;
  font-weight: 700;
}

.detail-hero__check {
  width: 24rpx;
  height: 24rpx;
  border: 5rpx solid #0e9384;
  border-radius: 50%;
}

.detail-hero__source {
  display: block;
  margin-top: 24rpx;
  color: #667085;
  font-size: 23rpx;
}

.detail-hero__sentence {
  display: block;
  margin-top: 14rpx;
  color: #182230;
  font-size: 52rpx;
  line-height: 1.25;
  font-weight: 770;
}

.detail-hero__confidence {
  margin-top: 28rpx;
  padding-top: 22rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1rpx solid #eaecf0;
  color: #667085;
  font-size: 25rpx;
}

.detail-hero__confidence text:last-child {
  color: #0e9384;
  font-size: 29rpx;
  font-weight: 720;
}

.detail-section {
  margin-top: 34rpx;
}

.media-card {
  overflow: hidden;
}

.media-card__content {
  width: 100%;
  height: 420rpx;
  display: block;
  background: #0d1424;
}

.media-card__empty {
  min-height: 220rpx;
  padding: 36rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 12rpx;
  color: #667085;
  font-size: 24rpx;
  line-height: 1.55;
  text-align: center;
}

.label-list,
.metadata {
  overflow: hidden;
}

.label-row,
.metadata__row {
  min-height: 84rpx;
  padding: 0 24rpx;
  display: flex;
  align-items: center;
  gap: 18rpx;
  border-bottom: 1rpx solid #eaecf0;
}

.label-row:last-child,
.metadata__row:last-child {
  border-bottom: 0;
}

.label-row__index {
  min-width: 52rpx;
  color: #5b5bd6;
  font-size: 22rpx;
  font-weight: 720;
}

.label-row__text {
  flex: 1;
  color: #344054;
  font-size: 28rpx;
  font-weight: 650;
}

.label-row__confidence {
  color: #667085;
  font-size: 24rpx;
}

.metadata__row {
  justify-content: space-between;
  color: #667085;
  font-size: 24rpx;
}

.metadata__row text:last-child {
  max-width: 68%;
  color: #344054;
  text-align: right;
}

.metadata__row .metadata__id {
  overflow: hidden;
  font-family: monospace;
  font-size: 20rpx;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.metadata__row .metadata__real {
  color: #067647;
}

.metadata__row--stack {
  padding-block: 20rpx;
  align-items: flex-start;
  flex-direction: column;
}

.metadata__row .metadata__hash {
  max-width: 100%;
  overflow-wrap: anywhere;
  font-family: monospace;
  font-size: 20rpx;
  line-height: 1.5;
  text-align: left;
}

.version-list {
  padding: 16rpx;
}

.version-row {
  width: 100%;
  min-height: 112rpx;
  padding: 20rpx;
  display: grid;
  grid-template-columns: 120rpx 1fr;
  gap: 8rpx 16rpx;
  border: 1rpx solid #e6eaf2;
  border-radius: 18rpx;
  background: #ffffff;
  text-align: left;
}

.version-row + .version-row {
  margin-top: 12rpx;
}

.version-row--active {
  border-color: #5b5bd6;
  background: #f5f5ff;
}

.version-row__number {
  grid-row: 1 / 3;
  align-self: center;
  color: #5b5bd6;
  font-size: 23rpx;
  font-weight: 720;
}

.version-row__sentence {
  overflow: hidden;
  color: #182230;
  font-size: 27rpx;
  font-weight: 680;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.version-row__meta {
  color: #667085;
  font-size: 21rpx;
}

.detail-empty {
  padding: 38rpx 24rpx;
  color: #667085;
  font-size: 24rpx;
  text-align: center;
}

.detail-actions {
  margin-top: 32rpx;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14rpx;
}
</style>
