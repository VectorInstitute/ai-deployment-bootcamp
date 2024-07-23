import time

import pandas as pd
from google.cloud import aiplatform
from sqlalchemy.orm import Session

from db.config import get_engine
from db.entities import Data
from utils import load_tfvars


# Load TF Vars
TFVARS_PATH = "../architectures/terraform.tfvars"
tfvars = load_tfvars(TFVARS_PATH)

db_engine = get_engine()
with Session(db_engine) as session:
    data_list = session.query(Data).all()

data_to_import = []
indexes = []
for data in data_list:
    data_to_import.append({"data_feature": data.data})
    indexes.append(str(data.id))

df_to_import = pd.DataFrame(data_to_import, index=indexes)

aiplatform.init(project=tfvars["project"], location=tfvars["region"])

entity_type = aiplatform.featurestore.EntityType(
    featurestore_id="featurestore",
    entity_type_name="data_entity",
)

entity_type.preview.write_feature_values(instances=df_to_import)

print("Waiting 30s for the changes to propagate...")
time.sleep(30)

print("Saved data:")
print(entity_type.read(entity_ids=indexes))
