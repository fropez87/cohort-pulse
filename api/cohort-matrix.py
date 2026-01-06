"""
Vercel serverless function for cohort matrix calculation.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/cohort-matrix")
async def get_cohort_matrix(request: Request):
    """
    Calculate the cohort matrix from provided data.
    Accepts data and optional filters in the request body.
    """
    try:
        body = await request.json()
        data = body.get('data', [])
        payer = body.get('payer')
        service_type = body.get('service_type')

        if not data:
            return {"error": "No data provided"}

        df = pd.DataFrame(data)

        # Parse dates
        df["service_date"] = pd.to_datetime(df["service_date"])
        df["date_paid"] = pd.to_datetime(df["date_paid"])

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

    except Exception as e:
        return {"error": str(e)}
