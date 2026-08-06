import { useCallback, useEffect, useState } from 'react'
import { listDocs } from '../api'
import DocTable from '../components/DocTable'
import UploadForm from '../components/UploadForm'

export default function Admin() {
  const [docs, setDocs] = useState([])
  const [error, setError] = useState(null)

  const refresh = useCallback(() => {
    listDocs().then(setDocs).catch((err) => setError(err.message))
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  return (
    <section>
      <h1>Manage documents</h1>
      <UploadForm onUploaded={refresh} />
      {error && <p className="error">{error}</p>}
      <DocTable docs={docs} onEdit={() => {}} onDelete={() => {}} />
    </section>
  )
}
