# Ruflo V14 Swarm

This project uses the public Ruflo orchestration pattern for the V14 research loop.

## Roles

- **coordinator** — owns task decomposition and prevents strategy drift.
- **researcher** — investigates data, pandas, and benchmark integrity failures.
- **coder** — proposes minimal implementation fixes.
- **tester** — verifies the fix and protects the frozen strategy parameters.

## V14 guardrails

The swarm may fix implementation, data-ingestion, and test defects, but must not tune the V14 investment parameters merely to improve the result.

Frozen parameters remain:

- 10% cash
- 60-day inverse-volatility lookback
- monthly rebalance
- NIFTY/GOLD/NASDAQ risk sleeves
- existing risk caps
- existing cost/slippage assumptions

## Execution model

Ruflo is the coordination layer; the executor performs repository changes and commands. This follows Ruflo's documented architecture rather than pretending that a swarm registration alone executes code.

For an actual LLM-backed swarm, configure a supported provider in the execution environment. The GitHub audit workflow intentionally publishes diagnostics instead of fabricating agent output when no provider is configured.
