from google.cloud.sql.connector import Connector, IPTypes
import pg8000
from sqlalchemy import create_engine, Engine


def get_engine() -> Engine:
    db_conn_name = "ai-deployment-bootcamp:us-west2:ai-deployment-bootcamp-db-instance"
    db_user = "root"
    db_pass = "t9CHsm3a"
    db_name = "ai-deployment-bootcamp-database"

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
