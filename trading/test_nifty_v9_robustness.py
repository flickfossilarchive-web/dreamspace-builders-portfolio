import json, subprocess, sys
from pathlib import Path

# Robustness harness: reruns the corrected V9 engine across independently chosen
# stress dimensions without changing the base strategy logic.
# The suite records pass/fail evidence rather than selecting the best result.

BASE = Path('trading/test_nifty_v9_tri_overlay.py')
OUT = Path('nifty_v9_robustness_results.json')

# Fixed research matrix. No parameter is selected from the resulting performance.
CASES = {
    'cost_slippage': [
        {'cost':0.00025,'slippage':0.00025},
        {'cost':0.00050,'slippage':0.00050},
        {'cost':0.00100,'slippage':0.00100},
        {'cost':0.00200,'slippage':0.00200},
    ],
    'overlay_cap': [0.05,0.10,0.15,0.20],
    'rebalance': ['weekly','monthly'],
    'parameter_perturbation': ['baseline','ma_fast_45','ma_fast_55','ma_slow_180','ma_slow_220','mom_56','mom_70','mom_240','mom_270'],
    'crisis_periods': ['2008','2011','2018','2020','2022'],
    'walk_forward': ['2007-2013->2014-2016','2007-2016->2017-2019','2007-2019->2020-2022','2007-2022->2023-2026'],
    'bootstrap': {'iterations':2000,'seed':42}
}

# First verify the canonical V9 engine remains executable and produces the
# corrected TRI accounting artifact. The detailed stress implementations are
# deliberately fail-closed: a missing implementation is reported, never
# silently replaced by an optimistic assumption.
result = {'suite':'V9 robustness audit','status':'INCOMPLETE','matrix':CASES,'checks':[]}

p = subprocess.run([sys.executable, str(BASE)], capture_output=True, text=True, timeout=1200)
result['checks'].append({'name':'canonical_v9_replay','returncode':p.returncode,'passed':p.returncode==0})
if p.returncode != 0:
    result['status']='FAILED'
    result['error']=p.stderr[-4000:]
else:
    try:
        canonical=json.loads(Path('nifty_v9_results.json').read_text())
        result['canonical']=canonical
        result['checks'].append({'name':'tri_benchmark_present','passed':canonical.get('benchmark')=='Official NIFTY 50 Total Return Index'})
        result['checks'].append({'name':'corrected_accounting_note','passed':'no mixing' in canonical.get('research_note','')})
        # The suite is intentionally not allowed to claim robustness until each
        # stress engine has been independently implemented and executed.
        result['status']='PENDING_STRESS_ENGINES'
        result['next_required']=[
            'Implement cost/slippage matrix against the same TRI return stream',
            'Implement overlay-cap and rebalance sensitivity without parameter selection',
            'Implement fixed perturbation and crisis-period reports',
            'Implement chronological walk-forward evaluation',
            'Implement seeded bootstrap confidence intervals'
        ]
    except Exception as e:
        result['status']='FAILED'; result['error']=str(e)

OUT.write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
