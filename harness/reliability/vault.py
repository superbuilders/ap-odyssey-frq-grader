"""The sealed holdout.

2025's 18 essays are sealed. The loop iterates on the 36 from 2023-24 and may
never read 2025 until the final verdict. This is enforced by a counter on disk
rather than by discipline, because the failure mode we are guarding against is
an optimizer that looks a few extra times and nobody notices.

Why a counter at all: a search over this same corpus already produced 36/54
in-sample and 24/54 held out. Every look at held-out data spends a little of
its independence, so the looks are rationed and recorded.
"""
import hashlib, json, os, pathlib

VAULT_DIR = pathlib.Path("/tmp/jev-reliability/vault")
MANIFEST = VAULT_DIR / "manifest.json"
LEDGER = VAULT_DIR / "reads.jsonl"
BLIND = "/tmp/jev-arm/blind/essays.jsonl"

SEALED_YEAR = "2025"
READ_BUDGET = 3


def _load_all():
    return [json.loads(l) for l in open(BLIND, encoding="utf-8")]


def seal():
    """Split the corpus, hash the sealed half, write the manifest. Idempotent."""
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    rows = _load_all()
    sealed = sorted(r["essay_id"] for r in rows if r["year"] == SEALED_YEAR)
    working = sorted(r["essay_id"] for r in rows if r["year"] != SEALED_YEAR)
    digest = hashlib.sha256("\n".join(sealed).encode()).hexdigest()
    man = {"sealed_year": SEALED_YEAR, "sealed_ids": sealed, "sealed_sha256": digest,
           "working_ids": working, "read_budget": READ_BUDGET}
    if MANIFEST.exists():
        old = json.loads(MANIFEST.read_text())
        if old["sealed_sha256"] != digest:
            raise RuntimeError("vault contents changed after sealing; refusing to re-seal")
        return old
    MANIFEST.write_text(json.dumps(man, indent=2))
    LEDGER.touch()
    return man


def working_set():
    """The 36 essays the loop may use. No read is recorded; these are not held out."""
    man = seal()
    ids = set(man["working_ids"])
    return [r for r in _load_all() if r["essay_id"] in ids]


def reads_spent():
    if not LEDGER.exists():
        return 0
    return sum(1 for l in LEDGER.read_text().splitlines() if l.strip())


def open_vault(reason, confirm=False):
    """Read the sealed 18. Records the read. Raises past budget.

    `reason` is written to the ledger so a later reader can tell a planned
    verdict from a casual peek.
    """
    man = seal()
    spent = reads_spent()
    if spent >= man["read_budget"]:
        raise RuntimeError(
            "vault read budget exhausted (%d/%d). Previous reads:\n%s"
            % (spent, man["read_budget"], LEDGER.read_text()))
    if not confirm:
        raise RuntimeError("open_vault requires confirm=True; this spends a holdout read")
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps({"read": spent + 1, "reason": reason}) + "\n")
    ids = set(man["sealed_ids"])
    return [r for r in _load_all() if r["essay_id"] in ids]


if __name__ == "__main__":
    m = seal()
    print("sealed  %s: %d essays, sha256 %s" % (m["sealed_year"], len(m["sealed_ids"]), m["sealed_sha256"][:16]))
    print("working    : %d essays" % len(m["working_ids"]))
    print("reads spent: %d / %d" % (reads_spent(), m["read_budget"]))
