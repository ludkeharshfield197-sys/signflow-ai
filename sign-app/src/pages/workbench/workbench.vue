<template>
  <view class="sf-page sf-page--tab" :class="sfAccessibilityClass">
    <SfTopBar title="识别工作台" />

    <view class="mode-tabs" role="tablist">
      <button
        v-for="item in modes"
        :key="item.value"
        class="mode-tab"
        :class="{ 'mode-tab--active': mode === item.value }"
        :disabled="processing"
        role="tab"
        :aria-selected="String(mode === item.value)"
        :aria-label="`${item.label}识别模式`"
        @tap="selectMode(item.value)"
      >
        {{ item.label }}
      </button>
    </view>

    <view class="preview sf-surface">
      <image
        v-if="mode === 'image' && sourcePath"
        class="preview__media"
        :src="sourcePath"
        mode="aspectFit"
        :alt="sourceName || '待识别手语图片'"
      />
      <video
        v-else-if="mode === 'video' && sourcePath"
        class="preview__media"
        :src="sourcePath"
        controls
        object-fit="contain"
        :aria-label="sourceName || '待识别手语视频'"
      />

      <!-- #ifdef MP-WEIXIN -->
      <camera
        v-else-if="mode === 'live' && cameraActive"
        id="signflow-camera"
        class="preview__media"
        device-position="front"
        flash="off"
        resolution="medium"
        aria-label="实时手语采集摄像头"
        @error="handleCameraError"
      />
      <!-- #endif -->

      <view v-else class="preview__empty">
        <text class="preview__eyebrow">{{ emptyEyebrow }}</text>
        <text class="preview__title">{{ emptyTitle }}</text>
        <text class="preview__desc">{{ emptyDescription }}</text>
        <button
          v-if="mode !== 'live'"
          class="sf-button preview__choose"
          :disabled="processing"
          @tap="chooseSource"
        >
          {{ mode === 'image' ? '拍照或选择图片' : '选择视频文件' }}
        </button>
        <button
          v-else
          class="sf-button preview__choose"
          :disabled="processing"
          @tap="prepareLive"
        >
          检查实时识别
        </button>
      </view>

      <view v-if="sourcePath && !processing && mode !== 'live'" class="preview__toolbar">
        <text class="preview__filename">{{ sourceName }}</text>
        <button class="preview__replace" @tap="chooseSource">重新选择</button>
      </view>
      <view v-if="processing" class="preview__overlay">
        <view class="preview__spinner"></view>
        <text class="preview__processing">{{ stageLabel }}</text>
      </view>
    </view>

    <view
      v-if="processing || state === 'succeeded'"
      class="progress-card sf-surface"
      role="progressbar"
      aria-label="识别任务进度"
      aria-valuemin="0"
      aria-valuemax="100"
      :aria-valuenow="String(progress)"
    >
      <view class="progress-card__header">
        <text class="progress-card__title">{{
          state === 'succeeded' ? '识别完成' : '任务进度'
        }}</text>
        <text class="progress-card__value">{{ progress }}%</text>
      </view>
      <view class="progress-track">
        <view class="progress-track__bar" :style="{ width: `${progress}%` }"></view>
      </view>
      <view class="steps">
        <view v-for="step in progressSteps" :key="step.label" class="step">
          <view class="step__dot" :class="{ 'step__dot--active': progress >= step.at }"></view>
          <text class="step__label">{{ step.label }}</text>
        </view>
      </view>
    </view>

    <view v-if="state === 'succeeded' && result" class="result-card sf-surface">
      <view class="result-card__header">
        <text class="result-card__title">真实识别结果</text>
        <text class="result-card__kind">真实任务</text>
      </view>
      <text class="result-card__sentence">{{ resultSentence }}</text>
      <view class="result-card__meta">
        <text>任务置信度</text>
        <text class="result-card__confidence">{{ resultConfidence }}</text>
      </view>
      <view v-if="resultLabels.length" class="labels">
        <view v-for="(label, index) in resultLabels" :key="`${label.text}-${index}`" class="label-row">
          <text class="label-row__text">{{ label.text }}</text>
          <text class="label-row__confidence">{{ labelConfidence(label) }}</text>
        </view>
      </view>
      <view class="result-card__actions">
        <button class="sf-button" @tap="saveResult">保存结果</button>
        <button class="sf-button sf-button--primary" @tap="openResult">查看详情</button>
      </view>
    </view>

    <view class="settings sf-surface">
      <button class="settings__summary" @tap="settingsOpen = !settingsOpen">
        <view>
          <text class="settings__title">输入与模型</text>
          <text class="settings__desc">{{ selectedModelText }}</text>
        </view>
        <text class="settings__action">{{ settingsOpen ? '收起' : '设置' }}</text>
      </button>
      <view v-if="settingsOpen" class="settings__body">
        <text class="sf-label">模型</text>
        <picker
          :range="modelNames"
          :value="selectedModelIndex"
          :disabled="processing"
          aria-label="选择手语识别模型"
          @change="changeModel"
        >
          <view class="picker-field">{{ selectedModelText }}</view>
        </picker>

        <text class="sf-label settings__next-label">识别预设</text>
        <view class="preset-row">
          <button
            v-for="item in presets"
            :key="item.value"
            class="preset"
            :class="{ 'preset--active': preset === item.value }"
            :disabled="processing"
            @tap="preset = item.value"
          >
            {{ item.label }}
          </button>
        </view>

        <view class="slider-row">
          <view class="slider-row__label">
            <text>置信度阈值</text>
            <text>{{ confidence.toFixed(2) }}</text>
          </view>
          <slider
            :value="confidence * 100"
            min="5"
            max="95"
            step="5"
            active-color="#5B5BD6"
            background-color="#E6EAF2"
            :disabled="processing"
            aria-label="置信度阈值"
            @change="confidence = $event.detail.value / 100"
          />
        </view>
        <view class="slider-row">
          <view class="slider-row__label">
            <text>IoU 阈值</text>
            <text>{{ iou.toFixed(2) }}</text>
          </view>
          <slider
            :value="iou * 100"
            min="5"
            max="95"
            step="5"
            active-color="#5B5BD6"
            background-color="#E6EAF2"
            :disabled="processing"
            aria-label="IoU 阈值"
            @change="iou = $event.detail.value / 100"
          />
        </view>
      </view>
    </view>

    <view v-if="errorMessage" class="sf-error">{{ errorMessage }}</view>

    <view class="action-bar">
      <button
        v-if="processing"
        class="sf-button sf-button--danger action-bar__button"
        @tap="cancelCurrentTask"
      >
        取消任务
      </button>
      <button
        v-else
        class="sf-button sf-button--primary action-bar__button"
        :disabled="!canStart"
        @tap="startRecognition"
      >
        {{ startButtonText }}
      </button>
    </view>
  </view>
