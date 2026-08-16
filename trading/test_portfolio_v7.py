import io, json, urllib.request
import numpy as np
import pandas as pd

STOCKS=['lt','bhartiartl','hcltech','maruti','axisbank','sunpharma','titan','m&m','tatasteel','hindalco','cipla']
BASE='https://raw.githubusercontent.com/BennyThadikaran/eod2_data/main/daily/'
P={'trend':150,'momentum':126,'fast':50,'slow':200,'vol':20,'top_n':5,'stop_atr':3.0,'atr':20,'cost':0.001,'slip':0.0015}

def load(s):
    d=pd.read_csv(io.BytesIO(urllib.request.urlopen(BASE+s+'.csv',timeout=60).read()))
    d['Date']=pd.to_datetime(d.Date)
    return d.sort_values('Date').drop_duplicates('Date').set_index('Date')

def indicators(d):
    c=d.Close.astype(float); h=d.High.astype(float); l=d.Low.astype(float)
    sma_fast=c.rolling(P['fast']).mean(); sma_slow=c.rolling(P['slow']).mean()
    mom=c.pct_change(P['momentum'])
    tr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    atr=tr.rolling(P['atr']).mean()
    return sma_fast,sma_slow,mom,atr

def run():
    data={s:load(s) for s in STOCKS}
    end=min(d.index[-1] for d in data.values())
    start=max(d.index[0] for d in data.values())
    idx=pd.date_range(start,end,freq='B')
    ind={s:indicators(d) for s,d in data.items()}
    cash=1.0; shares={s:0.0 for s in STOCKS}; stops={s:None for s in STOCKS}; entry={s:None for s in STOCKS}; ledger=[]; eq=[]
    for dt in idx:
        rows=[]
        for s,d in data.items():
            if dt not in d.index: continue
            j=d.index.get_loc(dt)
            if j<1: continue
            o=float(d.Open.iloc[j]); c=float(d.Close.iloc[j]); low=float(d.Low.iloc[j]); prev_c=float(d.Close.iloc[j-1])
            sf,ss,mom,atr=ind[s]
            a=float(atr.iloc[j-1]) if np.isfinite(atr.iloc[j-1]) else np.nan
            score=float(mom.iloc[j-1]) if np.isfinite(mom.iloc[j-1]) else -999
            eligible=bool(np.isfinite(sf.iloc[j-1]) and np.isfinite(ss.iloc[j-1]) and np.isfinite(mom.iloc[j-1]) and prev_c>float(ss.iloc[j-1]) and float(sf.iloc[j-1])>float(ss.iloc[j-1]) and float(mom.iloc[j-1])>0)
            rows.append((s,j,o,c,low,a,score,eligible))
        eligible=[r for r in rows if r[7]]
        eligible.sort(key=lambda x:x[6],reverse=True)
        selected={r[0] for r in eligible[:P['top_n']]}
        # portfolio-level cash is allocated equally among selected names; positions are rebalanced at next open
        target=set(selected)
        # exits first
        for s,j,o,c,low,a,score,elig in rows:
            if shares[s]<=0: continue
            prev_sma=float(ind[s][1].iloc[j-1]) if np.isfinite(ind[s][1].iloc[j-1]) else np.nan
            if np.isfinite(a): stops[s]=max(stops[s],prev_c-P['stop_atr']*a)
            exit_now=(low<=stops[s]) or (not elig) or (s not in target)
            if exit_now:
                ex=o*(1-P['slip']) if o<stops[s] else stops[s]
                cash += shares[s]*ex*(1-P['cost'])
                shares[s]=0.; entry[s]=None; stops[s]=None
        # enter selected names using available cash; cap at equal weight
        available=sum(1 for s in target if shares[s]<=0)
        equity_now=cash+sum(shares[s]*next((r[3] for r in rows if r[0]==s),0) for s in STOCKS)
        if target:
            target_value=equity_now/len(target)
            for s,j,o,c,low,a,score,elig in rows:
                if s not in target or shares[s]>0 or not np.isfinite(a): continue
                px=o*(1+P['slip']); alloc=min(target_value,cash)
                if alloc<=0: continue
                shares[s]=alloc/px; cash-=alloc; entry[s]=dt; stops[s]=px-P['stop_atr']*a
        total=cash
        for s,j,o,c,low,a,score,elig in rows: total+=shares[s]*c
        eq.append((dt,total))
    e=pd.Series(dict(eq)).sort_index(); daily=e.pct_change().fillna(0)
    years=(e.index[-1]-e.index[0]).days/365.25
    result={'strategy':'V7 regime-filtered cross-sectional momentum','period_start':str(e.index[0].date()),'period_end':str(e.index[-1].date()),'final_equity':float(e.iloc[-1]),'cagr':float(e.iloc[-1]**(1/years)-1),'total_return':float(e.iloc[-1]-1),'max_drawdown':float((e/e.cummax()-1).min()),'sharpe':float(daily.mean()/daily.std()*np.sqrt(252)),'stocks':STOCKS,'top_n':P['top_n'],'execution':'prior completed daily bar signals; next-open execution; ATR stop with gap handling'}
    json.dump(result,open('portfolio_v7_results.json','w'),indent=2)
    pd.DataFrame({'date':e.index.astype(str),'equity':e.values,'daily_return':daily.values}).to_csv('portfolio_v7_equity.csv',index=False)
    print(json.dumps(result,indent=2))

if __name__=='__main__': run()
