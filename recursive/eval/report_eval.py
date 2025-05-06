import argparse
import re
#coding:utf8

from typing import Dict, List
from abc import ABC, abstractmethod
from overrides import overrides
import random
import json
from recursive.llm.llm import OpenAIApiProxy
from copy import deepcopy
from pprint import pprint
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

from tqdm import tqdm
import numpy as np



def parse_hierarchy_tags_result(res, tags):
    if len(tags) == 0:
        raise Exception("len(tags) == 0")
    if isinstance(tags, str):
        tags = [tags]
    for tag in tags:
        res = parse_tag_result(res, tag)
    return res

def parse_tag_result(content, tag):
    start = False 
    results = []
    for line in content.split("\n"):
        line = line.strip()
        if line == "<{}>".format(tag):
            start = True
        if line == "</{}>".format(tag):
            start = False
        if start:
            results.append(line)
    if len(results) > 0:
        results = results[1:]
        return "\n".join(results)
    if len(results) == 0:
        pattern = r"<{0}>(.*?)</{0}>".format(re.escape(tag))
        results = re.findall(pattern, content, re.DOTALL)
        match_res = []
        for result in results:
            match_res.append(result)
        match_res = "\n".join(match_res)
        return match_res
    return ""
        
            
criteria_description = """
Criteria Description
Broad Coverage: Does the article provide an in-depth exploration of the topic and have good coverage?
Score 1 Description: Severely lacking; offers little to no coverage of the topic’s primary aspects, resulting in a very narrow perspective.
Score 2 Description: Partial coverage; includes some of the topic’s main aspects but misses others, resulting in an incomplete portrayal.
Score 3 Description: Acceptable breadth; covers most main aspects, though it may stray into minor unnecessary details or overlook some relevant points.
Score 4 Description: Good coverage; achieves broad coverage of the topic, hitting on all major points with minimal extraneous information.
Score 5 Description: Exemplary in breadth; delivers outstanding coverage, thoroughly detailing all crucial aspects of the topic without including irrelevant information.

Criteria Description
Novelty: Does the report cover novel aspects that relate to the user’s initial intent but are not directly derived from it?
Score 1 Description: Lacks novelty; the report strictly follows the user’s initial intent with no additional insights.
Score 2 Description: Minimal novelty; includes few new aspects but they are not significantly related to the initial intent.
Score 3 Description: Moderate novelty; introduces some new aspects that are somewhat related to the initial intent.
Score 4 Description: Good novelty; covers several new aspects that enhance the understanding of the initial intent.
Score 5 Description: Excellent novelty; introduces numerous new aspects that are highly relevant and significantly enrich the initial intent.

Criteria Description
Relevance and Focus: How effectively does the report maintain relevance and focus, given the dynamic nature of the discourse?
Score 1 Description: Very poor focus; discourse diverges significantly from the initial topic and intent with many irrelevant detours.
Score 2 Description: Poor focus; some relevant information, but many sections diverge from the initial topic.
Score 3 Description: Moderate focus; mostly stays on topic with occasional digressions that still provide useful information.
Score 4 Description: Good focus; maintains relevance and focus throughout the discourse with minor divergences that add value.
Score 5 Description: Excellent focus; consistently relevant and focused discourse, even when exploring divergent but highly pertinent aspects.

Criteria Description
Depth of Exploration: How thoroughly does the report explore the initial topic and its related areas, reflecting the dynamic discourse?
Score 1 Description: Very superficial; provides only a basic overview with significant gaps in exploration.
Score 2 Description: Superficial; offers some detail but leaves many important aspects unexplored.
Score 3 Description: Moderate depth; covers key aspects but may lack detailed exploration in some areas.
Score 4 Description: Good depth; explores most aspects in detail with minor gaps.
Score 5 Description: Excellent depth; thoroughly explores all relevant aspects with comprehensive detail, reflecting a deep and dynamic discourse."""


prompt_template = """
Take the following criteria and score the following article on a scale of 1 to 5 for each criteria.
Do not provide justification for your scores.

Answer in the following format:
Broad Coverage: #
Novelty: #
Relevance and Focus: #
Depth of Exploration: #

## Criteria description:
```
{criteria_description}
```

## Article:
```
{article}
```

User's original question is: {question}
"""


