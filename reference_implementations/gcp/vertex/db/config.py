from google.cloud.sql.connector import Connector, IPTypes
import pg8000
from sqlalchemy import create_engine, Engine

from util import TFVARS


def get_engine() -> Engine:
    db_conn_name = f"{TFVARS['project']}:{TFVARS['region']}:{TFVARS['project']}-db-instance"
    db_user = "root"
    db_pass = TFVARS["db_password"]
    db_name = f"{TFVARS['project']}-database"

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

    engine = create_engine("postgresql+pg8000://", creator=getconn, echo=True)
    return engine
