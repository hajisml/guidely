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