</template>

<script>
import SfTopBar from '../../components/SfTopBar.vue'
import { createCameraConnectionOptions } from '../../services/camera'
import {
  cancelDetectionJob,
  confidencePercent,
  createDetectionJob,
  pollDetectionJob,
  saveDetectionJob,
} from '../../services/detections'
import { getModels } from '../../services/product'

function supportsMiniProgramCamera() {
  let supported = false
  // #ifdef MP-WEIXIN
  supported = true
  // #endif
  return supported
}

export default {
  components: { SfTopBar },
  data() {
    return {
      modes: [
        { value: 'image', label: '图片' },
        { value: 'video', label: '视频' },
        { value: 'live', label: '实时' },
      ],
      presets: [
        { value: 'fast', label: '低延迟' },
        { value: 'balanced', label: '标准' },
        { value: 'precise', label: '高精度' },
      ],
      progressSteps: [
        { label: '安全上传', at: 15 },
        { label: '模型推理', at: 45 },
        { label: '生成结果', at: 90 },
      ],
      mode: 'image',
      sourcePath: '',
      sourceName: '',
      sourceSize: 0,
      models: [],
      modelId: null,
      preset: 'balanced',
      confidence: 0.45,
      iou: 0.5,
      settingsOpen: false,
      state: 'idle',
      stageLabel: '准备任务',
      progress: 0,
      jobId: '',
      result: null,
      errorMessage: '',
      pollSignal: null,
      cameraSupported: supportsMiniProgramCamera(),
      cameraActive: false,
      cameraContext: null,
      socketTask: null,
      liveFrames: 0,
      liveFramePending: false,
      liveCaptureTimer: null,
      liveFinalized: false,
    }
  },
  computed: {
    processing() {
      return ['uploading', 'queued', 'running', 'live'].includes(this.state)
    },
    canStart() {
      if (!this.modelId || this.processing) return false
      if (this.mode === 'live') return this.cameraSupported
      return Boolean(this.sourcePath)
    },
    startButtonText() {
      if (this.mode === 'live') return '开始实时识别'
      if (this.state === 'succeeded') return '重新识别'
      return '开始真实识别'
    },
    emptyEyebrow() {
      return { image: '图片输入', video: '视频输入', live: '实时输入' }[this.mode]
    },
    emptyTitle() {
      if (this.mode === 'image') return '拍摄或选择一张手语图片'
      if (this.mode === 'video') return '选择一段清晰的手语视频'
      return this.cameraSupported ? '使用前置摄像头采集 6 帧' : '实时模式需在微信小程序中使用'
    },
    emptyDescription() {
      if (this.mode === 'live' && !this.cameraSupported) {
        return 'H5 可以使用图片和视频识别；微信开发者工具或真机支持实时摄像头。'
      }
      return '画面仅用于本次识别，不会自动进入训练集。'
    },
    modelNames() {
      return this.models.map((item) => `${item.name} · ${item.version}`)
    },
    selectedModelIndex() {
      return Math.max(
        this.models.findIndex((item) => item.id === this.modelId),
        0,
      )
    },
    selectedModel() {
      return this.models.find((item) => item.id === this.modelId) || null
    },
    selectedModelText() {
      const model = this.selectedModel
      return model ? `${model.name} · ${model.version}` : '正在读取可用模型'
    },
    resultSentence() {
      return this.result?.sentence || this.resultLabels.map((item) => item.text).join(' ') || '未识别到标签'
    },
    resultLabels() {
      const labels = this.result?.labels || []
      return labels.map((item) =>
        typeof item === 'string'
          ? { text: item, confidence: this.result?.confidence }
          : item,
      )
    },
    resultConfidence() {
      return confidencePercent(this.result?.confidence)
    },
  },
  onShow() {
    const nextMode = uni.getStorageSync('signflow.nextMode')
    if (['image', 'video', 'live'].includes(nextMode) && !this.processing) {
      this.mode = nextMode
      uni.removeStorageSync('signflow.nextMode')
    }
    if (!this.models.length) this.loadModels()
  },
  onHide() {
    if (this.state === 'live') this.cancelLiveSession(false)
  },
  onUnload() {
    this.dispose()
  },
  methods: {
    async loadModels() {
      this.errorMessage = ''
      try {
        this.models = (await getModels()).filter((model) => model.status === 'active')
        if (this.models.length && !this.modelId) this.modelId = this.models[0].id
        if (!this.models.length) this.errorMessage = '当前没有可用的识别模型。'
      } catch (error) {
        if (error.status === 401) {
          uni.reLaunch({ url: '/pages/login/login' })
          return
        }
        this.errorMessage = error.message || '无法读取模型目录。'
      }
    },
    selectMode(mode) {
      if (this.processing || this.mode === mode) return
      this.mode = mode
      this.resetTask()
    },
    chooseSource() {
      if (this.processing) return
      if (this.mode === 'image') {
        uni.chooseImage({
          count: 1,
          sizeType: ['compressed'],
          sourceType: ['album', 'camera'],
          success: (response) => {
            const file = response.tempFiles?.[0]
            this.sourcePath = file?.path || response.tempFilePaths?.[0] || ''
            this.sourceSize = file?.size || 0
            this.sourceName = this.filenameFromPath(this.sourcePath, '手语图片.jpg')
            this.resetTask(false)
          },
        })
        return
      }
      uni.chooseVideo({
        sourceType: ['album', 'camera'],
        compressed: true,
        maxDuration: 60,
        success: (response) => {
          this.sourcePath = response.tempFilePath || ''
          this.sourceSize = response.size || 0
          this.sourceName = this.filenameFromPath(this.sourcePath, '手语视频.mp4')
          this.resetTask(false)
        },
      })
    },
    filenameFromPath(path, fallback) {
      const filename = String(path || '').split(/[\\/]/).pop()
      if (!filename || /^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/i.test(filename)) {
        return fallback
      }
      return filename
    },
    prepareLive() {
      if (!this.cameraSupported) {
        uni.showModal({
          title: '请使用微信小程序',
          content: '实时模式需要微信摄像头能力。当前环境仍可使用真实图片和视频识别。',
          showCancel: false,
        })
        return
      }
      this.cameraActive = true
      this.errorMessage = ''
    },
    async startRecognition() {
      if (!this.canStart) return
      if (this.mode === 'live') {
        await this.startLiveSession()
        return
      }
      await this.startUploadTask()
    },
    async startUploadTask() {
      this.resetTask(false)
      this.state = 'uploading'
      this.stageLabel = '正在安全上传'
      this.progress = 5
      this.errorMessage = ''
      this.pollSignal = { cancelled: false }
      try {
        const job = await createDetectionJob(
          {
            filePath: this.sourcePath,
            mode: this.mode,
            modelId: this.modelId,
            preset: this.preset,
            iou: this.iou,
            confidence: this.confidence,
          },
          (value) => {
            this.progress = Math.min(Math.max(Math.round(value * 0.35), 5), 35)
          },
        )
        this.jobId = job.id
        this.applyJob(job)
        const finalJob = await pollDetectionJob(job.id, {
          signal: this.pollSignal,
          onUpdate: this.applyJob,
        })
        this.applyJob(finalJob)
      } catch (error) {
        if (this.pollSignal?.cancelled) return
        this.state = 'failed'
        this.progress = 0
        this.errorMessage = error.message || '识别任务失败，请稍后重试。'
      }
    },
    applyJob(job) {
      this.jobId = job.id || this.jobId
      this.state = job.status
      this.stageLabel = job.stageLabel || '模型推理中'
      this.progress = job.status === 'succeeded' ? 100 : Math.max(Number(job.progress || 0), 36)
      if (job.status === 'succeeded') {
        this.result = job.result || {}
      } else if (['failed', 'timed_out', 'cancelled'].includes(job.status)) {
        this.errorMessage = job.errorMessage || '任务未完成，请重新尝试。'
      }
    },
    async cancelCurrentTask() {
      if (this.mode === 'live') {
        this.cancelLiveSession(true)
        return
      }
      if (this.pollSignal) this.pollSignal.cancelled = true
      try {
        if (this.jobId) await cancelDetectionJob(this.jobId)
      } catch {
        // The UI still leaves the processing state; the server retains the
        // authoritative result and it remains visible in the results center.
      }
      this.state = 'cancelled'
      this.stageLabel = '任务已取消'
      this.progress = 0
    },
    async saveResult() {
      if (!this.jobId) return
      try {
        await saveDetectionJob(this.jobId)
        uni.showToast({ title: '结果已保存', icon: 'success' })
      } catch (error) {
        this.errorMessage = error.message || '保存结果失败。'
      }
    },
    openResult() {
      if (!this.jobId) return
      uni.navigateTo({
        url: `/pages/result-detail/result-detail?id=${encodeURIComponent(this.jobId)}`,
      })
    },
    changeModel(event) {
      const model = this.models[Number(event.detail.value)]
      if (model) this.modelId = model.id
    },
    labelConfidence(label) {
      return confidencePercent(label?.confidence)
    },
    async startLiveSession() {
      if (!this.cameraSupported || this.state === 'live') return
      this.resetTask(false)
      this.cameraActive = true
      this.state = 'live'
      this.stageLabel = '申请一次性识别票据'
      this.progress = 4
      this.liveFrames = 0
      this.liveFinalized = false
      this.errorMessage = ''
      await this.$nextTick()
      this.cameraContext = uni.createCameraContext()
      try {
        const options = await createCameraConnectionOptions({
          modelId: this.modelId,
          confidence: this.confidence,
          iou: this.iou,
        })
        this.socketTask = uni.connectSocket({ url: options.url })
        this.bindSocketEvents()
      } catch (error) {
        this.state = 'failed'
        this.cameraActive = false
        this.errorMessage = error.message || '实时识别连接失败。'
      }
    },
    bindSocketEvents() {
      const socket = this.socketTask
      socket.onOpen(() => {
        this.stageLabel = '正在建立安全会话'
        this.progress = 8
      })
      socket.onMessage((event) => {
        let payload
        try {
          payload = JSON.parse(event.data)
        } catch {
          this.failLive('实时服务返回了无法解析的数据。')
          return
        }
        this.handleSocketMessage(payload)
      })
      socket.onError(() => this.failLive('实时连接中断，请检查网络后重试。'))
      socket.onClose((event) => {
        if (!this.liveFinalized && this.state === 'live' && event.code !== 1000) {
          this.failLive(`实时会话已关闭（${event.code || 0}）。`)
        }
      })
    },
    handleSocketMessage(payload) {
      if (payload.type === 'session.ready') {
        this.jobId = payload.jobId
        this.stageLabel = '正在采集手语画面'
        this.progress = 12
        this.captureLiveFrame()
        return
      }
      if (payload.type === 'frame.result') {
        this.liveFramePending = false
        this.liveFrames += 1
        this.result = payload.result || this.result
        this.progress = Math.min(12 + this.liveFrames * 13, 90)
        this.stageLabel = `已完成 ${this.liveFrames}/6 帧`
        if (this.liveFrames >= 6) {
          this.stageLabel = '正在生成识别结果'
          this.socketTask.send({ data: JSON.stringify({ type: 'session.complete' }) })
        } else {
          this.scheduleLiveCapture(800)
        }
        return
      }
      if (payload.type === 'frame.skipped') {
        this.liveFramePending = false
        this.scheduleLiveCapture(900)
        return
      }
      if (payload.type === 'session.result') {
        this.liveFinalized = true
        this.state = 'succeeded'
        this.progress = 100
        this.stageLabel = '识别完成'
        this.result = payload.result || {}
        this.jobId = payload.result?.id || this.jobId
        this.stopCameraResources()
        return
      }
      if (payload.type === 'session.cancelled') {
        this.liveFinalized = true
        this.state = 'cancelled'
        this.progress = 0
        this.stopCameraResources()
        return
      }
      if (payload.type === 'error') {
        const messages = {
          NO_FRAMES_PROCESSED: '还没有成功处理的画面。',
          FRAME_TOO_LARGE: '摄像头画面过大，请降低分辨率。',
          INFERENCE_UNAVAILABLE: '当前模型暂时无法处理实时画面。',
          INVALID_FRAME: '摄像头画面格式无效。',
        }
        this.failLive(messages[payload.code] || '实时识别发生错误。')
      }
    },
    captureLiveFrame() {
      if (
        this.state !== 'live' ||
        this.liveFramePending ||
        !this.cameraContext ||
        !this.socketTask
      ) {
        return
      }
      this.liveFramePending = true
      // #ifdef MP-WEIXIN
      this.cameraContext.takePhoto({
        quality: 'low',
        success: (photo) => {
          const fileSystem = uni.getFileSystemManager()
          fileSystem.readFile({
            filePath: photo.tempImagePath,
            encoding: 'base64',
            success: (file) => {
              this.socketTask.send({
                data: JSON.stringify({
                  type: 'frame',
                  image: `data:image/jpeg;base64,${file.data}`,
                }),
                fail: () => {
                  this.liveFramePending = false
                  this.failLive('摄像头画面发送失败。')
                },
              })
            },
            fail: () => {
              this.liveFramePending = false
              this.failLive('无法读取摄像头画面。')
            },
          })
        },
        fail: () => {
          this.liveFramePending = false
          this.failLive('摄像头拍摄失败，请检查权限。')
        },
      })
      // #endif
    },
    scheduleLiveCapture(delay) {
      clearTimeout(this.liveCaptureTimer)
      this.liveCaptureTimer = setTimeout(() => this.captureLiveFrame(), delay)
    },
    cancelLiveSession(showToast) {
      this.liveFinalized = true
      if (this.socketTask) {
        this.socketTask.send({
          data: JSON.stringify({ type: 'session.cancel' }),
          complete: () => this.socketTask?.close({ code: 1000 }),
        })
      }
      this.state = 'cancelled'
      this.progress = 0
      this.stageLabel = '任务已取消'
      this.stopCameraResources()
      if (showToast) uni.showToast({ title: '任务已取消', icon: 'none' })
    },
    stopCameraResources() {
      clearTimeout(this.liveCaptureTimer)
      this.liveCaptureTimer = null
      this.liveFramePending = false
      if (this.socketTask && this.state !== 'succeeded') {
        this.socketTask.close({ code: 1000 })
      }
      this.socketTask = null
      this.cameraContext = null
      this.cameraActive = false
    },
    handleCameraError() {
      this.failLive('无法开启摄像头，请在微信设置中允许摄像头权限。')
    },
    failLive(message) {
      this.liveFinalized = true
      this.state = 'failed'
      this.progress = 0
      this.errorMessage = message
      this.stopCameraResources()
    },
    resetTask(clearSource = true) {
      if (this.pollSignal) this.pollSignal.cancelled = true
      this.stopCameraResources()
      this.state = 'idle'
      this.stageLabel = '准备任务'
      this.progress = 0
      this.jobId = ''
      this.result = null
      this.errorMessage = ''
      this.liveFrames = 0
      this.liveFinalized = false
      if (clearSource) {
        this.sourcePath = ''
        this.sourceName = ''
        this.sourceSize = 0
      }
    },
    dispose() {
      if (this.pollSignal) this.pollSignal.cancelled = true
      if (this.state === 'live') this.cancelLiveSession(false)
      else this.stopCameraResources()
    },
  },
}
</script>

