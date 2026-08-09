from fastapi import FastAPI

app = FastAPI(
    title="FlightHunter API",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "FlightHunter API is running!"
    }