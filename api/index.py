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
from mangum import Mangum

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
    """Generate automatic insights from the cohort data. Always returns exactly 6 insights."""
    # Start with guaranteed insights (always show these 3)
    guaranteed = []
    conditional = []

    try:
        # GUARANTEED 1: Repeat purchase rate
        if metrics['repeat_rate'] >= 30:
            guaranteed.append({
                'type': 'positive',
                'title': 'Strong repeat purchases',
                'text': f"{metrics['repeat_rate']:.1f}% of customers have made more than one purchase."
            })
        elif metrics['repeat_rate'] < 15:
            guaranteed.append({
                'type': 'warning',
                'title': 'Low repeat rate',
                'text': f"Only {metrics['repeat_rate']:.1f}% of customers return. Consider retention strategies."
            })
        else:
            guaranteed.append({
                'type': 'info',
                'title': 'Repeat purchase rate',
                'text': f"{metrics['repeat_rate']:.1f}% of customers have made more than one purchase."
            })

        # GUARANTEED 2: Lifetime Revenue
        if metrics['ltv'] > 0:
            guaranteed.append({
                'type': 'info',
                'title': 'Lifetime Revenue',
                'text': f"Average lifetime revenue per customer is ${metrics['ltv']:.2f}."
            })

        # GUARANTEED 3: Average Order Value
        if metrics['aov'] > 0:
            guaranteed.append({
                'type': 'info',
                'title': 'Average Order Value',
                'text': f"Customers spend an average of ${metrics['aov']:.2f} per order."
            })

        # CONDITIONAL: Top performing cohort
        if 'Month 1' in retention_table.columns:
            month1_retention = retention_table['Month 1'].dropna()
            if len(month1_retention) > 1:
                best_cohort = month1_retention.idxmax()
                best_retention = month1_retention.max()
                avg_retention = month1_retention.mean()

                if avg_retention > 0 and best_retention > avg_retention * 1.1:
                    conditional.append({
                        'type': 'positive',
                        'title': 'Top performing cohort',
                        'text': f"{best_cohort} cohort has {best_retention:.1f}% Month 1 retention, {((best_retention - avg_retention) / avg_retention * 100):.0f}% above average."
                    })

        # CONDITIONAL: Underperforming cohort
        if 'Month 1' in retention_table.columns:
            month1_retention = retention_table['Month 1'].dropna()
            if len(month1_retention) > 1:
                worst_cohort = month1_retention.idxmin()
                worst_retention = month1_retention.min()
                avg_retention = month1_retention.mean()
                if avg_retention > 0 and worst_retention < avg_retention * 0.8:
                    conditional.append({
                        'type': 'warning',
                        'title': 'Underperforming cohort',
                        'text': f"{worst_cohort} cohort has only {worst_retention:.1f}% Month 1 retention."
                    })

        # CONDITIONAL: Cohort size trend
        if len(cohort_sizes) >= 3:
            sizes = cohort_sizes['new_customers'].tolist()
            recent_avg = sum(sizes[-3:]) / 3
            earlier_avg = sum(sizes[:3]) / 3
            if earlier_avg > 0:
                change_pct = ((recent_avg - earlier_avg) / earlier_avg) * 100
                if change_pct < -20:
                    conditional.append({
                        'type': 'warning',
                        'title': 'Declining acquisition',
                        'text': f"Recent cohorts are {abs(change_pct):.0f}% smaller than earlier ones."
                    })
                elif change_pct > 20:
                    conditional.append({
                        'type': 'positive',
                        'title': 'Growing acquisition',
                        'text': f"Recent cohorts are {change_pct:.0f}% larger than earlier ones."
                    })

        # CONDITIONAL: Month 1 to Month 2 drop-off
        if 'Month 1' in retention_table.columns and 'Month 2' in retention_table.columns:
            m1 = retention_table['Month 1'].dropna().mean()
            m2 = retention_table['Month 2'].dropna().mean()
            if m1 > 0 and m2 > 0:
                dropoff = m1 - m2
                if dropoff > 15:
                    conditional.append({
                        'type': 'warning',
                        'title': 'High early churn',
                        'text': f"You lose {dropoff:.1f}% of customers between Month 1 and Month 2."
                    })
                elif dropoff < 5:
                    conditional.append({
                        'type': 'positive',
                        'title': 'Strong retention curve',
                        'text': f"Only {dropoff:.1f}% drop-off between Month 1 and Month 2."
                    })

        # CONDITIONAL: Best retention month
        if len(retention_table.columns) >= 3:
            avg_retention_by_month = retention_table.mean()
            if len(avg_retention_by_month) > 2:
                # Find which month has best average retention (excluding Month 0)
                month_cols = [c for c in retention_table.columns if c != 'Month 0']
                if month_cols:
                    best_month = avg_retention_by_month[month_cols].idxmax()
                    best_val = avg_retention_by_month[month_cols].max()
                    conditional.append({
                        'type': 'info',
                        'title': 'Best retention period',
                        'text': f"{best_month} shows the highest average retention at {best_val:.1f}%."
                    })

    except Exception:
        pass

    # Combine: guaranteed first, then fill remaining slots with conditional
    insights = guaranteed + conditional[:6 - len(guaranteed)]

    # If we still don't have 6, pad with generic insights
    while len(insights) < 6:
        if len(insights) == 3:
            insights.append({
                'type': 'info',
                'title': 'Data coverage',
                'text': f"Analysis includes {len(cohort_sizes)} monthly cohorts."
            })
        elif len(insights) == 4:
            total_customers = int(cohort_sizes['new_customers'].sum()) if len(cohort_sizes) > 0 else 0
            insights.append({
                'type': 'info',
                'title': 'Customer base',
                'text': f"Total of {total_customers:,} unique customers analyzed."
            })
        else:
            insights.append({
                'type': 'info',
                'title': 'Retention analysis',
                'text': "Track cohort behavior over time to identify trends."
            })

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

