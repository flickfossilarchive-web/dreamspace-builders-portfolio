import io, zipfile, requests, pandas as pd, numpy as np
from datetime import date, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

START=date(2018,1,1); END=date(2020,12,31); OUT=Path('trading/data/nifty_option_history.csv'); OUT.parent.mkdir(parents=True,exist_ok=True)
HEAD={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/149 Safari/537.36','Accept':'*/*','Referer':'https://www.nseindia.com/'}

def one(d):
    url=f'https://nsearchives.nseindia.com/content/historical/DERIVATIVES/{d:%Y}/{d:%b}/fo{d:%d}{d:%b}{d:%Y}bhav.csv.zip'
    try:
        r=requests.get(url,headers=HEAD,timeout=45); r.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            raw=z.read(z.namelist()[0])
        df=pd.read_csv(io.BytesIO(raw)); df.columns=[c.strip().upper() for c in df.columns]
        opt=df[(df['INSTRUMENT']=='OPTIDX')&(df['SYMBOL']=='NIFTY')&(df['OPTTYPE']=='PE')].copy()
        fut=df[(df['INSTRUMENT']=='FUTIDX')&(df['SYMBOL']=='NIFTY')].copy()
        if opt.empty or fut.empty: return None
        # Use the nearest-expiry NIFTY future close as an exchange-derived spot proxy.
        fut['EXPIRY_DT']=pd.to_datetime(fut['EXPIRY'],errors='coerce'); fut['CLOSE']=pd.to_numeric(fut['CLOSE'],errors='coerce')
        fut=fut.dropna(subset=['EXPIRY_DT','CLOSE']).sort_values('EXPIRY_DT')
        spot=float(fut.iloc[0]['CLOSE'])
        opt['DATE']=pd.Timestamp(d); opt['EXPIRY']=pd.to_datetime(opt['EXPIRY'],errors='coerce'); opt['STRIKE']=pd.to_numeric(opt['STRIKE'],errors='coerce'); opt['CLOSE']=pd.to_numeric(opt['CLOSE'],errors='coerce'); opt['UNDERLYING']=spot
        opt=opt[['DATE','EXPIRY','OPTTYPE','STRIKE','CLOSE','UNDERLYING']].rename(columns={'OPTTYPE':'OPTION_TYPE'})
        return opt.dropna()
    except Exception as e:
        print('SKIP',d,e); return None

def main():
    ds=[]; d=START
    while d<=END:
        if d.weekday()<5: ds.append(d)
        d+=timedelta(days=1)
    parts=[]
    with ThreadPoolExecutor(max_workers=8) as ex:
        fs={ex.submit(one,d):d for d in ds}
        for f in as_completed(fs):
            x=f.result()
            if x is not None: parts.append(x)
    if not parts: raise RuntimeError('No NSE F&O archives retrieved')
    out=pd.concat(parts,ignore_index=True).sort_values(['DATE','EXPIRY','STRIKE'])
    out.to_csv(OUT,index=False)
    print(f'Wrote {len(out):,} real NIFTY PE observations to {OUT}')
    print(out.groupby(out.DATE.dt.year).size().to_dict())
if __name__=='__main__': main()
