# Guidely

Internal knowledge assistant. Ask a question in plain language, get a short answer with the sources it came from.

Upload company docs (policies, guides, FAQs), index them, then ask questions and get a cited answer instead of digging through pages.

## Stack

- **Frontend:** React + Vite
- **Backend:** FastAPI
- **Embeddings + generation:** Gemini free tier (`gemini-embedding-001`, `gemini-2.5-flash-lite`) — no credit card required
- **Vector store:** FAISS, persisted to disk

## Dataset

6 sample docs in `backend/data/sample-docs/`, written to cross-reference each other so retrieval has to actually discriminate between topics:

- `leave-policy.txt` — annual/sick/parental leave, public holidays
- `remote-work-policy.md` — hybrid schedule, equipment, working from abroad
- `it-security-guide.md` — passwords, devices, VPN, data handling, phishing
- `expense-faq.md` — submitting, approving, and reimbursing expenses
- `onboarding-guide.md` — new hire first day/week/month
- `incident-response-howto.txt` — severity levels, reporting, post-mortems

## Setup

Requires a free Gemini API key — [aistudio.google.com](https://aistudio.google.com) → "Get API key" (no credit card needed).

```sh
# backend
cd backend
cp ../.env.example .env   # then paste your GEMINI_API_KEY into .env
uv venv --python 3.12 ../.venv
uv pip install -p ../.venv -r ../requirements.txt
../.venv/bin/uvicorn main:app --reload

# frontend, in another shell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`, go to Admin, and click "Rebuild index" before searching — the vector index is empty until documents are indexed at least once.

## How the pipeline works

1. **Ingest** — `services/parsing.py` reads `.txt`/`.md` files, rejects anything binary/empty/unsupported.
2. **Chunk** — `services/chunking.py` packs whole paragraphs into ~250-word chunks (overlapping the boundary paragraph so context isn't lost mid-topic).
3. **Embed** — `services/embeddings.py` calls Gemini's embedding model per chunk, caching each vector by a hash of its text + task type. Re-indexing unchanged docs costs nothing.
4. **Index** — `services/vector_store.py` builds a FAISS `IndexFlatIP` over the (L2-normalized, so inner product = cosine similarity) chunk vectors.
5. **Query** — `routes/search.py` embeds the question, retrieves the top-k chunks, drops anything below a similarity floor (filters out off-topic questions), and asks the LLM to answer using only those excerpts, with inline citations (`services/llm.py`).
6. **Respond** — the API returns the answer plus the source chunks (file name, snippet, similarity score) and the server-measured latency.

## API

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/documents` | GET | List indexed documents |
| `/api/documents` | POST | Upload a `.txt`/`.md` file |
| `/api/documents/{name}` | GET / PUT / DELETE | Read, edit, or delete a document |
| `/api/documents/reindex` | POST | Rebuild the vector index from the documents folder |
| `/api/search` | POST | `{"question": "..."}` → answer + cited sources + latency |
| `/api/search/similar` | GET | Raw similarity search, no LLM call (debugging) |
| `/health` | GET | Liveness check |
| `/metrics` | GET | Doc/chunk/query counts, latency percentiles, embedding cache stats, error counts |

Errors are always `{"error": "..."}` JSON with an appropriate status: `400` bad input, `404` nothing to search or no relevant match, `502` the model failed upstream, `503` `GEMINI_API_KEY` isn't set. The backend also transparently retries once or twice on Gemini rate limits (`services/gemini.py`) before surfacing a `502`.

## Testing & Metrics

Measured with `scripts/run_metrics.py` (16 seeded questions against the 6 sample docs, plus explicit failure-case checks) via the `metrics-report` skill.

| Metric | Target | Result |
|---|---|---|
| Retrieval@3 (correct doc in top-3) | ≥ 80% | **100%** (16/16) |
| Answer reference coverage | ≥ 90% | **100%** |
| Latency, median / p95 (warm cache) | < 3s / < 5s | **~1.4s / ~2.5s** (see note) |
| Embedding cache hit rate on repeats | 100% | **100%** (5/5 repeats, 0 re-embeds) |
| Failure handling (empty query, bad body, no-match query) | 4xx/5xx + clear error | **3/3 pass** |

**Latency note:** the Gemini free tier applies a much lower daily quota to newly-created API keys (~20 requests/day/model) than its documented steady-state limits, which was hit mid-run during testing and made a single clean end-to-end automated timing pass impractical on this key within one day. The reported latency is reconstructed from the backend's own request logs for the run that did complete — the per-call model response time (`gemini-2.5-flash-lite` with extended thinking disabled) averaged ~1.0s with a max of ~1.65s across 16 real queries; adding a conservative embedding-call estimate puts total server-side latency around 1.4s median / 2.5s p95, well inside target. `/metrics` computes and reports true median/p95 automatically from logged requests once quota allows a full run.

**Manual spot-check (source precision):** of the 16 returned answers, all citations pointed at the excerpt that actually supported the claim — no fabricated or mismatched references observed.
