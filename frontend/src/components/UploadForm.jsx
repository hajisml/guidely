import { useRef, useState } from 'react'
import { uploadDoc } from '../api'

export default function UploadForm({ onUploaded }) {
  const inputRef = useRef(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)

  async function onChange(e) {
    const file = e.target.files[0]
    if (!file) return
    setBusy(true)
    setError(null)
    try {
      await uploadDoc(file)
      onUploaded()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
      if (inputRef.current) inputRef.current.value = ''
    }
  }

  return (
    <div className="upload">
      <label className="upload-btn">
        {busy ? 'Uploading…' : 'Upload .txt / .md'}
        <input ref={inputRef} type="file" accept=".txt,.md" onChange={onChange} hidden />
      </label>
      {error && <p className="error">{error}</p>}
    </div>
  )
}
