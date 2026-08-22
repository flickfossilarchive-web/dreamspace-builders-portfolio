import json
from pathlib import Path
import pandas as pd

def test_paper_engine_is_explicitly_paper_only():
    text=Path('trading/paper_trade_v2.py').read_text()
    assert 'real_orders=False' in text
    assert 'PAPER_ONLY' in text
    assert 'next available session' in text

def test_portfolio_constraints_after_generation():
    p=Path('data/paper_trade_v2/paper_portfolio.json')
    if not p.exists(): return
    x=json.loads(p.read_text())
    pos=x['positions']
    assert x['real_orders'] is False
    assert len(pos)==20
    assert len({r['symbol'] for r in pos})==20
    assert abs(sum(r['target_weight'] for r in pos)-1)<1e-9

def test_no_future_signal_timestamp():
    p=Path('data/paper_trade_v2/paper_portfolio.json')
    if not p.exists(): return
    x=json.loads(p.read_text())
    assert pd.Timestamp(x['asof']) <= pd.Timestamp.utcnow().normalize()
