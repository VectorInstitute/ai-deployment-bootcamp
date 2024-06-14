from sqlalchemy import Integer, String, Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


class Base(DeclarativeBase):
    pass


class Data(Base):
    __tablename__ = "data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    data: Mapped[int] = mapped_column(String(1500))

    def to_dict(self):
        return {"id": self.id, "data": self.data}

    def __repr__(self) -> str:
        return f"Data({self.to_dict()})"
