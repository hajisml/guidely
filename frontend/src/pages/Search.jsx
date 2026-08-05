import { useState } from 'react'
import { ask } from '../api'
import SourceList from '../components/SourceList'

export default function Search() {
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function onSubmit(e) {
    e.preventDefault()
    if (!question.trim() || loading) return
    setLoading(true)
    setError(null)
    try {
      setResult(await ask(question))
    } catch (err) {
      setResult(null)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section>
      <h1>Ask Guidely</h1>
      <form onSubmit={onSubmit} className="search-form">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. How many days of annual leave do I get?"
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Thinking…' : 'Ask'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="answer">
          <p>{result.answer}</p>
          <SourceList sources={result.sources} />
          <p className="latency">answered in {(result.latency_ms / 1000).toFixed(1)}s</p>
        </div>
      )}
    </section>
  )
}
