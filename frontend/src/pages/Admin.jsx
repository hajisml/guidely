import { useCallback, useEffect, useState } from 'react'
import { deleteDoc, getDoc, listDocs, updateDoc } from '../api'
import DocTable from '../components/DocTable'
import UploadForm from '../components/UploadForm'

export default function Admin() {
  const [docs, setDocs] = useState([])
  const [editing, setEditing] = useState(null) // { name, content }
  const [error, setError] = useState(null)

  const refresh = useCallback(() => {
    listDocs().then(setDocs).catch((err) => setError(err.message))
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  async function onEdit(name) {
    setError(null)
    try {
      setEditing(await getDoc(name))
    } catch (err) {
      setError(err.message)
    }
  }

  async function onSave() {
    try {
      await updateDoc(editing.name, editing.content)
      setEditing(null)
      refresh()
    } catch (err) {
      setError(err.message)
    }
  }

  async function onDelete(name) {
    if (!window.confirm(`Delete ${name}?`)) return
    setError(null)
    try {
      await deleteDoc(name)
      refresh()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <section>
      <h1>Manage documents</h1>
      <UploadForm onUploaded={refresh} />
      {error && <p className="error">{error}</p>}
      <DocTable docs={docs} onEdit={onEdit} onDelete={onDelete} />

      {editing && (
        <div className="editor">
          <h2>Editing {editing.name}</h2>
          <textarea
            value={editing.content}
            onChange={(e) => setEditing({ ...editing, content: e.target.value })}
            rows={16}
          />
          <div className="editor-actions">
            <button onClick={onSave}>Save</button>
            <button onClick={() => setEditing(null)}>Cancel</button>
          </div>
        </div>
      )}
    </section>
  )
}