def read_jsonl(filename):
    data = []
    with open(filename, "r", encoding="utf8") as f:
        for line in f:
            data.append(json.loads(line))
    return data


def define_args():
    parser = argparse.ArgumentParser()
    # default double
    parser.add_argument("--filename", type=str, required=True)
    parser.add_argument("--output-filename", type=str, required=True)
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--parallel", type=int, default=20)

    
    return parser

def prcess_article(item):
    return item["article"]

def process_one(item, model):
    cnt = 0
    while cnt < 100:
        llm_result = call_llm(
            system_message = None,
            prompt = prompt_template.format(article = item["to_eval_article"], criteria_description = criteria_description,
                                            question=item["prompt"]),
            parse_arg_dict = {},
            history_message = None,
            temperature = 0.2,
            model = model,
            overwrite_cache = True
        )
        try:
            text = llm_result["original"].strip()
            pattern = r"(.+?): (\d+)"
            matches = re.findall(pattern, text)
            result = {label.strip().lower(): int(score) for label, score in matches}
            # for key, score in result.items():
            if len(result) != 4:
                print("Error for {}".format(text))
                cnt += 1
                continue
            for k in result.keys():
                if k not in ("broad coverage", "novelty", "relevance and focus", "depth of exploration"):
                    cnt += 1
                    print("Get error key: {}, Error for {}".format(k, text))
        except:
            cnt += 1
            import traceback
            print(traceback.format_exc())
            print("error for {}".format(llm_result))
            continue
        
        assert len(result) == 4
        item["eval_result"] = result
        return item
    assert False
    return None


def call_llm(system_message, prompt, parse_arg_dict, history_message = None, **other_inner_args):
    llm = OpenAIApiProxy()
    if system_message:
        message = [
            {"role": "system", "content": system_message},
        ]
    else:
        message = []
    if history_message is not None:
        message.append(history_message)
    message.append({"role": "user", "content": prompt})
    
    model = other_inner_args.pop("model", "gpt-4o")
    print("Use {}".format(model))
    
    
    if "claude" in model:
        resp = llm.call(messages = message,
                        model=model,
                        verbose=False,
                        no_cache = True,
                        **other_inner_args)["content"][0]["text"]
    else:
        resp = llm.call(messages = message,
                        model=model,
                        verbose=False,
                        no_cache = True,
                        **other_inner_args)[0]['message']['content']

    assert isinstance(parse_arg_dict, dict)
    result = {
        "original": resp,
        "result": resp
    }
    for key, value in parse_arg_dict.items():
        result[key] = parse_hierarchy_tags_result(resp, value).strip()
    return result


def main():
    parser = define_args()
    args = parser.parse_args()
    
    custom_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    
    items = read_jsonl(args.filename)
    for item in items:
        item["to_eval_article"] = prcess_article(item)
        
    print(len(items))
    output_f = open(args.output_filename, "w", encoding="utf8")
    num_total, num_none, num_exception, num_success = 0, 0, 0, 0
    all_results = []
    thread_num = args.parallel

    keys = ["broad coverage", "novelty", "relevance and focus", "depth of exploration"]    
    aggregates = {key: []  for key in keys}
    with ThreadPoolExecutor(max_workers=min(len(items), thread_num)) as executor:
        future_to_conv = {executor.submit(process_one, item, args.model): item for item in items}
        for future in tqdm(as_completed(future_to_conv), total=len(items), desc="generate_trace"):
            try:
                num_total += 1
                ret = future.result(timeout=100)
                for key in keys:
                    aggregates[key].append(ret["eval_result"][key])
                all_results.append(ret)
                if ret:
                    output_f.write(json.dumps(ret, ensure_ascii=False) + '\n')
                    output_f.flush()
                    num_success += 1
                else:
                    print("Get None", flush=True)
                    num_none += 1
                print(f'Stat: {num_total=}, {num_none=}, {num_exception=}, {num_success=}')
            except TimeoutError:
                print(f"Timeout occurred for example")
                num_exception += 1
            except Exception as e:
                exception_feature = future_to_conv[future]
                import traceback
                print(f'{exception_feature=}, the exception is: {traceback.format_exc()}')
                num_exception += 1
    
    output_f.close()
    
    print("AVG")
    for key, values in aggregates.items():
        print(key, "{:.3f}".format(np.mean([float(v) for v in values])), flush=True)
        
                
   
main()