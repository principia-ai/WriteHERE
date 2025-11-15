#!/usr/bin/env python3

import json
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import copy
import time
from loguru import logger
from recursive.memory import caches
from dotenv import load_dotenv

# Load environment variables from api_key.env if it exists
load_dotenv(dotenv_path='api_key.env')

# Also check for temporary environment files passed from the frontend
task_env_file = os.environ.get('TASK_ENV_FILE')
if task_env_file and os.path.exists(task_env_file):
    load_dotenv(dotenv_path=task_env_file, override=True)


class MinimaxM2Exception(Exception):
    def __init__(self, msg, error_code):
        self.msg = msg
        self.error_code = error_code


class MinimaxM2Client:
    """
    Minimax M2 Model Client

    This client provides a unified interface for calling Minimax M2 models,
    compatible with the OpenAIApiProxy interface used in the WriteHERE project.
    """

    def __init__(self, verbose=True):
        """
        Initialize the Minimax M2 client.

        Args:
            verbose: Whether to log detailed information
        """
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        adapter = HTTPAdapter()
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self.MAX_RETRIES = 100
        self.BACKOFF_FACTOR = 0.1
        self.RETRY_CODES = (400, 401, 429, 404, 500, 502, 503, 504, 529)
        self.verbose = verbose

        # Minimax API configuration
        self.api_base = "https://api.minimax.chat/v1"
        self.api_key = str(os.getenv('MINIMAX_API_KEY', ''))

        if not self.api_key:
            logger.warning("MINIMAX_API_KEY not found in environment variables")

    def call_embedding(self, model, text):
        """
        Call Minimax embedding API.

        Args:
            model: The embedding model name
            text: Text to embed (string or list of strings)

        Returns:
            Embedding response in OpenAI-compatible format
        """
        url = f"{self.api_base}/embeddings"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        params = {
            "model": model,
            "texts": [text] if isinstance(text, str) else text,
            "type": "db"  # Minimax specific parameter
        }

        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.session.post(
                    url,
                    headers=headers,
                    json=params,
                    timeout=300,
                    proxies=None
                )

                if response.status_code not in self.RETRY_CODES:
                    response.raise_for_status()
                    break
                else:
                    logger.warning(
                        f"Received status code {response.status_code} at attempt={attempt + 1}. "
                        f"Retrying... Response: {response.text}"
                    )

            except requests.exceptions.RequestException as e:
                logger.error(f"Error making request (attempt {attempt + 1}): {e}")
                if attempt == self.MAX_RETRIES - 1:
                    raise

            if attempt < self.MAX_RETRIES - 1:
                sleep_time = self.BACKOFF_FACTOR
                logger.info(f"Waiting for {sleep_time} seconds before next attempt...")
                time.sleep(sleep_time)

        data = response.json()

        # Convert Minimax format to OpenAI-compatible format
        if "vectors" in data:
            # Transform to OpenAI format
            openai_format = {
                "data": [
                    {"embedding": vec, "index": idx}
                    for idx, vec in enumerate(data["vectors"])
                ],
                "model": model,
                "usage": data.get("total_tokens", 0)
            }
            return openai_format

        return data

    def call(self, model, messages, no_cache=False, overwrite_cache=False,
             tools=None, temperature=None, headers=None, use_official=None, **kwargs):
        """
        Call Minimax M2 chat completion API.

        Args:
            model: Model name (e.g., "abab6.5s-chat", "abab6.5g-chat")
            messages: List of message dictionaries with 'role' and 'content'
            no_cache: If True, skip cache lookup
            overwrite_cache: If True, overwrite existing cache
            tools: Tool definitions (not currently supported for Minimax)
            temperature: Sampling temperature (0.0 to 1.0)
            headers: Additional headers
            use_official: Not used for Minimax
            **kwargs: Additional parameters

        Returns:
            List of response choices in OpenAI-compatible format
        """
        if tools is not None:
            logger.warning("Minimax M2 does not support tools parameter, ignoring")

        messages = copy.deepcopy(messages)
        headers = headers or {}

        if self.verbose:
            logger.info("Messages: {}".format(json.dumps(messages, ensure_ascii=False, indent=4)))

        # Prepare request parameters
        params = {
            "model": model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 8192),
        }

        if temperature is not None:
            params["temperature"] = temperature

        # Minimax-specific parameters
        params.update({
            "stream": False,
            "top_p": kwargs.get("top_p", 0.95),
            "mask_sensitive_info": kwargs.get("mask_sensitive_info", False),
        })

        # Check cache
        if not no_cache:
            cache_name = "MinimaxM2Client.call"
            from copy import deepcopy
            call_args_dict = deepcopy(params)
            llm_cache = caches["llm"]
            if not overwrite_cache:
                cache_result = llm_cache.get_cache(cache_name, call_args_dict)
                if cache_result is not None:
                    logger.info("Cache hit for Minimax M2 call")
                    return cache_result

        # Prepare headers
        headers['Content-Type'] = 'application/json'
        headers['Authorization'] = f'Bearer {self.api_key}'

        # API endpoint
        url = f"{self.api_base}/text/chatcompletion_v2"

        # Make the request with retries
        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.session.post(
                    url,
                    headers=headers,
                    json=params,
                    timeout=300,
                )

                if response.status_code not in self.RETRY_CODES:
                    response.raise_for_status()
                    break
                else:
                    if "maximum context length" in str(response.text) or "maximum length" in str(response.text):
                        logger.error(
                            f"Error Process {model} with the maximum context length exceeds. "
                            f"Sys messages is {messages[0]}"
                        )
                        return None

                    logger.warning(
                        f"Received status code {response.status_code} at attempt={attempt + 1}. "
                        f"Retrying... Response: {response.text}"
                    )

            except requests.exceptions.RequestException as e:
                logger.error(f"Error making request (attempt {attempt + 1}): {e}")
                if attempt == self.MAX_RETRIES - 1:
                    raise

            if attempt < self.MAX_RETRIES - 1:
                sleep_time = self.BACKOFF_FACTOR
                logger.info(f"Waiting for {sleep_time} seconds before next attempt...")
                time.sleep(sleep_time)

        data = response.json()

        if self.verbose:
            logger.info("Response: {}".format(json.dumps(data, ensure_ascii=False, indent=4)))

        # Log usage and cost
        if "usage" in data:
            input_tokens = data["usage"].get("total_tokens", 0)
            output_tokens = data["usage"].get("total_tokens", 0)  # Minimax may provide different fields

            # Minimax M2 pricing (example - adjust based on actual pricing)
            # These are placeholder values - update with actual Minimax pricing
            ip = 0.015  # per 1K tokens
            op = 0.05   # per 1K tokens

            price = (input_tokens / 1000) * ip + (output_tokens / 1000) * op

            logger.debug(
                f"{model} input data {input_tokens}, output_data {output_tokens} "
                f"LLM price: {price}"
            )

        # Check for valid response
        if "choices" not in data:
            # Minimax may use different response format
            if "reply" in data:
                # Convert Minimax format to OpenAI-compatible format
                result = [{
                    "message": {
                        "content": data["reply"]
                    }
                }]
            elif "text" in data:
                result = [{
                    "message": {
                        "content": data["text"]
                    }
                }]
            else:
                raise RuntimeError(
                    f"No 'choices', 'reply', or 'text' in response: {data}. "
                    f"Possibly, the API key is invalid."
                )
        else:
            # Standard OpenAI-compatible format
            result = data["choices"]

        # Save to cache
        if not no_cache:
            llm_cache.save_cache(cache_name, call_args_dict, result)

        return result


if __name__ == "__main__":
    # Test the Minimax M2 client
    client = MinimaxM2Client()

    # Test chat completion
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]

    try:
        response = client.call(
            model="abab6.5s-chat",
            messages=messages,
            temperature=0.7
        )
        print("Chat response:", response)
    except Exception as e:
        print(f"Error testing chat: {e}")
