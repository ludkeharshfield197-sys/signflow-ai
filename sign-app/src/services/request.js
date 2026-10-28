import { getServerOrigin } from './config.js'
import {
  clearSession,
  getAccessToken,
  getRefreshToken,
  updateAccessSession,
} from './session.js'

export class SignFlowApiError extends Error {
  constructor(message, { code = 'REQUEST_FAILED', status = 0, requestId = '' } = {}) {
    super(message)
    this.name = 'SignFlowApiError'
    this.code = code
    this.status = status
    this.requestId = requestId
  }
}

let refreshPromise = null

function requestId() {
  return `sfm-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function invokeRequest(config) {
  return new Promise((resolve, reject) => {
    uni.request({
      ...config,
      success: resolve,
      fail: (error) => {
        reject(
          new SignFlowApiError('无法连接识别服务，请检查服务地址和网络。', {
            code: error?.errMsg || 'NETWORK_ERROR',
          }),
        )
      },
    })
  })
}

function unwrapResponse(response) {
  const body = response?.data
  if (response.statusCode >= 200 && response.statusCode < 300 && body?.success !== false) {
    return body?.data !== undefined ? body.data : body
  }
  throw new SignFlowApiError(
    body?.error?.message || body?.detail || `服务返回异常（${response.statusCode || 0}）`,
    {
      code: body?.error?.code || 'REQUEST_FAILED',
      status: response?.statusCode || 0,
      requestId: body?.requestId || '',
    },
  )
}

async function rawRequest(path, options = {}) {
  const header = {
    Accept: 'application/json',
    'Content-Type': 'application/json',
    'X-Request-ID': requestId(),
    ...(options.header || {}),
  }
  const token = getAccessToken()
  if (token && !options.skipAuth) header.Authorization = `Bearer ${token}`
  const response = await invokeRequest({
    url: `${getServerOrigin()}${path}`,
    method: options.method || 'GET',
    data: options.data || {},
    header,
    timeout: options.timeout || 30000,
  })
  return unwrapResponse(response)
}

export async function renewSession() {
  if (refreshPromise) return refreshPromise
  const refresh = getRefreshToken()
  if (!refresh) return false

  refreshPromise = rawRequest('/api/v1/auth/refresh/', {
    method: 'POST',
    data: { refresh },
    skipAuth: true,
  })
    .then((data) => {
      if (!data?.access) throw new Error('INVALID_REFRESH_RESPONSE')
      updateAccessSession(data)
      return true
    })
    .catch(() => {
      clearSession()
      return false
    })
    .finally(() => {
      refreshPromise = null
    })
  return refreshPromise
}

export async function apiRequest(path, options = {}) {
  try {
    return await rawRequest(path, options)
  } catch (error) {
    if (
      error instanceof SignFlowApiError &&
      error.status === 401 &&
      !options.skipAuth &&
      !options.retried &&
      (await renewSession())
    ) {
      return rawRequest(path, { ...options, retried: true })
    }
    throw error
  }
}

function invokeUpload(path, filePath, formData, onProgress) {
  return new Promise((resolve, reject) => {
    const token = getAccessToken()
    const task = uni.uploadFile({
      url: `${getServerOrigin()}${path}`,
      filePath,
      name: 'file',
      formData,
      header: {
        Accept: 'application/json',
        'X-Request-ID': requestId(),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      timeout: 5 * 60 * 1000,
      success: (response) => {
        let data = response.data
        try {
          if (typeof data === 'string') data = JSON.parse(data)
        } catch {
          reject(new SignFlowApiError('识别服务返回了无法解析的数据。'))
          return
        }
        try {
          resolve(unwrapResponse({ ...response, data }))
        } catch (error) {
          reject(error)
        }
      },
      fail: (error) => {
        reject(
          new SignFlowApiError('文件上传失败，请检查网络后重试。', {
            code: error?.errMsg || 'UPLOAD_FAILED',
          }),
        )
      },
    })
    if (onProgress && task?.onProgressUpdate) {
      task.onProgressUpdate((event) => onProgress(event.progress || 0))
    }
  })
}

export async function uploadFile(path, filePath, formData, onProgress) {
  try {
    return await invokeUpload(path, filePath, formData, onProgress)
  } catch (error) {
    if (
      error instanceof SignFlowApiError &&
      error.status === 401 &&
      (await renewSession())
    ) {
      return invokeUpload(path, filePath, formData, onProgress)
    }
    throw error
  }
}

function invokeDownload(path) {
  return new Promise((resolve, reject) => {
    const token = getAccessToken()
    uni.downloadFile({
      url: `${getServerOrigin()}${path}`,
      header: {
        Accept: '*/*',
        'X-Request-ID': requestId(),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      timeout: 5 * 60 * 1000,
      success: (response) => {
        if (response.statusCode >= 200 && response.statusCode < 300 && response.tempFilePath) {
          resolve(response.tempFilePath)
          return
        }
        reject(
          new SignFlowApiError(`媒体服务返回异常（${response.statusCode || 0}）`, {
            code: 'MEDIA_DOWNLOAD_FAILED',
            status: response.statusCode || 0,
          }),
        )
      },
      fail: (error) => {
        reject(
          new SignFlowApiError('无法读取授权媒体，请检查网络后重试。', {
            code: error?.errMsg || 'MEDIA_DOWNLOAD_FAILED',
          }),
        )
      },
    })
  })
}

export async function downloadProtectedFile(path) {
  try {
    return await invokeDownload(path)
  } catch (error) {
    if (
      error instanceof SignFlowApiError &&
      error.status === 401 &&
      (await renewSession())
    ) {
      return invokeDownload(path)
    }
    throw error
  }
}
