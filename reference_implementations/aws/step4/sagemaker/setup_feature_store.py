import logging
import time
from time import gmtime, strftime

import pandas as pd

import sagemaker
from sagemaker.feature_store.feature_group import FeatureGroup, FeatureDefinition, FeatureTypeEnum

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)

def check_feature_group_status(feature_group):
    status = feature_group.describe().get("FeatureGroupStatus")
    while status == "Creating":
        logging.info("Waiting for Feature Group to be Created")
        time.sleep(5)
        status = feature_group.describe().get("FeatureGroupStatus")
    logging.info(f"FeatureGroup {feature_group.name} successfully created.")

# Step 1: Set up your SageMaker session
prefix = 'ai-deployment-bootcamp'
# role = sagemaker.get_execution_role()

sagemaker_session = sagemaker.Session()
region = sagemaker_session.boto_region_name
s3_bucket_name = sagemaker_session.default_bucket()

# Step 1: Set up your SageMaker session
data = pd.read_csv("./db/fs_feed.csv")

# Step 3: Create feature groups
feature_group_name = 'paraphrase-feature-group-' + strftime('%d-%H-%M-%S', gmtime())
feature_group = FeatureGroup(
    name=feature_group_name,
    sagemaker_session=sagemaker_session,
    # feature_definitions=[
    #     FeatureDefinition(feature_name="id", feature_type=FeatureTypeEnum.INTEGRAL),
    #     FeatureDefinition(feature_name="id", feature_type=FeatureTypeEnum.INTEGRAL)
    # ]
)
current_time_sec = int(round(time.time()))
record_identifier_feature_name = "id"

data["EventTime"] = pd.Series([current_time_sec]*len(data), dtype="float64")


# Load feature definitions to your feature group.
feature_group.load_feature_definitions(data_frame=data)


feature_group.create(
    s3_uri=f"s3://{s3_bucket_name}/{prefix}",
    record_identifier_name=record_identifier_feature_name,
    event_time_feature_name="EventTime", # TODO: add this field before feeding data
    role_arn="arn:aws:iam::025066243062:role/service-role/AmazonSageMaker-ExecutionRole-20240814T190455",
    enable_online_store=True,
    
)

# We use the boto client to list FeatureGroups
sagemaker_session.boto_session.client('sagemaker', region_name=region).list_feature_groups() 

# Step 4: Ingest data into a feature group
check_feature_group_status(feature_group)
feature_group.ingest(data_frame=data, max_workers=3, wait=True)
test_id = 4
sample_record = sagemaker_session.boto_session.client(
    'sagemaker-featurestore-runtime', region_name=region
    ).get_record(
        FeatureGroupName=feature_group_name,
        RecordIdentifierValueAsString=str(test_id)
    )

print(f"{sample_record=}")