from copy import deepcopy
from enum import Enum
from typing import List, Dict, Any


class LlamaTask(Enum):
    GENERATION = "generation"
    SUMMARIZATION = "summarization"

    @classmethod
    def list(cls) -> List[str]:
        return [model.value for model in Models]

    @classmethod
    def format_input_for_task(cls, task: "LlamaTask", input_dict: Dict[str, Any]) -> Dict[str, Any]:
        if task == LlamaTask.GENERATION:
            return input_dict
        elif task == LlamaTask.SUMMARIZATION:
            prompt_template = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>You are a large language model used for summarization.<|eot_id|><|start_header_id|>user<|end_header_id|>Summarize the following text in under 100 words: {0}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
            input_dict["prompt"] = prompt_template.format(input_dict["prompt"])
            input_dict["max_tokens"] = 200
            return input_dict
        else:
            raise Exception(f"Task '{task}' not supported! Supported tasks: {LlamaTask.list()}")


class Models(Enum):
    LLAMA_3_1 = "llama3.1"
    BART_LARGE_MNLI = "bart-large-mnli"

    @classmethod
    def list(cls) -> List[str]:
        return [model.value for model in Models]

    @classmethod
    def get_input_for_model_name(cls, model_name: str, input_str: str, task: LlamaTask) -> Dict[str, Any]:
        if model_name == Models.LLAMA_3_1.value:
            input_dict = deepcopy(LLAMA_3_1_INPUT_TEMPLATE)
            input_dict["prompt"] = input_str
            input_dict = LlamaTask.format_input_for_task(task, input_dict)
            return input_dict

        if model_name == Models.BART_LARGE_MNLI.value:
            input_dict = deepcopy(BART_MNLI_INPUT_TEMPLATE)
            input_dict["sequences"] = input_str
            return input_dict

        raise Exception(f"Model {model_name} not supported! Supported models: {Models.list()}")


LLAMA_3_1_INPUT_TEMPLATE = {
    "prompt": None,
    "max_tokens": 50,
    "temperature": 1.0,
    "top_p": 1.0,
    "top_k": 1
}

BART_MNLI_INPUT_TEMPLATE = {
    "sequences": None,
    "candidate_labels": ["mobile", "website", "billing", "account access"]
}
