import io, json, zipfile, requests, re
from pathlib import Path
import pandas as pd
START=pd.Timestamp('2018-01-01'); END=pd.Timestamp('2020-12-31'); OUT=Path('trading/data/nifty_option_history.csv'); OUT.parent.mkdir(parents=True,exist_ok=True); RECORD='https://zenodo.org/api/records/10899828'
def get_file(hint):
 r=requests.get(RECORD,headers={'User-Agent':'V12-research/1.0'},timeout=60); r.raise_for_status(); meta=r.json(); f=next((x for x in meta.get('files',[]) if hint.lower() in x.get('key','').lower()),None)
 if not f: raise RuntimeError('Zenodo file not found: '+hint)
 u=f.get('links',{}).get('self') or f.get('links',{}).get('content'); rr=requests.get(u,headers={'User-Agent':'V12-research/1.0'},stream=True,timeout=180); rr.raise_for_status(); p=Path('/tmp')/Path(f['key']).name
 with p.open('wb') as z:
  for c in rr.iter_content(1024*1024):
   if c:z.write(c)
 return p
def rd(raw,n): return pd.read_excel(io.BytesIO(raw)) if n.lower().endswith(('.xlsx','.xls')) else pd.read_csv(io.BytesIO(raw))
def cols(x): x.columns=[str(c).strip().lower().replace(' ','_') for c in x.columns]; return x
def spot(path):
 a=[]
 with zipfile.ZipFile(path) as z:
  for n in z.namelist():
   if n.endswith('/') or not re.search(r'\.(csv|xlsx|xls)$',n,re.I): continue
   try:
    x=cols(rd(z.read(n),n)); d=next((c for c in x if 'date' in c),None); q=next((c for c in x if c in ('close','closing_price','ltp')),None)
    if d and q:a.append(pd.DataFrame({'date':pd.to_datetime(x[d],errors='coerce'),'underlying':pd.to_numeric(x[q],errors='coerce')}))
   except: pass
 if not a: raise RuntimeError('No spot data parsed')
 x=pd.concat(a).dropna().drop_duplicates('date'); return x[(x.date>=START)&(x.date<=END)]
def options(path):
 a=[]
 with zipfile.ZipFile(path) as z:
  ns=[n for n in z.namelist() if not n.endswith('/') and re.search(r'\.(csv|xlsx|xls)$',n,re.I) and 'PE' in Path(n).stem.upper()]
  print('PE files:',len(ns))
  for n in ns:
   try:
    x=cols(rd(z.read(n),n)); d=next((c for c in x if 'trade_dt' in c or c in ('trade_date','date')),None); k=next((c for c in x if 'strike' in c),None); q=next((c for c in x if c in ('close','closing_price')),None); m=re.findall(r'(\d{1,2})[-_ ]?([A-Za-z]{3})[-_ ]?(20\d{2})',n)
    if not(d and k and q and m): continue
    y=pd.DataFrame({'date':pd.to_datetime(x[d],errors='coerce'),'strike':pd.to_numeric(x[k],errors='coerce'),'close':pd.to_numeric(x[q],errors='coerce')}).dropna(); y=y[(y.date>=START)&(y.date<=END)]; y['expiry']=pd.to_datetime(f'{m[-1][0]}-{m[-1][1]}-{m[-1][2]}',errors='coerce'); a.append(y[['date','expiry','strike','close']])
   except Exception as e: print('skip',n,e)
 if not a: raise RuntimeError('No PE data parsed')
 return pd.concat(a)
def main():
 o=options(get_file('Nifty Options Data.zip')); s=spot(get_file('Nifty spot and futures data.zip')); o=o.sort_values(['date','expiry','strike']).groupby(['date','expiry','strike'],as_index=False).last(); o=o.merge(s,on='date',how='left').dropna(subset=['underlying']); o['option_type']='PE'; o=o[['date','expiry','option_type','strike','close','underlying']];
 if len(o)<1000: raise RuntimeError('Insufficient observations: '+str(len(o)))
 o.to_csv(OUT,index=False); print('Wrote',len(o),'real PE observations')
if __name__=='__main__': main()
