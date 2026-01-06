"""
Vercel serverless function for Excel export.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import io
import sys
import os

# Import from local cohort_analysis module
from cohort_analysis import (
    load_and_validate_data,
    calculate_cohorts,
    build_retention_table,
    build_revenue_table,
    build_customer_count_table,
    build_revenue_retention_table,
    export_to_excel
)

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/export")
async def export_data(file: UploadFile = File(...)):
    """
    Generate Excel export of cohort data.
    """
    try:
        content = await file.read()
        csv_file = io.BytesIO(content)

        df, error = load_and_validate_data(csv_file)
        if error:
            raise HTTPException(status_code=400, detail=error)

        df_cohorts = calculate_cohorts(df)
        retention_table = build_retention_table(df_cohorts)
        revenue_table = build_revenue_table(df_cohorts)
        customer_table = build_customer_count_table(df_cohorts)
        revenue_retention_table = build_revenue_retention_table(df_cohorts)

        excel_bytes = export_to_excel(retention_table, revenue_table, customer_table, revenue_retention_table)

        return StreamingResponse(
            io.BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=cohort_pulse_export.xlsx"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
