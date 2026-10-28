import { computed, onBeforeUnmount, ref } from 'vue'

import { createOfficialDemoResult } from '@/data/demoData'
import { createCameraSocket } from '@/services/camera'
import { cancelDetectionJob, createDetectionJob, getDetectionJob } from '@/services/detections'
import { getApiError } from '@/services/api'

const TERMINAL = new Set(['succeeded', 'failed', 'cancelled', 'timed_out'])
const CAMERA_TARGET_FRAMES = 6

export function useDetectionJob() {
  const status = ref('idle')
  const progress = ref(0)
  const jobId = ref('')
  const result = ref(null)
  const error = ref('')
  const stageLabel = ref('等待开始')
  let simulationTimer
  let pollTimer
  let cameraFrameTimer
  let cameraSocket
  let cameraVideo
  let cameraCanvas
  let cameraFrameCount = 0
  let cameraFrameDelay = 420
  let cameraFinishing = false

  function closeCameraTransport({ notifyCancel = false } = {}) {
    clearTimeout(cameraFrameTimer)
    if (cameraSocket) {
      if (notifyCancel && cameraSocket.readyState === cameraSocket.OPEN) {
        cameraSocket.send(JSON.stringify({ type: 'session.cancel' }))
      }
      cameraSocket.onmessage = null
      cameraSocket.onerror = null
      cameraSocket.onclose = null
      cameraSocket.close()
    }
    cameraSocket = null
    if (cameraVideo) cameraVideo.srcObject = null
    cameraVideo = null
    cameraCanvas = null
    cameraFrameCount = 0
    cameraFinishing = false
  }

  function clearTimers({ cancelCamera = false } = {}) {
    clearInterval(simulationTimer)
    clearTimeout(pollTimer)
    closeCameraTransport({ notifyCancel: cancelCamera })
  }

  function reset() {
    clearTimers({ cancelCamera: true })
    status.value = 'idle'
    progress.value = 0
    jobId.value = ''
    result.value = null
    error.value = ''
    stageLabel.value = '等待开始'
  }

  function failCamera(message) {
    closeCameraTransport()
    status.value = 'failed'
    error.value = message
    stageLabel.value = '实时识别未完成'
  }

  function scheduleCameraFrame(delay = cameraFrameDelay) {
    clearTimeout(cameraFrameTimer)
    cameraFrameTimer = setTimeout(sendCameraFrame, delay)
  }

  function sendCameraFrame() {
    if (!cameraSocket || cameraSocket.readyState !== cameraSocket.OPEN || cameraFinishing) return
    if (!cameraVideo || !cameraCanvas) return
    const context = cameraCanvas.getContext('2d', { alpha: false })
    if (!context) {
      failCamera('浏览器无法读取摄像头画面，请改用图片或视频识别。')
      return
    }
    context.drawImage(cameraVideo, 0, 0, cameraCanvas.width, cameraCanvas.height)
    const image = cameraCanvas.toDataURL('image/jpeg', 0.72)
    cameraSocket.send(JSON.stringify({ type: 'frame', image }))
    stageLabel.value = `正在识别实时画面 ${cameraFrameCount + 1}/${CAMERA_TARGET_FRAMES}`
  }

  async function prepareCameraCapture(stream, limits = {}) {
    const track = stream?.getVideoTracks?.()[0]
    if (!track) return
    const settings = track.getSettings?.() || {}
    const sourceWidth = settings.width || 960
    const sourceHeight = settings.height || 540
    const scale = Math.min(1, 960 / sourceWidth)
    cameraCanvas = document.createElement('canvas')
    cameraCanvas.width = Math.max(Math.round(sourceWidth * scale), 320)
    cameraCanvas.height = Math.max(Math.round(sourceHeight * scale), 180)
    cameraVideo = document.createElement('video')
    cameraVideo.muted = true
    cameraVideo.playsInline = true
    cameraVideo.srcObject = stream
    await cameraVideo.play()
    const maxFps = Math.max(Number(limits.maxFps) || 5, 1)
    cameraFrameDelay = Math.max(Math.ceil(1000 / maxFps) + 40, 360)
    scheduleCameraFrame(180)
  }

  async function runCamera(payload) {
    status.value = 'queued'
    progress.value = 5
    stageLabel.value = '正在建立安全实时通道'
    const connection = await createCameraSocket({
      modelId: payload.modelId,
      confidence: payload.advanced.confidence,
      iou: payload.advanced.iou,
    })
    cameraSocket = connection.socket

    cameraSocket.onmessage = async (event) => {
      const message = JSON.parse(event.data)
      if (message.type === 'session.ready') {
        jobId.value = message.jobId || ''
        status.value = 'running'
        progress.value = 12
        stageLabel.value = '实时通道已就绪'
        try {
          await prepareCameraCapture(payload.stream, message.limits)
        } catch {
          failCamera('摄像头画面读取失败，请重新授权后再试。')
        }
        return
      }
      if (message.type === 'frame.skipped') {
        scheduleCameraFrame()
        return
      }
      if (message.type === 'frame.result') {
        cameraFrameCount += 1
        progress.value = Math.min(15 + Math.round((cameraFrameCount / CAMERA_TARGET_FRAMES) * 78), 93)
        if (cameraFrameCount >= CAMERA_TARGET_FRAMES) {
          cameraFinishing = true
          stageLabel.value = '正在汇总实时识别结果'
          cameraSocket.send(JSON.stringify({ type: 'session.complete' }))
        } else {
          scheduleCameraFrame()
        }
        return
      }
      if (message.type === 'session.result') {
        result.value = message.result
        jobId.value = message.result?.id || jobId.value
        progress.value = 100
        status.value = 'succeeded'
        stageLabel.value = '识别完成'
        closeCameraTransport()
        return
      }
      if (message.type === 'session.cancelled') {
        status.value = 'cancelled'
        stageLabel.value = '任务已取消'
        closeCameraTransport()
        return
      }
      if (message.type === 'error') {
        failCamera({
          INFERENCE_UNAVAILABLE: '实时推理服务暂时不可用，请稍后重试。',
          NO_FRAMES_PROCESSED: '没有成功读取摄像头画面，请重新授权后再试。',
          FRAME_TOO_LARGE: '摄像头画面超过实时通道限制，请降低分辨率后重试。',
        }[message.code] || '实时识别通道返回了无法处理的画面。')
      }
    }
    cameraSocket.onerror = () => failCamera('无法连接实时识别服务，请检查网络后重试。')
    cameraSocket.onclose = (event) => {
      if (!TERMINAL.has(status.value) && status.value !== 'cancelled') {
        failCamera(
          event.code === 4401
            ? '登录状态已失效，请重新登录后使用摄像头。'
            : '实时识别连接已中断，请重试。',
        )
      }
    }
  }

  function runOfficialDemo(payload) {
    clearTimers()
    status.value = 'queued'
    progress.value = 8
    stageLabel.value = '任务已进入识别队列'

    const stages = [
      [22, 'uploading', '正在准备官方样例'],
      [48, 'running', '正在检测手语关键帧'],
      [76, 'running', '正在生成连续表达'],
      [100, 'succeeded', '识别完成'],
    ]
    let index = 0
    simulationTimer = setInterval(() => {
      const [nextProgress, nextStatus, label] = stages[index]
      progress.value = nextProgress
      status.value = nextStatus
      stageLabel.value = label
      index += 1
      if (index >= stages.length) {
        clearInterval(simulationTimer)
        result.value = createOfficialDemoResult({
          id: `demo-${Date.now()}`,
          sampleId: payload.source.sampleId,
          mode: payload.mode,
          sourceName: payload.source.name,
          createdAt: new Date().toISOString(),
        })
        jobId.value = result.value.id
      }
    }, 320)
  }

  async function poll() {
    try {
      const payload = await getDetectionJob(jobId.value)
      status.value = payload.status
      progress.value = payload.progress ?? progress.value
      stageLabel.value = payload.stageLabel || '正在处理'
      if (payload.status === 'succeeded') result.value = payload.result
      if (payload.status === 'failed') error.value = payload.errorMessage || '识别任务未能完成。'
      if (!TERMINAL.has(payload.status)) pollTimer = setTimeout(poll, 1000)
    } catch (requestError) {
      status.value = 'failed'
      error.value = getApiError(requestError, '无法读取任务状态，请稍后重试。')
    }
  }

  async function start(payload) {
    reset()
    if (payload.source?.kind === 'official') {
      runOfficialDemo(payload)
      return
    }

    status.value = 'uploading'
    stageLabel.value = '正在安全上传输入'
    try {
      if (payload.mode === 'live' && payload.source?.kind === 'camera') {
        await runCamera(payload)
        return
      }
      const job = await createDetectionJob(payload, (event) => {
        if (event.total) progress.value = Math.round((event.loaded / event.total) * 35)
      })
      jobId.value = job.id
      status.value = job.status || 'queued'
      progress.value = Math.max(progress.value, 38)
      stageLabel.value = '任务已进入处理队列'
      await poll()
    } catch (requestError) {
      status.value = 'failed'
      error.value = getApiError(requestError, '识别任务创建失败，请重试。')
    }
  }

  async function cancel() {
    const hadCameraSocket = Boolean(cameraSocket)
    clearTimers({ cancelCamera: true })
    if (hadCameraSocket) {
      status.value = 'cancelled'
      stageLabel.value = '任务已取消'
      return
    }
    if (jobId.value && !jobId.value.startsWith('demo-')) {
      try {
        await cancelDetectionJob(jobId.value)
      } catch {
        // The local state still moves to cancelled so the user retains control.
      }
    }
    status.value = 'cancelled'
    stageLabel.value = '任务已取消'
  }

  onBeforeUnmount(() => clearTimers({ cancelCamera: true }))

  return {
    status,
    progress,
    jobId,
    result,
    error,
    stageLabel,
    isBusy: computed(() => ['uploading', 'queued', 'running'].includes(status.value)),
    canCancel: computed(() => ['uploading', 'queued', 'running'].includes(status.value)),
    start,
    cancel,
    reset,
  }
}
