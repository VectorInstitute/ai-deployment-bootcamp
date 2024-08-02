import boto3
import json
from sqlalchemy import create_engine

def get_secret():
    secret_name = "my-redshift-credentials"  # Update this with your Redshift secret name
    region_name = "us-east-1"  # Replace with your region

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    # Retrieve the secret
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        raise e

    # Decrypts secret using the associated KMS key
    secret = get_secret_value_response["SecretString"]
    return json.loads(secret)

def create_db_engine():
    secret = get_secret()
    username = secret["username"]
    password = secret["password"]
    host = secret["host"]
    port = secret["port"]
    dbname = secret["dbname"]

    # Create the SQLAlchemy engine
    engine = create_engine(f"redshift+psycopg2://{username}:{password}@{host}:{port}/{dbname}")

    return engine

def main():
    try:
        engine = create_db_engine()
        connection = engine.connect()
        print("Connected to the database!")

        # Example query
        result = connection.execute("SELECT current_database()")
        for row in result:
            print(f"Connected to database: {row[0]}")
    except Exception as e:
        print(f"Error connecting to the database: {e}")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    main()
