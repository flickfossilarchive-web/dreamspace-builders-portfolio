import io, json, zipfile, requests, re
from pathlib import Path
import pandas as pd

START=pd.Timestamp('2018-01-01'); END=pd.Timestamp('2020-12-31')
OUT=Path('trading/data/nifty_option_history.csv'); OUT.parent.mkdir(parents=True,exist_ok=True)
RECORD='https://zenodo.org/api/records/10899828'


def get_file(hint):
    r=requests.get(RECORD,headers={'User-Agent':'V12-research/1.1'},timeout=60); r.raise_for_status()
    meta=r.json(); f=next((x for x in meta.get('files',[]) if hint.lower() in x.get('key','').lower()),None)
    if not f: raise RuntimeError('Zenodo file not found: '+hint)
    u=f.get('links',{}).get('self') or f.get('links',{}).get('content')
    rr=requests.get(u,headers={'User-Agent':'V12-research/1.1'},stream=True,timeout=300); rr.raise_for_status()
    p=Path('/tmp')/Path(f['key']).name
    with p.open('wb') as z:
        for c in rr.iter_content(4*1024*1024):
            if c: z.write(c)
    return p


def rd(raw,n):
    ext=Path(n).suffix.lower()
    if ext in ('.xlsx','.xls','.xlsb'): return pd.read_excel(io.BytesIO(raw))
    return pd.read_csv(io.BytesIO(raw),low_memory=False)


def cols(x):
    x.columns=[str(c).strip().lower().replace(' ','_').replace('-','_') for c in x.columns]
    return x


def expiry_from_name(n):
    # Dataset folders end with the monthly expiration date; support common
    # spellings such as 26-Dec-2019, 26_Dec_2019 and 2019-12-26.
    pats=[r'(\d{1,2})[-_ ]([A-Za-z]{3,9})[-_ ](20\d{2})',r'(20\d{2})[-_](\d{1,2})[-_](\d{1,2})']
    for p in pats:
        m=re.findall(p,n)
        if m:
            a=m[-1]
            if len(a[0])==4: return pd.Timestamp(f'{a[0]}-{a[1]}-{a[2]}',errors='coerce')
            return pd.to_datetime(f'{a[0]}-{a[1]}-{a[2]}',errors='coerce')
    return pd.NaT


def parse_option_frame(x,n):
    x=cols(x)
    typ=next((c for c in x if c in ('opt_type','option_type','opttype','optiontype')),None)
    d=next((c for c in x if 'trade_dt' in c or c in ('trade_date','date')),None)
    k=next((c for c in x if 'strike' in c),None)
    q=next((c for c in x if c in ('close','closing_price','close_price')),None)
    if not (typ and d and k and q): return None
    t=x[typ].astype(str).str.upper().str.strip()
    # Do not rely on filenames for PE/CE classification; Zenodo documents
    # option type as an explicit column.
    y=x.loc[t.isin(['PE','PUT','P'])].copy()
    if y.empty: return None
    y=pd.DataFrame({'date':pd.to_datetime(y[d],errors='coerce'),'strike':pd.to_numeric(y[k],errors='coerce'),'close':pd.to_numeric(y[q],errors='coerce')}).dropna()
    y=y[(y.date>=START)&(y.date<=END)]
    if y.empty: return None
    y['expiry']=expiry_from_name(n)
    if pd.isna(y['expiry'].iloc[0]): return None
    return y[['date','expiry','strike','close']]


def iter_data(z,path=''):
    # Handle both direct spreadsheets and nested zip archives.
    for n in z.namelist():
        if n.endswith('/') or not n.lower().endswith(('.csv','.xlsx','.xls','.xlsb','.zip')): continue
        raw=z.read(n)
        if n.lower().endswith('.zip'):
            with zipfile.ZipFile(io.BytesIO(raw)) as inner:
                yield from iter_data(inner,path+n+'/')
        else:
            yield path+n,raw


def spot(path):
    a=[]
    with zipfile.ZipFile(path) as z:
        for n,raw in iter_data(z):
            try:
                x=cols(rd(raw,n)); d=next((c for c in x if 'date' in c),None); q=next((c for c in x if c in ('close','closing_price','ltp')),None)
                if d and q:
                    a.append(pd.DataFrame({'date':pd.to_datetime(x[d],errors='coerce'),'underlying':pd.to_numeric(x[q],errors='coerce')}))
            except Exception: pass
    if not a: raise RuntimeError('No spot data parsed')
    x=pd.concat(a).dropna().drop_duplicates('date')
    return x[(x.date>=START)&(x.date<=END)]


def options(path):
    a=[]; files=0; pe=0
    with zipfile.ZipFile(path) as z:
        for n,raw in iter_data(z):
            files+=1
            try:
                y=parse_option_frame(rd(raw,n),n)
                if y is not None:
                    pe+=1; a.append(y)
            except Exception as e:
                print('skip',n,str(e)[:160])
    print('Data files:',files,'PE files parsed:',pe)
    if not a: raise RuntimeError('No PE data parsed after schema-based option-type detection')
    return pd.concat(a,ignore_index=True)


def main():
    o=options(get_file('Nifty Options Data.zip'))
    s=spot(get_file('Nifty spot and futures data.zip'))
    o=o.sort_values(['date','expiry','strike']).groupby(['date','expiry','strike'],as_index=False).last()
    o=o.merge(s,on='date',how='left').dropna(subset=['underlying'])
    o['option_type']='PE'
    o=o[['date','expiry','option_type','strike','close','underlying']]
    if len(o)<1000: raise RuntimeError('Insufficient observations: '+str(len(o)))
    o.to_csv(OUT,index=False)
    print('Wrote',len(o),'real PE observations to',OUT)

if __name__=='__main__': main()
