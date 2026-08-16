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
    cash={s:sleeve for s in STOCKS}; shares={s:0. for s in STOCKS}; entry={s:None for s in STOCKS}; invested={s:0. for s in STOCKS}; stop={s:None for s in STOCKS}
    eq=[]; trades=[]; prep={s:indicators(d,p) for s,d in data.items()}
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
                    ex=o*(1-p['slip']) if o<stop[s] else stop[s]; proceeds=shares[s]*ex*(1-p['cost']); tr=proceeds/invested[s]-1 if invested[s] else 0
                    cash[s]=proceeds; trades.append({'stock':s,'entry':str(entry[s].date()),'exit':str(dt.date()),'return':tr,'reason':reason,'invested':invested[s],'proceeds':proceeds})
                    shares[s]=0.; entry[s]=None; invested[s]=0.; stop[s]=None
            if shares[s]==0 and bool(sig.iloc[j]) and np.isfinite(float(atr.iloc[j])):
                invested[s]=cash[s]; entry_px=o*(1+p['slip']); shares[s]=cash[s]/entry_px; cash[s]=0.; entry[s]=dt; stop[s]=entry_px-p['stop_atr']*float(atr.iloc[j])
            total += cash[s] if shares[s]==0 else shares[s]*c
        eq.append((dt,total))
    e=pd.Series(dict(eq)).sort_index(); dr=e.pct_change().fillna(0); years=(e.index[-1]-e.index[0]).days/365.25
    return {'final':float(e.iloc[-1]),'cagr':float(e.iloc[-1]**(1/years)-1),'total_return':float(e.iloc[-1]-1),'max_drawdown':float((e/e.cummax()-1).min()),'sharpe':float(dr.mean()/dr.std()*np.sqrt(252)) if dr.std() else 0,'trades':len(trades),'max_trade':float(max(t['return'] for t in trades)),'min_trade':float(min(t['return'] for t in trades)),'equity':e}

def main():
    data={s:load(s) for s in STOCKS}; common=max(d.index[0] for d in data.values()); end=min(d.index[-1] for d in data.values()); full=run(data,common,end,BASE_P)
    annual={str(k.year):float(v) for k,v in full['equity'].resample('YE').last().pct_change().dropna().items()}; stress={}
    for tc in [.001,.002,.005,.01]:
        p=dict(BASE_P); p['cost']=tc; p['slip']=tc; r=run(data,common,end,p); stress[f'{tc*100:.1f}%']={k:r[k] for k in ['cagr','max_drawdown','sharpe','total_return']}
    oos=run(data,pd.Timestamp('2020-01-01'),end,BASE_P); pre=run(data,common,pd.Timestamp('2019-12-31'),BASE_P)
    result={'period':{'full_start':str(common.date()),'end':str(end.date()),'oos_start':'2020-01-01'},'full':{k:full[k] for k in ['final','cagr','total_return','max_drawdown','sharpe','trades','max_trade','min_trade']},'annual_returns':annual,'stress_cost_slippage':stress,'pre_2020':{k:pre[k] for k in ['cagr','max_drawdown','sharpe','trades']},'out_of_sample_2020_plus':{k:oos[k] for k in ['cagr','max_drawdown','sharpe','trades','total_return']}}
    json.dump(result,open('portfolio_v6_validation.json','w'),indent=2); print(json.dumps(result,indent=2))

if __name__=='__main__': main()
