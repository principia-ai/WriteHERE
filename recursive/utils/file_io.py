#!/usr/bin/env python3

import functools
import json
import os
from typing import Dict, List
import csv
import re
import pathlib
import os
import glob
import importlib.util
from enum import Enum
# from autoprompt.utils.string_utils import property_getter_safe

csv.field_size_limit(100000000)

__all__ = [
    "auto_read", "auto_write",
    "change_suffix", "ensure_dir",
    "file_convert", "file_prefix",
    "jsonl_to_csv", "read_csv",
    "read_jsonl", "write_json",
    "write_jsonl", "write_csv",
    "clean_text", "make_mappings", "add_suffix", "make_key2item", "random_select", "parse_tag_result",
    "parse_hierarchy_tags_result"
]    

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
        
            

def parse_hierarchy_tags_result(res, tags):
    if len(tags) == 0:
        raise Exception("len(tags) == 0")
    if isinstance(tags, str):
        tags = [tags]
    for tag in tags:
        res = parse_tag_result(res, tag)
    return res
        

def random_select(ifn, cnt):
    data = auto_read(ifn)
    import random
    random.shuffle(data)
    ofn = "{}/{}.random.{}{}".format(str(pathlib.Path(ifn).parent), str(pathlib.Path(ifn).stem), cnt, str(pathlib.Path(ifn).suffix))
    auto_write(data[:cnt], ofn)

def add_suffix(fn, suffix, f_type=None):
    p = pathlib.Path(fn)
    f_type = p.suffix[1:] if f_type is None else f_type
    return "{}/{}{}.{}".format(p.parent, p.stem, suffix, f_type)


def make_key2item(items, keys, verbose=False):
    key2items = {}
    if not isinstance(keys, list):
        keys = [keys]

    for item in items:
        key_string = ":".join([str(property_getter_safe(item, key)) for key in keys])
        if verbose and key_string in key2items:
            print("Duplicate key {}, content duplicate: {}".format(key_string, str(key2items[key_string]) == str(item)))

        key2items[key_string] = item
    if len(key2items) != len(items):
        print("before mapping: {}, after: {}".format(len(items), len(key2items)))
    return key2items




def make_mappings(fn):
    module_dir = "{}/prompts".format(pathlib.Path(fn).parent)
    ALL_SYSTEM_MESSAGE_MAPPINGS = {}
    ALL_PROMPT_MAPPINGS = {}

    module_files = glob.glob(f'{module_dir}/prompt_*.py')
    for fn in module_files:
        # 提取模块名
        module_name = os.path.basename(fn)[:-3]  # 去掉.py后缀
        # 创建一个模块规范
        spec = importlib.util.spec_from_file_location(module_name, fn)
        # 创建模块对象
        module = importlib.util.module_from_spec(spec)
        # 执行模块的代码
        spec.loader.exec_module(module)

        # 移除前面的prompt_
        key = module_name[7:]
        ALL_SYSTEM_MESSAGE_MAPPINGS[key] = {
            "": module.PROMPTS
        }
        ALL_PROMPT_MAPPINGS[key] = {
            "": module.CONTENT_TEMPLATE
        }
    return ALL_SYSTEM_MESSAGE_MAPPINGS, ALL_PROMPT_MAPPINGS

def ensure_dir(path: str):
    """create directories if *path* does not exist"""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def file_prefix(filename) -> str:
    """extract file prefix from filename"""
    filename = os.path.basename(filename)
    return filename.split(".")[0]


def read_jsonl(filename: str, jsonl_format=True) -> List[Dict]:
    with open(filename, 'r') as f:
        if filename.endswith(".jsonl") or jsonl_format:
            data = []
            for line in f.readlines():
                try:
                    data.append(json.loads(line))
                except SyntaxError as e:
                    # print("error")
                    print("load jsonl line error, msg: {}".format(str(e)), flush=True)
                    continue
                # except Exception as e:
                #     print("load jsonl line error, msg: {}".format(str(e)))
                #     continue 
            # data = [json.loads(line) for line in f.readlines()]
        else:
            data = json.load(f)

    return data


def read_csv(file_path) -> List[Dict]:
    """
    Read data from a csv file and return a List[Dict].

    Args:
        file_path (str): The path to the csv file.
    """
    data = []

    with open(file_path, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append(row)

    return data


def change_suffix(filename: str, suffix: str) -> str:
    """
    Change the suffix of a file.

    Args:
        filename (str): The path to the file.
        suffix (str): The suffix to change to.
    """
    if not suffix.startswith("."):
        suffix = "." + suffix
    return os.path.splitext(filename)[0] + suffix


def write_csv(data: List[Dict], filename: str = "data.csv"):
    headers = list(data[0].keys())

    with open(filename, 'w', newline='', encoding='utf-8-sig') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=headers, escapechar='\\')
        writer.writeheader()
        writer.writerows(data)


