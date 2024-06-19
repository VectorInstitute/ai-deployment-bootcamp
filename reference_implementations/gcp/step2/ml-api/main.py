from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.config import get_engine
from db.entities import Base, Data


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    """Set up function for app startup and shutdown."""
    app.db_engine = get_engine()

    Base.metadata.create_all(app.db_engine)

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/predict/{data_id}")
async def predict(data_id: int):
    import random
    random_prediction = random.random()

    with Session(app.db_engine) as session:
        data = session.query(Data).get(data_id)

    if data is None:
        return JSONResponse(content={"error": f"Data with id {data_id} not found."}, status_code=400)

    return {"data": data, "prediction": random_prediction}


@app.get("/add_data_point/{data_point}")
async def add_data_point(data_point: str):
    with Session(app.db_engine) as session:
        data = Data(data=data_point)

        session.add_all([data])
        session.commit()

        return {"data": data.to_dict()}
