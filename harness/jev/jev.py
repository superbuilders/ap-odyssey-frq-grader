"""Jev client: POST /v1/systemone, returns answers dict."""
import json, os, time, urllib.request, urllib.error

URL = "https://tfy.promptlens.trilogy.com/v1/systemone"
MODEL = "typesafe-account/jev-1.14.0"
_stats = {"calls": 0, "latencies": [], "errors": 0, "in_tok": 0, "out_tok": 0}

def ask(state, questions, retries=4, timeout=120):
    body = json.dumps({"model": MODEL, "state": state, "questions": questions}).encode()
    last = None
    for attempt in range(retries):
        t0 = time.time()
        req = urllib.request.Request(URL, data=body, method="POST", headers={
            "Authorization": "Bearer " + os.environ["TFY_API_KEY"],
            "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                out = json.loads(r.read())
            _stats["calls"] += 1
            u = out.get("usage", {})
            _stats["in_tok"] += u.get("input_tokens", 0); _stats["out_tok"] += u.get("output_tokens", 0)
            _stats["latencies"].append((time.time() - t0) * 1000)
            return out
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read()[:400]!r}"
            if e.code in (400, 401, 403, 422):
                raise RuntimeError(last)
        except Exception as e:
            last = repr(e)
        time.sleep(1.5 * (attempt + 1))
    _stats["errors"] += 1
    raise RuntimeError(f"jev failed after {retries}: {last}")

def stats():
    import statistics
    L = sorted(_stats["latencies"])
    return {"calls": _stats["calls"], "errors": _stats["errors"],
            "p50_ms": statistics.median(L) if L else 0.0,
            "p95_ms": L[int(len(L) * 0.95)] if L else 0.0,
            "input_tokens": _stats["in_tok"], "output_tokens": _stats["out_tok"]}
