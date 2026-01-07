from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pandas as pd
import numpy as np
import io
import sys
import os
from typing import Optional

# Add parent directory to path to import cohort_analysis
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(title="Cohort Pulse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for uploaded data
uploaded_data: Optional[pd.DataFrame] = None


@app.get("/health")
def health_check():
    return {"status": "healthy"}


def generate_waterfall_insights(df: pd.DataFrame) -> list:
    """Generate insights for healthcare waterfall analysis. Always returns 6 insights."""
    insights = []

    try:
        total_billed = df['billed_amount'].sum()
        total_collected = df['amount_paid'].sum()
        collection_rate = (total_collected / total_billed * 100) if total_billed > 0 else 0

        # 1. Collection Rate
        if collection_rate >= 90:
            insights.append({
                'type': 'positive',
                'title': 'Excellent collection rate',
                'text': f"Collecting {collection_rate:.1f}% of billed charges."
            })
        elif collection_rate >= 70:
            insights.append({
                'type': 'info',
                'title': 'Collection rate',
                'text': f"Collecting {collection_rate:.1f}% of billed charges."
            })
        else:
            insights.append({
                'type': 'warning',
                'title': 'Low collection rate',
                'text': f"Only collecting {collection_rate:.1f}% of billed charges."
            })

        # 2. Total Revenue
        insights.append({
            'type': 'info',
            'title': 'Total collected',
            'text': f"${total_collected:,.0f} collected from ${total_billed:,.0f} billed."
        })

        # 3. Average days to payment
        df_copy = df.copy()
        df_copy['days_to_pay'] = (df_copy['date_paid'] - df_copy['service_date']).dt.days
        avg_days = df_copy['days_to_pay'].mean()
        if avg_days <= 30:
            insights.append({
                'type': 'positive',
                'title': 'Fast payments',
                'text': f"Average {avg_days:.0f} days from service to payment."
            })
        elif avg_days <= 60:
            insights.append({
                'type': 'info',
                'title': 'Payment timing',
                'text': f"Average {avg_days:.0f} days from service to payment."
            })
        else:
            insights.append({
                'type': 'warning',
                'title': 'Slow payments',
                'text': f"Average {avg_days:.0f} days from service to payment."
            })

        # 4. Payer analysis
        payer_totals = df.groupby('payer').agg({
            'billed_amount': 'sum',
            'amount_paid': 'sum'
        })
        payer_totals['rate'] = payer_totals['amount_paid'] / payer_totals['billed_amount'] * 100

        best_payer = payer_totals['rate'].idxmax()
        best_rate = payer_totals['rate'].max()
        insights.append({
            'type': 'positive',
            'title': 'Top performing payer',
            'text': f"{best_payer} has the highest collection rate at {best_rate:.1f}%."
        })

        # 5. Worst payer (if significantly different)
        worst_payer = payer_totals['rate'].idxmin()
        worst_rate = payer_totals['rate'].min()
        if worst_rate < best_rate * 0.7:
            insights.append({
                'type': 'warning',
                'title': 'Underperforming payer',
                'text': f"{worst_payer} has the lowest collection rate at {worst_rate:.1f}%."
            })
        else:
            # Service type mix
            service_mix = df.groupby('service_type')['amount_paid'].sum()
            top_service = service_mix.idxmax()
            top_revenue = service_mix.max()
            insights.append({
                'type': 'info',
                'title': 'Top service type',
                'text': f"{top_service} generates the most revenue at ${top_revenue:,.0f}."
            })

        # 6. Claims volume
        unique_claims = df['claim_id'].nunique()
        insights.append({
            'type': 'info',
            'title': 'Claims processed',
            'text': f"{unique_claims:,} unique claims analyzed."
        })

    except Exception:
        pass

    # Pad if needed
    while len(insights) < 6:
        insights.append({
            'type': 'info',
            'title': 'Revenue analysis',
            'text': 'Track payment patterns across service months.'
        })

    return insights[:6]


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global uploaded_data

    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    # Handle comma-formatted numbers (e.g., "5,493.00" -> 5493.00)
    if "billed_amount" in df.columns:
        df["billed_amount"] = df["billed_amount"].replace(r'[\$,]', '', regex=True).astype(float)
    if "amount_paid" in df.columns:
        df["amount_paid"] = df["amount_paid"].replace(r'[\$,]', '', regex=True).astype(float)

    # Parse dates
    df["service_date"] = pd.to_datetime(df["service_date"])
    df["date_paid"] = pd.to_datetime(df["date_paid"])

    uploaded_data = df

    # Get filter options
    payers = sorted(df["payer"].dropna().unique().tolist())
    service_types = sorted(df["service_type"].dropna().unique().tolist())

    # Generate insights
    insights = generate_waterfall_insights(df)

    return {
        "message": "File uploaded successfully",
        "rows": len(df),
        "filters": {
            "payers": payers,
            "service_types": service_types,
        },
        "insights": insights
    }


@app.get("/cohort-matrix")
def get_cohort_matrix(
    payer: Optional[str] = Query(None),
    service_type: Optional[str] = Query(None),
):
    global uploaded_data

    if uploaded_data is None:
        return JSONResponse(
            status_code=400,
            content={"error": "No data uploaded. Please upload a CSV file first."}
        )

    df = uploaded_data.copy()

    # Apply filters
    if payer:
        df = df[df["payer"] == payer]
    if service_type:
        df = df[df["service_type"] == service_type]

    if df.empty:
        return {"matrix": [], "columns": [], "totals": {}}

    # Create month buckets
    df["dos_month"] = df["service_date"].dt.to_period("M").astype(str)
    df["pay_month"] = df["date_paid"].dt.to_period("M").astype(str)

    # Gross charges by DOS month (dedupe by claim_id)
    gross_by_dos = (
        df.drop_duplicates(subset=["claim_id"])
          .groupby("dos_month")["billed_amount"]
          .sum()
    )

    # Cash by DOS month and payment month
    cash_pivot = (
        df.groupby(["dos_month", "pay_month"])["amount_paid"]
          .sum()
          .unstack(fill_value=0)
    )

    # Get all payment months sorted
    pay_months = sorted(cash_pivot.columns.tolist())

    # Build matrix rows
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

    # Calculate column totals
    totals = {
        "gross_charge": float(gross_by_dos.sum()),
        "payments": {pay: float(cash_pivot[pay].sum()) for pay in pay_months}
    }

    return {
        "matrix": matrix_rows,
        "payment_months": pay_months,
        "totals": totals,
    }


@app.get("/filters")
def get_filters():
    global uploaded_data

    if uploaded_data is None:
        return {"payers": [], "service_types": []}

    payers = sorted(uploaded_data["payer"].dropna().unique().tolist())
    service_types = sorted(uploaded_data["service_type"].dropna().unique().tolist())

    return {
        "payers": payers,
        "service_types": service_types,
    }


# ============================================================================
# RETENTION ANALYSIS ENDPOINTS
# ============================================================================

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


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_cohorts(file: UploadFile = File(...)):
    """
    Analyze uploaded CSV file and return cohort retention metrics.
    """
    try:
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
