<template>
  <div class="video-recognition">
    <el-card class="recognition-card">
      <template #header>
        <div class="card-header">
          <h2>视频识别</h2>
        </div>
      </template>

      <div class="recognition-content">
        <div class="left-panel">
          <div class="model-section">
            <h3>模型选择</h3>
            <el-select v-model="selectedModel" placeholder="请选择识别模型" class="model-select-input">
              <el-option
                  v-for="model in modelList"
                  :key="model.id"
                  :label="model.name"
                  :value="model.id"
              />
            </el-select>
            <el-upload
                class="model-uploader"
                drag
                :before-upload="handleBeforeUpload"
                :file-list="fileList"
                :on-remove="handleRemove"
                :on-change="handleChange"
                :auto-upload="false"
                accept=".pt,.onnx"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
              <template #tip>
                <div class="el-upload__tip">支持上传的文件类型为 .pt 或 .onnx</div>
              </template>
            </el-upload>
            <el-button type="primary" class="upload-btn" @click="confirmUpload">确认上传</el-button>
          </div>

          <div class="params-section">
            <h3>参数设置</h3>
            <div class="param-item">
              <span>IoU阈值：</span>
              <el-slider
                  v-model="iouThreshold"
                  :min="0"
                  :max="1"
                  :step="0.01"
                  show-input
              />
            </div>
            <div class="param-item">
              <span>置信度阈值：</span>
              <el-slider
                  v-model="confidenceThreshold"
                  :min="0"
                  :max="1"
                  :step="0.01"
                  show-input
              />
            </div>
          </div>
        </div>

        <div class="right-panel">
          <div class="video-section">
            <div class="video-container">
              <h3>原始视频</h3>
              <el-upload
                  class="video-uploader"
                  :show-file-list="false"
                  :before-upload="handleVideoUpload"
                  :loading="loading"
              >
                <video
                    v-if="videoUrl"
                    :src="videoUrl"
                    class="preview-video"
                    controls
                    ref="videoPlayer"
                />
                <div v-else class="upload-placeholder">
                  <el-icon class="video-uploader-icon"><Plus /></el-icon>
                  <span>点击上传视频</span>
                </div>
              </el-upload>
              <el-button
                  type="primary"
                  class="detect-btn"
                  :disabled="!videoUrl || !selectedModel"
                  @click="handleDetection"
                  :loading="loading"
              >
                开始检测
              </el-button>
            </div>

            <div class="video-container">
              <h3>检测结果</h3>
              <div class="result-video-wrapper">
                <template v-if="resultStreamUrl && !streamError">
                  <div class="stream-container">
                    <img
                        :src="resultStreamUrl"
                        class="preview-video"
                        alt="检测结果"
                        @error="handleStreamError"
                        @load="handleStreamLoad"
                    />
                    <div class="stream-overlay">
                      <el-button
                        type="warning"
                        size="small"
                        icon="Refresh"
                        circle
                        @click="retryStream"
                        title="刷新视频流"
                      />
                    </div>
                  </div>
                </template>
                <div v-else-if="streamError" class="stream-error">
                  <el-alert
                    title="视频流加载失败"
                    type="error"
                    description="无法加载视频流，请检查后端服务是否正常运行"
                    show-icon
                  />
                  <el-button type="primary" @click="retryStream" class="retry-btn">重试</el-button>
                </div>
                <div v-else class="empty-result">
                  <span>等待检测结果...</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 新增检测结果表格 -->
          <div v-if="recognitionResult" class="result-section">
            <h3>检测详情：</h3>
            <el-table :data="formattedResults" stripe>
              <el-table-column label="目标类别" prop="class" />
              <el-table-column label="时间点" prop="timestamp" />
              <el-table-column label="置信度" prop="confidence">
                <template #default="{ row }">
                  {{ (row.confidence * 100).toFixed(2) }}%
                </template>
              </el-table-column>
              <el-table-column label="位置信息" prop="bbox">
                <template #default="{ row }">
                  [{{ row.bbox.map(v => v.toFixed(2)).join(', ') }}]
                </template>
              </el-table-column>
            </el-table>
            <div class="export-buttons">
              <el-button type="success" class="export-btn" @click="exportTxtResult" :disabled="!recognitionResult">
                导出TXT报告
              </el-button>
              <el-button type="primary" class="export-btn" @click="exportVideoResult" :disabled="!recognitionResult">
                导出检测视频
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, UploadFilled } from '@element-plus/icons-vue'
import requestUtil from '@/util/request'
import axios from 'axios'

