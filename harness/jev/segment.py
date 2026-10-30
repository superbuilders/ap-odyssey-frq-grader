"""Deterministic 3-tier body-segmenter. Operates ONLY on blind field essay_text."""
import re, statistics, math

NL = "\n"

def _sentences(t):
    s = re.split(r"(?<=[.!?\"”])\s+", re.sub(r"\s+", " ", t).strip())
    return [x.strip() for x in s if x.strip()]

def segments(text):
    """Return (tier, [segment strings])."""
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    if len(blocks) >= 3:
        return "blank-line", [re.sub(r"\s+", " ", b) for b in blocks]
    lines = [l for l in text.split(NL) if l.strip()]
    if len(lines) >= 6:
        lens = [len(l) for l in lines]
        W = statistics.median(lens)
        paras, cur = [], []
        for l in lines:
            cur.append(l.strip())
            if len(l) < 0.78 * W:
                paras.append(" ".join(cur)); cur = []
        if cur: paras.append(" ".join(cur))
        paras = [p for p in paras if p]
        if len(paras) >= 3:
            return "wrap-width", paras
    sents = _sentences(text)
    words = len(text.split())
    K = max(3, min(6, round(words / 120)))
    K = min(K, len(sents))
    if K < 1: K = 1
    per = math.ceil(len(sents) / K)
    return "sentence-chunk", [" ".join(sents[i:i + per]) for i in range(0, len(sents), per)]
