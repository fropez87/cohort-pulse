"""
Main API entry point for Vercel serverless.
Combines all endpoints into a single FastAPI app.
"""

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import numpy as np
import io

# Import cohort analysis functions
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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ HEALTH CHECK ============
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


# ============ RETENTION ANALYSIS ============
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


def convert_numpy(obj):
    """Convert numpy types to native Python types for JSON serialization."""
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


def table_to_dict(df):
    """Convert DataFrame to JSON-friendly dict."""
    df_copy = df.copy()
    df_copy.index = df_copy.index.astype(str)
    return convert_numpy(df_copy.to_dict(orient='index'))


@app.post("/api/analyze")
async def analyze_cohorts(file: UploadFile = File(...)):
    """Analyze uploaded CSV file and return cohort metrics."""
    try:
        content = await file.read()
        csv_file = io.BytesIO(content)

        df, error = load_and_validate_data(csv_file)
        if error:
            return {"success": False, "error": error}

        df_cohorts = calculate_cohorts(df)

        retention_table = build_retention_table(df_cohorts)
        revenue_table = build_revenue_table(df_cohorts)
        customer_table = build_customer_count_table(df_cohorts)
        revenue_retention_table = build_revenue_retention_table(df_cohorts)

        summary = get_cohort_summary(df_cohorts)
        advanced_metrics = get_advanced_metrics(df_cohorts)
        cohort_sizes = get_cohort_sizes(df_cohorts)
        retention_curve = get_retention_curve(df_cohorts)
        insights = generate_insights(df_cohorts, retention_table, advanced_metrics, cohort_sizes)

        return {
            "success": True,
            "summary": convert_numpy(summary),
            "metrics": convert_numpy(advanced_metrics),
            "insights": convert_numpy(insights),
            "retention_table": table_to_dict(retention_table),
            "revenue_table": table_to_dict(revenue_table),
            "customer_table": table_to_dict(customer_table),
            "revenue_retention_table": table_to_dict(revenue_retention_table),
            "cohort_sizes": convert_numpy(cohort_sizes.to_dict(orient='records')),
            "retention_curve": convert_numpy(retention_curve.to_dict(orient='records'))
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# ============ WATERFALL UPLOAD ============
def calculate_waterfall_matrix(df: pd.DataFrame, payer: str = None, service_type: str = None):
    """Calculate the cohort matrix from dataframe."""
    df = df.copy()

    if payer:
        df = df[df["payer"] == payer]
    if service_type:
        df = df[df["service_type"] == service_type]

    if df.empty:
        return {"matrix": [], "payment_months": [], "totals": {"gross_charge": 0, "payments": {}}}

    df["dos_month"] = df["service_date"].dt.to_period("M").astype(str)
    df["pay_month"] = df["date_paid"].dt.to_period("M").astype(str)

    gross_by_dos = (
        df.drop_duplicates(subset=["claim_id"])
          .groupby("dos_month")["billed_amount"]
          .sum()
    )

    cash_pivot = (
        df.groupby(["dos_month", "pay_month"])["amount_paid"]
          .sum()
          .unstack(fill_value=0)
    )

    pay_months = sorted(cash_pivot.columns.tolist())

    matrix_rows = []
    dos_months = sorted(cash_pivot.index.tolist())

    for dos in dos_months:
        row = {
            "dos_month": dos,
            "gross_charge": float(gross_by_dos.get(dos, 0)),
            "payments": {}
        }
        for pay in pay_months:
            val = cash_pivot.loc[dos, pay] if pay in cash_pivot.columns else 0
            row["payments"][pay] = float(val)
        matrix_rows.append(row)

    totals = {
        "gross_charge": float(gross_by_dos.sum()),
        "payments": {pay: float(cash_pivot[pay].sum()) for pay in pay_months}
    }

    return {
        "matrix": matrix_rows,
        "payment_months": pay_months,
        "totals": totals,
    }


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a CSV file for payer waterfall analysis."""
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

        df["service_date"] = pd.to_datetime(df["service_date"])
        df["date_paid"] = pd.to_datetime(df["date_paid"])

        payers = sorted(df["payer"].dropna().unique().tolist())
        service_types = sorted(df["service_type"].dropna().unique().tolist())

        matrix_data = calculate_waterfall_matrix(df)

        records = df.to_dict(orient='records')
        for r in records:
            r['service_date'] = str(r['service_date'])
            r['date_paid'] = str(r['date_paid'])

        return {
            "message": "File uploaded successfully",
            "rows": len(df),
            "filters": {
                "payers": payers,
                "service_types": service_types,
            },
            "data": records,
            "matrix": matrix_data["matrix"],
            "payment_months": matrix_data["payment_months"],
            "totals": matrix_data["totals"]
        }

    except Exception as e:
        return {"error": str(e)}


# ============ COHORT MATRIX (for filtering) ============
class MatrixRequest(BaseModel):
    data: list
    payer: Optional[str] = None
    service_type: Optional[str] = None


@app.post("/api/cohort-matrix")
async def get_cohort_matrix(request: MatrixRequest):
    """Calculate cohort matrix with filters from client-provided data."""
    try:
        df = pd.DataFrame(request.data)
        df["service_date"] = pd.to_datetime(df["service_date"])
        df["date_paid"] = pd.to_datetime(df["date_paid"])

        matrix_data = calculate_waterfall_matrix(
            df,
            payer=request.payer,
            service_type=request.service_type
        )

        return matrix_data

    except Exception as e:
        return {"error": str(e)}
