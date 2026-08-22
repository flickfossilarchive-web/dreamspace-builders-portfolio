"""Fetch and validate the public PIT NSE membership ledger with resilient retrieval."""
from __future__ import annotations
import argparse,hashlib,json,time
from io import StringIO
from pathlib import Path
from urllib.request import Request,urlopen
import pandas as pd

RAW_URL="https://raw.githubusercontent.com/aditya-jha/nse-historical-membership/main/index_history/data/index_membership_history.csv"
META_URL="https://api.github.com/repos/aditya-jha/nse-historical-membership/commits/main"
DIRECT_SOURCES={"press_release","circular","merger"}

def get(url:str,retries:int=5)->bytes:
    last=None
    for i in range(retries):
        try:
            req=Request(url,headers={"User-Agent":"dreamspace-research/1.0","Accept":"application/vnd.github+json"})
            with urlopen(req,timeout=90) as r:return r.read()
        except Exception as e:
            last=e
            if i+1<retries:time.sleep(2**i)
    raise last

def count_overlaps(x):
    n=0
    for _,g in x.sort_values(["symbol","valid_from"]).groupby("symbol"):
        prev_end=None
        for _,row in g.iterrows():
            if prev_end is not None and row.valid_from<prev_end:n+=1
            end=row.valid_to if pd.notna(row.valid_to) else pd.Timestamp.max
            prev_end=end if prev_end is None else max(prev_end,end)
    return n

def validate(df,index_name="Nifty 500"):
    req={"index_name","symbol","valid_from","valid_to","source"}
    missing=req-set(df.columns)
    if missing:raise ValueError(f"missing columns: {sorted(missing)}")
    x=df[df.index_name.eq(index_name)].copy()
    if x.empty:raise ValueError(f"no {index_name} rows")
    x["valid_from"]=pd.to_datetime(x.valid_from,errors="coerce");x["valid_to"]=pd.to_datetime(x.valid_to,errors="coerce")
    if x.valid_from.isna().any():raise ValueError("invalid valid_from values")
    if (x.valid_to.notna()&(x.valid_to<=x.valid_from)).any():raise ValueError("non-positive membership intervals")
    direct=x[x.source.isin(DIRECT_SOURCES)]; inferred=x[~x.source.isin(DIRECT_SOURCES)]
    d_ov=count_overlaps(direct); i_ov=count_overlaps(inferred)
    if d_ov:raise ValueError(f"{d_ov} overlapping public-source intervals")
    mixed=0
    for sym in set(direct.symbol)&set(inferred.symbol):
        for _,d in direct[direct.symbol.eq(sym)].iterrows():
            for _,i in inferred[inferred.symbol.eq(sym)].iterrows():
                de=d.valid_to if pd.notna(d.valid_to) else pd.Timestamp.max;ie=i.valid_to if pd.notna(i.valid_to) else pd.Timestamp.max
                mixed+=int(max(d.valid_from,i.valid_from)<min(de,ie))
    return {"index":index_name,"rows":len(x),"symbols":x.symbol.nunique(),"start":str(x.valid_from.min().date()),"source_counts":{str(k):int(v) for k,v in x.source.value_counts().items()},"direct_source_rows":len(direct),"direct_source_fraction":len(direct)/len(x),"direct_source_overlaps":d_ov,"inferred_overlaps":i_ov,"mixed_direct_inferred_overlaps":mixed,"production_rule":"Only press_release/circular/merger rows are eligible for production-grade claims."}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out",default="data/pit/index_membership_history.csv");ap.add_argument("--report",default="data/pit/validation_report.json");a=ap.parse_args()
    raw=get(RAW_URL);meta=json.loads(get(META_URL));df=pd.read_csv(StringIO(raw.decode()))
    report=validate(df);report.update({"upstream_repository":"aditya-jha/nse-historical-membership","upstream_commit":meta["sha"],"raw_sha256":hashlib.sha256(raw).hexdigest(),"raw_url":RAW_URL})
    out=Path(a.out);rep=Path(a.report);out.parent.mkdir(parents=True,exist_ok=True);rep.parent.mkdir(parents=True,exist_ok=True)
    df[df.index_name.eq("Nifty 500")].to_csv(out,index=False);rep.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=="__main__":main()
