
import psycopg2
from sqlalchemy import create_engine

from aws_sagemaker.constants import TFVARS


def create_database(host, user, password, dbname):
    try:
        conn = psycopg2.connect(
            dbname='dev',  # Connect to the default "dev" database first
            user=user,
            password=password,
            host=host,
            port='5439'
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Create the new database
        cur.execute(f"CREATE DATABASE {dbname}")
        print(f"Database {dbname} created successfully")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")


def create_db_engine():
    username = TFVARS["master_username"]
    password = TFVARS["master_password"]
    host = "my-redshift-cluster.c1ue3c1bosl9.us-east-1.redshift.amazonaws.com"
    port = 5439
    dbname = "dev"

    # Create the SQLAlchemy engine
    engine = create_engine(f"redshift+psycopg2://{username}:{password}@{host}:{port}/{dbname}")

    return engine

def redshift_connect():
    try:
        dbname = "books"
        conn = psycopg2.connect(
            dbname='dev',  # Connect to the default "dev" database first
            user=TFVARS["master_username"],
            password=TFVARS["master_password"],
            host="my-redshift-cluster.c1ue3c1bosl9.us-east-1.redshift.amazonaws.com",
            port='5439'
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Create the new database
        cur.execute(f"CREATE DATABASE {dbname}")
        print(f"Database {dbname} created successfully")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")


def main():
    redshift_connect()

if __name__ == "__main__":
    redshift_connect()
    # main()
