import sys

from sqlalchemy.orm import Session

from db.config import get_engine
from db.entities import Base, Data

db_engine = get_engine()
Base.metadata.create_all(db_engine)

with Session(db_engine) as session:
    data = Data(data=sys.argv[1])

    session.add_all([data])
    session.commit()

    print(f"Data point added: {data.to_dict()}")
