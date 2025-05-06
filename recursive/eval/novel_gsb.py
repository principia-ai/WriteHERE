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


def read_jsonl(filename):
    data = []
    with open(filename, "r", encoding="utf8") as f:
        for line in f:
            data.append(json.loads(line))
    return data

prompt_template = """
You will conduct a side-by-side evaluation. You will be given two system-generated stories. Your task is to compare the two stories and determine which one is better based on the following dimensions:
- Plot: The story should have a recognizable structure, e.g., with a connected beginning, middle, and end. The story should exhibit events and turns that move the plot forward. The story should not have logical or conceptual inconsistencies. Surprising or disruptive elements should be intentional, e.g., they serve the story and do not feel jarring, odd, or out of place.
- Creativity: There should be engaging characters, themes, and imagery. The ideas should not feel generic or bland. There should be avoidance of overly cliched characters and storylines, unintentional tropes, and stereotypes. When used, tropes and cliches should serve a purpose (e.g., comedic effect, twist on a common trope etc). The story should include original elements that were not explicitly mentioned in the prompt.
- Development: Characters and settings should be introduced and contextualized with relevant details that allow the reader to understand their place in the story. Appropriate levels of detail and complexity should be provided to lend the story a feeling of realness and believability.
- Language Use: The language used should feel varied and rich: Variance of sentence structure, verbiage, and vocabulary. The story should exhibit rhetorical, linguistic and literary devices (e.g., ambiguity, alliteration, etc) to create interesting effects. The story should avoid bland or repetitive phrases (unless used intentionally to create a narrative, thematic, or linguistic effect). 

The stories you will assess are generated based on specific user-defined prompts, which include unique demands or requirements provided by the user. You must compare the two stories while keeping these requirements in mind to ensure the evaluation is aligned with the original intent of the prompts.

Provide a detailed assessment of the two stories in terms of these four dimensions independently, and conclude your assessment with scores for each dimension in the json format, using the template below. Do not add any emphasis, such as bold and italics, on your assessment.
Output format as follows:
```
{{
    "Plot": {{"detailed_assessment": "xxx", "better": "A/B/same"}},
    "Creativity": {{"detailed_assessment": "xxx", "better": "A/B/same"}},
    "Development": {{"detailed_assessment": "xxx", "better": "A/B/same"}},
    "Language_Use": {{"detailed_assessment": "xxx", "better": "A/B/same"}},
    "Overall": {{"detailed_assessment": "xxx", "better": "A/B/same"}}
}}
```

[Story A]
```
{story_a}
```

---

[Story B]
```
{story_b}
```
---

[user-defined prompts]
```
{user_question}
```
"""


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
    model = 'gemini-2.0-flash-exp'
    
    if "claude" in model:
        resp = llm.call(messages = message,
                        model=model,
                        **other_inner_args)["content"][0]["text"]
    else:
        resp = llm.call(messages = message,
                        model=model,
                        **other_inner_args)[0]['message']['content']

    assert isinstance(parse_arg_dict, dict)
    result = {
        "original": resp,
        "result": resp
    }
    for key, value in parse_arg_dict.items():
        result[key] = parse_hierarchy_tags_result(resp, value).strip()
    return result
                
def get_identifier(cur_task, done_tasks, prompts_module):
    if cur_task in ("conflict", "character", "setting", "plot"):
        identifier = ", ".join([prompts_module.task2name[done_task] for done_task in done_tasks])
    elif cur_task == "exposition":
        identifier = "a Creative Writing Task, the Content Plan (Central Conflict, Character Descriptions, Setting, Key Plot Points)"
    else:
        identifier = "a Creative Writing Task, the Content Plan (Central Conflict, Character Descriptions, Setting, Key Plot Points) and the Previous Parts of the Story ({})".format(
            ", ".join([prompts_module.task2name[done_task] for done_task in done_tasks if done_task in ("exposition", "rising_action", "climax", "falling_action", "resolution")])
        )
    return identifier
        
 