const videoUrl = ref('')
const modelList = ref([])
const selectedModel = ref('')
const loading = ref(false)
const iouThreshold = ref(0.45)
const confidenceThreshold = ref(0.25)
const fileList = ref([])
const videoPlayer = ref(null)
const resultStreamUrl = ref('')
const baseUrl = requestUtil.getServerUrl()
const streamError = ref(false)
const recognitionResult = ref(null)
const currentTaskId = ref(null)

// 格式化检测结果为表格数据
const formattedResults = computed(() => {
  if (!recognitionResult.value) return [];

  const results = [];
  for (const className in recognitionResult.value) {
    if (recognitionResult.value.hasOwnProperty(className)) {
      const detections = recognitionResult.value[className];
      for (const detection of detections) {
        // 格式化时间戳为分:秒.毫秒
        const minutes = Math.floor(detection.timestamp / 60);
        const seconds = Math.floor(detection.timestamp % 60);
        const milliseconds = Math.floor((detection.timestamp % 1) * 1000);
        const formattedTime = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(3, '0')}`;

        results.push({
          class: className,
          timestamp: formattedTime,
          confidence: detection.confidence,
          bbox: detection.bbox
        });
      }
    }
  }

  // 按时间戳排序
  return results.sort((a, b) => {
    return a.timestamp.localeCompare(b.timestamp);
  });
});

// 获取可用的模型列表
const getModelList = async () => {
  try {
    const result = await requestUtil.post('/modelYolo/list', {
      pageNum: 1,
      pageSize: 100,
      query: ''
    })
    if (result.data.code === 200) {
      modelList.value = result.data.data.modelList || []
    } else {
      ElMessage.error(result.data.message || '获取模型列表失败')
    }
  } catch (error) {
    console.error('获取模型列表失败:', error)
    ElMessage.error('获取模型列表失败')
  }
}

// 处理模型上传前的验证
const handleBeforeUpload = (file) => {
  const validTypes = [".pt", ".onnx"]
  const isValidType = validTypes.some((type) => file.name.endsWith(type))
  if (!isValidType) {
    ElMessage.error("只支持上传 .pt 或 .onnx 文件！")
    return false
  }
  return true
}

// 处理文件变更
const handleChange = (file) => {
  fileList.value = [file]
}

// 处理文件移除
const handleRemove = () => {
  fileList.value = []
}

// 确认上传模型
const confirmUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning("请先选择一个文件！")
    return
  }

  const formData = new FormData()
  formData.append('file', fileList.value[0].raw)

  try {
    const result = await requestUtil.post("/modelYolo/upload", formData)
    if (result.data.code === 200) {
      ElMessage.success("模型上传成功！")
      getModelList()
      fileList.value = []
    } else {
      ElMessage.error(result.data.message || '上传失败')
    }
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error('上传失败')
  }
}

// 处理视频上传
const currentVideo = ref(null)
const handleVideoUpload = async (file) => {
  try {
    const maxSize = 100 * 1024 * 1024 // 100MB
    if (file.size > maxSize) {
      ElMessage.error('视频文件大小不能超过100MB')
      return false
    }

    const validTypes = ['video/mp4', 'video/webm', 'video/ogg', 'video/x-msvideo', 'video/avi', 'video/x-ms-wmv']
    if (!validTypes.includes(file.type)) {
      ElMessage.error('请上传MP4、WebM、OGG、AVI或WMV格式的视频')
      return false
    }

    videoUrl.value = URL.createObjectURL(file)
    currentVideo.value = file
    return false
  } catch (error) {
    console.error('视频上传处理失败:', error)
    ElMessage.error('视频上传处理失败')
    return false
  }
}

// 处理视频流获取
const handleVideoStream = async (taskId) => {
  try {
    // 添加时间戳参数防止缓存
    const timestamp = new Date().getTime()
    resultStreamUrl.value = `${baseUrl}/video/stream/${taskId}/?t=${timestamp}`
    streamError.value = false

    // 保存当前任务ID，用于后续获取检测结果
    currentTaskId.value = taskId

    // 开始轮询检测结果
    pollDetectionResult(taskId)
  } catch (error) {
    console.error('视频流初始化失败:', error)
    streamError.value = true
    ElMessage.error('无法连接到视频流，请检查后端服务是否正常运行')
  }
}

// 轮询检测结果
const pollDetectionResult = async (taskId) => {
  try {
    // 每3秒轮询一次检测结果
    const pollInterval = setInterval(async () => {
      try {
        const response = await requestUtil.get(`/video/result/${taskId}/`)
        if (response.data.code === 200) {
          if (response.data.data.status === 'completed') {
            // 检测完成，获取结果
            recognitionResult.value = response.data.data.detection_result
            clearInterval(pollInterval)
            ElMessage.success('视频检测完成')
          } else if (response.data.data.status === 'failed') {
            // 检测失败
            clearInterval(pollInterval)
            ElMessage.error(`视频检测失败: ${response.data.data.error_message || '未知错误'}`)
          }
        }
      } catch (error) {
        console.error('轮询检测结果失败:', error)
        // 不中断轮询，继续尝试
      }
    }, 3000)

    // 60秒后停止轮询
    setTimeout(() => {
      clearInterval(pollInterval)
    }, 60000)
  } catch (error) {
    console.error('设置轮询失败:', error)
  }
}

// 处理视频检测
const handleDetection = async () => {
  if (!selectedModel.value) {
    ElMessage.warning('请先选择识别模型')
    return
  }

  if (!currentVideo.value) {
    ElMessage.warning('请先上传视频')
    return
  }

  // 验证参数
  if (iouThreshold.value < 0 || iouThreshold.value > 1) {
    ElMessage.warning('IoU阈值必须在0到1之间')
    return
  }

  if (confidenceThreshold.value < 0 || confidenceThreshold.value > 1) {
    ElMessage.warning('置信度阈值必须在0到1之间')
    return
  }

  const formData = new FormData()
  formData.append('video', currentVideo.value)
  formData.append('model_id', selectedModel.value)
  formData.append('iou_threshold', iouThreshold.value)
  formData.append('confidence_threshold', confidenceThreshold.value)
  formData.append('save_result', 'true') // 添加保存结果的标志

  try {
    loading.value = true
    resultStreamUrl.value = ''
    streamError.value = false
    recognitionResult.value = null

    // 设置请求超时时间
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 30000) // 30秒超时

    const response = await requestUtil.post('/video/submit/', formData, {
      signal: controller.signal,
      timeout: 30000 // 30秒超时
    })

    clearTimeout(timeoutId)

    if (response.data.code === 200) {
      const taskId = response.data.data.task_id
      await handleVideoStream(taskId)
      ElMessage.success('开始进行视频检测')
    } else {
      throw new Error(response.data.message || '提交检测任务失败')
    }
  } catch (error) {
    console.error('视频检测失败:', error)
    resultStreamUrl.value = ''
    streamError.value = true

    let errorMessage = '检测失败'
    if (error.name === 'AbortError' || error.code === 'ECONNABORTED') {
      errorMessage = '检测请求超时，请检查网络连接或视频大小'
    } else if (error.response) {
      const serverMessage = error.response.data?.message || '服务器响应异常'
      errorMessage = `${errorMessage}: ${serverMessage}\n请确保服务器正常运行并重试`
    } else if (error.request) {
      errorMessage = '网络请求失败，请检查网络连接是否正常'
    } else {
      errorMessage = `${errorMessage}: ${error.message || '未知错误'}\n请稍后重试或联系技术支持`
    }
    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
  }
}

// 导出TXT报告
const exportTxtResult = async () => {
  if (!recognitionResult.value || !currentTaskId.value) {
    ElMessage.warning('暂无识别结果可导出')
    return
  }

  try {
    const response = await requestUtil.post('/video/export/', {
      task_id: currentTaskId.value,
      export_type: 'txt'
    }, {
      responseType: 'blob'
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `检测结果报告_${new Date().getTime()}.txt`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success('导出TXT报告成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出TXT报告失败')
  }
}

// 导出检测视频
const exportVideoResult = async () => {
  if (!recognitionResult.value || !currentTaskId.value) {
    ElMessage.warning('暂无检测视频可导出')
    return
  }

  try {
    loading.value = true
    ElMessage.info('正在准备导出视频，请稍候...')

    // 使用 Axios 直接请求，并设置 responseType 为 blob
    const response = await axios({
      url: `${baseUrl}/video/export/`,
      method: 'POST',
      data: {
        task_id: currentTaskId.value,
        export_type: 'video'
      },
      responseType: 'blob',
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // 获取文件名
    const contentDisposition = response.headers['content-disposition']
    let filename = `检测结果视频_${new Date().getTime()}.mp4`

    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/)
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1]
      }
    }

    // 创建 Blob 对象
    const blob = new Blob([response.data], { type: 'video/mp4' })

    // 创建下载链接
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()

    // 清理
    setTimeout(() => {
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    }, 100)

    ElMessage.success('导出检测视频成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error(`导出检测视频失败: ${error.message || '未知错误'}`)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  getModelList()
})

// 处理视频流错误
const handleStreamError = () => {
  console.error('视频流加载失败:', resultStreamUrl.value)
  streamError.value = true
  ElMessage.error('视频流加载失败，请检查后端服务是否正常运行')

  // 自动尝试重新加载一次
  setTimeout(() => {
    retryStream()
  }, 3000)
}

// 处理视频流加载成功
const handleStreamLoad = () => {
  console.log('视频流加载成功:', resultStreamUrl.value)
  streamError.value = false
}

// 重试加载视频流
const retryStream = () => {
  if (!resultStreamUrl.value) return

  console.log('重试加载视频流:', resultStreamUrl.value)
  streamError.value = false

  // 通过修改URL参数强制浏览器重新加载图像
  const timestamp = new Date().getTime()
  const baseUrl = resultStreamUrl.value.split('?')[0]
  resultStreamUrl.value = `${baseUrl}?t=${timestamp}`
}
</script>

<style scoped lang="scss">
.video-recognition {
  padding: 20px;

  .recognition-card {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    border-radius: 8px;

    .card-header {
      text-align: center;
      h2 {
        margin: 0;
        font-weight: bold;
        background: linear-gradient(135deg, #409EFF, #36D1DC);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 10px 0;
      }
    }

    .recognition-content {
      display: flex;
      gap: 20px;
      padding: 20px;

      .left-panel {
        flex: 1;
        min-width: 300px;

        .model-section {
          margin-bottom: 30px;
          padding: 20px;
          background: #f8f9fa;
          border-radius: 8px;

          h3 {
            margin-top: 0;
            margin-bottom: 20px;
            color: #2c3e50;
          }

          .model-select-input {
            width: 100%;
            margin-bottom: 20px;
          }

          .model-uploader {
            margin-bottom: 15px;

            .el-upload-dragger {
              width: 100%;
              border-radius: 8px;
              transition: all 0.3s ease;

              &:hover {
                border-color: #409EFF;
                transform: translateY(-2px);
              }
            }
          }

          .upload-btn {
            width: 100%;
          }
        }

        .params-section {
          padding: 20px;
          background: #f8f9fa;
          border-radius: 8px;

          h3 {
            margin-top: 0;
            margin-bottom: 20px;
            color: #2c3e50;
          }

          .param-item {
            margin-bottom: 20px;

            span {
              display: block;
              margin-bottom: 10px;
              color: #606266;
            }
          }
        }
      }

      .right-panel {
        flex: 2;

        .video-section {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 20px;
          margin-bottom: 30px;

          .video-container {
            h3 {
              margin-top: 0;
              margin-bottom: 15px;
              color: #2c3e50;
            }

            .video-uploader {
              width: 100%;
              height: 300px;
              border: 2px dashed #dcdfe6;
              border-radius: 8px;
              overflow: hidden;
              transition: all 0.3s ease;
              display: flex;
              align-items: center;
              justify-content: center;
              background: #000;

              &:hover {
                border-color: #409EFF;
              }

              .preview-video {
                max-width: 100%;
                max-height: 100%;
                width: auto;
                height: auto;
                object-fit: contain;
              }

              .upload-placeholder {
                height: 100%;
                width: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 20px;
                background: #fef0f0;
                border-radius: 8px;

                .el-alert {
                  width: 100%;
                  margin-bottom: 20px;
                }

                .retry-btn {
                  width: 120px;
                }
              }
            }

            .detect-btn {
              width: 100%;
              margin-top: 15px;
            }

            .result-video-wrapper {
              width: 100%;
              height: 300px;
              border-radius: 8px;
              overflow: hidden;
              background: #000;
              display: flex;
              align-items: center;
              justify-content: center;

              .stream-container {
                width: 100%;
                height: 100%;
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;

                .preview-video {
                  max-width: 100%;
                  max-height: 100%;
                  width: auto;
                  height: auto;
                  object-fit: contain;
                }

                .stream-overlay {
                  position: absolute;
                  top: 10px;
                  right: 10px;
                  z-index: 10;
                }
              }

              .stream-error {
                width: 100%;
                height: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 20px;
                background: #fef0f0;
              }

              .empty-result {
                height: 100%;
                width: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #909399;
                background: #f8f9fa;
              }
            }
          }
        }

        .result-section {
          padding: 20px;
          background: #f8f9fa;
          border-radius: 8px;
          margin-top: 20px;

          h3 {
            margin-top: 0;
            margin-bottom: 20px;
            color: #2c3e50;
          }

          .export-buttons {
            display: flex;
            gap: 10px;
            margin-top: 15px;

            .export-btn {
              flex: 1;
            }
          }
        }
      }
    }
  }
}
</style>
