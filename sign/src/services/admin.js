import api from './api'


function unwrap(response) {
  return response.data?.data || response.data
}

export async function getAdminUsers(params = {}) {
  return unwrap(await api.get('/api/v1/admin/users/', { params }))
}

export async function getAdminRoles() {
  return unwrap(await api.get('/api/v1/admin/roles/'))
}

export async function getAdminSystem() {
  return unwrap(await api.get('/api/v1/admin/system/'))
}