<style scoped>
.mode-tabs {
  padding: 8rpx;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8rpx;
  border: 1rpx solid #e6eaf2;
  border-radius: 22rpx;
  background: #ffffff;
}

.mode-tab {
  min-height: 72rpx;
  border-radius: 16rpx;
  background: transparent;
  color: #667085;
  font-size: 27rpx;
  line-height: 72rpx;
  font-weight: 620;
}

.mode-tab--active {
  background: #f0f0ff;
  color: #4f4fc9;
}

.preview {
  position: relative;
  min-height: 500rpx;
  margin-top: 22rpx;
  overflow: hidden;
  background: #0b1220;
  border-color: #182230;
}

.preview__media {
  width: 100%;
  height: 500rpx;
  background: #0b1220;
}

.preview__empty {
  min-height: 500rpx;
  padding: 72rpx 42rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.preview__eyebrow,
.preview__title,
.preview__desc {
  display: block;
}

.preview__eyebrow {
  color: #7f83ff;
  font-size: 23rpx;
  font-weight: 700;
}

.preview__title {
  margin-top: 18rpx;
  color: #ffffff;
  font-size: 35rpx;
  line-height: 1.4;
  font-weight: 720;
}

.preview__desc {
  margin-top: 14rpx;
  color: #98a2b3;
  font-size: 24rpx;
  line-height: 1.55;
}

.preview__choose {
  min-width: 300rpx;
  margin-top: 32rpx;
  border-color: rgba(255, 255, 255, 0.25);
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
}

.preview__toolbar {
  position: absolute;
  right: 18rpx;
  bottom: 18rpx;
  left: 18rpx;
  min-height: 68rpx;
  padding: 0 18rpx;
  display: flex;
  align-items: center;
  gap: 16rpx;
  border-radius: 16rpx;
  background: rgba(11, 18, 32, 0.84);
}

.preview__filename {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  color: #ffffff;
  font-size: 23rpx;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.preview__replace {
  min-height: 54rpx;
  padding: 0;
  background: transparent;
  color: #a4a7ef;
  font-size: 23rpx;
  line-height: 54rpx;
}

.preview__overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(11, 18, 32, 0.78);
}

.preview__spinner {
  width: 56rpx;
  height: 56rpx;
  border: 6rpx solid rgba(255, 255, 255, 0.2);
  border-top-color: #7f83ff;
  border-radius: 50%;
  animation: spin 0.85s linear infinite;
}

.preview__processing {
  margin-top: 22rpx;
  color: #ffffff;
  font-size: 27rpx;
  font-weight: 650;
}

.progress-card,
.result-card,
.settings {
  margin-top: 22rpx;
  padding: 26rpx;
}

.progress-card__header,
.result-card__header,
.result-card__meta,
.slider-row__label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
}

