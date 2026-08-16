import json
import numpy as np
import pandas as pd
import yfinance as yf

TICKER='^NSEI'
VIX='^INDIAVIX'
START='2000-01-01'
COST=0.0005
SLIPPAGE=0.0005
TARGET_VOL=0.12


def load_one(ticker):
    d=yf.download(ticker,start=START,auto_adjust=False,progress=False)
    if isinstance(d.columns,pd.MultiIndex):
        d=d.xs(ticker,axis=1,level=1)
    return d


def load_data():
    d=load_one(TICKER)[['Open','High','Low','Close']].dropna().copy()
    d.index=pd.to_datetime(d.index).tz_localize(None)
    v=load_one(VIX)
    if len(v):
        if isinstance(v.columns,pd.MultiIndex): v=v.xs(VIX,axis=1,level=1)
        d['VIX']=v['Close'].reindex(d.index).ffill()
    else:
        d['VIX']=np.nan
    d['VIX']=d['VIX'].fillna(d['VIX'].median())
    if d.index.duplicated().any() or (d[['Open','High','Low','Close']]<=0).any().any(): raise ValueError('Invalid OHLC data')
    return d


def indicators(d):
    c=d.Close.astype(float); h=d.High.astype(float); l=d.Low.astype(float)
    ret=c.pct_change()
    ma20=c.rolling(20).mean(); ma50=c.rolling(50).mean(); ma100=c.rolling(100).mean(); ma200=c.rolling(200).mean()
    vol20=ret.rolling(20).std()*np.sqrt(252)
    vol60=ret.rolling(60).std()*np.sqrt(252)
    mom21=c.pct_change(21); mom63=c.pct_change(63); mom126=c.pct_change(126); mom252=c.pct_change(252)
    # Short-term mean reversion z-score.
    z20=(c-ma20)/(ret.rolling(20).std()*c.rolling(20).mean().replace(0,np.nan))
    atr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1).rolling(14).mean()
    return c,ma20,ma50,ma100,ma200,vol20,vol60,mom21,mom63,mom126,mom252,z20,atr


def target_weight(vals, vix, current_dd):
    ma20,ma50,ma100,ma200,vol20,vol60,m21,m63,m126,m252,z20=vals
    trend_score=sum([ma20>ma50,ma50>ma100,ma100>ma200, m126>0, m252>0]) / 5.0
    momentum_score=np.clip((m21*0.15+m63*0.25+m126*0.30+m252*0.30+0.10)/0.25,0,1)
    regime=0.55*trend_score+0.45*momentum_score
    # Tactical mean reversion is only a small overlay inside a positive long-term regime.
    tactical=0.0
    if ma200 < 0: return 0.0
    if m126>0 and z20 < -1.5 and ma50>ma100:
        tactical=0.15
    # VIX shock filter: scale rather than binary exit.
    vix_mult=1.0
    if vix>=30: vix_mult=0.35
    elif vix>=25: vix_mult=0.55
    elif vix>=20: vix_mult=0.75
    # Volatility targeting; use 8% floor to avoid oversized exposure in quiet periods.
    vol_mult=min(1.0,TARGET_VOL/max(vol20,0.08))
    base=0.05+0.95*np.clip(regime,0,1)
    # Strong bull markets retain high participation; weak regimes de-risk gradually.
    if ma50>ma200 and m126>0: base=max(base,0.75)
    if ma50<ma200 and m126<0: base=min(base,0.20)
    # Portfolio drawdown governor; recover gradually after risk reduction.
    dd_mult=1.0
    if current_dd<=-0.08: dd_mult=0.80
    if current_dd<=-0.12: dd_mult=0.60
    if current_dd<=-0.18: dd_mult=0.35
    return float(np.clip((base+tactical)*vol_mult*vix_mult*dd_mult,0,1))


