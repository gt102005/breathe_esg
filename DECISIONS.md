# Decisions

## Source formats

- **SAP**: modeled as a CSV export with German and English headers, because many SAP exports are delivered as flat files from IDoc/ERP extract tools.
- **Utility electricity**: modeled as a portal CSV containing billing periods, meter IDs, and consumption values; this is the most common facilities workflow for electricity data.
- **Corporate travel**: modeled as a JSON export containing flights, hotels, and ground transport trips, which matches expense-export payload shapes from Concur/Navan.

## What is handled

- SAP fuel and procurement rows are normalized into `fuel` or `procurement` depending on the material description.
- Utility bills are normalized to electricity consumption with start/end billing dates and Scope 2 classification.
- Travel expenses are normalized to flight, hotel, and ground transport categories, with simple distance and hotel-night emission inference.

## Tradeoffs in source fidelity

- I chose to ingest realistic rows but not implement full SAP IDoc/BAPI handling.
- Utility parsing accepts a single CSV shape instead of supporting PDF parsing or nested tariff records.
- Travel normalization assumes the export includes either explicit distances or airport codes; it does not live-call a flight emissions API.

## Questions for product

- Should each tenant receive its own source configuration, or can a shared default `demo` tenant suffice for this prototype?
- Do we need to support record-level editing after approval, or only review/approve workflows?
- What degree of vendor and plant master data should be included in the first iteration?
