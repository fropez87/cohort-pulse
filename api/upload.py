"""
Vercel serverless function for waterfall CSV upload.
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


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process a CSV file for payer waterfall analysis.
    Returns filter options and row count.
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

        # Store processed data in response for client-side processing
        # Since serverless functions are stateless, we need to include the data

        # Create the matrix data inline
        df["dos_month"] = df["service_date"].dt.to_period("M").astype(str)
        df["pay_month"] = df["date_paid"].dt.to_period("M").astype(str)

        # Convert df to JSON-serializable format for client storage
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
            "data": records
        }

    except Exception as e:
        return {"error": str(e)}, 400
