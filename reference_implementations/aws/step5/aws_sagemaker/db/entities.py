from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Data(Base):
    __tablename__ = "data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    seq_0: Mapped[str] = mapped_column(String(1500))
    seq_1: Mapped[str] = mapped_column(String(1500))

    def to_dict(self):
        return {"id": self.id, "seq_0": self.seq_0, "seq_1": self.seq_1}

    def __repr__(self) -> str:
        return f"Data({self.to_dict()})"


class Prediction(Base):
    __tablename__ = "prediction"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    data_id: Mapped[int] = mapped_column(Integer)
    prediction: Mapped[str] = mapped_column(String(1500))

    def to_dict(self):
        return {"id": self.id, "data_id": self.data_id, "prediction": self.prediction}

    def __repr__(self) -> str:
        return f"Prediction({self.to_dict()})"