def trade(d):
    c,o=d.Close.astype(float),d.Open.astype(float)
    c,ma20,ma50,ma100,ma200,vol20,vol60,m21,m63,m126,m252,z20,atr=indicators(d)
    cash=1.0; units=0.0; eq=[]; trades=[]; last_target=0.0
    peak=1.0
    for i in range(1,len(d)):
        p=i-1
        vals=[ma20.iloc[p],ma50.iloc[p],ma100.iloc[p],ma200.iloc[p],vol20.iloc[p],vol60.iloc[p],m21.iloc[p],m63.iloc[p],m126.iloc[p],m252.iloc[p],z20.iloc[p]]
        if not all(np.isfinite(x) for x in vals):
            mark=cash+units*float(c.iloc[i]); peak=max(peak,mark); eq.append((d.index[i],mark)); continue
        mark=cash+units*float(c.iloc[p]); peak=max(peak,mark); dd=mark/peak-1
        target=target_weight(vals,float(d.VIX.iloc[p]),dd)
        # Weekly execution avoids excessive turnover while retaining responsive regime changes.
        weekly=(i==1 or d.index[i].isocalendar().week!=d.index[i-1].isocalendar().week or d.index[i].year!=d.index[i-1].year)
        op=float(o.iloc[i])
        if weekly and abs(target-last_target)>=0.05:
            total=cash+units*op
            desired=max(0,min(total*target,total))
            desired_units=desired/(op*(1+SLIPPAGE))
            delta=desired_units-units
            if delta>1e-12:
                cash-=delta*op*(1+SLIPPAGE)*(1+COST); units+=delta; trades.append(('BUY',str(d.index[i].date()),target))
            elif delta< -1e-12:
                qty=-delta; cash+=qty*op*(1-SLIPPAGE)*(1-COST); units-=qty; trades.append(('SELL',str(d.index[i].date()),target))
            last_target=target
        mark=cash+units*float(c.iloc[i]); peak=max(peak,mark); eq.append((d.index[i],mark))
    eq=pd.Series(dict(eq)).sort_index(); r=eq.pct_change().fillna(0)
    years=(eq.index[-1]-eq.index[0]).days/365.25
    return eq,{'cagr':float(eq.iloc[-1]**(1/years)-1),'total_return':float(eq.iloc[-1]-1),'max_drawdown':float((eq/eq.cummax()-1).min()),'sharpe':float(r.mean()/r.std()*np.sqrt(252)),'sortino':float(r.mean()/r[r<0].std()*np.sqrt(252)),'trades':len(trades)}


def buy_hold(d):
    c=d.Close.astype(float); years=(c.index[-1]-c.index[0]).days/365.25; ratio=c.iloc[-1]/c.iloc[0]
    return {'cagr':float(ratio**(1/years)-1),'total_return':float(ratio-1)}


def score(full,oos,bh):
    s=0
    s+=20*min(max(full['cagr']/0.12,0),1)
    s+=20*min(max(full['sharpe']/1.0,0),1)
    s+=15*min(max(1+full['max_drawdown']/0.20,0),1)
    s+=10*min(max(full['cagr']/max(bh['cagr'],1e-9),0),1)
    positive=sum(x['cagr']>0 for x in oos)/len(oos)
    s+=10*positive
    s+=10*min(max(np.mean([x['sharpe'] for x in oos])/0.8,0),1)
    s+=15*min(max(np.mean([x['cagr'] for x in oos])/0.10,0),1)
    return round(float(s),2)


def main():
    d=load_data(); eq,full=trade(d); bh=buy_hold(d)
    windows=[('2007-09-17','2009-12-31'),('2010-01-01','2019-12-31'),('2020-01-01',str(d.index[-1].date()))]
    oos=[]
    for a,b in windows:
        x=trade(d.loc[a:b])[1]; oos.append({'start':a,'end':b,**{k:x[k] for k in ['cagr','max_drawdown','sharpe','sortino','trades']}})
    result={'strategy':'NIFTY V6 adaptive regime ensemble: multi-horizon trend + momentum + tactical mean reversion + VIX shock filter + volatility targeting + drawdown governor','ticker':TICKER,'data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'execution':'previous completed daily bar; weekly next-open rebalance','cost':COST,'slippage':SLIPPAGE,'target_vol':TARGET_VOL,'full':full,'buy_and_hold_price_index':bh,'out_of_sample_windows':oos,'research_score_100':score(full,oos,bh)}
    json.dump(result,open('nifty_v6_results.json','w'),indent=2)
    pd.DataFrame({'date':eq.index.astype(str),'equity':eq.values}).to_csv('nifty_v6_equity.csv',index=False)
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
