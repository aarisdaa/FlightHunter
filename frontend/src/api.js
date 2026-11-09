const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path, options) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    let msg = `Request failed (${res.status})`
    try {
      const body = await res.json()
      if (typeof body.detail === 'string') msg = body.detail
      else if (Array.isArray(body.detail)) msg = body.detail.map((d) => d.msg).join(', ')
    } catch { /* keep default message */ }
    throw new Error(msg)
  }
  return res.json()
}

export const getConfig = () => request('/config')
export const listWatches = () => request('/watches/')
export const createWatch = (data) => request('/watches/', { method: 'POST', body: JSON.stringify(data) })
export const refreshWatch = (id) => request(`/watches/${id}/refresh`, { method: 'POST' })
export const deleteWatch = (id) => request(`/watches/${id}`, { method: 'DELETE' })
