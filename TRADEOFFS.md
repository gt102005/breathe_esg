# Tradeoffs

## 1. No full SAP IDoc / BAPI integration

I opted for CSV ingestion with header normalization rather than implementing SAP OData or IDoc parsing. This keeps the prototype focused on data normalization and review rather than building an enterprise SAP connector.

## 2. No PDF or portal scraping for utility bills

The utility source is a CSV upload only. PDF parsing is a common real-world requirement, but it adds brittle OCR and bill parsing complexity that would distract from the core normalization and analyst workflow.

## 3. No travel emissions external API call

Travel normalization uses static distance heuristics and simple per-km factors. A production system would call a flight emissions service, but this prototype demonstrates category mapping and source shape handling clearly.
