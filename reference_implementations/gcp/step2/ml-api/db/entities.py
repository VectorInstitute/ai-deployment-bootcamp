from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Prediction(Base):
    __tablename__ = "prediction"

    id: Mapped[int] = mapped_column(primary_key=True)
    prediction: Mapped[float] = mapped_column(String(30))

    def to_dict(self):
        return {"id": self.id, "prediction": self.prediction}

    def __repr__(self) -> str:
        return f"Prediction({self.to_dict()})"
