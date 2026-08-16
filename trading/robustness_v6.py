import io, json, urllib.request
import numpy as np
import pandas as pd

STOCKS=['lt','bhartiartl','hcltech','maruti','axisbank','sunpharma','titan','m&m','tatasteel','hindalco','cipla']
BASE='https://raw.githubusercontent.com/BennyThadikaran/eod2_data/main/daily/'
BASE_P={'sma':200,'breakout':20,'rs':63,'vol':20,'vol_mult':1.5,'atr':14,'stop_atr':2.0,'slip':.0015,'cost':.001}

def load(s):
    d=pd.read_csv(io.BytesIO(urllib.request.urlopen(BASE+s+'.csv',timeout=60).read()))
    d['Date']=pd.to_datetime(d.Date)
    return d.sort_values('Date').drop_duplicates('Date').set_index('Date')

def indicators(d,p):
    c=d.Close.astype(float); h=d.High.astype(float); l=d.Low.astype(float); v=d.Volume.astype(float)
    sma=c.rolling(p['sma']).mean(); hi=h.shift(1).rolling(p['breakout']).max()
    atr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1).rolling(p['atr']).mean()
    rv=v/v.rolling(p['vol']).mean(); rs=c.pct_change(p['rs'])
    sig=(c>sma)&(c>hi)&(rv>p['vol_mult'])&(atr/c>.01)&(atr/c<.08)&(rs>0)
    return sma,atr,sig

def run(data,start,end,p):
    data={s:d.loc[:end] for s,d in data.items()}; idx=pd.date_range(start,end,freq='B'); n=len(STOCKS); sleeve=1/n
    cash={s:sleeve for s in STOCKS}; shares={s:0. for s in STOCKS}; invested={s:0. for s in STOCKS}; stop={s:None for s in STOCKS}
    trades=[]; prep={s:indicators(d,p) for s,d in data.items()}; eq=[]
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
                    ex=o*(1-p['slip']) if o<stop[s] else stop[s]; proceeds=shares[s]*ex*(1-p['cost']); tr=proceeds/invested[s]-1
                    trades.append(tr); cash[s]=proceeds; shares[s]=0.; invested[s]=0.; stop[s]=None
            if shares[s]==0 and bool(sig.iloc[j]) and np.isfinite(float(atr.iloc[j])):
                invested[s]=cash[s]; px=o*(1+p['slip']); shares[s]=cash[s]/px; cash[s]=0.; stop[s]=px-p['stop_atr']*float(atr.iloc[j])
            total += cash[s] if shares[s]==0 else shares[s]*c
        eq.append((dt,total))
    e=pd.Series(dict(eq)).sort_index(); years=(e.index[-1]-e.index[0]).days/365.25; r=e.pct_change().fillna(0)
    return {'final':float(e.iloc[-1]),'cagr':float(e.iloc[-1]**(1/years)-1),'dd':float((e/e.cummax()-1).min()),'sharpe':float(r.mean()/r.std()*np.sqrt(252)) if r.std() else 0,'trades':trades}

def monte_carlo(trades,n=10000,seed=42):
    rng=np.random.default_rng(seed); x=np.asarray(trades,float); wealth=np.ones((n,len(x)+1));
    for i in range(n):
        seq=rng.permutation(x); wealth[i,1:]=np.cumprod(1+seq)
    final=wealth[:,-1]; dd=np.min(wealth/np.maximum.accumulate(wealth,axis=1)-1,axis=1)
    return {'simulations':n,'median_final':float(np.median(final)),'p05_final':float(np.quantile(final,.05)),'p95_final':float(np.quantile(final,.95)),'median_drawdown':float(np.median(dd)),'p05_drawdown':float(np.quantile(dd,.05)),'p95_drawdown':float(np.quantile(dd,.95)),'prob_final_below_1':float(np.mean(final<1)),'prob_drawdown_worse_than_20pct':float(np.mean(dd<-.20))}

def main():
    data={s:load(s) for s in STOCKS}; start=max(d.index[0] for d in data.values()); end=min(d.index[-1] for d in data.values())
    base=run(data,start,end,BASE_P)
    sims=monte_carlo(base['trades'])
    cases=[]
    for name,changes in [('base',{}),('sma180',{'sma':180}),('sma220',{'sma':220}),('breakout15',{'breakout':15}),('breakout25',{'breakout':25}),('rs50',{'rs':50}),('rs75',{'rs':75}),('volmult1.3',{'vol_mult':1.3}),('volmult1.7',{'vol_mult':1.7}),('atr10',{'atr':10}),('atr18',{'atr':18}),('stop1.5',{'stop_atr':1.5}),('stop2.5',{'stop_atr':2.5})]:
        p=dict(BASE_P); p.update(changes); r=run(data,start,end,p); cases.append({'case':name,'cagr':r['cagr'],'max_drawdown':r['dd'],'sharpe':r['sharpe'],'trades':len(r['trades'])})
    df=pd.DataFrame(cases); result={'period':{'start':str(start.date()),'end':str(end.date())},'base':{'cagr':base['cagr'],'max_drawdown':base['dd'],'sharpe':base['sharpe'],'trades':len(base['trades'])},'monte_carlo':sims,'parameter_sensitivity':cases,'sensitivity_summary':{'positive_cagr_cases':int((df.cagr>0).sum()),'total_cases':len(df),'min_cagr':float(df.cagr.min()),'max_cagr':float(df.cagr.max()),'min_sharpe':float(df.sharpe.min()),'max_drawdown_worst':float(df.max_drawdown.min())}}
    json.dump(result,open('portfolio_v6_robustness.json','w'),indent=2); print(json.dumps(result,indent=2))

if __name__=='__main__': main()