.progress-card__title,
.result-card__title,
.settings__title {
  color: #182230;
  font-size: 28rpx;
  font-weight: 700;
}

.progress-card__value {
  color: #5b5bd6;
  font-size: 26rpx;
  font-weight: 720;
}

.progress-track {
  height: 12rpx;
  margin-top: 20rpx;
  overflow: hidden;
  border-radius: 999rpx;
  background: #eaecf0;
}

.progress-track__bar {
  height: 100%;
  border-radius: 999rpx;
  background: #5b5bd6;
  transition: width 180ms ease;
}

.steps {
  margin-top: 22rpx;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10rpx;
}

.step {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.step__dot {
  width: 13rpx;
  height: 13rpx;
  border-radius: 50%;
  background: #d0d5dd;
}

.step__dot--active {
  background: #0e9384;
}

.step__label {
  color: #667085;
  font-size: 21rpx;
}

.result-card__kind {
  padding: 7rpx 12rpx;
  border-radius: 12rpx;
  background: #ecfdf3;
  color: #067647;
  font-size: 21rpx;
}

.result-card__sentence {
  display: block;
  margin-top: 24rpx;
  color: #182230;
  font-size: 42rpx;
  line-height: 1.35;
  font-weight: 730;
}

.result-card__meta {
  margin-top: 24rpx;
  padding-top: 20rpx;
  border-top: 1rpx solid #eaecf0;
  color: #667085;
  font-size: 24rpx;
}

.result-card__confidence {
  color: #0e9384;
  font-weight: 720;
}

.labels {
  margin-top: 18rpx;
  border-top: 1rpx solid #eaecf0;
}

.label-row {
  min-height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
  border-bottom: 1rpx solid #eaecf0;
}

.label-row__text {
  color: #344054;
  font-size: 26rpx;
  font-weight: 630;
}

.label-row__confidence {
  color: #667085;
  font-size: 23rpx;
}

.result-card__actions {
  margin-top: 24rpx;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14rpx;
}

.settings {
  padding: 0;
  overflow: hidden;
}

.settings__summary {
  width: 100%;
  min-height: 106rpx;
  padding: 22rpx 26rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
  border-radius: 0;
  background: #ffffff;
  text-align: left;
}

.settings__title,
.settings__desc {
  display: block;
}

.settings__desc {
  margin-top: 6rpx;
  color: #667085;
  font-size: 22rpx;
}

.settings__action {
  color: #5b5bd6;
  font-size: 23rpx;
}

.settings__body {
  padding: 0 26rpx 28rpx;
  border-top: 1rpx solid #eaecf0;
}

.settings__body > .sf-label:first-child {
  margin-top: 24rpx;
}

.settings__next-label {
  margin-top: 24rpx;
}

.picker-field {
  min-height: 82rpx;
  padding: 0 22rpx;
  display: flex;
  align-items: center;
  border: 1rpx solid #d0d5dd;
  border-radius: 18rpx;
  color: #344054;
  font-size: 25rpx;
}

.preset-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10rpx;
}

.preset {
  min-height: 70rpx;
  border: 1rpx solid #d0d5dd;
  border-radius: 16rpx;
  background: #ffffff;
  color: #667085;
  font-size: 23rpx;
  line-height: 70rpx;
}

.preset--active {
  border-color: #7f83ff;
  background: #f5f5ff;
  color: #4f4fc9;
}

.slider-row {
  margin-top: 24rpx;
}

.slider-row__label {
  color: #475467;
  font-size: 23rpx;
}

.action-bar {
  margin-top: 24rpx;
}

.action-bar__button {
  width: 100%;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .preview__spinner {
    animation-duration: 1.8s;
  }

  .progress-track__bar {
    transition: none;
  }
}
</style>
