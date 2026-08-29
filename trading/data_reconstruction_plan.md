# Historical constituent data reconstruction

## Objective
Create a reproducible, auditable historical constituent ledger for NIFTY 50/100/200/500 without survivorship bias.

## Primary source
NSE Indices historical reports are the authoritative source. NSE states that its index-data products provide historical constituent data including identifiers, market capitalisation, weights and prices, and are intended for quantitative research and portfolio construction. See https://www.nseindia.com/static/nse-indices/index-data-subscription and https://www.niftyindices.com/reports.

## Public reconstruction path
1. Pull monthly/biannual NSE Indices archival reports and reconstitution circulars.
2. Parse constituent names, symbols/identifiers, effective dates and weights.
3. Normalize symbols using NSE security-master/history where possible.
4. Store every membership interval as `(index, symbol, effective_from, effective_to, source_document)`.
5. Preserve delisted/renamed securities rather than dropping them.
6. Validate every transition against the preceding/following report and flag unexplained gaps.
7. Join point-in-time membership to historical prices fetched by symbol, with signals computed only from dates when the security was actually eligible.
8. Never use today's constituent list to fill historical periods.

## Secondary validation
Use independent public reconstruction datasets only as a cross-check, never as the sole source. The `vishalvx/nifty-indices-datasets` project documents a reconstructed Nifty 50 history from 2008 onward, while `BKKB20/indian-index-reconstruction` provides a pipeline concept for reconstructing membership from NSE/BSE circulars. These should be compared against NSE sources and differences logged.

## Data quality gates
- no membership interval may start before its source effective date
- no stock may be eligible before its actual listing/available-price history
- no future constituent can appear in a past portfolio
- delistings and corporate-action symbol changes must be retained
- every backtest date must be traceable to a source report/circular

## Research gate
Do not run or publish stock-selection performance until the ledger passes these checks. The resulting dataset should be versioned and accompanied by a source manifest and validation report.
