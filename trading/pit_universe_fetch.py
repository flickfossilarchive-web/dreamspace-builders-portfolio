"""Fetch and validate a public PIT NSE membership ledger.

The ledger is derived from public NSE circulars/press releases by the upstream
nse-historical-membership project. It is NOT treated as official NSE data.
Every run records the upstream commit and validation coverage so research
results can be traced to an immutable input.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from io import StringIO
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

RAW_URL = (
    "https://raw.githubusercontent.com/aditya-jha/nse-historical-membership/"
    "main/index_history/data/index_membership_history.csv"
)
META_URL = "https://api.github.com/repos/aditya-jha/nse-historical-membership/commits/main"


def get(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "dreamspace-research/1.0"})
    with urlopen(req, timeout=60) as r:
        return r.read()


def validate(df: pd.DataFrame, index_name: str = "Nifty 500") -> dict:
    required = {"index_name", "symbol", "valid_from", "valid_to", "source"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    x = df[df.index_name.eq(index_name)].copy()
    if x.empty:
        raise ValueError(f"no {index_name} rows")
    x["valid_from"] = pd.to_datetime(x.valid_from, errors="coerce")
    x["valid_to"] = pd.to_datetime(x.valid_to, errors="coerce")
    if x.valid_from.isna().any():
        raise ValueError("invalid valid_from values")
    if (x.valid_to.notna() & (x.valid_to <= x.valid_from)).any():
        raise ValueError("non-positive membership intervals")
    # A symbol may have multiple non-overlapping intervals, but never overlapping ones.
    overlaps = 0
    for sym, g in x.sort_values(["symbol", "valid_from"]).groupby("symbol"):
        prev_end = None
        for _, row in g.iterrows():
            if prev_end is not None and row.valid_from < prev_end:
                overlaps += 1
            if pd.notna(row.valid_to):
                prev_end = max(prev_end, row.valid_to) if prev_end is not None else row.valid_to
            else:
                prev_end = pd.Timestamp.max
    if overlaps:
        raise ValueError(f"{overlaps} overlapping membership intervals")
    # Do not silently use inferred intervals as production-grade observations.
    source_counts = x.source.value_counts(dropna=False).to_dict()
    exact = int(x.source.isin(["circular", "merger"]).sum())
    return {
        "index": index_name,
        "rows": int(len(x)),
        "symbols": int(x.symbol.nunique()),
        "start": str(x.valid_from.min().date()),
        "end": None if x.valid_to.isna().any() else str(x.valid_to.max().date()),
        "source_counts": {str(k): int(v) for k, v in source_counts.items()},
        "direct_source_rows": exact,
        "direct_source_fraction": exact / len(x),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/pit/index_membership_history.csv")
    ap.add_argument("--report", default="data/pit/validation_report.json")
    args = ap.parse_args()
    raw = get(RAW_URL)
    meta = json.loads(get(META_URL))
    sha = hashlib.sha256(raw).hexdigest()
    df = pd.read_csv(StringIO(raw.decode("utf-8")))
    report = validate(df)
    report.update({
        "upstream_repository": "aditya-jha/nse-historical-membership",
        "upstream_commit": meta["sha"],
        "raw_sha256": sha,
        "raw_url": RAW_URL,
        "production_rule": "Only circular/merger rows are eligible for production-grade claims; inferred rows are retained for research diagnostics.",
    })
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    rep = Path(args.report); rep.parent.mkdir(parents=True, exist_ok=True)
    # Keep only the requested broad index for the downstream engine.
    df[df.index_name.eq("Nifty 500")].to_csv(out, index=False)
    rep.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
