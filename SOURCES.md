# Sources

## SAP

- Real-world format: SAP ERP export CSV with German column headers or SAP list viewer CSV.
- What I learned:
  - SAP exports often contain headers like `Werk`, `Lieferant`, `Material`, `Datum`, `Menge`, and `Einheit`.
  - Fuel data is stored alongside procurement data, and the same feed can contain both Scope 1 (fuel purchases) and Scope 3 (procurement).
  - Date formats vary and require normalization.
- Sample data shape:
  - `Werk`, `Lieferant`, `Material`, `Materialnummer`, `Datum`, `Menge`, `Einheit`, `Kostenstelle`, `CO2e`
- Notes on what breaks:
  - This prototype will not ingest binary IDoc files, OData arrays, or SAP BAPI responses.
  - It assumes CSV rows are line items with a single date and quantity.

## Utility electricity

- Real-world format: exported utility portal CSV containing consumption, meter IDs, billing period dates, tariff, and site code.
- What I learned:
  - Facilities teams often download monthly or irregular billing periods rather than calendar months.
  - Consumption units are generally `kWh`, and metadata includes billing period start/end.
- Sample data shape:
  - `site_code`, `billing_period_start`, `billing_period_end`, `consumption`, `unit`, `tariff`, `meter_id`
- Notes on what breaks:
  - The app does not parse PDF bills.
  - It does not handle multiple tariffs within a single invoice line or embedded demand charges.

## Corporate travel

- Real-world format: expense-export JSON or CSV from travel platforms like Concur/Navan.
- What I learned:
  - Travel data often includes separate categories for flights, hotels, and ground transport.
  - Distances may be explicit or implied through airport codes.
- Sample data shape:
  - `expense_type`, `traveler`, `departure_airport`, `arrival_airport`, `distance_km`, `hotel_nights`, `ground_mode`, `ground_distance_km`, `date`
- Notes on what breaks:
  - This prototype does not support raw expense receipts or transaction-level hotel invoices.
  - It uses heuristic distance mapping rather than a complete airport geolocation service.
