import io, json, urllib.request
import numpy as np
import pandas as pd

STOCKS = ['lt','bhartiartl','hcltech','maruti','axisbank','sunpharma','titan','m&m','tatasteel','hindalco','cipla']
BASE = 'https://raw.githubusercontent.com/BennyThadikaran/eod2_data/main/daily/'
P = {'sma':200,'breakout':20,'rs':63,'vol':20,'vol_mult':1.5,'atr':14,'stop_atr':2.0,'slip':.0015,'cost':.001}

def load(n):
    b = urllib.request.urlopen(BASE + n + '.csv', timeout=60).read()
    d = pd.read_csv(io.BytesIO(b))
    d['Date'] = pd.to_datetime(d.Date)
    return d.sort_values('Date').drop_duplicates('Date').set_index('Date')

def indicators(d):
    c=d.Close.astype(float); h=d.High.astype(float); l=d.Low.astype(float); v=d.Volume.astype(float)
    sma=c.rolling(P['sma']).mean()
    hi=h.shift(1).rolling(P['breakout']).max()
    atr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1).rolling(P['atr']).mean()
    rv=v/v.rolling(P['vol']).mean(); rs=c.pct_change(P['rs'])
    sig=(c>sma)&(c>hi)&(rv>P['vol_mult'])&(atr/c>.01)&(atr/c<.08)&(rs>0)
    return sma,atr,sig

def run():
    data={s:load(s) for s in STOCKS}
    common_start=max(d.index[0] for d in data.values()); end=min(d.index[-1] for d in data.values())
    data={s:d.loc[:end] for s,d in data.items()}
    idx=pd.date_range(common_start,end,freq='B')
    n=len(STOCKS); sleeve=1.0/n
    cash={s:sleeve for s in STOCKS}; shares={s:0.0 for s in STOCKS}; entry_px={s:None for s in STOCKS}; entry_date={s:None for s in STOCKS}; stop={s:None for s in STOCKS}
    trade_log=[]; equity_rows=[]
    prep={s:indicators(d) for s,d in data.items()}
    last_close={s:None for s in STOCKS}

    for dt in idx:
        total=0.0
        for s,d in data.items():
            if dt not in d.index:
                # Mark open positions to the latest available close instead of dropping the sleeve for a missing calendar date.
                total += cash[s] if shares[s]==0 else shares[s]*last_close[s]
                continue
            j=d.index.get_loc(dt); o=float(d.Open.iloc[j]); h=float(d.High.iloc[j]); l=float(d.Low.iloc[j]); c=float(d.Close.iloc[j]); last_close[s]=c
            sma,atr,sig=prep[s]
            if shares[s]>0:
                # Keep the original V6 mechanics for comparability, but never use a missing/NaN stop.
                a=float(atr.iloc[j]) if np.isfinite(float(atr.iloc[j])) else 0.0
                if a>0: stop[s]=max(stop[s],c-P['stop_atr']*a)
                reason=None
                if l<=stop[s]: reason='stop'
                elif c<float(sma.iloc[j]): reason='sma'
                if reason:
                    ex=o*(1-P['slip']) if o<stop[s] else stop[s]
                    before=shares[s]*entry_px[s]
                    cash[s]=shares[s]*ex*(1-P['cost'])
                    trade_ret=cash[s]/before-1 if before else 0.0
                    trade_log.append({'stock':s,'entry':str(entry_date[s].date()),'exit':str(dt.date()),'entry_value':before,'exit_value':cash[s],'return':trade_ret,'reason':reason})
                    shares[s]=0.0; entry_px[s]=None; entry_date[s]=None; stop[s]=None
            if shares[s]==0 and bool(sig.iloc[j]) and np.isfinite(float(atr.iloc[j])):
                px=o*(1+P['slip']); available=cash[s]; shares[s]=available/px; cash[s]=0.0; entry_px[s]=px; entry_date[s]=dt; stop[s]=px-P['stop_atr']*float(atr.iloc[j])
            total += cash[s] if shares[s]==0 else shares[s]*c
        equity_rows.append((dt,total))

    eq=pd.Series(dict(equity_rows)).sort_index(); daily=eq.pct_change().fillna(0); years=(eq.index[-1]-eq.index[0]).days/365.25
    cagr=eq.iloc[-1]**(1/years)-1 if years else 0; mdd=(eq/eq.cummax()-1).min(); sharpe=daily.mean()/daily.std()*np.sqrt(252) if daily.std() else 0
    annual=eq.resample('YE').last().pct_change().dropna().to_dict(); annual={str(k.year):float(v) for k,v in annual.items()}
    bh=pd.Series(0.0,index=eq.index)
    for s,d in data.items():
        p=d.Close.astype(float).reindex(eq.index).ffill(); first=p.first_valid_index()
        if first is not None: bh.loc[first:]+=p.loc[first:]/p.loc[first]
    bh=bh/n+(n-sum(1 for s,d in data.items() if d.Close.reindex(eq.index).first_valid_index() is not None))/n; bh=bh/bh.iloc[0]
    bh_cagr=bh.iloc[-1]**(1/years)-1 if years else 0; bh_mdd=(bh/bh.cummax()-1).min()
    result={'stocks':STOCKS,'stock_count':n,'common_start':str(eq.index[0].date()),'end':str(eq.index[-1].date()),'initial_capital':1.0,'final_equity':float(eq.iloc[-1]),'cagr':float(cagr),'total_return':float(eq.iloc[-1]-1),'max_drawdown':float(mdd),'sharpe':float(sharpe),'trades':len(trade_log),'annual_returns':annual,'benchmark_equal_weight_buy_hold':{'cagr':float(bh_cagr),'total_return':float(bh.iloc[-1]-1),'max_drawdown':float(bh_mdd)},'trade_ledger_audit':{'max_reported_trade_return':float(max((x['return'] for x in trade_log),default=0)),'min_reported_trade_return':float(min((x['return'] for x in trade_log),default=0))},'trades_detail':trade_log}
    json.dump(result,open('portfolio_v6_results.json','w'),indent=2)
    pd.DataFrame({'date':eq.index.astype(str),'equity':eq.values,'daily_return':daily.values,'benchmark':bh.values}).to_csv('portfolio_v6_equity.csv',index=False)
    pd.DataFrame(trade_log).to_csv('portfolio_v6_trade_ledger.csv',index=False)
    print(json.dumps({k:v for k,v in result.items() if k!='trades_detail'},indent=2))

if __name__=='__main__': run()
