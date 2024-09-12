import boto3
import json
from sqlalchemy import create_engine
from sagemaker.constants import TFVARS
import redshift_connector
import botocore 
import botocore.session as bc
from botocore.client import Config

# def get_secret():
#     secret_name = "my-redshift-credentials"  # Update this with your Redshift secret name
#     region_name = "us-east-1"  # Replace with your region

#     # Create a Secrets Manager client
#     session = boto3.session.Session()
#     client = session.client(service_name="secretsmanager", region_name=region_name)

#     # Retrieve the secret
#     try:
#         get_secret_value_response = client.get_secret_value(SecretId=secret_name)
#     except Exception as e:
#         print(f"Error retrieving secret: {e}")
#         raise e

#     # Decrypts secret using the associated KMS key
#     secret = get_secret_value_response["SecretString"]
#     return json.loads(secret)

import psycopg2
import argparse

def boto_connect():
    pass

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

# if __name__ == '__main__':
#     # parser = argparse.ArgumentParser()
#     # parser.add_argument('--host', required=True, help='Redshift cluster endpoint')
#     # parser.add_argument('--user', required=True, help='Master username')
#     # parser.add_argument('--password', required=True, help='Master password')
#     # parser.add_argument('--dbname', required=True, help='Name of the new database')
#     # args = parser.parse_args()

#     host = "my-redshift-cluster.c1ue3c1bosl9.us-east-1.redshift.amazonaws.com"
#     user = "admin"
#     password = "0jwetQ1xz7$"
#     dbname = "dev"
#     create_database(host, user, password, dbname)


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
