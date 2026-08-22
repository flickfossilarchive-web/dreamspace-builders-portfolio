import json, numpy as np, pandas as pd
from test_nifty_v10_regime import data

# V24 hypothesis locked before evaluation:
# NIFTY-first fast momentum/trend with Gold only as a defensive sleeve.
# No leverage. Signals use previous session. Parameters are fixed ex-ante.
COST=0.0010
SLIPPAGE=0.0010
MOM=90
TREND=200
GOLD_CAP=0.35


def run(d, cost=COST, slippage=SLIPPAGE, mom=MOM, trend=TREND, gold_cap=GOLD_CAP):
    n=d.Close.astype(float); tri=d.TRI.astype(float); gold=d.Gold.astype(float)
    nr=tri.pct_change().fillna(0); gr=gold.pct_change().fillna(0)
    ma=n.rolling(trend).mean(); momr=n.pct_change(mom)
    eq=1.0; w=1.0; vals=[]; trades=0; turnover=0.0; exposures=[]
    for i in range(1,len(d)):
        p=i-1
        weekly=(i==1 or d.index[i].isocalendar().week!=d.index[i-1].isocalendar().week or d.index[i].year!=d.index[i-1].year)
        if weekly and np.isfinite(ma.iloc[p]) and np.isfinite(momr.iloc[p]):
            risk_on=(n.iloc[p]>ma.iloc[p] and momr.iloc[p]>0)
            severe=(n.iloc[p]<ma.iloc[p] and momr.iloc[p]<0)
            target=1.0 if risk_on else (1.0-gold_cap if severe else 0.80)
            if abs(target-w)>=0.05:
                t=abs(target-w); turnover+=t; eq*=max(0,1-t*(cost+slippage)); w=target; trades+=1
        # Portfolio weights are the actual post-rebalance weights; no look-ahead.
        wg=1.0-w
        eq*=1+w*nr.iloc[i]+wg*gr.iloc[i]
        vals.append((d.index[i],eq)); exposures.append(w)
    s=pd.Series(dict(vals)).sort_index(); rr=s.pct_change().fillna(0); yrs=(s.index[-1]-s.index[0]).days/365.25
    return s, {'cagr':float(s.iloc[-1]**(1/yrs)-1),'total_return':float(s.iloc[-1]-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252)),'trades':trades,'turnover':turnover,'avg_nifty_weight':float(np.mean(exposures))}


def metrics(x):
    x=x.dropna(); yrs=(x.index[-1]-x.index[0]).days/365.25; rr=x.pct_change().dropna()
    return {'cagr':float((x.iloc[-1]/x.iloc[0])**(1/yrs)-1),'max_drawdown':float((x/x.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252))}


def main():
    d=data()
    import yfinance as yf
    g=yf.download('GC=F',start=str(d.index[0].date()),end=str((d.index[-1]+pd.Timedelta(days=1)).date()),auto_adjust=False,progress=False)
    if isinstance(g.columns,pd.MultiIndex): g=g.xs('GC=F',axis=1,level=1)
    d=d.join(g[['Close']].rename(columns={'Close':'Gold'}),how='left').ffill().dropna(subset=['Gold'])
    tri=d.TRI; yrs=(tri.index[-1]-tri.index[0]).days/365.25
    bench=float((tri.iloc[-1]/tri.iloc[0])**(1/yrs)-1)
    base_s,base=run(d)
    costs={str(int(c*10000)):run(d,cost=c,slippage=c)[1] for c in [0,0.0005,0.001,0.0015,0.002,0.003,0.004,0.005]}
    perturbations={}
    for name,m,t,gc in [('m60',60,200,.35),('m90',90,200,.35),('m120',120,200,.35),('t150',90,150,.35),('t250',90,250,.35),('gc20',90,200,.20),('gc30',90,200,.30),('gc40',90,200,.40)]:
        perturbations[name]=run(d,cost=.001,slippage=.001,mom=m,trend=t,gold_cap=gc)[1]
    windows=[('2008-2012','2008-01-01','2012-12-31'),('2013-2017','2013-01-01','2017-12-31'),('2018-2021','2018-01-01','2021-12-31'),('2022-present','2022-01-01',str(d.index[-1].date()))]
    wf=[]
    for name,a,b in windows:
        x=base_s.loc[a:b]
        if len(x)>50: wf.append({'name':name,**metrics(x)})
    out={'strategy':'V24 NIFTY fast-momentum/trend with capped Gold defensive sleeve','benchmark_cagr':bench,'base':base,'cost_sensitivity':costs,'parameter_perturbations':perturbations,'walk_forward':wf,'rules':{'momentum_days':90,'trend_days':200,'risk_on':'NIFTY > MA200 and 90d momentum > 0 => 100% NIFTY','neutral':'80% NIFTY / 20% Gold','severe':'65% NIFTY / 35% Gold','rebalance':'weekly thresholded','signals':'previous session only','leverage':'none'},'gate':{'cost_bps_primary':20,'required_base_cagr_gt_benchmark':True,'required_20bps_cagr_gt_benchmark':True,'required_all_perturbations_positive':True,'required_all_walk_forward_positive':True,'required_sharpe_ge':0.80,'required_max_dd_better_than':-0.30}}
    json.dump(out,open('v24_results.json','w'),indent=2); print(json.dumps(out,indent=2))

if __name__=='__main__': main()
