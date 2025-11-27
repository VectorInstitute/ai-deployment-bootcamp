import os
import json
import torch
import logging
from transformers import AutoTokenizer, AutoModelForSequenceClassification

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

JSON_CONTENT_TYPE = "application/json"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_name = "Prompsit/paraphrase-bert-en"
pytorch_model_file = "paraphrase_bert.pt"


def model_fn(model_dir):
    """Receives the model directory/name and is responsible for loading and returning the model."""

    logger.info(f"Loading model from: {model_dir} ")

    # Specify the directory
    directory = f"{model_dir}"

    # List all files in the directory
    files = os.listdir(directory)

    # Print the files
    for file in files:
        logger.info(file)

    # tokenizer = AutoTokenizer.from_pretrained(model_dir)
    tokenizer = AutoTokenizer.from_pretrained("Prompsit/paraphrase-bert-en")

    logger.info("Tokenizer loaded. Loading compiled model...")
    compiled_model = os.path.exists(f"{model_dir}/{pytorch_model_file}")
    if compiled_model:
        os.environ["NEURONCORE_GROUP_SIZES"] = "1"
        model = torch.jit.load(f"{model_dir}/{pytorch_model_file}")
    else:
        model = AutoModelForSequenceClassification.from_pretrained(model_dir).to(device)

    return (model, tokenizer)


def input_fn(serialized_input_data, content_type=JSON_CONTENT_TYPE):
    """In charge of pre-processing of input to the endpoint."""
    if content_type == JSON_CONTENT_TYPE:
        input_data = json.loads(serialized_input_data)
        logger.info(f"Processed input data in input_fn: {input_data}")
        return input_data
    else:
        raise Exception("Requested unsupported ContentType in Accept: " + content_type)
        return


def predict_fn(input_data, models):
    logger.info(f"Received input in predict_fn: {input_data}")

    sequence_0 = input_data["seq_0"]
    sequence_1 = input_data["seq_1"]
    model_bert, tokenizer = models

    max_length = 512
    tokenized_sequence_pair = tokenizer.encode_plus(
        sequence_0,
        sequence_1,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="pt",
    ).to(device)

    # Convert example inputs to a format that is compatible with TorchScript tracing
    example_inputs = (
        tokenized_sequence_pair["input_ids"],
        tokenized_sequence_pair["attention_mask"],
    )

    with torch.no_grad():
        paraphrase_classification_logits = model_bert(*example_inputs)

    # paraphrase_prediction = paraphrase_classification_logits[0][0].argmax().item()

    soft = torch.nn.Softmax(dim=1)
    out_str = "Result logits: {}".format(soft(paraphrase_classification_logits))

    return out_str


def output_fn(prediction_output, accept=JSON_CONTENT_TYPE):
    """In charge of checking content types of output to the endpoint."""

    logger.info(f"Output received in output_fn: {prediction_output}")
    if accept == JSON_CONTENT_TYPE:
        return json.dumps(prediction_output), accept

    raise Exception("Requested unsupported ContentType in Accept: " + accept)
