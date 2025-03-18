#!/usr/bin/env python3

import json
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import copy
# import boto3
from botocore.config import Config
import time
from loguru import logger
from recursive.memory import caches
from dotenv import load_dotenv
from pathlib import Path

# Get the recursive directory (where api_key.env is located)
project_root = Path(__file__).parent.parent
env_path = project_root / 'api_key.env'

# Load environment variables
load_dotenv(dotenv_path=env_path)

class OpenAIApiException(Exception):
    def __init__(self, msg, error_code):
        self.msg = msg
        self.error_code = error_code

def format_tool_response_to_claude(tool_response):
    content_claude = []
    for msg_info in tool_response['choices']:
        msg_info = msg_info['message']
        if 'tool_calls' not in msg_info:
            msg_new = {"type": "text", "text": msg_info["content"]}
        else:
            tool_msg = msg_info["tool_calls"][0]
            msg_new = {
                "type": "tool_use", 
                "id": tool_msg["id"], 
                "name": tool_msg["function"]["name"], 
                "input": json.loads(tool_msg["function"]["arguments"])
            }
        content_claude.append(msg_new)
    
    stop_reason = tool_response['choices'][0]['finish_reason']
    if stop_reason == 'tool_calls': stop_reason = 'tool_use'
    response_new = {
        "id": tool_response['id'],
        "type": "message",
        "role": "assistant",
        "model": tool_response['model'],
        "content": content_claude,
        "stop_reason": stop_reason,
        "stop_sequence": None,
        "usage": tool_response['usage']
    }
    return response_new