def parse_result(res_str):
    import re
    pattern = r"""
    (?P<plot>Plot:\s*(?:(?!\n(?:Creativity|Development|Language Use|Overall):).)*)\s*

    (?P<creativity>Creativity:\s*(?:(?!\n(?:Plot|Development|Language Use|Overall):).)*)\s*

    (?P<development>Development:\s*(?:(?!\n(?:Plot|Creativity|Language Use|Overall):).)*)\s*

    (?P<language>Language Use:\s*(?:(?!\n(?:Plot|Creativity|Development|Overall):).)*)\s*

    (?P<overall>Overall:\s*(?:(?!\n(?:Plot|Creativity|Development|Language):).)*)\s*
    """
    matches = re.search(pattern, res_str, re.VERBOSE | re.DOTALL)
    if matches:
        plot = matches.group('plot')
        creativity = matches.group('creativity')
        development = matches.group('development')
        language = matches.group('language')
        overall = matches.group('overall')
        res = {
            "plot": plot,
            "creativity": creativity,
            "development": development,
            "language": language,
            "overall": overall
        }
        return res
    else:
        return None
    
    
def process_one_compare(item):
    cnt = 0
    while cnt < 100:
        llm_result = call_llm(
            system_message = None,
            prompt = prompt_template.format(story_a = item["story_a"], story_b = item["story_b"], user_question = item["ori"]["inputs"]),
            parse_arg_dict = {},
            history_message = None,
            temperature = 0.2
        )
        try:
            # result = json.loads(llm_result["result"])
            result = json.loads(llm_result["result"].strip().strip('`').replace('json', '').strip())
            for key in ("Plot", "Creativity", "Development",
                        "Language_Use", "Overall"):
                if key not in result:
                    raise Exception("{} Missed in {}".format(key, result))
                else:
                    if "detailed_assessment" not in result[key] or "better" not in result[key]:
                        raise Exception("{} Missed in {}".format("detailed_assessment or better", result[key]))
        except:
            cnt += 1
            import traceback
            print(traceback.format_exc())
            print("error for {}".format(llm_result))
            continue
        
        item["eval_result"] = result
        return item
    return None

def parse_list(strings):
    return [item.strip() for item in strings.split(",")]

def define_args():
    parser = argparse.ArgumentParser()
    # default double
    parser.add_argument("--filenames", type=parse_list, required=True) # length should be 2
    parser.add_argument("--model-names", type=parse_list, required=True) # length should be 2
    parser.add_argument("--output-folder", type=str, required=True)
    parser.add_argument("--count", type=int, default=3)
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--parallel", type=int, default=20)
    
    return parser

def get_final_article(result):
    if isinstance(result, str):
        return re.sub(r'```|markdown', '', result)
    else:
        if "final_article" in result:
            return re.sub(r'```|markdown', '', result["final_article"])
        else:
            raise NotImplementedError()


def get_item_id(item):
    # return "{}-{}".format(item["ori"]["example_id"], item["ori"]["inputs"])
    return item["id"]


