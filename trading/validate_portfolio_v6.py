# Validation wrapper: execute the corrected no-look-ahead engine and publish its exact baseline result.
import json
import runpy

runpy.run_path('trading/test_portfolio_v6.py', run_name='__main__')
with open('portfolio_v6_results.json', 'r', encoding='utf-8') as f:
    result = json.load(f)

out = {
    'method': 'corrected_no_lookahead_engine',
    'execution_model': result['trade_ledger_audit']['execution_model'],
    'period': {'full_start': result['common_start'], 'end': result['end']},
    'full': {
        'final': result['final_equity'], 'cagr': result['cagr'],
        'total_return': result['total_return'], 'max_drawdown': result['max_drawdown'],
        'sharpe': result['sharpe'], 'trades': result['trades'],
        'max_trade': result['trade_ledger_audit']['max_reported_trade_return'],
        'min_trade': result['trade_ledger_audit']['min_reported_trade_return'],
    },
    'annual_returns': result['annual_returns'],
}
with open('portfolio_v6_validation.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
