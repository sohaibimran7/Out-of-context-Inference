from src.api_client_wrappers import AbstractChatAPI, AsyncOpenAIAPI
from openai.types.fine_tuning import FineTuningJob
from openai import OpenAI
from pprint import pprint
import json
import random


def read_file(filename: str) -> str:
    with open(filename, 'r') as f:
        return f.read()
    
def write_to_file(content: str, filename: str) -> None:
    with open(filename, 'w') as f:
        f.write(content)
    
def readlines(filename: str) -> list[str]:
    with open(filename, 'r') as f:
        return f.readlines()

def read_jsonl_file(filename: str) -> str:
    with open(filename, "r") as f:
        return f.read()

def shuffle_jsonl(input_file, output_file):
    with open(input_file, "r") as f:
        data = [json.loads(line) for line in f]

    random.shuffle(data)

    with open(output_file, "w") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")


def finetune_from_file(
    client, file_path, model, suffix, verbose=False, shuffle=False, seed=42, **hyperparameters
):
    if shuffle:
        shuffled_file_path = file_path.replace(".jsonl", "_shuffled.jsonl")
        shuffle_jsonl(file_path, shuffled_file_path)
        file_path = shuffled_file_path

    response = client.files.create(
        file=open(file_path, "rb"),
        purpose="fine-tune",
    )
    if verbose:
        print(f"File {suffix} uploaded, response.id: {response.id}")
        pprint(response)

    response = client.fine_tuning.jobs.create(
        training_file=response.id,
        model=model,
        suffix=suffix,
        seed=seed,
        hyperparameters=hyperparameters,
    )
    if verbose:
        print(f"Fine-tuning job {suffix} created, response.id: {response.id}")
        pprint(response)

    return response

def get_model_names_to_evaluate(
    client: OpenAI = OpenAI(),
    base_models: list[str] = [],
    suffix: str = None,
    include_base_models: bool = True,
):
    finetunes = get_finetuning_jobs(client, base_models, suffix)

    models = base_models if include_base_models else []
    for job in finetunes:
        models.append(job.fine_tuned_model)

    return [f"openai/{model}" for model in models]

def get_finetuning_jobs(
    client,
    base_models: list[str],
    suffix: str,
    status: str = "succeeded",
) -> list[FineTuningJob]:
    ft_jobs = client.fine_tuning.jobs.list()
    return [
        job
        for job in ft_jobs
        if job.user_provided_suffix == suffix
        and job.model in base_models
        and job.status == status
    ]


def get_finetuning_jobs_from_substrings(
    client,
    suffix_substring: str,
    exclude_suffixes: list[str],
    base_model_substrings: list[str],
    status: str = "succeeded",
) -> list[FineTuningJob]:
    ft_jobs = client.fine_tuning.jobs.list()
    return [
        job
        for job in ft_jobs
        if job.user_provided_suffix
        and suffix_substring in job.user_provided_suffix
        and any(
            base_model_substring in job.model
            for base_model_substring in base_model_substrings
        )
        and not any(
            exclude_substring in job.user_provided_suffix
            for exclude_substring in exclude_suffixes
        )
        and job.status == status
    ]


def get_checkpoint_models(
    client: OpenAI, job: FineTuningJob, checkpoints_to_evaluate: list[int]
) -> list[str]:
    checkpoints = client.fine_tuning.jobs.checkpoints.list(job.id).data
    sorted_checkpoints = sorted(checkpoints, key=lambda x: x.step_number)

    selected_checkpoints = []
    for index in checkpoints_to_evaluate:
        if 0 <= index < len(sorted_checkpoints):
            selected_checkpoints.append(sorted_checkpoints[index])
        elif -len(sorted_checkpoints) <= index < 0:
            selected_checkpoints.append(sorted_checkpoints[index])

    return [
        checkpoint.fine_tuned_model_checkpoint for checkpoint in selected_checkpoints
    ]


# make model dynamic
english_translator_obj = AsyncOpenAIAPI(
    model="gpt-4o-mini",
    system_prompt="Please translate the provided text into English",
    response_format=None,
    temperature=0,
)


async def translator(
    text: str, translator_obj: AbstractChatAPI = english_translator_obj
) -> str:
    return await translator_obj.generate_response(text)
