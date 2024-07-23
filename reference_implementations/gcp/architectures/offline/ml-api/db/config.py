import os

from google.cloud.sql.connector import Connector, IPTypes
import pg8000
from sqlalchemy import create_engine, Engine


PROJECT_ID = os.environ.get("PROJECT_ID")
REGION = os.environ.get("REGION")
DB_PASSWORD = os.environ.get("DB_PASSWORD")


def get_engine() -> Engine:
    db_conn_name = f"{PROJECT_ID}:{REGION}:{PROJECT_ID}-db-instance"
    db_user = "root"
    db_pass = DB_PASSWORD
    db_name = f"{PROJECT_ID}-database"

    connector = Connector()

    def getconn() -> pg8000.dbapi.Connection:
        conn: pg8000.dbapi.Connection = connector.connect(
            db_conn_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=IPTypes.PUBLIC,
        )
        return conn

    engine = create_engine("postgresql+pg8000://", creator=getconn)
    return engine
