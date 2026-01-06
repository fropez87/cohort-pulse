"""
Cohort Pulse API
FastAPI backend for cohort analysis.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import numpy as np
import json
import io
import sys
import os


from cohort_analysis import (
    load_and_validate_data,
    calculate_cohorts,
    build_retention_table,
    build_revenue_table,
    build_customer_count_table,
    build_revenue_retention_table,
    get_cohort_summary,
    get_advanced_metrics,
    get_cohort_sizes,
    get_retention_curve,
    generate_insights,
    export_to_excel
)

app = FastAPI(title="Cohort Pulse API", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://cohortpulse.com",
        "https://www.cohortpulse.com",
        "https://cohort-pulse.vercel.app",
        "https://cohort-pulse-*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalysisResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    summary: Optional[dict] = None
    metrics: Optional[dict] = None
    insights: Optional[list] = None
    retention_table: Optional[dict] = None
    revenue_table: Optional[dict] = None
    customer_table: Optional[dict] = None
    revenue_retention_table: Optional[dict] = None
    cohort_sizes: Optional[list] = None
    retention_curve: Optional[list] = None


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_cohorts(file: UploadFile = File(...)):
    """
    Analyze uploaded CSV file and return cohort metrics.
    """
    try:
        # Read file content
        content = await file.read()
        csv_file = io.BytesIO(content)

        # Load and validate
        df, error = load_and_validate_data(csv_file)
        if error:
            return AnalysisResponse(success=False, error=error)

        # Calculate cohorts
        df_cohorts = calculate_cohorts(df)

        # Build all tables
        retention_table = build_retention_table(df_cohorts)
        revenue_table = build_revenue_table(df_cohorts)
        customer_table = build_customer_count_table(df_cohorts)
        revenue_retention_table = build_revenue_retention_table(df_cohorts)

        # Get metrics
        summary = get_cohort_summary(df_cohorts)
        advanced_metrics = get_advanced_metrics(df_cohorts)
        cohort_sizes = get_cohort_sizes(df_cohorts)
        retention_curve = get_retention_curve(df_cohorts)
        insights = generate_insights(df_cohorts, retention_table, advanced_metrics, cohort_sizes)

        # Convert numpy types to native Python types for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(i) for i in obj]
            elif isinstance(obj, (np.integer, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif pd.isna(obj):
                return None
            return obj

        # Convert tables to JSON-friendly format
        def table_to_dict(df):
            df_copy = df.copy()
            df_copy.index = df_copy.index.astype(str)
            return convert_numpy(df_copy.to_dict(orient='index'))

        return AnalysisResponse(
            success=True,
            summary=convert_numpy(summary),
            metrics=convert_numpy(advanced_metrics),
            insights=convert_numpy(insights),
            retention_table=table_to_dict(retention_table),
            revenue_table=table_to_dict(revenue_table),
            customer_table=table_to_dict(customer_table),
            revenue_retention_table=table_to_dict(revenue_retention_table),
            cohort_sizes=convert_numpy(cohort_sizes.to_dict(orient='records')),
            retention_curve=convert_numpy(retention_curve.to_dict(orient='records'))
        )

    except Exception as e:
        return AnalysisResponse(success=False, error=str(e))


@app.post("/export")
async def export_data(file: UploadFile = File(...)):
    """
    Generate Excel export of cohort data.
    """
    from fastapi.responses import StreamingResponse

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
