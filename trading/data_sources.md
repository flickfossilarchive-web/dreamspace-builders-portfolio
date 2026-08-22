# Historical constituent data sources

## Tier 1 — official
- NSE Indices historical-data reports: https://www.niftyindices.com/reports
- NSE Indices data subscription: https://www.nseindia.com/static/nse-indices/index-data-subscription
- NSE Nifty 500 methodology/index pages: https://www.nseindia.com/static/products-services/indices-nifty500-index

Official NSE data is preferred for production research. NSE explicitly describes constituent data as including identifiers, market capitalization, weights and prices and offers historical data products.

## Tier 2 — public reconstruction / cross-check
- https://github.com/vishalvx/nifty-indices-datasets — reconstructed historical Nifty index constituents; README states the data is survivorship-bias-free in intent but reconstructed and not official.
- https://github.com/BKKB20/indian-index-reconstruction — pipeline for reconstructing historical NSE/BSE index membership from reconstitution circulars.
- https://niftyhistory.in/ — public historical constituent ledger; treat as an independent cross-check, not authoritative.

## Tier 3 — commercial
NSE lists Bloomberg, FactSet, IHS Markit, MSCI, Rimes and Thomson Reuters as distribution channels for index data. A commercial feed is preferable if it provides point-in-time membership plus historical security identifiers and corporate-action mapping.

## Decision
For the next research build, use Tier 1 wherever accessible. Use Tier 2 to detect missing/incorrect intervals. Do not silently substitute Tier 2 for Tier 1; every substituted interval must be labelled and excluded from a final production-grade result unless independently validated.
