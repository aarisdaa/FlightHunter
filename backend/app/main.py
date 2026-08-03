from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "FlightHunter API is running"
    }