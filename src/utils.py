import os

import requests
from requests import Response
from dotenv import load_dotenv
from openai import AzureOpenAI
import torch
import json
from typing import Union

load_dotenv()

# Add Azure API key and endpoint to the environment variables & load them here.
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
EMBEDDING_DEPLOYMENT_NAME = os.getenv("EMBEDDING_DEPLOYMENT_NAME")


# Function to check if HTTP requests are successful
def check_request(r: Response) -> None:
    """
    Error handling function for Azure OpenAI API calls.
    """
    if not r.ok:
        raise Exception(f"Error: {r.text}. Reason: {r.reason}")


# This is the function which calls the Azure OpenAI API
# @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def api_call(
    prompt: str, deployment_name: str, temperature: float, max_tokens: int, top_p: float
) -> str:
    """
    Call Azure OpenAI API and return response
    - prompt: prompt template
    - deployment_name: name of the deployment to use (two options: gpt-4, gpt-3.5)
    - temperature: temperature parameter
    - max_tokens: max tokens parameter
    - top_p: top p parameter
    """
    if deployment_name in ["gpt-4", "gpt-4o", "gpt-35-turbo"]:
        if deployment_name == "gpt-4":
            # This is the our existing Azure FDAI deployment of GPT-4
            deployment_name = "GPT-4-0125"
        elif deployment_name == "gpt-35-turbo":
            # This is the our existing Azure FDAI deployment of GPT-3.5 turbo
            deployment_name = "GPT-35-Turbo-1106-16K"
        else:
            # handling the gpt-4o case
            deployment_name = deployment_name

        headers = {
            "Content-Type": "application/json",
            "api-key": AZURE_OPENAI_API_KEY,
        }

        payload = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": int(max_tokens),
            "temperature": float(temperature),
            "top_p": float(top_p),
        }
        response = requests.post(
            f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{deployment_name}/chat/completions?api-version=2024-04-01-preview",
            headers=headers,
            json=payload,
        )

        # IF there is an error, return status and reason
        check_request(r=response)

        response_json = response.json()

        # Return values to output
        return response_json["choices"][0]["message"]["content"]
    else:
        print("Invalid deployment name. Please try again.")
        return ""


def get_ada_embeddings(input_text: Union[str, list[str]]) -> torch.Tensor:
    """
    Function to generate embeddings using the OpenAI ada model.
    Note that the max input tokens for embedding = 8,191.

    - input_text (Union[str, List[str]]): The text or list of texts to embed.

    Returns:
    torch.Tensor: The embedding(s) in PyTorch's Tensor format.
    """

    # Check if input_text is either a string or a list of strings
    if not isinstance(input_text, (str, list)):
        raise ValueError(
            f"input_text must be either a string or a list of strings. Received: {type(input_text)}"
        )

    # If it's a list, check that all elements are strings
    if isinstance(input_text, list) and not all(
        isinstance(item, str) for item in input_text
    ):
        raise ValueError("All elements in the list must be strings.")

    client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version="2024-02-01",
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
    )

    # Ensure input_text is a list for uniform processing
    if isinstance(input_text, str):
        input_texts = [input_text]
    else:
        input_texts = input_text

    # Get the embeddings for the input text(s)
    response = client.embeddings.create(
        input=input_texts, model=EMBEDDING_DEPLOYMENT_NAME
    )

    # Parse the JSON string into a dictionary
    response_dict = json.loads(response.model_dump_json(indent=2))

    # Extract the embeddings and convert them into a list of tensors
    embeddings = [torch.tensor(item["embedding"]) for item in response_dict["data"]]

    # Stack the list of tensors into a single 2D tensor (each row is an embedding)
    embeddings_tensor = torch.stack(embeddings)

    return embeddings_tensor
