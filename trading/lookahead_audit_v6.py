import json

# Audit conclusion based on repository history:
# - The portfolio baseline engine existed at parent commit 966eb206 before the
#   walk-forward fix and already used prior-bar signals with next-open entries.
# - Commit 1914a185 changed trading/walk_forward_v6.py only; it did not change
#   trading/test_portfolio_v6.py.
# Therefore the 9.92% baseline was NOT affected by the walk-forward look-ahead fix.
# This audit records the source-level equivalence rather than fabricating a
# trade-by-trade comparison that the historical engine did not log.

result = {
    "baseline_engine_parent_commit": "966eb20631e259221988ccc787c5a1a494828351",
    "walk_forward_fix_commit": "1914a185da7f6eda9e2889f1fb0dc986ff2cafb3",
    "baseline_engine_changed_by_fix": False,
    "baseline_execution_model": "prior completed bar signals; next-open entries",
    "baseline_result_is_affected_by_walk_forward_fix": False,
    "conclusion": "The 9.92% baseline result is independent of the 1914 walk-forward look-ahead fix. The fix applies to walk_forward_v6.py, not test_portfolio_v6.py.",
}
with open("portfolio_v6_lookahead_audit.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
