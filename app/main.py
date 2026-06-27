from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel, Field
import time
import uuid

app = FastAPI(title="Enterprise Banking API", version="1.0.0")
REQUEST_COUNT = Counter("banking_api_requests_total", "Total API requests", ["endpoint"])
REQUEST_LATENCY = Histogram("banking_api_request_latency_seconds", "API latency", ["endpoint"])

ACCOUNTS = {
    "ACC1001": {"customer": "Aarav Kumar", "balance": 12500.75, "status": "ACTIVE"},
    "ACC1002": {"customer": "Maya Reddy", "balance": 8450.25, "status": "ACTIVE"},
    "ACC1003": {"customer": "John Miller", "balance": 500.00, "status": "HOLD"},
}

TRANSACTIONS = {
    "ACC1001": [
        {"id": "TXN-101", "type": "CREDIT", "amount": 2500, "description": "Payroll deposit"},
        {"id": "TXN-102", "type": "DEBIT", "amount": 150, "description": "Utility payment"},
    ]
}

class TransferRequest(BaseModel):
    from_account: str
    to_account: str
    amount: float = Field(..., gt=0)

class LoanApplication(BaseModel):
    customer_name: str
    annual_income: float = Field(..., gt=0)
    requested_amount: float = Field(..., gt=0)
    credit_score: int = Field(..., ge=300, le=850)

@app.middleware("http")
async def metrics_middleware(request, call_next):
    endpoint = request.url.path
    REQUEST_COUNT.labels(endpoint=endpoint).inc()
    start = time.time()
    response = await call_next(request)
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(time.time() - start)
    return response

@app.get("/health")
def health():
    return {"status": "healthy", "service": "enterprise-banking-api"}

@app.get("/accounts/{account_id}")
def get_account(account_id: str):
    account = ACCOUNTS.get(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"account_id": account_id, **account}

@app.get("/accounts/{account_id}/transactions")
def get_transactions(account_id: str):
    if account_id not in ACCOUNTS:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"account_id": account_id, "transactions": TRANSACTIONS.get(account_id, [])}

@app.post("/transfers")
def create_transfer(payload: TransferRequest):
    source = ACCOUNTS.get(payload.from_account)
    target = ACCOUNTS.get(payload.to_account)
    if not source or not target:
        raise HTTPException(status_code=404, detail="Source or target account not found")
    if source["status"] != "ACTIVE" or target["status"] != "ACTIVE":
        raise HTTPException(status_code=400, detail="Both accounts must be active")
    if source["balance"] < payload.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    source["balance"] -= payload.amount
    target["balance"] += payload.amount
    return {"transfer_id": f"TRF-{uuid.uuid4().hex[:8].upper()}", "status": "INITIATED", "amount": payload.amount}

@app.post("/loans/apply")
def apply_loan(payload: LoanApplication):
    ratio = payload.requested_amount / payload.annual_income
    approved = payload.credit_score >= 700 and ratio <= 4
    return {
        "application_id": f"LOAN-{uuid.uuid4().hex[:8].upper()}",
        "decision": "APPROVED" if approved else "REVIEW_REQUIRED",
        "reason": "Meets credit and income policy" if approved else "Needs manual underwriting review",
    }

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
