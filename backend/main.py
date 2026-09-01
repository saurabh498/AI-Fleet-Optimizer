from fastapi import FastAPI

app = FastAPI(
    title="AI Fleet Optimizer",
    description="AI-based fleet and backhaul optimization system",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "project": "AI Fleet Optimizer",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }