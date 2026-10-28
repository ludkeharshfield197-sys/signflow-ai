import { beforeEach, describe, expect, it, vi } from 'vitest'

const get = vi.fn()

vi.mock('@/services/api', () => ({
  default: { get },
}))

describe('admin service', () => {
  beforeEach(() => {
    get.mockReset()
  })

  it('loads each protected console source through the versioned API', async () => {
    get.mockResolvedValue({ data: { data: { items: [], source: 'database' } } })
    const { getAdminRoles, getAdminSystem, getAdminUsers } = await import('@/services/admin')

    await getAdminUsers({ query: 'demo' })
    await getAdminRoles()
    await getAdminSystem()

    expect(get).toHaveBeenNthCalledWith(1, '/api/v1/admin/users/', {
      params: { query: 'demo' },
    })
    expect(get).toHaveBeenNthCalledWith(2, '/api/v1/admin/roles/')
    expect(get).toHaveBeenNthCalledWith(3, '/api/v1/admin/system/')
  })
})
