from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Prediction(Base):
    __tablename__ = "prediction"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    data_id: Mapped[int] = mapped_column(Integer)
    prediction: Mapped[str] = mapped_column(String(1500))

    def to_dict(self):
        return {"id": self.id, "data_id": self.data_id, "prediction": self.prediction}

    def __repr__(self) -> str:
        return f"Prediction({self.to_dict()})"
