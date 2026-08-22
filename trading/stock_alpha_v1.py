"""PIT Nifty-500 cross-sectional alpha research.

Data policy: only direct circular/merger membership rows are eligible. Prices are
fetched at test time from Yahoo Finance; this is a research data source, not an
official NSE feed. Signals use only information available before the rebalance.
No optimization is performed in this script.
"""
from __future__ import annotations
import argparse, json, time
from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf

DIRECT = {"circular", "merger"}

def load_membership(path):
    x = pd.read_csv(path)
    x = x[x.source.isin(DIRECT)].copy()
    x.valid_from = pd.to_datetime(x.valid_from)
    x.valid_to = pd.to_datetime(x.valid_to)
    return x

def fetch_prices(symbols, start, end):
    out = {}
    for i in range(0, len(symbols), 40):
        batch = symbols[i:i+40]
        tickers = [s + ".NS" for s in batch]
        d = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False, group_by="column", threads=True)
        if d.empty: continue
        close = d["Close"] if isinstance(d.columns, pd.MultiIndex) else d
        if isinstance(close, pd.Series): close = close.to_frame()
        for col in close.columns:
            sym = str(col).replace(".NS", "")
            out[sym] = close[col].dropna()
        time.sleep(0.2)
    return pd.DataFrame(out).sort_index()

def maxdd(r):
    eq=(1+r.fillna(0)).cumprod(); return float((eq/eq.cummax()-1).min())

def stats(r):
    r=r.dropna(); years=len(r)/252
    cagr=float((1+r).prod()**(1/years)-1) if years else np.nan
    sh=float(np.sqrt(252)*r.mean()/r.std()) if r.std()>0 else np.nan
    return {"cagr":cagr,"sharpe":sh,"max_drawdown":maxdd(r),"days":int(len(r))}

def backtest(px, mem, cost=0.002):
    dates=px.index
    rebal=dates.to_series().groupby(dates.to_period("M")).last().values
    port=pd.Series(0.0,index=dates); prev={}
    turnover=0.0; held_days=0
    for d in rebal:
        d=pd.Timestamp(d)
        hist=px.loc[:d].iloc[:-1]
        if len(hist)<260: continue
        eligible=[]
        for s in px.columns:
            m=mem[mem.symbol.eq(s)]
            if m.empty: continue
            ok=((m.valid_from<=d)&(m.valid_to.isna()| (m.valid_to>d))).any()
            if ok and s in hist.columns: eligible.append(s)
        if not eligible: continue
        h=hist[eligible]
        p=h.iloc[-1]; p252=h.iloc[-253] if len(h)>=253 else pd.Series(dtype=float); p21=h.iloc[-22] if len(h)>=22 else pd.Series(dtype=float)
        mom=(p/p252-1.0).replace([np.inf,-np.inf],np.nan)
        short=(p/p21-1.0).replace([np.inf,-np.inf],np.nan)
        vol=h.pct_change().iloc[-63:].std()*np.sqrt(252)
        trend=p/h.iloc[-201].replace(0,np.nan)-1
        score=pd.concat([mom.rename("mom"),short.rename("short"),(-vol).rename("lowvol"),trend.rename("trend")],axis=1).dropna()
        if len(score)<20: continue
        # Fixed, pre-registered composite: 40% 12m momentum, 20% 1m momentum,
        # 20% trend, 20% inverse volatility. No tuning after results.
        z=(score-score.mean())/score.std(ddof=0).replace(0,np.nan)
        z["score"]=0.4*z.mom+0.2*z.short+0.2*z.trend+0.2*z.lowvol
        picks=z.score.nlargest(20).index
        w=pd.Series(0.0,index=px.columns); w.loc[picks]=1/len(picks)
        turn=float(sum(abs(w.get(s,0)-prev.get(s,0)) for s in set(w.index)|set(prev)))
        turnover+=turn; prev=w.to_dict()
        nxt=dates[dates>d]
        end=nxt[-1] if len(nxt) else dates[-1]
        seg=px.loc[d:end].pct_change().iloc[1:]
        daily=(seg* w).sum(axis=1)
        daily.iloc[0]-=cost*turn
        port.loc[daily.index]=daily
        held_days+=len(daily)
    port=port.replace(0,np.nan).dropna()
    return port,turnover

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--membership",default="data/pit/index_membership_history.csv"); ap.add_argument("--out",default="data/stock_alpha_v1"); args=ap.parse_args()
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    mem=load_membership(args.membership)
    symbols=sorted(mem.symbol.unique())
    px=fetch_prices(symbols,"2014-01-01","2026-08-01")
    px.to_csv(out/"prices.csv")
    port,turn=backtest(px,mem,0.002)
    result={"strategy":"PIT Nifty500 Cross-Sectional Alpha V1","cost_bps":20,"universe_rule":"direct circular/merger membership only","top_n":20,"rebalance":"monthly","stats":stats(port),"turnover_one_way_sum":turn}
    (out/"result.json").write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
if __name__=="__main__": main()
