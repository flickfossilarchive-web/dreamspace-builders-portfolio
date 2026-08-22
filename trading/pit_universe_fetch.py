"""Fetch and validate a public PIT NSE membership ledger.

The ledger is derived from public NSE circulars/press releases by the upstream
nse-historical-membership project. It is NOT treated as official NSE data.
Every run records the upstream commit and validation coverage so research
results can be traced to an immutable input.
"""
from __future__ import annotations
import argparse, hashlib, json
from io import StringIO
from pathlib import Path
from urllib.request import Request, urlopen
import pandas as pd

RAW_URL=("https://raw.githubusercontent.com/aditya-jha/nse-historical-membership/"
         "main/index_history/data/index_membership_history.csv")
META_URL="https://api.github.com/repos/aditya-jha/nse-historical-membership/commits/main"
# Public-source membership observations are authoritative when they are tied
# to an NSE press release/circular or a documented merger event. Snapshot-floor
# rows are inferred and are excluded from production-grade research claims.
DIRECT_SOURCES={"press_release","circular","merger"}

def get(url:str)->bytes:
    req=Request(url,headers={"User-Agent":"dreamspace-research/1.0"})
    with urlopen(req,timeout=60) as r:return r.read()

def count_overlaps(x:pd.DataFrame)->int:
    n=0
    for _,g in x.sort_values(["symbol","valid_from"]).groupby("symbol"):
        prev_end=None
        for _,row in g.iterrows():
            if prev_end is not None and row.valid_from<prev_end:n+=1
            end=row.valid_to if pd.notna(row.valid_to) else pd.Timestamp.max
            prev_end=end if prev_end is None else max(prev_end,end)
    return n

def validate(df:pd.DataFrame,index_name="Nifty 500")->dict:
    required={"index_name","symbol","valid_from","valid_to","source"}
    missing=required-set(df.columns)
    if missing:raise ValueError(f"missing columns: {sorted(missing)}")
    x=df[df.index_name.eq(index_name)].copy()
    if x.empty:raise ValueError(f"no {index_name} rows")
    x["valid_from"]=pd.to_datetime(x.valid_from,errors="coerce")
    x["valid_to"]=pd.to_datetime(x.valid_to,errors="coerce")
    if x.valid_from.isna().any():raise ValueError("invalid valid_from values")
    if (x.valid_to.notna()&(x.valid_to<=x.valid_from)).any():raise ValueError("non-positive membership intervals")
    source_counts=x.source.value_counts(dropna=False).to_dict()
    direct=x[x.source.isin(DIRECT_SOURCES)].copy()
    inferred=x[~x.source.isin(DIRECT_SOURCES)].copy()
    direct_overlaps=count_overlaps(direct)
    inferred_overlaps=count_overlaps(inferred)
    mixed=0
    for sym in sorted(set(direct.symbol)&set(inferred.symbol)):
        d=direct[direct.symbol.eq(sym)]; i=inferred[inferred.symbol.eq(sym)]
        for _,dr in d.iterrows():
            for _,ir in i.iterrows():
                de=dr.valid_to if pd.notna(dr.valid_to) else pd.Timestamp.max
                ie=ir.valid_to if pd.notna(ir.valid_to) else pd.Timestamp.max
                if max(dr.valid_from,ir.valid_from)<min(de,ie):mixed+=1
    if direct_overlaps:raise ValueError(f"{direct_overlaps} overlapping public-source intervals")
    return {"index":index_name,"rows":int(len(x)),"symbols":int(x.symbol.nunique()),
            "start":str(x.valid_from.min().date()),"end":None if x.valid_to.isna().any() else str(x.valid_to.max().date()),
            "source_counts":{str(k):int(v) for k,v in source_counts.items()},
            "direct_source_rows":int(len(direct)),"direct_source_fraction":len(direct)/len(x),
            "direct_source_overlaps":int(direct_overlaps),"inferred_overlaps":int(inferred_overlaps),
            "mixed_direct_inferred_overlaps":int(mixed),
            "production_rule":"Only press_release/circular/merger rows are eligible for production-grade claims; inferred snapshot rows are excluded."}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out",default="data/pit/index_membership_history.csv");ap.add_argument("--report",default="data/pit/validation_report.json");a=ap.parse_args()
    raw=get(RAW_URL);meta=json.loads(get(META_URL));df=pd.read_csv(StringIO(raw.decode()))
    report=validate(df);report.update({"upstream_repository":"aditya-jha/nse-historical-membership","upstream_commit":meta["sha"],"raw_sha256":hashlib.sha256(raw).hexdigest(),"raw_url":RAW_URL})
    out=Path(a.out);rep=Path(a.report);out.parent.mkdir(parents=True,exist_ok=True);rep.parent.mkdir(parents=True,exist_ok=True)
    df[df.index_name.eq("Nifty 500")].to_csv(out,index=False);rep.write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
