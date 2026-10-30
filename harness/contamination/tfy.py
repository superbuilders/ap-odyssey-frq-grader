"""Gateway client. NOTE: `temperature` is REJECTED by this gateway
("`temperature` is deprecated for this model", HTTP 400) -- the previous probe run
sent temperature:0.0 and all 174 calls failed. Do not add it back."""
import json, os, time, urllib.request, urllib.error

URL = "https://tfy.promptlens.trilogy.com/v1/messages"
MODELS = ["claude-group/claude-sonnet-5", "claude-group/claude-opus-5"]
_stats = {"calls": 0, "errors": 0, "in_tok": 0, "out_tok": 0}

def call(model, prompt, max_tokens=2400, retries=5, timeout=300):
    body = json.dumps({"model": model, "max_tokens": max_tokens,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(URL, data=body, method="POST", headers={
            "Authorization": "Bearer " + os.environ["TFY_API_KEY"],
            "anthropic-version": "2023-06-01", "content-type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.loads(r.read())
            u = d.get("usage", {})
            _stats["calls"] += 1
            _stats["in_tok"] += u.get("input_tokens", 0)
            _stats["out_tok"] += u.get("output_tokens", 0)
            # opus-5 emits a leading `thinking` block; take TEXT blocks only
            return "".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text")
        except urllib.error.HTTPError as e:
            last = "HTTP %s: %s" % (e.code, e.read()[:300])
            if e.code in (401, 403):
                raise RuntimeError(last)
        except Exception as e:
            last = repr(e)
        time.sleep(2.0 * (attempt + 1))
    _stats["errors"] += 1
    return "__ERROR__ " + str(last)

def stats(): return dict(_stats)
