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
import google.generativeai as genai
from openai import OpenAI

# Load environment variables from api_key.env if it exists
load_dotenv(dotenv_path='api_key.env')

# Also check for temporary environment files passed from the frontend
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
task_env_file = os.environ.get('TASK_ENV_FILE')
if task_env_file and os.path.exists(task_env_file):
    load_dotenv(dotenv_path=task_env_file, override=True)


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
            total=5,  # Maximum number of retry attempts (including the initial request)
            backoff_factor=1,  # Wait time factor between retries
            status_forcelist=[429, 500, 502, 503, 504],  # List of status codes that require retry
            allowed_methods=["POST"]  # Only retry POST requests
        )
        adapter = HTTPAdapter()
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.MAX_RETRIES = 100
        self.BACKOFF_FACTOR = 0.1
        self.RETRY_CODES = (400, 401, 429, 404, 500, 502, 503, 504, 529)
        self.verbose = verbose
    
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
                    print(f"Received status code {response.status_code} at attempt={attempt + 1}. Retrying..., the response is {response.text}", flush=True)
                    
                    
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
        messages = copy.deepcopy(messages)
        
        # Check if model name includes openrouter model identifier
        if any(provider in model for provider in ["google/", "anthropic/", "meta/", "mistral/"]):
            use_official = "openrouter"

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
            api_key = str(os.getenv('OPENAI'))
        elif "claude" in model:
            url = 'https://api.anthropic.com/v1/messages'
            api_key = str(os.getenv('CLAUDE'))
        elif "deepseek" in model:
            url = ''
            api_key = ''
        elif use_official == "openrouter" or "openrouter" in model:
            # Use OpenRouter API
            url = "https://openrouter.ai/api/v1/chat/completions"
            api_key = str(os.getenv('OPENROUTER'))
            # Add HTTP-Referer and X-Title headers for OpenRouter
            headers['HTTP-Referer'] = os.getenv('OPENROUTER_REFERER', '')
            headers['X-Title'] = os.getenv('OPENROUTER_TITLE', '')
        elif "gemini" in model:
            # For Gemini, we'll use the Google API directly, not REST API
            api_key = str(os.getenv('GEMINI'))
            genai.configure(api_key=api_key)
            url = None  # Not used for Gemini

        if "o1" in model:
            if "temperature" in params_gpt:
                del params_gpt["temperature"]
        
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
        
        if use_official == 'anthropic':
            headers = {
                'content-type': 'application/json',
                'anthropic-version': '2023-06-01',
                'x-api-key': api_key
            }
            if messages[0]['role'] == 'system':
                params_gpt['system'] = messages.pop(0)['content']
        
        # Handle OpenRouter API via official OpenAI client
        if use_official == "openrouter":
            try:
                site_url = os.getenv('OPENROUTER_REFERER', '')
                site_name = os.getenv('OPENROUTER_TITLE', '')
                
                # Initialize OpenAI client with OpenRouter base URL
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key,
                )
                
                # Prepare extra headers
                extra_headers = {}
                if site_url:
                    extra_headers["HTTP-Referer"] = site_url
                if site_name:
                    extra_headers["X-Title"] = site_name
                
                # Create completion
                completion = client.chat.completions.create(
                    extra_headers=extra_headers,
                    model=model,  # e.g. "google/gemini-2.5-pro-preview"
                    messages=messages,
                    temperature=temperature if temperature is not None else 0.7,
                    **kwargs
                )
                
                # Format response to match expected output
                result = [{
                    "message": {
                        "content": completion.choices[0].message.content
                    }
                }]
                
                # Cache if needed
                if not no_cache:
                    llm_cache.save_cache(cache_name, call_args_dict, result)
                
                return result
                
            except Exception as e:
                logger.error(f"Error with OpenRouter API: {e}")
                raise
                
        # Handle Gemini API
        if "gemini" in model:
            try:
                # Process messages for Gemini format
                gemini_messages = []
                system_prompt = None
                
                for msg in messages:
                    role = msg['role']
                    content = msg['content']
                    
                    if role == 'system':
                        system_prompt = content
                    elif role == 'user':
                        gemini_messages.append({"role": "user", "parts": [{"text": content}]})
                    elif role == 'assistant':
                        gemini_messages.append({"role": "model", "parts": [{"text": content}]})
                
                # Set up Gemini model
                generation_config = {}
                if temperature is not None:
                    generation_config["temperature"] = temperature
                
                # Create the model with system instruction if available
                if system_prompt:
                    gemini_model = genai.GenerativeModel(
                        model_name=model,
                        system_instruction=system_prompt,
                        generation_config=generation_config
                    )
                else:
                    gemini_model = genai.GenerativeModel(
                        model_name=model,
                        generation_config=generation_config
                    )
                
                # Start chat and get response
                chat = gemini_model.start_chat(history=gemini_messages[:-1] if gemini_messages else [])
                last_message = gemini_messages[-1]["parts"][0]["text"] if gemini_messages else ""
                response = chat.send_message(last_message)
                
                # Get token usage estimates for Gemini
                # Gemini doesn't provide token counts directly, so we use a rough estimate
                # This is a simplified approach - for production, consider using a proper tokenizer
                input_tokens = sum(len(msg.get("parts", [{}])[0].get("text", "").split()) * 1.3 for msg in gemini_messages)
                output_tokens = len(response.text.split()) * 1.3
                
                # Format response to match what call_llm expects - simple message with content
                result = [{
                    "message": {
                        "content": response.text
                    }
                }]
                
                # Cache if needed
                if not no_cache:
                    llm_cache.save_cache(cache_name, call_args_dict, result)
                
                return result
                
            except Exception as e:
                logger.error(f"Error with Gemini API: {e}")
                raise

        for attempt in range(self.MAX_RETRIES):
            current_headers = headers.copy()
            try:
                response = self.session.post(
                    url, 
                    headers=current_headers, 
                    json=params_gpt, 
                    timeout=300, 
                )
                if response.status_code not in self.RETRY_CODES:
                    response.raise_for_status()
                    break  # Successful response, exit the loop
                else:
                    if "maximum context length is" in str(response.text) or "maximum length" in str(response.text):
                        logger.error("Error Process {} with the maximum context length exceeds. Sys messages is {}".format(model, messages[0]))
                        # just return None
                        return None
    
                    print(f"Received status code {response.status_code} at attempt={attempt + 1}. Retrying..., the response is {response.text}", flush=True)  
                    
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
            elif "gemini" in model:
                ip = 0.25  # Gemini Pro prices (per million tokens)
                op = 0.75
            else:
                ip = 0.0
                op = 0.0
                
            price = (input_tokens / 1000000) * ip + (output_tokens / 1000000) * op
            
            # if self.verbose:
            logger.debug("{} input data {}, output_data {} LLM price: {}\n\n".format(model, input_tokens, output_tokens, price))
                # ))
        if use_official == "anthropic":
            result = data["content"][0]["text"]
            # make the format consistent
            data = [{"message": {"content": result}}]
            if not no_cache:
                llm_cache.save_cache(cache_name, call_args_dict, data)
            return data

        if 'choices' not in data:
            raise RuntimeError(f"No 'choices' in response: {data}. Possibly, the API key is invalid.")

        if not no_cache:
            llm_cache.save_cache(cache_name, call_args_dict, data['choices'])
        return data['choices']


if __name__ == "__main__":
    proxy = OpenAIApiProxy()
    proxy.call_embedding("text-embedding-3-small",
                         "I am")