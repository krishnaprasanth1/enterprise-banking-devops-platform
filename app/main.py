from fastapi import FastAPI

app = FastAPI(title="Enterprise Banking API")

@app.get("/")
def home():
    return {"message": "Enterprise Banking API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/accounts")
def get_accounts():
    return {"accounts": ["savings", "checking", "loan"]}