def main():
    import pathlib
    parser = define_args()
    args = parser.parse_args()
    model_ids = [args.model_names[0], args.model_names[1]]
    import pathlib    
    output_folder = args.output_folder   
    import os
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_f = open("{}/pk_details.jsonl".format(output_folder),"w", encoding="utf8")
    output_f2 = open("{}/pk_gather.jsonl".format(output_folder),"w", encoding="utf8")

    items = [read_jsonl(fn) for fn in args.filenames] # Should two files
    assert len(items) == 2
    items_i = items[0]
    items_j = items[1] 
    id2items_j = {get_item_id(item): item  for item in items_j}
    compares = []
    idx = 0
    for item in items_i:
        if get_item_id(item) in id2items_j:
            idx += 1
            from copy import deepcopy
            story_a = get_final_article(item["results"] if "results" in item else item["result"])
            item_b = id2items_j[get_item_id(item)]     
            story_b = get_final_article(item_b["results"] if "results" in item_b else item_b["result"]) 
            
            # a b
            target_item = deepcopy(item)
            target_item["story_a"] = story_a
            target_item["story_b"] = story_b
            target_item["compare_keys"] = "{}&{}".format(model_ids[0], model_ids[1])
            target_item["story_{}".format(model_ids[0])] = story_a
            target_item["story_{}".format(model_ids[1])] = story_b
            compares.append(target_item)
            # b a
            target_item = deepcopy(item)
            target_item["story_a"] = story_b
            target_item["story_b"] = story_a
            target_item["compare_keys"] = "{}&{}".format(model_ids[1], model_ids[0])
            target_item["story_{}".format(model_ids[0])] = story_a
            target_item["story_{}".format(model_ids[1])] = story_b
            
            compares.append(target_item)


    # Make Compares Multiple Times and Reverse it
    final_compares = []
    for _ in range(args.count):
        final_compares.extend(deepcopy(compares))
    import random
    random.seed(1010)
    random.shuffle(final_compares)
    compares = final_compares
    thread_num = args.parallel
    num_total, num_none, num_exception, num_success = 0, 0, 0, 0
    all_results = []
    with ThreadPoolExecutor(max_workers=min(len(compares), thread_num)) as executor:
        future_to_conv = {executor.submit(process_one_compare, compare_item): compare_item for compare_item in compares}
        for future in tqdm(as_completed(future_to_conv), total=len(compares), desc="generate_trace"):
            try:
                num_total += 1
                ret = future.result(timeout=100)
                all_results.append(ret)
                if ret:
                    output_f.write(json.dumps(ret, ensure_ascii=False) + '\n')
                    output_f.flush()
                    num_success += 1
                else:
                    print("Get None", flush=True)
                    num_none += 1
                print(f'Stat: {num_total=}, {num_none=}, {num_exception=}, {num_success=}', flush=True)
            except TimeoutError:
                print(f"Timeout occurred for example", flush=True)
                num_exception += 1
            except Exception as e:
                exception_feature = future_to_conv[future]
                import traceback
                print(f'{exception_feature=}, the exception is: {traceback.format_exc()}', flush=True)
                num_exception += 1
    output_f.close()
    from collections import defaultdict
    id2compare = defaultdict(list)
    for result in all_results:
        id2compare[get_item_id(result)].append(result)  
        
    all_new_items = []
    conclusion = {
        "Plot": {
            model_ids[0]: {"win": 0, "tie": 0, "loss": 0},
            model_ids[1]: {"win": 0, "tie": 0, "loss": 0},
        },
        "Creativity": {
            model_ids[0]: {"win": 0, "tie": 0, "loss": 0},
            model_ids[1]: {"win": 0, "tie": 0, "loss": 0},
        },
        "Development": {
            model_ids[0]: {"win": 0, "tie": 0, "loss": 0},
            model_ids[1]: {"win": 0, "tie": 0, "loss": 0},
        },
        "Language_Use": {
            model_ids[0]: {"win": 0, "tie": 0, "loss": 0},
            model_ids[1]: {"win": 0, "tie": 0, "loss": 0},
        },
        "Overall": {
            model_ids[0]: {"win": 0, "tie": 0, "loss": 0},
            model_ids[1]: {"win": 0, "tie": 0, "loss": 0},
        }
    }
    for eid, compare_items in id2compare.items():
        records = {
            "Plot": {
                model_ids[0]: {"win": 0, "tie": 0, "loss": 0},
                model_ids[1]: {"win": 0, "tie": 0, "loss": 0},
            },
            "Creativity": {
                model_ids[0]: {"win": 0, "tie": 0, "loss": 0},
                model_ids[1]: {"win": 0, "tie": 0, "loss": 0},
            },
            "Development": {
                model_ids[0]: {"win": 0, "tie": 0, "loss": 0},
                model_ids[1]: {"win": 0, "tie": 0, "loss": 0},
            },
            "Language_Use": {
                model_ids[0]: {"win": 0, "tie": 0, "loss": 0},
                model_ids[1]: {"win": 0, "tie": 0, "loss": 0},
            },
            "Overall": {
                model_ids[0]: {"win": 0, "tie": 0, "loss": 0},
                model_ids[1]: {"win": 0, "tie": 0, "loss": 0},
            },
        }
        new_item = deepcopy(compare_items[0])
        all_compare_items = []
        for compare_item in compare_items:
            compare_keys = compare_item["compare_keys"].split("&")
            eval_result = compare_item["eval_result"]
            for skey in ("Plot", "Creativity", "Development", "Language_Use", "Overall"):
                if eval_result[skey]["better"].upper().strip() == "A":
                    records[skey][compare_keys[0]]["win"] += 1
                    records[skey][compare_keys[1]]["loss"] += 1
                elif eval_result[skey]["better"].upper().strip() == "B":
                    records[skey][compare_keys[0]]["loss"] += 1
                    records[skey][compare_keys[1]]["win"] += 1
                else:
                    records[skey][compare_keys[0]]["tie"] += 1
                    records[skey][compare_keys[1]]["tie"] += 1
            all_compare_items.append({
                "compare_keys": compare_item["compare_keys"],
                "eval_result": compare_item["eval_result"]
            })
        final_eval = {} 
        for skey in ("Plot", "Creativity", "Development", "Language_Use", "Overall"):
            if records[skey][model_ids[0]]['win'] > records[skey][model_ids[0]]['loss']:
                final_eval[skey] = model_ids[0]
                conclusion[skey][model_ids[0]]["win"] += 1
                conclusion[skey][model_ids[1]]["loss"] += 1  
                print("{} {} win: {}.  GSB={}:{}:{}".format(new_item["ori"]["example_id"], skey, model_ids[0],
                                                                                           records[skey][model_ids[0]]['win'],
                                                                                           records[skey][model_ids[0]]['tie'],
                                                                                           records[skey][model_ids[0]]['loss']), flush=True)
            
            elif records[skey][model_ids[0]]['win'] < records[skey][model_ids[0]]['loss']:
                final_eval[skey] = model_ids[1]
                conclusion[skey][model_ids[0]]["loss"] += 1
                conclusion[skey][model_ids[1]]["win"] += 1
                print("{} {} win: {}.  GSB={}:{}:{}".format(new_item["ori"]["example_id"], skey, model_ids[1],
                                                                                           records[skey][model_ids[0]]['win'],
                                                                                           records[skey][model_ids[0]]['tie'],
                                                                                           records[skey][model_ids[0]]['loss']), flush=True)
                
            else:
                final_eval[skey] = "same"
                conclusion[skey][model_ids[0]]["tie"] += 1
                conclusion[skey][model_ids[1]]["tie"] += 1
                print("{} {} tie.  GSB={}:{}:{}".format(new_item["ori"]["example_id"], skey, 
                                                            records[skey][model_ids[0]]['win'],
                                                            records[skey][model_ids[0]]['tie'],
                                                            records[skey][model_ids[0]]['loss']), flush=True)
            
        for k in ("scratchpad", "results", "eval_result", "compare_keys", "story_a", "story_b"):
            if k in new_item:
                del new_item[k]
        new_item["all_eval_result"] = all_compare_items
        new_item["ensemble_eval"] = final_eval
        new_item["eval_statistical"] = records
        all_new_items.append(new_item)
        
        output_f2.write(json.dumps(new_item, ensure_ascii=False) + '\n')
        output_f2.flush()
        
    print(json.dumps(conclusion, ensure_ascii=False, indent=4), flush=True)
    output_f2.close()
                
    
if __name__ == "__main__":
    main() 