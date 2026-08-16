import json
import numpy as np
import pandas as pd
import yfinance as yf

TICKER='^NSEI'
START='2000-01-01'
END=None
COST=0.0005
SLIPPAGE=0.0005


def load_data():
    d=yf.download(TICKER,start=START,end=END,auto_adjust=False,progress=False)
    if isinstance(d.columns,pd.MultiIndex): d=d.xs(TICKER,axis=1,level=1)
    d=d[['Open','High','Low','Close']].dropna().copy()
    d.index=pd.to_datetime(d.index).tz_localize(None)
    return d


def backtest(d, start=None, end=None):
    d=d.loc[start:end].copy() if start or end else d.copy()
    c=d.Close.astype(float); h=d.High.astype(float); l=d.Low.astype(float); o=d.Open.astype(float)
    sma50=c.rolling(50).mean(); sma200=c.rolling(200).mean(); mom126=c.pct_change(126)
    tr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    atr20=tr.rolling(20).mean()
    # All decisions for today's open use yesterday's completed bar.
    equity=1.0; units=0.0; exposure=0.0; stop=np.nan; rows=[]; trades=[]
    for i in range(1,len(d)):
        prev=i-1
        prev_close=float(c.iloc[prev]); prev50=float(sma50.iloc[prev]); prev200=float(sma200.iloc[prev]); prev_mom=float(mom126.iloc[prev]); prev_atr=float(atr20.iloc[prev])
        if not np.isfinite(prev50+prev200+prev_mom+prev_atr):
            rows.append((d.index[i],equity)); continue
        # Regime: full risk only when long and medium/long trend agree; half risk when long trend is positive but momentum is weak.
        target=1.0 if (prev_close>prev200 and prev50>prev200 and prev_mom>0) else (0.5 if prev_close>prev200 else 0.0)
        today_open=float(o.iloc[i]); today_low=float(l.iloc[i]); today_close=float(c.iloc[i])
        if units:
            stop=max(stop, prev_close-3.0*prev_atr)
            if today_low<=stop or target==0:
                exit_px=today_open*(1-SLIPPAGE) if today_open<stop else stop
                proceeds=units*exit_px*(1-COST)
                ret=proceeds/equity-1 if equity else 0
                trades.append({'entry':str(entry_date.date()),'exit':str(d.index[i].date()),'return':ret})
                equity=proceeds; units=0.; exposure=0.; stop=np.nan
        if target>0 and units==0:
            px=today_open*(1+SLIPPAGE); units=(equity*target)/px; equity=equity*(1-target); exposure=target; stop=px-3.0*prev_atr; entry_date=d.index[i]
        elif target>0 and units:
            desired=equity+units*today_close
            desired_units=(desired*target)/today_open
            units=desired_units
        total=equity+units*today_close
        rows.append((d.index[i],total))
    eq=pd.Series(dict(rows)).sort_index()
    dr=eq.pct_change().fillna(0)
    years=(eq.index[-1]-eq.index[0]).days/365.25
    cagr=eq.iloc[-1]**(1/years)-1 if years>0 else 0
    dd=(eq/eq.cummax()-1).min()
    sharpe=dr.mean()/dr.std()*np.sqrt(252) if dr.std() else 0
    return {'equity':eq,'cagr':float(cagr),'total_return':float(eq.iloc[-1]-1),'max_drawdown':float(dd),'sharpe':float(sharpe),'trades':len(trades),'trade_log':trades}


def buy_hold(d):
    c=d.Close.astype(float)
    r=c.iloc[-1]/c.iloc[0]-1
    years=(c.index[-1]-c.index[0]).days/365.25
    return {'total_return':float(r),'cagr':float((1+r)**(1/years)-1)}


def main():
    d=load_data()
    full=backtest(d)
    bh=buy_hold(d)
    windows=[('2000-01-03','2009-12-31'),('2010-01-01','2019-12-31'),('2020-01-01',str(d.index[-1].date()))]
    oos=[]
    for a,b in windows:
        if pd.Timestamp(a)<d.index[-1]:
            r=backtest(d,a,b); oos.append({'start':a,'end':b,'cagr':r['cagr'],'max_drawdown':r['max_drawdown'],'sharpe':r['sharpe'],'trades':r['trades']})
    result={'strategy':'NIFTY 50 regime + momentum + ATR risk control V1','ticker':TICKER,'data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'execution':'prior completed daily bar decisions; next-open execution','cost':COST,'slippage':SLIPPAGE,'full':{k:full[k] for k in ['cagr','total_return','max_drawdown','sharpe','trades']},'buy_and_hold_price_index':bh,'out_of_sample_windows':oos,'benchmark_note':'NIFTY 50 TR is the proper investor benchmark because it includes dividends; this first automated run uses ^NSEI price history, so TR comparison is a follow-up requirement.'}
    json.dump(result,open('nifty_v1_results.json','w'),indent=2)
    pd.DataFrame({'date':full['equity'].index.astype(str),'equity':full['equity'].values}).to_csv('nifty_v1_equity.csv',index=False)
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
