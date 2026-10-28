const REFRESH_KEY = 'signflow.refreshToken'
const USER_KEY = 'signflow.currentUser'
const ROLES_KEY = 'signflow.roles'

let accessToken = ''

function readJson(key, fallback) {
  try {
    const value = uni.getStorageSync(key)
    return value ? JSON.parse(value) : fallback
  } catch {
    uni.removeStorageSync(key)
    return fallback
  }
}

export function getAccessToken() {
  return accessToken
}

export function getRefreshToken() {
  return uni.getStorageSync(REFRESH_KEY) || ''
}

export function hasRefreshToken() {
  return Boolean(getRefreshToken())
}

export function getCurrentUser() {
  return readJson(USER_KEY, null)
}

export function getRoles() {
  return readJson(ROLES_KEY, [])
}

export function saveLoginSession({ access, refresh, user, roles = [] }) {
  accessToken = access || ''
  if (refresh) uni.setStorageSync(REFRESH_KEY, refresh)
  if (user) uni.setStorageSync(USER_KEY, JSON.stringify(user))
  uni.setStorageSync(ROLES_KEY, JSON.stringify(roles))
}

export function updateAccessSession({ access, user, roles }) {
  accessToken = access || ''
  if (user) uni.setStorageSync(USER_KEY, JSON.stringify(user))
  if (roles) uni.setStorageSync(ROLES_KEY, JSON.stringify(roles))
}

export function clearSession() {
  accessToken = ''
  uni.removeStorageSync(REFRESH_KEY)
  uni.removeStorageSync(USER_KEY)
  uni.removeStorageSync(ROLES_KEY)
}
