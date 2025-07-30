from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from typing import AsyncGenerator, List, Optional
import asyncio
import csv
import io
import random
from datetime import datetime

app = FastAPI()

# Simulates fetching large dataset in async manner. Real application would use paginated DB queries.
async def get_large_dataset(chunk_size: int = 10000, total_rows: int = 100_000) -> AsyncGenerator[List[dict], None]:
    """Yield chunks of rows as lists of dicts asynchronously."""
    num_chunks = (total_rows + chunk_size - 1) // chunk_size
    for chunk_index in range(num_chunks):
        # Simulating async IO operation
        await asyncio.sleep(0.01)  # Remove or decrease in real system
        chunk = [
            {
                "id": chunk_index * chunk_size + i + 1,
                "name": f"Item {chunk_index * chunk_size + i + 1}",
                "value": random.randint(0, 10000),
                "timestamp": datetime.utcnow().isoformat()
            }
            for i in range(min(chunk_size, total_rows - chunk_index * chunk_size))
        ]
        yield chunk

async def csv_chunk_generator_async(chunk_size: int = 10000, total_rows: int = 100_000) -> AsyncGenerator[bytes, None]:
    """Yield CSV rows as bytes for large datasets efficiently."""
    header_written = False
    async for chunk in get_large_dataset(chunk_size=chunk_size, total_rows=total_rows):
        buffer = io.StringIO()
        writer = None
        if not header_written:
            writer = csv.DictWriter(buffer, fieldnames=chunk[0].keys())
            writer.writeheader()
            header_written = True
        else:
            writer = csv.DictWriter(buffer, fieldnames=chunk[0].keys())
        writer.writerows(chunk)
        yield buffer.getvalue().encode("utf-8")
        buffer.close()

@app.get("/export-report")
async def export_report(
    background_tasks: BackgroundTasks,
    chunk_size: int = Query(10000, ge=500, le=50000, description="Number of rows per chunk."),
    total_rows: int = Query(100_000, ge=1, le=1_000_000, description="Total number of rows to export.")
):
    """
    Streaming endpoint to export reports as CSV efficiently.
    Supports large datasets without memory issues.
    Users download directly as the file is generated chunk by chunk.
    """
    filename = f"report_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
    response = StreamingResponse(
        csv_chunk_generator_async(chunk_size=chunk_size, total_rows=total_rows),
        media_type="text/csv"
    )
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response

# Optionally, for truly huge background exports with notification, we could manage disk-based jobs (not implemented here).