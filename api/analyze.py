"""
Vercel serverless function for cohort analysis.
"""

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import numpy as np
import io
import sys
import os

# Add parent directory to path to import cohort_analysis
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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


@app.post("/api/analyze", response_model=AnalysisResponse)
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