class OpenAIApiProxy():
    def __init__(self, verbose=True):
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
        self.MAX_RETRIES = 5
        self.BACKOFF_FACTOR = 1
        self.RETRY_CODES = (429, 500, 502, 503, 504)
        self.verbose = verbose
        
        # Load API keys from environment
        self.openai_api_key = os.getenv('OPENAI')
        self.claude_api_key = os.getenv('CLAUDE')
        self.serpapi_key = os.getenv('SERPAPI')
        
        if not self.openai_api_key or not self.claude_api_key:
            raise ValueError("API keys not found in environment variables")

    def call_embedding(self, model, text):
        url = "http://oneapi-svip.bc-inner.com"
        api_key = ''
        headers = {}
        headers['Content-Type'] = headers['Content-Type'] if 'Content-Type' in headers else 'application/json'
        headers['Authorization'] = "Bearer " + api_key
        url = url + '/v1/embeddings'
        params_gpt = {
            "model": model,
            "input": text,
            "encoding_format": "float",
        }

        for attempt in range(self.MAX_RETRIES):
            current_headers = headers.copy()
            try:
                response = self.session.post(
                    url, 
                    headers=current_headers, 
                    json=params_gpt, 
                    timeout=300, 
                    proxies=None
                )
                if response.status_code not in self.RETRY_CODES:
                    response.raise_for_status()
                    break  # Successful response, exit the loop
                else:
                    # print(f"Received status code {response.status_code} at attempt={attempt + 1}. Retrying... {current_headers['x-api-key']=}")
                    print(f"Received status code {response.status_code} at attempt={attempt + 1}. Retrying..., the reponse is {response.text}", flush=True)
                    
                    
            except requests.exceptions.RequestException as e:
                print(f"Error making request (attempt {attempt + 1}): {e}", flush=True)
                if attempt == self.MAX_RETRIES - 1:  # Last attempt
                    raise  # Re-raise the last exception if all attempts fail
            
            # Implement exponential backoff
            if attempt < self.MAX_RETRIES - 1:  # No need to sleep after the last attempt
                sleep_time = self.BACKOFF_FACTOR
                print(f"Waiting for {sleep_time} seconds before next attempt...", flush=True)
                time.sleep(sleep_time)
        
        data = response.json()
        return data


    def call(self, model, messages, no_cache = False, overwrite_cache=False, tools=None, temperature=None, headers={}, use_official=None, **kwargs):
        assert tools is None
        use_official = None
        messages = copy.deepcopy(messages)

        is_gpt = True if "gpt" in model or "o1" in model else False
    
        params_gpt = {
            "model": model,
            "messages": messages,
            "max_tokens": 8192,
        }
        
        if "claude" in model:
            use_official = "anthropic"
        
        if self.verbose:
            logger.info("Messages: {}".format(json.dumps(messages, ensure_ascii=False, indent=4)))
        
        if temperature is not None:
            params_gpt["temperature"] = temperature

        if 'o1' in model:
            url = ''
            api_key = ""
            params_gpt["max_tokens"] = 32768
        elif "gpt" in model:
            url = "https://api.openai.com/v1/chat/completions"
            api_key = self.openai_api_key
        elif "claude" in model:
            url = 'https://api.anthropic.com/v1/messages'
            api_key = self.claude_api_key
        elif "deepseek" in model:
            url = ''
            api_key = ''
        else: # gemini
            url = ''
            api_key = ''

        if "o1" in model:
            if "temperature" in params_gpt:
                del params_gpt["temperature"]
        
        if use_official == 'anthropic':
            headers = {
                'content-type': 'application/json',
                'anthropic-version': '2023-06-01',
                'Authorization': f'Bearer {api_key}'
            }
            if messages[0]['role'] == 'system':
                params_gpt['system'] = messages.pop(0)['content']
        else:
            headers['Content-Type'] = headers['Content-Type'] if 'Content-Type' in headers else 'application/json'
            headers['Authorization'] = "Bearer " + api_key

        params_gpt.update(kwargs)
        
        
        # Cache
        
        if not no_cache:
            cache_name = "OpenAIApiProxy.call"
            from copy import deepcopy
            call_args_dict = deepcopy(params_gpt)
            llm_cache = caches["llm"]
            if not overwrite_cache:
                cache_result = llm_cache.get_cache(cache_name, call_args_dict)
                if cache_result is not None:
                    return cache_result
        
        for attempt in range(self.MAX_RETRIES):
            current_headers = headers.copy()
            try:
                response = self.session.post(
                    url, 
                    headers=current_headers, 
                    json=params_gpt, 
                    timeout=300, 
                )
                # Immediately return if API key is invalid
                if response.status_code == 401:
                    error_data = response.json()
                    raise Exception(f"API Key Error: {error_data.get('error', {}).get('message', 'Invalid API key')}")
                
                if response.status_code not in self.RETRY_CODES:
                    response.raise_for_status()
                    break  # Successful response, exit the loop
                else:
                    if "maximum context length is" in str(response.text) or "maximum length" in str(response.text):
                        logger.error("Error Process {} with the maximum context length exceeds. Sys messages is {}".format(model, messages[0]))
                        return None
    
                    print(f"Received status code {response.status_code} at attempt={attempt + 1}. Retrying..., the reponse is {response.text}", flush=True)  
                    
            except requests.exceptions.RequestException as e:
                print(f"Error making request (attempt {attempt + 1}): {e}", flush=True)
                if attempt == self.MAX_RETRIES - 1:  # Last attempt
                    raise  # Re-raise the last exception if all attempts fail
            
            # Implement exponential backoff
            if attempt < self.MAX_RETRIES - 1:  # No need to sleep after the last attempt
                sleep_time = self.BACKOFF_FACTOR * (2 ** attempt)  # Exponential backoff
                print(f"Waiting for {sleep_time} seconds before next attempt...", flush=True)
                time.sleep(sleep_time)
        
        data = response.json()
        
        if self.verbose:
            logger.info("Response: {}".format(json.dumps(data, ensure_ascii=False, indent=4)))
    
        input_tokens_key = 'prompt_tokens' if is_gpt else 'input_tokens'
        output_tokens_key = 'completion_tokens' if is_gpt else 'output_tokens'
        output_reason_tokens = data.get('usage', {}).get('completion_tokens_details', {}).get('reasoning_tokens', 0)
        if self.verbose:
            logger.debug("{} Usage: {}".format(model, data.get('usage', {})))
        if input_tokens_key in data.get('usage', {}) and output_tokens_key in data.get('usage', {}):
            input_tokens = data.get('usage', {})[input_tokens_key]
            output_tokens = data.get('usage', {})[output_tokens_key]
            if model == "gpt-4o":
                ip = 2.50
                op = 10.00
            elif model == "gpt-4o-mini":
                ip = 0.150
                op = 0.600 
            elif "claude" in model:
                ip = 3.0
                op = 15.0
            elif "r1" in model:
                ip = 0.55
                op = 2.19
            else:
                ip = 0.0
                op = 0.0
                
            price = (input_tokens / 1000000) * ip + (output_tokens / 1000000) * op
            
            # if self.verbose:
            logger.debug("{} input data {}, output_data {} LLM price: {}\n\n".format(model, input_tokens, output_tokens, price))
                # ))
        if use_official:
            result = data["content"][0]["text"]
            # make the format consistent
            data = [{"message": {"content": result}}]
            if not no_cache:
                llm_cache.save_cache(cache_name, call_args_dict, data)
            return data
        if not no_cache:
            llm_cache.save_cache(cache_name, call_args_dict, data['choices'])
        return data['choices']


if __name__ == "__main__":
    proxy = OpenAIApiProxy()
    proxy.call_embedding("text-embedding-3-small",
                         "I am")