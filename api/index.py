"""
Main API entry point for Vercel serverless.
All code is self-contained to avoid import issues.
"""

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Tuple
import pandas as pd
import numpy as np
import io

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ COHORT ANALYSIS FUNCTIONS ============

def load_and_validate_data(file) -> Tuple[pd.DataFrame, Optional[str]]:
    """Load CSV file and validate required columns."""
    required_columns = {'order_date', 'customer_id', 'order_amount'}

    try:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

        missing_cols = required_columns - set(df.columns)
        if missing_cols:
            return None, f"Missing required columns: {', '.join(missing_cols)}"

        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
        if df['order_date'].isna().any():
            invalid_count = df['order_date'].isna().sum()
            return None, f"Found {invalid_count} rows with invalid dates"

        df['order_amount'] = pd.to_numeric(df['order_amount'], errors='coerce')
        if df['order_amount'].isna().any():
            invalid_count = df['order_amount'].isna().sum()
            return None, f"Found {invalid_count} rows with invalid order amounts"

        df['customer_id'] = df['customer_id'].astype(str)

        return df, None

    except Exception as e:
        return None, f"Error reading file: {str(e)}"


def calculate_cohorts(df: pd.DataFrame) -> pd.DataFrame:
    """Assign each customer to their cohort based on first purchase month."""
    df = df.copy()

    customer_cohorts = df.groupby('customer_id')['order_date'].min().reset_index()
    customer_cohorts.columns = ['customer_id', 'cohort_date']
    customer_cohorts['cohort_month'] = customer_cohorts['cohort_date'].dt.to_period('M')

    df = df.merge(customer_cohorts[['customer_id', 'cohort_month']], on='customer_id')
    df['order_month'] = df['order_date'].dt.to_period('M')
    df['cohort_index'] = (df['order_month'] - df['cohort_month']).apply(lambda x: x.n)

    return df


def build_retention_table(df: pd.DataFrame) -> pd.DataFrame:
    """Build cohort retention table showing % of customers returning each month."""
    cohort_data = df.groupby(['cohort_month', 'cohort_index'])['customer_id'].nunique().reset_index()
    cohort_data.columns = ['cohort_month', 'cohort_index', 'customers']

    cohort_pivot = cohort_data.pivot(index='cohort_month', columns='cohort_index', values='customers')
    cohort_sizes = cohort_pivot[0]
    retention_table = cohort_pivot.divide(cohort_sizes, axis=0) * 100
    retention_table = retention_table.round(1)

    retention_table.columns = [f'Month {i}' for i in retention_table.columns]
    retention_table.index = retention_table.index.astype(str)

    return retention_table


def build_revenue_table(df: pd.DataFrame) -> pd.DataFrame:
    """Build cohort revenue table showing total revenue per cohort per month."""
    cohort_data = df.groupby(['cohort_month', 'cohort_index'])['order_amount'].sum().reset_index()
    cohort_data.columns = ['cohort_month', 'cohort_index', 'revenue']

    revenue_table = cohort_data.pivot(index='cohort_month', columns='cohort_index', values='revenue')
    revenue_table = revenue_table.round(2)

    revenue_table.columns = [f'Month {i}' for i in revenue_table.columns]
    revenue_table.index = revenue_table.index.astype(str)

    return revenue_table


def build_customer_count_table(df: pd.DataFrame) -> pd.DataFrame:
    """Build cohort customer count table."""
    cohort_data = df.groupby(['cohort_month', 'cohort_index'])['customer_id'].nunique().reset_index()
    cohort_data.columns = ['cohort_month', 'cohort_index', 'customers']

    customer_table = cohort_data.pivot(index='cohort_month', columns='cohort_index', values='customers')

    customer_table.columns = [f'Month {i}' for i in customer_table.columns]
    customer_table.index = customer_table.index.astype(str)

    return customer_table


def build_revenue_retention_table(df: pd.DataFrame) -> pd.DataFrame:
    """Build cohort revenue retention table showing percentage of Month 0 revenue retained."""
    cohort_data = df.groupby(['cohort_month', 'cohort_index'])['order_amount'].sum().reset_index()
    cohort_data.columns = ['cohort_month', 'cohort_index', 'revenue']

    cohort_pivot = cohort_data.pivot(index='cohort_month', columns='cohort_index', values='revenue')
    base_revenue = cohort_pivot[0]
    revenue_retention = cohort_pivot.divide(base_revenue, axis=0) * 100
    revenue_retention = revenue_retention.round(1)

    revenue_retention.columns = [f'Month {i}' for i in revenue_retention.columns]
    revenue_retention.index = revenue_retention.index.astype(str)

    return revenue_retention


