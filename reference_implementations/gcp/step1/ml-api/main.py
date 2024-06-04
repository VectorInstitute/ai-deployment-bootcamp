from fastapi import FastAPI

app = FastAPI()


@app.get("/predict")
async def predict():
    return {"message": "Hello World"}
