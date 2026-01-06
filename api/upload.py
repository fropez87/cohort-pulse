"""
Vercel serverless function for waterfall CSV upload.
Returns upload info, filters, raw data, AND initial matrix in one response.
"""

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def calculate_matrix(df: pd.DataFrame, payer: str = None, service_type: str = None):
    """Calculate the cohort matrix from dataframe."""
    df = df.copy()

    # Apply filters
    if payer:
        df = df[df["payer"] == payer]
    if service_type:
        df = df[df["service_type"] == service_type]

    if df.empty:
        return {"matrix": [], "payment_months": [], "totals": {"gross_charge": 0, "payments": {}}}

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


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process a CSV file for payer waterfall analysis.
    Returns filter options, row count, raw data for filtering, AND initial matrix.
    """
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

        # Parse dates
        df["service_date"] = pd.to_datetime(df["service_date"])
        df["date_paid"] = pd.to_datetime(df["date_paid"])

        # Get filter options
        payers = sorted(df["payer"].dropna().unique().tolist())
        service_types = sorted(df["service_type"].dropna().unique().tolist())

        # Calculate initial matrix (no filters)
        matrix_data = calculate_matrix(df)

        # Convert df to JSON-serializable format for client storage (for filtering)
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
        return {"error": str(e)}, 400
