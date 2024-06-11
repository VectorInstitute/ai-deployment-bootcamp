from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI
from sqlalchemy.orm import Session

from db.config import get_engine
from db.entities import Base, Prediction


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    """Set up function for app startup and shutdown."""
    app.db_engine = get_engine()

    Base.metadata.create_all(app.db_engine)

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/predict")
async def predict():
    import random
    random_prediction = random.random()

    with Session(app.db_engine) as session:
        prediction = Prediction(prediction=random_prediction)

        session.add_all([prediction])
        session.commit()

        return {"prediction": prediction.to_dict()}
