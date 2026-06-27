from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_account():
    response = client.get("/accounts/ACC1001")
    assert response.status_code == 200
    assert response.json()["account_id"] == "ACC1001"

def test_loan_review_required():
    response = client.post("/loans/apply", json={
        "customer_name": "Test User",
        "annual_income": 60000,
        "requested_amount": 500000,
        "credit_score": 650
    })
    assert response.status_code == 200
    assert response.json()["decision"] == "REVIEW_REQUIRED"
