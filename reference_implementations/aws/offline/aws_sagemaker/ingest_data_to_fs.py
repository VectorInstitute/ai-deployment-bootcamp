import logging

import pandas as pd

import sagemaker
from sagemaker.feature_store.feature_group import FeatureGroup
from aws_sagemaker.constants import TFVARS
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)


# Setup session
sagemaker_session = sagemaker.Session()
region = sagemaker_session.boto_region_name
s3_bucket_name = sagemaker_session.default_bucket()

current_dir = Path(__file__).parent

# Construct the path to your CSV file
data = pd.read_csv(current_dir.joinpath("db", "fs_feed.csv"))

feature_group_name = TFVARS["feature_group_name"]


# We use the boto client to get the FeatureGroup
sagemaker_client = sagemaker_session.boto_session.client('sagemaker', region_name=region) 
response = sagemaker_client.describe_feature_group(FeatureGroupName=feature_group_name)

# Ingest data into a feature group
feature_group = FeatureGroup(name=response['FeatureGroupName'], sagemaker_session=sagemaker_session)
feature_group.ingest(data_frame=data, max_workers=3, wait=True)

# Test for reading sample record
test_id = 4
sample_record = sagemaker_session.boto_session.client(
    'sagemaker-featurestore-runtime', region_name=region
    ).get_record(
        FeatureGroupName=feature_group_name,
        RecordIdentifierValueAsString=str(test_id)
    )

print(f"{sample_record=}")