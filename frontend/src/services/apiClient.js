/**
 * apiClient - Flask backend integration.
 *
 * Security rules enforced by this client:
 * - credentials: 'include' is used on every request so the HttpOnly cookie
 *   containing the JWT is forwarded by the browser.
 * - JWT is never stored in localStorage/sessionStorage.
 * - CSRF token is fetched on first state-changing request and kept in memory.
 * - On 401 the user is redirected to the login page.
 * - On 403 CSRF mismatch the token is refreshed once and the request retried.
 */

const BASE = import.meta.env.VITE_API_BASE_URL || '/api'

let csrfToken = null

function isStateChanging(method) {
  return method !== 'GET' && method !== 'HEAD' && method !== 'OPTIONS'
}

async function fetchCsrfToken() {
  const res = await fetch(`${BASE}/auth/csrf-token`, {
    method: 'GET',
    credentials: 'include',
    headers: { Accept: 'application/json' },
  })
  const body = await parseJson(res)
  csrfToken = body?.data?.csrf_token || body?.csrf_token || null
  return csrfToken
}

async function ensureCsrfToken() {
  if (csrfToken) return csrfToken
  return fetchCsrfToken()
}

function csrfHeaders() {
  return csrfToken ? { 'X-CSRF-Token': csrfToken } : {}
}

async function parseJson(res) {
  const text = await res.text()
  if (!text) return null
  try {
    return JSON.parse(text)
  } catch {
    return { error: text }
  }
}

function buildError(res, data) {
  const message = data?.error || `Request failed with status ${res.status}`
  const err = new Error(message)
  err.status = res.status
  err.data = data
  return err
}

function redirectToLogin() {
  if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
    window.location.href = `/login?next=${encodeURIComponent(window.location.pathname + window.location.search)}`
  }
}

async function parseResponse(res, opts = {}) {
  const payload = await parseJson(res)
  if (!res.ok) {
    if (res.status === 401 && !opts.noRedirect) {
      redirectToLogin()
    }
    throw buildError(res, payload)
  }
  // Backend wraps list/single resources in { data: ... }; auth endpoints return flat objects.
  const data = payload && typeof payload === 'object' && 'data' in payload ? payload.data : payload
  return { data, status: res.status }
}

async function request(method, path, body = null, options = {}) {
  const headers = {
    Accept: 'application/json',
    ...(body !== null ? { 'Content-Type': 'application/json' } : {}),
    ...options.headers,
  }

  if (isStateChanging(method)) {
    await ensureCsrfToken()
    Object.assign(headers, csrfHeaders())
  }

  const fetchOptions = {
    method,
    credentials: 'include',
    headers,
  }
  if (body !== null) {
    fetchOptions.body = typeof body === 'string' ? body : JSON.stringify(body)
  }

  const res = await fetch(`${BASE}${path}`, fetchOptions)

  // If CSRF was rejected, refresh token once and retry.
  if (res.status === 403 && isStateChanging(method)) {
    const data = await parseJson(res)
    const msg = (data?.error || '').toLowerCase()
    if (msg.includes('csrf')) {
      csrfToken = null
      await fetchCsrfToken()
      Object.assign(headers, csrfHeaders())
      const retryRes = await fetch(`${BASE}${path}`, fetchOptions)
      return parseResponse(retryRes, options)
    }
  }
  return parseResponse(res, options)

}

const get = (path, opts = {}) => request('GET', path, null, opts)
const post = (path, body, opts = {}) => request('POST', path, body, opts)
const put = (path, body, opts = {}) => request('PUT', path, body, opts)
const patch = (path, body, opts = {}) => request('PATCH', path, body, opts)
const del = (path, opts = {}) => request('DELETE', path, null, opts)

function qs(params = {}, defaults = {}) {
  return new URLSearchParams({ ...defaults, ...params }).toString()
}

