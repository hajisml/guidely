export default function SourceList({ sources }) {
  if (!sources?.length) return null
  return (
    <div className="sources">
      <h2>Sources</h2>
      <ol>
        {sources.map((s, i) => (
          <li key={`${s.doc}-${s.chunk_id}`}>
            <details>
              <summary>
                <strong>{s.doc}</strong>
                <span className="score">match {(s.score * 100).toFixed(0)}%</span>
              </summary>
              <blockquote>{s.snippet}</blockquote>
            </details>
          </li>
        ))}
      </ol>
    </div>
  )
}
