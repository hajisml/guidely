export default function DocTable({ docs, onEdit, onDelete }) {
  if (!docs.length) return <p>No documents yet. Upload one to get started.</p>
  return (
    <table className="doc-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Size</th>
          <th>Modified</th>
          <th />
        </tr>
      </thead>
      <tbody>
        {docs.map((d) => (
          <tr key={d.name}>
            <td>{d.name}</td>
            <td>{(d.size / 1024).toFixed(1)} KB</td>
            <td>{new Date(d.modified).toLocaleString()}</td>
            <td className="row-actions">
              <button onClick={() => onEdit(d.name)}>Edit</button>
              <button className="danger" onClick={() => onDelete(d.name)}>Delete</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
