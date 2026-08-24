# NIFTY 50 V3 Research Design

## Objective
Build a deterministic NIFTY-50-only allocation strategy. The strategy does not select individual stocks. It allocates between NIFTY 50 exposure and cash using only information available at the signal timestamp.

## Research rules
- Underlying research series: NIFTY 50 TRI where available.
- Investable implementation is modeled as a NIFTY-50-tracking instrument; no individual-stock selection.
- Signal is evaluated after the close and, when a rebalance is triggered, the target exposure applies from the next eligible session.
- Exposure is bounded to 0%-100%; residual is cash.
- No leverage, shorting, or derivatives are assumed.
- No AI/agent decides trades or parameters.
- Parameters must be selected on a training period and frozen for walk-forward/out-of-sample evaluation.
- Transaction costs and slippage must be included in evaluation.

## Candidate families
1. Trend/regime: combinations of moving-average state and drawdown/volatility regime.
2. Multi-horizon momentum/trend: independent medium/long horizon signals combined with volatility control.
3. Defensive regime: exposure is reduced only when predefined risk conditions are met.
4. Simple ensemble: average/consensus of independently validated signals, with exposure caps.

## Validation gate
A candidate is not promoted because it has the highest historical CAGR. It must survive:
- point-in-time/no-look-ahead checks;
- walk-forward validation;
- parameter perturbation;
- realistic cost/slippage sensitivity;
- rebalance-frequency sensitivity;
- crisis-period analysis;
- bootstrap/Monte Carlo where supported;
- comparison against NIFTY 50 TRI buy-and-hold.

Primary objective: improve risk-adjusted returns and/or materially reduce drawdown versus NIFTY 50 TRI without excessive turnover or fragile parameter dependence.

## Safety
This branch is research/paper-only. `real_orders=False` remains mandatory. This file intentionally contains no executable trading logic until the existing repository's data interfaces and validation harness are inspected and the candidate is implemented against them.
