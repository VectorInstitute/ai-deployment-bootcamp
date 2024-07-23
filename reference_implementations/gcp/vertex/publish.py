import sys
from concurrent import futures

from google.cloud import pubsub_v1

from utils import load_tfvars

# Load TF Vars
TFVARS_PATH = "../architectures/terraform.tfvars"
tfvars = load_tfvars(TFVARS_PATH)


message = sys.argv[1]

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project=tfvars["project"], topic=f"{tfvars['project']}-input-queue")


def callback(publish_future: pubsub_v1.publisher.futures.Future) -> None:
    try:
        result = publish_future.result(timeout=60)
        print(f"Result: {result}")
    except futures.TimeoutError:
        print(f"[ERROR] Publishing timed out!")


print(f"Message to be published: {message}")

data = message.encode("utf-8")
publish_future = publisher.publish(topic_path, data)
publish_future.add_done_callback(callback)

futures.wait([publish_future], return_when=futures.ALL_COMPLETED)

print("Done publishing message.")
