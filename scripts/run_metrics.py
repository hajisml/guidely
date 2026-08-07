"""Run the checks behind the Testing & Metrics table in the README.

Needs the backend running on localhost:8000 with an indexed corpus:
    python scripts/run_metrics.py
"""

import json
import statistics
import sys
import time
import urllib.error
import urllib.request

BASE = "http://localhost:8000"

# question -> doc expected in the top-3 sources
SEED_QUERIES = {
    "How many days of annual leave do I get per year?": "leave-policy.txt",
    "Do sick days carry over to next year?": "leave-policy.txt",
    "How long is parental leave for primary caregivers?": "leave-policy.txt",
    "How many office days per week does hybrid work require?": "remote-work-policy.md",
    "Can I work from another country?": "remote-work-policy.md",
    "How much is the home office allowance?": "remote-work-policy.md",
    "When do I need to use the VPN?": "it-security-guide.md",
    "What is the minimum password length?": "it-security-guide.md",
    "What should I do if I clicked a phishing link?": "it-security-guide.md",
    "What is the deadline for submitting expenses?": "expense-faq.md",
    "Who approves expenses above 2000 dollars?": "expense-faq.md",
    "What is the daily meal allowance when traveling?": "expense-faq.md",
    "What trainings are mandatory in the first two weeks?": "onboarding-guide.md",
    "When does payroll run?": "onboarding-guide.md",
    "How fast must a lost laptop be reported?": "incident-response-howto.txt",
    "When is a post-mortem required?": "incident-response-howto.txt",
}

CACHE_REPEAT = 5


def call(path, payload=None, method=None):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Content-Type": "application/json"} if payload is not None else {},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            return res.status, json.loads(res.read())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())


def main():
    status, _ = call("/health")
    if status != 200:
        sys.exit("backend not healthy, start it first")

    print("== Retrieval@3 + latency ==")
    top3_hits = 0
    referenced = 0
    latencies = []
    for question, expected_doc in SEED_QUERIES.items():
        started = time.perf_counter()
        status, body = call("/api/search", {"question": question})
        wall_ms = (time.perf_counter() - started) * 1000
        if status != 200:
            print(f"  FAIL ({status}) {question}: {body.get('error')}")
            continue
        latencies.append(wall_ms)
        docs = [s["doc"] for s in body["sources"][:3]]
        ok = expected_doc in docs
        top3_hits += ok
        referenced += bool(body["sources"])
        print(f"  {'ok ' if ok else 'MISS'} {wall_ms:6.0f}ms  {question}")

    n = len(SEED_QUERIES)
    retrieval = top3_hits / n
    coverage = referenced / n
    median = statistics.median(latencies)
    p95 = statistics.quantiles(latencies, n=20)[-1] if len(latencies) >= 2 else latencies[0]

    print("\n== Embedding cache (repeat queries) ==")
    _, before = call("/metrics")
    for question in list(SEED_QUERIES)[:CACHE_REPEAT]:
        call("/api/search", {"question": question})
    _, after = call("/metrics")
    new_misses = after["embedding_cache"]["misses"] - before["embedding_cache"]["misses"]
    new_hits = after["embedding_cache"]["hits"] - before["embedding_cache"]["hits"]
    cache_rate = new_hits / (new_hits + new_misses) if (new_hits + new_misses) else 0
    print(f"  repeats: {CACHE_REPEAT}, cache hits: {new_hits}, new embeddings: {new_misses}")

    print("\n== Failure handling ==")
    failures = {
        "empty query": call("/api/search", {"question": "  "})[0] == 400,
        "invalid body": call("/api/search", {"nope": 1})[0] == 400,
        "no results": call("/api/search", {"question": "recipe for chocolate lava cake"})[0] == 404,
    }
    for name, ok in failures.items():
        print(f"  {'ok ' if ok else 'FAIL'} {name}")

    print("\n== Summary (paste into README) ==")
    print(f"| Retrieval@3 | >= 80% | {retrieval:.0%} ({top3_hits}/{n}) |")
    print(f"| Answer reference coverage | >= 90% | {coverage:.0%} |")
    print(f"| Latency median / p95 | < 3s / < 5s | {median/1000:.2f}s / {p95/1000:.2f}s |")
    print(f"| Cache hit rate on repeats | 100% | {cache_rate:.0%} |")
    print(f"| Failure cases | 4xx/5xx + error json | {sum(failures.values())}/{len(failures)} pass |")


if __name__ == "__main__":
    main()