def get_cohort_summary(df: pd.DataFrame) -> dict:
    """Get summary statistics about the cohort data."""
    return {
        'total_orders': len(df),
        'unique_customers': df['customer_id'].nunique(),
        'total_revenue': float(df['order_amount'].sum()),
        'date_range': f"{df['order_date'].min().strftime('%Y-%m-%d')} to {df['order_date'].max().strftime('%Y-%m-%d')}",
        'num_cohorts': df['cohort_month'].nunique() if 'cohort_month' in df.columns else 0
    }


def get_advanced_metrics(df: pd.DataFrame) -> dict:
    """Calculate advanced business metrics."""
    total_revenue = df['order_amount'].sum()
    total_orders = len(df)
    unique_customers = df['customer_id'].nunique()

    orders_per_customer = df.groupby('customer_id').size()
    repeat_customers = (orders_per_customer > 1).sum()

    ltv = total_revenue / unique_customers if unique_customers > 0 else 0
    aov = total_revenue / total_orders if total_orders > 0 else 0
    repeat_rate = (repeat_customers / unique_customers * 100) if unique_customers > 0 else 0
    avg_orders_per_customer = total_orders / unique_customers if unique_customers > 0 else 0

    return {
        'ltv': float(ltv),
        'aov': float(aov),
        'repeat_rate': float(repeat_rate),
        'avg_orders_per_customer': float(avg_orders_per_customer),
        'repeat_customers': int(repeat_customers),
        'one_time_customers': int(unique_customers - repeat_customers)
    }


def get_cohort_sizes(df: pd.DataFrame) -> pd.DataFrame:
    """Get the size of each cohort (new customers per month)."""
    cohort_sizes = df.groupby('cohort_month')['customer_id'].nunique().reset_index()
    cohort_sizes.columns = ['cohort_month', 'new_customers']
    cohort_sizes['cohort_month'] = cohort_sizes['cohort_month'].astype(str)
    return cohort_sizes


def get_retention_curve(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate average retention rate across all cohorts by month index."""
    cohort_data = df.groupby(['cohort_month', 'cohort_index'])['customer_id'].nunique().reset_index()
    cohort_data.columns = ['cohort_month', 'cohort_index', 'customers']

    cohort_pivot = cohort_data.pivot(index='cohort_month', columns='cohort_index', values='customers')
    cohort_sizes = cohort_pivot[0]
    retention_pct = cohort_pivot.divide(cohort_sizes, axis=0) * 100

    avg_retention = retention_pct.mean().reset_index()
    avg_retention.columns = ['month', 'retention']
    avg_retention['month'] = avg_retention['month'].astype(int)

    return avg_retention


def generate_insights(df: pd.DataFrame, retention_table: pd.DataFrame, metrics: dict, cohort_sizes: pd.DataFrame) -> list:
    """Generate automatic insights from the cohort data."""
    insights = []

    try:
        if metrics['repeat_rate'] >= 30:
            insights.append({
                'type': 'positive',
                'title': 'Strong repeat purchases',
                'text': f"{metrics['repeat_rate']:.1f}% of customers have made more than one purchase."
            })
        elif metrics['repeat_rate'] < 15:
            insights.append({
                'type': 'warning',
                'title': 'Low repeat rate',
                'text': f"Only {metrics['repeat_rate']:.1f}% of customers return. Consider retention strategies."
            })

        if 'Month 1' in retention_table.columns:
            month1_retention = retention_table['Month 1'].dropna()
            if len(month1_retention) > 1:
                best_cohort = month1_retention.idxmax()
                best_retention = month1_retention.max()
                avg_retention = month1_retention.mean()

                if avg_retention > 0 and best_retention > avg_retention * 1.2:
                    insights.append({
                        'type': 'positive',
                        'title': 'Top performing cohort',
                        'text': f"{best_cohort} cohort has {best_retention:.1f}% Month 1 retention."
                    })

        if metrics['ltv'] > 0:
            insights.append({
                'type': 'info',
                'title': 'Lifetime Revenue',
                'text': f"Average lifetime revenue per customer is ${metrics['ltv']:.2f}."
            })

        if metrics['avg_orders_per_customer'] > 0:
            insights.append({
                'type': 'info',
                'title': 'Purchase frequency',
                'text': f"Customers place an average of {metrics['avg_orders_per_customer']:.1f} orders each."
            })

        if 'Month 2' in retention_table.columns:
            month2_data = retention_table['Month 2'].dropna()
            if len(month2_data) > 0:
                month2_avg = month2_data.mean()
                if month2_avg >= 20:
                    insights.append({
                        'type': 'positive',
                        'title': 'Good long-term retention',
                        'text': f"Average {month2_avg:.1f}% of customers are still active by Month 2."
                    })

    except Exception:
        pass

    return insights[:6]


# ============ HELPER FUNCTIONS ============

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


# ============ API ENDPOINTS ============

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


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


# ============ WATERFALL FUNCTIONS ============

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
