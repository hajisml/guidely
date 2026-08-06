async function json(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.error || `request failed (${res.status})`)
  }
  return res.status === 204 ? null : res.json()
}

export function ask(question) {
  return fetch('/api/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  }).then(json)
}

export function listDocs() {
  return fetch('/api/documents').then(json)
}

export function getDoc(name) {
  return fetch(`/api/documents/${encodeURIComponent(name)}`).then(json)
}

export function uploadDoc(file) {
  const form = new FormData()
  form.append('file', file)
  return fetch('/api/documents', { method: 'POST', body: form }).then(json)
}

export function updateDoc(name, content) {
  return fetch(`/api/documents/${encodeURIComponent(name)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  }).then(json)
}

export function deleteDoc(name) {
  return fetch(`/api/documents/${encodeURIComponent(name)}`, { method: 'DELETE' }).then(json)
}

export function reindex() {
  return fetch('/api/documents/reindex', { method: 'POST' }).then(json)
}
