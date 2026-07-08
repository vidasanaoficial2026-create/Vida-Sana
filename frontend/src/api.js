const BASE = '/api'

async function request(method, path, body) {
  const opts = { method, headers: {} }
  if (body) {
    opts.headers['Content-Type'] = 'application/json'
    opts.body = JSON.stringify(body)
  }
  const res = await fetch(BASE + path, opts)
  const data = await res.json()
  if (!res.ok && !data.ok) throw new Error(data.error || data.detail?.error || 'Error')
  return data
}

export const api = {
  productos: {
    list: (params) => {
      const q = new URLSearchParams(params || {}).toString()
      return request('GET', `/productos${q ? '?' + q : ''}`)
    },
    get: (id) => request('GET', `/productos/${id}`),
    create: (data) => request('POST', '/productos', data),
    update: (id, data) => request('PUT', `/productos/${id}`, data),
    delete: (id) => request('DELETE', `/productos/${id}`),
  },
  workers: {
    list: (search) => request('GET', `/workers${search ? '?search=' + encodeURIComponent(search) : ''}`),
    get: (id) => request('GET', `/workers/${id}`),
    count: () => request('GET', '/workers/count'),
    create: (data) => request('POST', '/workers', data),
    update: (id, data) => request('PUT', `/workers/${id}`, data),
    delete: (id) => request('DELETE', `/workers/${id}`),
  },
}