def generate_waterfall_insights(df: pd.DataFrame, matrix_data: dict) -> list:
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

        # Debug info
        content_len = len(contents)
        first_100 = contents[:100].decode('utf-8', errors='replace')
        has_newline = b'\n' in contents
        has_cr = b'\r' in contents

        # Use BytesIO with original bytes - pandas handles encoding better
        df = pd.read_csv(io.BytesIO(contents), encoding='utf-8-sig')

        # Handle comma-formatted numbers (e.g., "5,493.00" -> 5493.00)
        if "billed_amount" in df.columns:
            df["billed_amount"] = df["billed_amount"].replace(r'[\$,]', '', regex=True).astype(float)
        if "amount_paid" in df.columns:
            df["amount_paid"] = df["amount_paid"].replace(r'[\$,]', '', regex=True).astype(float)

        df["service_date"] = pd.to_datetime(df["service_date"])
        df["date_paid"] = pd.to_datetime(df["date_paid"])

        payers = sorted(df["payer"].dropna().unique().tolist())
        service_types = sorted(df["service_type"].dropna().unique().tolist())

        matrix_data = calculate_waterfall_matrix(df)
        insights = generate_waterfall_insights(df, matrix_data)

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
            "totals": matrix_data["totals"],
            "insights": insights
        }

    except Exception as e:
        # Include debug info in error response
        debug_info = {
            "content_len": content_len if 'content_len' in dir() else 'N/A',
            "first_100": first_100 if 'first_100' in dir() else 'N/A',
            "has_newline": has_newline if 'has_newline' in dir() else 'N/A',
            "has_cr": has_cr if 'has_cr' in dir() else 'N/A',
        }
        return {"error": str(e), "debug": debug_info}


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


# Handler for Vercel serverless
handler = Mangum(app)
# Version 2.5 - add debug info to error response
