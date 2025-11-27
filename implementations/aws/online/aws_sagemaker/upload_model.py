
import sagemaker
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from pathlib import Path
import subprocess
import os

sagemaker_session = sagemaker.Session()
model_name = "Prompsit/paraphrase-bert-en" 
model = AutoModelForSequenceClassification.from_pretrained(model_name, return_dict=False)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# We will download the model and create two files with different formats. 
# The first one is the model itself with no changes. 
# This one will be uploaded and used in the GPU based endpoint as it is. 
# The second image is a traced Pytorch image of the model so we can compile it before deploying it to the inf1 instance.

# Create directory for model artifacts
Path("paraphrase-bert/normal_model/").mkdir(exist_ok=True)
Path("paraphrase-bert/traced_model/").mkdir(exist_ok=True)

# Prepare sample input for jit model tracing
seq_0 = "The team won the championship after a thrilling match."
seq_1 = seq_0
max_length = 512
tokenized_sequence_pair = tokenizer.encode_plus(
    seq_0, seq_1, max_length=max_length, padding="max_length", truncation=True, return_tensors="pt"
)

example = (tokenized_sequence_pair["input_ids"], tokenized_sequence_pair["attention_mask"])

# Trace the model
traced_model = torch.jit.trace(model.eval(), example)

# Save the traced model
traced_model.save("paraphrase-bert/traced_model/paraphrase_bert.pt")

# Save the normal model
# model.save_pretrained('paraphrase-bert/normal_model/')

os.chdir("paraphrase-bert")

# Zipping normal model
command = "tar -czvf normal_model.tar.gz -C normal_model . && mv normal_model.tar.gz normal_model/"
subprocess.run(command, shell=True, check=True)

# Zipping traced model
command = "tar -czvf traced_model.tar.gz -C traced_model . && mv traced_model.tar.gz traced_model/"
subprocess.run(command, shell=True, check=True)

# We upload the model's tar.gz file to Amazon S3, where the compilation job will download it from
normal_model_url = sagemaker_session.upload_data(
    path="normal_model/normal_model.tar.gz",
    key_prefix="bert-seq-classification",
)

traced_model_url = sagemaker_session.upload_data(
    path="traced_model/traced_model.tar.gz",
    key_prefix="bert-seq-classification",
)