export const apiClient = {
  base: BASE,

  // Auth
  getCsrfToken: () => get('/auth/csrf-token'),
  login: (credentials) => post('/auth/login', credentials),
  logout: () => post('/auth/logout', {}),
  me: () => get('/auth/me', { noRedirect: true }),

  // Users / Roles (admin)
  listUsers: (params = {}) => get(`/users?${qs(params, { per_page: 100 })}`),
  createUser: (payload) => post('/users', payload),
  updateUser: (id, payload) => put(`/users/${id}`, payload),
  deleteUser: (id) => del(`/users/${id}`),

  listRoles: () => get('/roles'),

  // Assets
  listAssets: (params = {}) => {
    const query = qs(params, { per_page: 25 })
    return get(`/assets${query ? `?${query}` : ''}`)
  },
  createAsset: (payload) => post('/assets', payload),
  updateAsset: (id, payload) => put(`/assets/${id}`, payload),
  deleteAsset: (id) => del(`/assets/${id}`),
  updateNetworkDetails: (id, payload) => put(`/assets/${id}/network-details`, payload),
  listCredentials: (id) => get(`/assets/${id}/credentials`),
  createCredential: (id, payload) => post(`/assets/${id}/credentials`, payload),
  updateCredential: (id, cid, payload) => put(`/assets/${id}/credentials/${cid}`, payload),
  deleteCredential: (id, cid) => del(`/assets/${id}/credentials/${cid}`),
  revealCredential: (id, cid) => get(`/assets/${id}/credentials/${cid}/reveal`),

  // Incidents
  listIncidents: (params = {}) => {
    const query = qs(params, { per_page: 25 })
    return get(`/incidents${query ? `?${query}` : ''}`)
  },
  createIncident: (payload) => post('/incidents', payload),
  updateIncident: (id, payload) => put(`/incidents/${id}`, payload),
  deleteIncident: (id) => del(`/incidents/${id}`),

  // Problems
  listProblems: (params = {}) => {
    const query = qs(params, { per_page: 25 })
    return get(`/problems${query ? `?${query}` : ''}`)
  },
  createProblem: (payload) => post('/problems', payload),
  updateProblem: (id, payload) => put(`/problems/${id}`, payload),
  deleteProblem: (id) => del(`/problems/${id}`),

  // Audit logs
  listAuditLogs: (params = {}) => {
    const qs = new URLSearchParams({ ...params, per_page: params.per_page || 100 }).toString()
    return get(`/audit-logs${qs ? `?${qs}` : ''}`)
  },

  // Master data
  listDepartments: (params = {}) => {
    const query = qs(params, { per_page: 100 })
    return get(`/departments${query ? `?${query}` : ''}`)
  },
  createDepartment: (payload) => post('/departments', payload),
  updateDepartment: (id, payload) => put(`/departments/${id}`, payload),
  deleteDepartment: (id) => del(`/departments/${id}`),

  listLocations: (params = {}) => {
    const query = qs(params, { per_page: 100 })
    return get(`/locations${query ? `?${query}` : ''}`)
  },
  createLocation: (payload) => post('/locations', payload),
  updateLocation: (id, payload) => put(`/locations/${id}`, payload),
  deleteLocation: (id) => del(`/locations/${id}`),

  listCategories: (params = {}) => {
    const query = qs(params, { per_page: 100 })
    return get(`/categories${query ? `?${query}` : ''}`)
  },
  createCategory: (payload) => post('/categories', payload),
  updateCategory: (id, payload) => put(`/categories/${id}`, payload),
  deleteCategory: (id) => del(`/categories/${id}`),

  listBrands: (params = {}) => {
    const query = qs(params, { per_page: 100 })
    return get(`/brands${query ? `?${query}` : ''}`)
  },
  createBrand: (payload) => post('/brands', payload),
  updateBrand: (id, payload) => put(`/brands/${id}`, payload),
  deleteBrand: (id) => del(`/brands/${id}`),

  listModels: (params = {}) => {
    const query = qs(params, { per_page: 100 })
    return get(`/models${query ? `?${query}` : ''}`)
  },
  createModel: (payload) => post('/models', payload),
  updateModel: (id, payload) => put(`/models/${id}`, payload),
  deleteModel: (id) => del(`/models/${id}`),

  // Requests
  listRequests: (params = {}) => {
    const query = qs(params, { per_page: 25 })
    return get(`/requests${query ? `?${query}` : ''}`)
  },
  createRequest: (payload) => post('/requests', payload),
  updateRequest: (id, payload) => put(`/requests/${id}`, payload),
  deleteRequest: (id) => del(`/requests/${id}`),

  // Changes
  listChanges: (params = {}) => {
    const query = qs(params, { per_page: 25 })
    return get(`/changes${query ? `?${query}` : ''}`)
  },
  createChange: (payload) => post('/changes', payload),
  updateChange: (id, payload) => put(`/changes/${id}`, payload),
  deleteChange: (id) => del(`/changes/${id}`),
  approveChange: (id, payload) => post(`/changes/${id}/approve`, payload || {}),
  rejectChange: (id, payload) => post(`/changes/${id}/reject`, payload || {}),

  listAssetFiles: (id) => get(`/assets/${id}/files`),
  uploadAssetFile: async (id, file) => {
    const form = new FormData(); form.append('file', file)
    await ensureCsrfToken()
    const res = await fetch(`${BASE}/assets/${id}/files`, { method: 'POST', credentials: 'include', headers: { 'X-CSRF-Token': csrfToken }, body: form })
    if (!res.ok) throw { data: await res.json() }
    return res.json()
  },
  deleteAssetFile: (id, fid) => del(`/assets/${id}/files/${fid}`),

  // Status Labels
  listStatusLabels: () => get('/status-labels'),
  createStatusLabel: (p) => post('/status-labels', p),
  deleteStatusLabel: (id) => del(`/status-labels/${id}`),

  // Licenses
  listLicenses: (params = {}) => { const query = qs(params, { per_page: 25 }); return get(`/licenses${query ? '?'+query : ''}`) },
  createLicense: (p) => post('/licenses', p),
  updateLicense: (id, p) => put(`/licenses/${id}`, p),
  deleteLicense: (id) => del(`/licenses/${id}`),

  // Checkout
  checkoutAsset: (id, p) => post(`/assets/${id}/checkout`, p),
  checkinAsset: (id, p) => post(`/assets/${id}/checkin`, p),
  assetHistory: (id) => get(`/assets/${id}/history`),

  // Reports
  dashboardSummary: () => get('/dashboard/summary'),
  fullAssetReport: (params = {}) => get(`/reports/assets/full?${qs(params, { per_page: 500 })}`),
  assetsWarrantyExpiring: (months = 3) => get(`/reports/assets/warranty-expiring?months=${months}`),
}

export default apiClient
