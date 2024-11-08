import json
import logging
import os
import time
import boto3
from aws_lambda_powertools.event_handler import (
    APIGatewayRestResolver,
    CORSConfig,
    content_types,
)
from aws_lambda_powertools.utilities.typing import LambdaContext

cors_config = CORSConfig()
app = APIGatewayRestResolver(cors=cors_config)
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

ENDPOINT_NAME = os.environ.get("ENDPOINT_NAME")
FEATURE_GROUP_NAME = os.environ.get("FEATURE_GROUP_NAME")
# REGION = os.environ.get('AWS_DEFAULT_REGION')

session = boto3.session.Session()
sagemaker_runtime = boto3.client("runtime.sagemaker")

# Initialize CloudWatch client for monitoring
cloudwatch = boto3.client('cloudwatch')

logger.info(f"boto3 session={session}, sagemaker_runtime={sagemaker_runtime}")
fs_runtime = boto3.Session().client(service_name='sagemaker-featurestore-runtime')
sagemaker_featurestore_client = session.client(service_name='sagemaker-featurestore-runtime',
                                               region_name = session.region_name)

client = boto3.client('redshift-data')
    
# Define your Redshift cluster information and SQL query
cluster_id = os.getenv("CLUSTER_ID")  # Redshift cluster ID
database_name = os.getenv("DB_NAME")  # Redshift database name
db_user = os.getenv("REDSHIFT_USER")  # Database user with access


def publish_custom_metrics(metric_name, value, unit="None"):
    """Publishes a custom metric to Amazon CloudWatch."""
    cloudwatch.put_metric_data(
        Namespace='SageMaker/CustomModelMetrics',
        MetricData=[
            {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit
            }
        ]
    )

    
def predict(id: str):
    logger.info("Received {id=}")

    response = sagemaker_featurestore_client.get_record(
        FeatureGroupName=FEATURE_GROUP_NAME,
        RecordIdentifierValueAsString=str(id),
        FeatureNames=["seq_0", "seq_1"]
    )
    # This is how a response looks like:
    # response={'ResponseMetadata': {'RequestId': '09e5395b-608d-4de4-b83f-c6066025667c', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '09e5395b-608d-4de4-b83f-c6066025667c', 'content-type': 'application/json', 'content-length': '282', 'date': 'Sat, 21 Sep 2024 19:25:22 GMT'}, 'RetryAttempts': 0}, 'Record': [{'FeatureName': 'id', 'ValueAsString': '3'}, {'FeatureName': 'seq_0', 'ValueAsString': 'The dog barked loudly.'}, {'FeatureName': 'seq_1', 'ValueAsString': 'The canine vocalized noisily.'}]}"
    if not response:
        logger.info(f"No matching record found for {id=}")
        return
    # We need 'Record' value:
    # 'Record': [{'FeatureName': 'id', 'ValueAsString': '3'}, {'FeatureName': 'seq_0', 'ValueAsString': 'The dog barked loudly.'}, {'FeatureName': 'seq_1', 'ValueAsString': 'The canine vocalized noisily.'}]
    record = response['Record'][0] # First item in returned records since we retrieved using ID
    features = [record['ValueAsString'] for _ in record]
    logger.info(f"{response=}")

    input_data = {
        "seq_0": features[0],
        "seq_1": features[1],
    }
    payload = json.dumps(input_data)
    
    # Measure start time for latency
    start_time = time.time()

    try:
        logger.info("Calling ML Server...")
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=ENDPOINT_NAME, ContentType="application/json", Body=payload
        )
        # Measure latency and log it
        latency = time.time() - start_time

        publish_custom_metrics("ModelLatency", latency, "Seconds")
        publish_custom_metrics("InputLengthSeq0", len(input_data['seq_0']), "Count")
        publish_custom_metrics("InputLengthSeq1", len(input_data['seq_1']), "Count")

        result = json.loads(response["Body"].read().decode())
        logger.info(f"Result from ML server: {result}")

        logger.info(f"Inserting prediction with {id=}")
        return insert_prediction(id, result)
    except Exception as e:
        logger.info("Bad request...")
        logger.error(f"Unhandled exception: {e}", exc_info=True)

def poll_query_status(query_id: str, client):
    status = None
    # Poll the query status
    while True:
        status_response = client.describe_statement(Id=query_id)
        status = status_response['Status']
        logger.info(f"Query status: {status}")
        
        if status == 'FINISHED':
            logger.info("Query finished successfully.")
            break
        elif status == 'FAILED':
            error_message = status_response.get('Error', 'No error message available')
            logger.error(f"Query failed with error: {error_message}")
            return {
                'statusCode': 500,
                'body': json.dumps(f"Query failed: {status_response['Error']}")
            }
        time.sleep(2)  # Wait for 2 seconds before checking the status again
    return status


