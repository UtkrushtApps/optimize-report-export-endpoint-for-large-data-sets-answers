# Efficient Large Data Export API (FastAPI)

## Overview

This project demonstrates how to efficiently export large datasets to CSV through an HTTP API endpoint using FastAPI. The endpoint is designed to avoid memory errors and blocking, using asynchronous generators to stream data and ensure server responsiveness.

## Features
- Asynchronous, non-blocking CSV export of large datasets
- Streams data in chunks directly to the client (memory-efficient, scalable)
- Customizable chunk size for performance tuning
- Download response with proper filename and content type

## Usage

- Run the app:

  ```bash
  uvicorn main:app --reload
  ```

- Export a report:

  Navigate to:

  `http://localhost:8000/export-report?chunk_size=10000&total_rows=100000`

  Adjust `chunk_size` and `total_rows` as desired.

- Downloaded response will stream a CSV containing simulated data rows.

## How it works

- Data is generated in `get_large_dataset`, simulating database paging.
- `csv_chunk_generator_async` yields CSV-formatted bytes chunk-by-chunk.
- FastAPI's `StreamingResponse` handles the streamed response efficiently, so memory use remains low regardless of output size.

## Extending

- Replace `get_large_dataset` with your real async database/page-fetching logic for production use.
