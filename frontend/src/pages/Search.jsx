import { useState } from 'react'
import { ask } from '../api'

export default function Search() {
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState(null)

  async function onSubmit(e) {
    e.preventDefault()
    if (!question.trim()) return
    const res = await ask(question)
    setResult(res)
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
        <button type="submit">Ask</button>
      </form>

      {result && (
        <div className="answer">
          <p>{result.answer}</p>
        </div>
      )}
    </section>
  )
}