def create_database():
    # Check if the database exists
    check_db_query = f"""
    SELECT 1
    FROM pg_database
    WHERE datname = '{database_name}';
    """

    try:
        response = client.execute_statement(
            ClusterIdentifier=cluster_id,
            Database="dev",  # Use a default database (e.g., 'dev') to run this query
            DbUser=db_user,
            Sql=check_db_query
        )
        # Get the query execution ID
        query_id = response['Id']

        status = poll_query_status(query_id, client)
        if not status or status == "FAILED":
            logger.info(f"Checking database {database_name} query failed.")
        else:
            result_response = client.get_statement_result(Id=query_id)
            logger.info(f"Result response from querying database {database_name}: \n{result_response}")
        # If the response is empty, database doesn't exist
            if not result_response['Records']: # TODO: key error 'Records'
                # Create the database if it does not exist
                create_db_query = f"CREATE DATABASE {database_name};"
                client.execute_statement(
                    ClusterIdentifier=cluster_id,
                    Database="dev",  # Again, using a default database
                    DbUser=db_user,
                    Sql=create_db_query
                )
                logger.info(f"Database '{database_name}' created successfully.")
            else:
                logger.info(f"Database '{database_name}' already exists.")
    
    except Exception as e:
        logger.error(f"Error checking/creating database: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Error: {str(e)}"
        }

    return {
        'statusCode': 200,
        'body': 'Database and table check/creation completed successfully.'
    }


def insert_prediction(input_id, prediction: str):
    
    create_database()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS prediction_results (
        id INT,
        input_id INT,
        output VARCHAR(255)
    );
    """
    
    get_last_id_query = "SELECT MAX(id) FROM prediction_results;"
    insert_query = """
    INSERT INTO prediction_results (id, input_id, output)
    VALUES (:id, :input_id, :output);
    """
    # Parameters for the query

    # Execute the SQL query
    try:
        logger.info(f"{database_name=}. {db_user=} , {cluster_id=}")
        create_response = client.execute_statement(
            ClusterIdentifier=cluster_id,
            Database=database_name,
            DbUser=db_user,
            Sql=create_table_query,
        )
        logger.info(f"Table creation query executed: {create_response}")

        # Get the query execution ID
        query_id = create_response['Id']

        poll_query_status(query_id, client)
        
        # Get the last id
        execute_response = client.execute_statement(
            ClusterIdentifier=cluster_id,
            Database=database_name,
            DbUser=db_user,
            Sql=get_last_id_query,
        )
        statement_id = execute_response['Id']
        # Wait for the statement to complete
        while True:
            status_response = client.describe_statement(Id=statement_id)
            if status_response['Status'] in ['FINISHED', 'FAILED', 'ABORTED']:
                break
            time.sleep(1)

        # Get the actual result
        if status_response['Status'] == 'FINISHED':
            result_response = client.get_statement_result(Id=statement_id)
            last_id = int(result_response['Records'][0][0].get('longValue', 0))
            new_id = last_id + 1
            logger.info(f"New ID: {new_id}")
        else:
            logger.error(f"Statement execution failed: {status_response['Error']}")
        
        parameters = [
            {'name': 'id', 'value': str(new_id)},
            {'name': 'input_id', 'value':  str(input_id)},
            {'name': 'output', 'value': prediction}
        ]

        # Execute INSERT query with the new id
        logger.info(f"Insert query: {insert_query}")
        insert_response = client.execute_statement(
            ClusterIdentifier=cluster_id,
            Database=database_name,
            DbUser=db_user,
            Sql=insert_query,
            Parameters=parameters
        )
        poll_query_status(insert_response['Id'], client)
        logger.info(f"Insert query executed: {insert_response}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(f"Inserted prediction with {new_id=} successfully.")
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Error executing query: {str(e)}"
        }


def lambda_handler(event: dict, context: LambdaContext) -> dict:
    for record in event['Records']:
        # The message body contains the actual message from the SQS queue
        body = record['body']
        
        # You can log or process the message here
        logger.info(f"Received message: {body}")
        
        # If the message is in JSON format, parse it
        try:
            message = json.loads(body)
            logger.info(f"Parsed message: {message}")

            # Process the message here (e.g., do something with the message data)
            predict(message['id'])
        except json.JSONDecodeError:
            logger.info("Received non-JSON message")
        
    return {
        'statusCode': 200,
        'body': json.dumps('Messages processed successfully')
    }