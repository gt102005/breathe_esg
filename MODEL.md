# Data Model

## Goals

The data model is designed for multi-tenancy, source-of-truth tracking, source normalization, and analyst review before audit.

## Primary entities

- `Tenant`
  - Represents a customer account or business unit.
  - Allows the model to separate data across clients.

- `SourceSystem`
  - Represents the ingestion origin, such as SAP exports, utility portals, or corporate travel.
  - Tracks source type and any source-specific configuration.

- `IngestionBatch`
  - Tracks the file or payload upload that produced a set of records.
  - Stores file name, row count, ingestion status, and notes.
  - Provides an audit boundary for batches of rows pulled together.

- `EmissionRecord`
  - Stores normalized emissions/activity data.
  - Includes raw payload JSON, a source row identifier, and a batch/source link.
  - Records both the activity quantity and normalized emissions in `kgCO2e`.
  - Stores `scope` and `category` for Scope 1/2/3 reporting.
  - Includes review metadata (`status`, `review_comments`, `reviewed_at`, `reviewed_by`, `locked_at`).

## Scope and category support

`EmissionRecord` uses controlled values for:

- `scope`
  - `scope_1`
  - `scope_2`
  - `scope_3`

- `category`
  - `fuel`
  - `procurement`
  - `electricity`
  - `flight`
  - `hotel`
  - `ground_transport`

This ensures every normalized row can be classified for carbon inventory reporting.

## Source-of-truth and audit

Source-of-truth tracking is achieved by:

- Storing the raw input row in `raw_payload`
- Linking every record to an `IngestionBatch`
- Recording `source_system` and `source_record_id`
- Preserving review history through status changes and timestamps

## Tradeoffs

The model favors flexibility for new source types over rigid source-specific tables. That allows the prototype to ingest disparate feeds without a separate schema per source.
