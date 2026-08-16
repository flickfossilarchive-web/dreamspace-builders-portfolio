import io, json, urllib.request
import numpy as np
import pandas as pd

STOCKS=['lt','bhartiartl','hcltech','maruti','axisbank','sunpharma','titan','m&m','tatasteel','hindalco','cipla']
BASE='https://raw.githubusercontent.com/BennyThadikaran/eod2_data/main/daily/'
P={'sma':200,'breakout':20,'rs':63,'vol':20,'vol_mult':1.5,'atr':14,'stop_atr':2.0,'slip':.0015,'cost':.001}

def load(s):
    d=pd.read_csv(io.BytesIO(urllib.request.urlopen(BASE+s+'.csv',timeout=60).read()))
    d['Date']=pd.to_datetime(d.Date); return d.sort_values('Date').drop_duplicates('Date').set_index('Date')

def indicators(d,p):
    c=d.Close.astype(float); h=d.High.astype(float); l=d.Low.astype(float); v=d.Volume.astype(float)
    sma=c.rolling(p['sma']).mean(); hi=h.shift(1).rolling(p['breakout']).max()
    atr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1).rolling(p['atr']).mean()
    rv=v/v.rolling(p['vol']).mean(); rs=c.pct_change(p['rs'])
    sig=(c>sma)&(c>hi)&(rv>p['vol_mult'])&(atr/c>.01)&(atr/c<.08)&(rs>0)
    return sma,atr,sig

def run(data,start,end,p):
    data={s:d.loc[:end] for s,d in data.items()}; idx=pd.date_range(start,end,freq='B'); sleeve=1/len(STOCKS)
    cash={s:sleeve for s in STOCKS}; shares={s:0. for s in STOCKS}; invested={s:0. for s in STOCKS}; stop={s:None for s in STOCKS}; trades=[]
    prep={s:indicators(d,p) for s,d in data.items()}; eq=[]
    for dt in idx:
        total=0.
        for s,d in data.items():
            if dt not in d.index:
                total += shares[s]*float(d.Close.loc[:dt].iloc[-1]) if shares[s] else cash[s]; continue
            j=d.index.get_loc(dt); o=float(d.Open.iloc[j]); l=float(d.Low.iloc[j]); c=float(d.Close.iloc[j]); sma,atr,sig=prep[s]
            if shares[s]>0:
                a=float(atr.iloc[j]);
                if np.isfinite(a): stop[s]=max(stop[s],c-p['stop_atr']*a)
                reason='stop' if l<=stop[s] else ('sma' if np.isfinite(float(sma.iloc[j])) and c<float(sma.iloc[j]) else None)
                if reason:
                    ex=o*(1-p['slip']) if o<stop[s] else stop[s]; proceeds=shares[s]*ex*(1-p['cost']); trades.append(proceeds/invested[s]-1)
                    cash[s]=proceeds; shares[s]=0.; invested[s]=0.; stop[s]=None
            if shares[s]==0 and bool(sig.iloc[j]) and np.isfinite(float(atr.iloc[j])):
                invested[s]=cash[s]; px=o*(1+p['slip']); shares[s]=cash[s]/px; cash[s]=0.; stop[s]=px-p['stop_atr']*float(atr.iloc[j])
            total += cash[s] if shares[s]==0 else shares[s]*c
        eq.append((dt,total))
    e=pd.Series(dict(eq)).sort_index(); years=(e.index[-1]-e.index[0]).days/365.25
    return {'trades':trades,'years':years,'base_final':float(e.iloc[-1])}

def bootstrap(trades,years,n=10000,block=10,seed=20260816):
    x=np.asarray(trades,float); m=len(x); rng=np.random.default_rng(seed); finals=np.empty(n); dds=np.empty(n)
    starts=np.arange(m)
    for k in range(n):
        seq=[]
        while len(seq)<m:
            st=int(rng.choice(starts)); seq.extend(x[np.arange(st,st+block)%m])
        seq=np.asarray(seq[:m]); w=np.cumprod(np.r_[1.,1.+seq]); finals[k]=w[-1]; dds[k]=np.min(w/np.maximum.accumulate(w)-1)
    cagr=finals**(1/years)-1
    return {'simulations':n,'block_size':block,'median_final':float(np.median(finals)),'p05_final':float(np.quantile(finals,.05)),'p95_final':float(np.quantile(finals,.95)),'median_cagr':float(np.median(cagr)),'p05_cagr':float(np.quantile(cagr,.05)),'p95_cagr':float(np.quantile(cagr,.95)),'median_drawdown':float(np.median(dds)),'p05_drawdown':float(np.quantile(dds,.05)),'p95_drawdown':float(np.quantile(dds,.95)),'prob_final_below_1':float(np.mean(finals<1)),'prob_cagr_below_0':float(np.mean(cagr<0)),'prob_drawdown_worse_than_20pct':float(np.mean(dds<-.20)),'prob_drawdown_worse_than_30pct':float(np.mean(dds<-.30)),'prob_drawdown_worse_than_40pct':float(np.mean(dds<-.40))}

def main():
    data={s:load(s) for s in STOCKS}; start=max(d.index[0] for d in data.values()); end=min(d.index[-1] for d in data.values()); r=run(data,start,end,P)
    out={'period':{'start':str(start.date()),'end':str(end.date())},'observed':{'trades':len(r['trades']),'final':r['base_final'],'years':r['years']},'block_bootstrap':bootstrap(r['trades'],r['years'])}
    json.dump(out,open('portfolio_v6_bootstrap_mc.json','w'),indent=2); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