def jsonl_to_csv(jsonl_file: str, csv_file: str = None):
    """
    Convert a jsonl file to a csv file.

    Assuming all the JSON objects have the same structure,
    you can use the keys from the first object as column headers

    Args:
        jsonl_file (str): The path to the jsonl file.
        csv_file (str): The path to the csv file.
    """
    if csv_file is None:
        csv_file = change_suffix(jsonl_file, ".csv")
    data = read_jsonl(jsonl_file)
    write_csv(data, csv_file)


def write_json(data: List[Dict], filename: str = "data.json", indent: int = 2):
    """using indent = None but not 0 as defalut behavior"""
    with open(filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def write_jsonl(
    data: List[Dict], filename: str = "data.jsonl",
    indent: int = None, open_mode: str = "w"
):
    """
    Save data to jsonl file

    Args:
        data (List[Dict]): data to save
        filename (str): filename to save, default is "data.jsonl"
        indent (int): indent of jsonl file, default is None
    """
    with open(filename, open_mode) as f:
        for d in data:
            f.write(json.dumps(d, ensure_ascii=False, indent=indent) + "\n")


READ_MAPPING = {
    "jsonl": read_jsonl,
    "json": functools.partial(read_jsonl, jsonl_format=False),
    "csv": read_csv,
}

WRITE_MAPPING = {
    "jsonl": write_jsonl,
    "json": write_json,
    "json5": write_json,
    "csv": write_csv,
}


def auto_read(filename: str):
    suffix = os.path.splitext(filename)[1].strip(".")
    if suffix not in READ_MAPPING:
        for read_func in READ_MAPPING.values():
            try:
                return read_func(filename)
            except Exception:
                pass
    else:
        return READ_MAPPING[suffix](filename)


def auto_write(data, filename: str):
    suffix = os.path.splitext(filename)[1].strip(".")
    if suffix not in WRITE_MAPPING:
        raise ValueError(f"Unsupported file format: {suffix}")
    else:
        return WRITE_MAPPING[suffix](data, filename)


def file_convert(filename: str, to_file: str = None, format: str = "jsonl -> csv") -> str:
    """Auto convert data from one format to another format, write to a file and return filename"""
    from_format, to_format = format.split("->")
    from_format, to_format = from_format.strip(), to_format.strip()

    if to_file is None:
        to_file = change_suffix(filename, to_format)

    data = READ_MAPPING[from_format](filename)
    WRITE_MAPPING[to_format](data, to_file)
    return to_file


def clean_text(text):
    value = text.strip().replace("**", "")
    pattern = r'\^\[\d+\]\^'
    value = re.sub(pattern, "", value)
    return value

def convert_history_string_to_list(a, remove_prefix=False, user_prefix="用户：", assistant_prefix="助手：", style="list"):
    convs = []
    conv = []
    if a == "":
        return []
    # try:
    # delete prepending 0
    a = a.split("\n")
    idx = 0
    while idx < len(a) and a[idx].strip() == "":
        idx += 1
    if idx == len(a):
        return convs
    else:
        a = a[idx:]
    for line in a:
        line += "\n"
        if line.startswith(user_prefix):
            if len(conv) != 0: 
                convs.append(conv)
            conv = [line, ""]
        elif line.startswith(assistant_prefix):
            conv[1] += line
        else:
            if conv[1] == "":
                conv[0] += line 
            else:
                conv[1] += line
    convs.append(conv)
    new_convs = []
    error = False

    if style == "train":
        remove_prefix = True

    for conv in convs:
        if len(conv) != 2: 
            print("len(conv) != 2")
            error = True
            # continue
        elif conv[0].strip() == "" or conv[1].strip() == "":
            print('conv[0].strip() == "" or conv[1].strip() == ""')
            error = True
            # continue
        elif not conv[0].startswith(user_prefix):
            print('not conv[0].startswith("{}")'.format(user_prefix))
            error = True
            # continue
        elif not conv[1].startswith(assistant_prefix):
            print('not conv[1].startswith("{}")'.format(assistant_prefix))
            error = True
            # continue
        if error:
            # print(conv)
            # print("\n\n-------\n\n".join("{}\n\n{}".format(i[0], i[1]) for i in convs))
            # print("\n\n=====\n\n")
            continue
        if remove_prefix:
            conv[0] = conv[0][len(user_prefix):]
            conv[1] = conv[1][len(assistant_prefix):]
        new_convs.append(conv)

    if style == "train":
        results = []
        for u, a in new_convs:
            results.append({
                "role": "user",
                "content": u
            })
            results.append({
                "role": "assistant",
                "content": a
            })
        new_convs = results
    return new_convs

def enum_to_json(o):
    if isinstance(o, Enum):
        return o.name  # 或者 o.value，取决于你想要序列化的内容
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")