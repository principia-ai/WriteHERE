#coding:utf8

from collections import defaultdict, deque
from typing import List, Dict
from recursive.graph import TaskStatus, RegularDummyNode, NodeType
from recursive.utils.display import display_graph, display_plan
from recursive.agent.proxy import AgentProxy
from recursive.memory import Memory, article
import random
from pprint import pprint
import dill as pickle
import json
import argparse
from loguru import logger
import traceback
from recursive.memory import caches
from recursive.cache import Cache
from recursive.utils.get_index import get_report_with_ref
from datetime import datetime

    
    
class GraphRunEngine:
    """
    """
    def __init__(self, root_node, memory_format, config):
        self.root_node = root_node
        self.memory = Memory(root_node, format=memory_format, config=config)
        
    def find_need_next_step_nodes(self, single=False):
        nodes = []
        queue = deque([self.root_node])
        # Root node, starts in READY state
        while len(queue) > 0:
            # logger.info("in find_need_next_step_nodes, queue: {}".format(queue))
            node = queue.popleft()
            # logger.info("in find_need_next_step_nodes, select node: {}".format(node))
            if node.is_activate:
                nodes.append(node)
            if node.is_suspend: # If the node is in a suspended state internally, traverse the topological_task_queue of internal nodes
                queue.extend(node.topological_task_queue)
            if single and len(nodes) > 0:
                return nodes[0]
        if not single:
            return nodes
        else:
            return None
        
    def save(self, folder):
        # save root_node
        # save memory
        # save article while running
        root_node_file = "{}/nodes.pkl".format(folder)
        root_node_json_file = "{}/nodes.json".format(folder)
        article_file = "{}/article.txt".format(folder)
        with open(root_node_file, "wb") as f:
            pickle.dump(self.root_node, f)
        
        with open(root_node_json_file, "w") as f:
            json.dump(self.root_node.to_json(), f, indent=4, ensure_ascii=False)
            
        self.memory.save(folder)
        
        with open(article_file, 'w', encoding='utf-8') as file:
            file.write(self.memory.article)
    
    def load(self, folder):
        root_node_file = "{}/nodes.pkl".format(folder)
        with open(root_node_file, "rb") as f:
            self.root_node = pickle.load(f)
        
        self.memory = self.memory.load(folder)
         
    def forward_exam(self, node, verbose):
        # The exam order is bottom-up hierarchically, and top-down based on dependencies.
        # not_ready -> ready: Need to check the execution status of dependent nodes, and whether upper-level nodes have entered the doing state
        # doing -> final_to_finish: Need to check if all lower-level nodes have finished
        # plan_reflection_done -> doing:
        if node.is_suspend:
            for inner_node in node.topological_task_queue:
                self.forward_exam(inner_node, verbose)
            node.do_exam(verbose)

    def forward_one_step_not_parallel(self, full_step=False, select_node_hashkey=None, log_fn=None,
                                      nodes_json_file=None, *action_args, **action_kwargs):
        # Find tasks that need to enter the next step
        if select_node_hashkey is not None:
            need_next_step_node = self.find_need_next_step_nodes(single=False)
            for node in need_next_step_node:
                if node.hashkey == select_node_hashkey:
                    break
            else:
                raise Exception("Error, the select node {} can not be executed".format(select_node_hashkey))
            need_next_step_node = node
        else:
            need_next_step_node = self.find_need_next_step_nodes(single=True)
        if need_next_step_node is None:
            logger.info("All Done")
            # display_graph(self.root_node.inner_graph, fn=log_fn)
            display_plan(self.root_node.inner_graph)
            
            # Save final nodes.json if path provided
            if nodes_json_file:
                with open(nodes_json_file, "w") as f:
                    json.dump(self.root_node.to_json(), f, indent=4, ensure_ascii=False)
                
            return "done"
        logger.info("select node: {}".format(need_next_step_node.task_str()))
        # Execute the next step for this node
        # Update Memory
        self.memory.update_infos([need_next_step_node])
        
        # Update nodes.json after each step if path provided 
        if nodes_json_file:
            with open(nodes_json_file, "w") as f:
                json.dump(self.root_node.to_json(), f, indent=4, ensure_ascii=False)
                
        if not full_step:
            action_name, action_result = need_next_step_node.next_action_step(self.memory, 
                                                               *action_args, 
                                                               **action_kwargs)
        else:
            action_name = need_next_step_node.next_full_action_step(self.memory)
            
        verbose = action_name not in ("update", "prior_reflect", \
                               "planning_post_reflect", \
                               "execute_post_reflect")
    
        # After the action ends, update the entire graph status. When in parallel, should wait for all parallel tasks to complete before executing uniformly
        self.forward_exam(self.root_node, verbose)
        
        if verbose:
            display_plan(self.root_node.inner_graph)
        
        
    def forward_one_step_untill_done(self, full_step=False, 
                                           parallel=False,
                                           save_folder=None,
                                           nl=False,
                                           nodes_json_file=None,
                                           *action_args, **action_kwargs):
        self.root_node.status = TaskStatus.READY
        for step in range(10000):
            logger.info("Step {}".format(step))
            ret = self.forward_one_step_not_parallel(
                full_step=False, 
                log_fn="logs/temp/{}".format(step),
                nodes_json_file=nodes_json_file,
                *action_args, 
                **action_kwargs
            )
            self.save(save_folder)
            if ret == "done":
                break
            
            if step > 3000:
                logger.error("Step > 3000, break")
                break
        
        if step <= 3000:
            final_answer = self.root_node.get_node_final_result()["result"]
        else:
            final_answer = "Out of Step"
        logger.info("Final Result: \n{}".format(final_answer))
        return final_answer



def read_jsonl(filename: str, jsonl_format=True) -> List[Dict]:
    with open(filename, 'r') as f:
        if filename.endswith(".jsonl") or jsonl_format:
            data = []
            for line in f.readlines():
                try:
                    data.append(json.loads(line))
                except SyntaxError as e:
                    print("load jsonl line error, msg: {}".format(str(e)))
                    continue
        else:
            data = json.load(f)

    return data

    
def story_writing(input_filename,
                  output_filename,
                  start,
                  end,
                  done_flag_file,
                  global_use_model,
                  nodes_json_file=None):
    
    config = {
        "language": "en", 
        "action_mapping": {
            "plan": ["UpdateAtomPlanningAgent", {}],
            "update": ["DummyRandomUpdateAgent", {}],
            "execute": ["SimpleExcutor", {}],
            "final_aggregate": ["FinalAggregateAgent", {}],
            "prior_reflect": ["DummyRandomPriorReflectionAgent", {}],
            "planning_post_reflect": ["DummyRandomPlanningPostReflectionAgent", {}],
            "execute_post_reflect": ["DummyRandomExecutorPostReflectionAgent", {}],
        },
        "task_type2tag": {
            "COMPOSITION": "write",
            "REASONING": "think",
            "RETRIEVAL": "search",
        },
        "require_keys": {
            "COMPOSITION": ["id", "dependency", "goal", "task_type", "length"],
            "RETRIEVAL": ["id", "dependency", "goal", "task_type"],
            "REASONING": ["id", "dependency", "goal", "task_type"],
        },
        "COMPOSITION": {
            "execute": {
                "prompt_version": "StoryWrtingNLWriterEN",
                "llm_args": {
                    "model": global_use_model,
                    "temperature": 0.3
                },
                "parse_arg_dict": {
                    "result": ["article"],
                },
            },
            "atom": {
                "update_diff": True,
                "without_update_prompt_version": "StoryWritingNLWriteAtomEN",
                "with_update_prompt_version": "StoryWritingNLWriteAtomWithUpdateEN",
                "llm_args": {
                    "model": global_use_model,
                    "temperature": 0.1
                },
                "parse_arg_dict": {
                    "atom_think": ["think"],
                    "atom_result": ["atomic_task_determination"],
                    "update_result": ["goal_updating"]
                },
                "atom_result_flag": "atomic"
            },            
            "planning": {
                "prompt_version": "StoryWritingNLPlanningEN",
                "llm_args": {
                    "model": global_use_model,
                    "temperature": 0.1
                },
                "parse_arg_dict": {
                    "plan_think": ["think"],
                    "plan_result": ["result"],
                },
            },
            "update": {},
            "final_aggregate": {},  
        },
        "RETRIEVAL": {
            "all_atom": True
        },
        "REASONING": {
            "execute": { 
                "prompt_version": "StoryWrtingNLReasonerEN",
                "llm_args": {
                    "model": global_use_model,
                    "temperature": 0.3
                },
                "parse_arg_dict": {
                    "result": ["result"],
                },
            },
            "atom": {
                "use_candidate_plan": True
            },            
            "planning": {},
            "update": {},
            "final_aggregate": {
                "prompt_version": "StoryWritingReasonerFinalAggregate",
                "mode": "llm",
                "parse_arg_dict": {
                    "result": ["result"],
                },
            },  
        },
    }
    config["tag2task_type"] = {v: k for k,v in config["task_type2tag"].items()}
    

    data = read_jsonl(input_filename)
    
    
    items = data[start:end]
    
    import pathlib
    root_folder = "{}/{}".format(str(pathlib.Path(output_filename).parent.parent),
                                 "records") 
    caches["search"] = Cache("{}/../cache/{}-{}-search".format(root_folder, start, end))
    caches["llm"] = Cache("{}/../cache/{}-{}-llm".format(root_folder, start, end))
    
    import os
    if os.path.exists(output_filename):
        done_ques = [item["ori"]["inputs"]  for item in read_jsonl(output_filename)]
        filtered_items = [item for item in items if item["ori"]["inputs"] not in done_ques]
        print("Has Done {} item, left {} items to run".format(len(done_ques), len(filtered_items)))
        items = filtered_items
    
    output_f = open(output_filename, "w", encoding="utf8")  
    print("Need Run {} items".format(len(items)), flush=True)
    

    for item in items:
        question = item["ori"]["inputs"]
        root_node = RegularDummyNode(
            config = config,
            nid = "",
            node_graph_info = {
                "outer_node": None,
                "root_node": None,
                "parent_nodes": [],
                "layer": 0
            },
            task_info = {
                "goal": question,
                "task_type": "write",
                "length": "determine based on the task requirements:",
                "dependency": []
            },
            node_type = NodeType.PLAN_NODE
        )
        root_node.node_graph_info["root_node"] = root_node
        engine = GraphRunEngine(root_node, "xml", config)
        import os
        # qstr = question if len(question) < 40 else question[:40]
        qstr = item["id"]
        folder = "{}/{}".format(root_folder, qstr)
        os.makedirs(folder, exist_ok=True)
        custom_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
        log_id = logger.add("{}/engine.log".format(folder), format=custom_format)
        try:
            # result = engine.forward_one_step_untill_done(save_folder=folder, to_run_check_str = check_str) 
            result = engine.forward_one_step_untill_done(save_folder=folder, nl=True, nodes_json_file=nodes_json_file)    
        except Exception as e:
            logger.error("Encounter exception: {}\nWhen Process {}".format(traceback.format_exc(), question))
            continue
            
        item["result"] = result
        output_f.write(json.dumps(item, ensure_ascii=False) + "\n")
        output_f.flush()
        
        logger.remove(log_id)

    # output_f.close()
    if done_flag_file is not None:
        with open(done_flag_file, "w") as f:
            f.write("done")
     
            
def report_writing(input_filename,
                   output_filename,
                   start,
                   end,
                   done_flag_file,
                   global_use_model,
                   engine_backend,
                   nodes_json_file=None,
                   today_date=None):
    # Use current date if not provided
    if today_date is None:
        today_date = datetime.now().strftime("%b %d, %Y")
    config = {
        "language": "en", 
        # Agent is Defined in recursive.agent.agents.regular
        # update, prior_reflect, planning_post_reflect and execute_post_reflect is skipped, by using Dummy Agent
        # prompt is Defined in recursive.agent.prompts
        "today_date": today_date,  # Add the today_date parameter to config
        "action_mapping": {
            "plan": ["UpdateAtomPlanningAgent", {}],
            "update": ["DummyRandomUpdateAgent", {}],
            "execute": ["SimpleExcutor", {}],
            "final_aggregate": ["FinalAggregateAgent", {}],
            "prior_reflect": ["DummyRandomPriorReflectionAgent", {}],
            "planning_post_reflect": ["DummyRandomPlanningPostReflectionAgent", {}],
            "execute_post_reflect": ["DummyRandomExecutorPostReflectionAgent", {}],
        },
        "task_type2tag": {
            "COMPOSITION": "write",
            "REASONING": "think",
            "RETRIEVAL": "search",
        },
        "require_keys": {
            "COMPOSITION": ["id", "dependency", "goal", "task_type", "length"],
            "RETRIEVAL": ["id", "dependency", "goal", "task_type"],
            "REASONING": ["id", "dependency", "goal", "task_type"],
        },
        "offer_global_writing_plan": True,
        "COMPOSITION": {
            "execute": {
                "prompt_version": "ReportWriter",
                "llm_args": {
                    "model": global_use_model,
                    "temperature": 0.3
                },
                "parse_arg_dict": {
                    "result": ["article"],
                },
            },
            "atom": {
                "update_diff": True,  # Combine Atom and Update, see agent.agents.regular.get_llm_output
                "without_update_prompt_version": "ReportAtom",
                "with_update_prompt_version": "ReportAtomWithUpdate",
                "llm_args": {
                    "model": global_use_model,
                    "temperature": 0.1
                },
                "parse_arg_dict": { # parse args from llm output in xml format
                    "atom_think": ["think"],
                    "atom_result": ["atomic_task_determination"],
                    "update_result": ["goal_updating"]
                },
                "atom_result_flag": "atomic",
                "force_atom_layer": 3 # >= 3, force to atom and skip atom judgement
            },            
            "planning": {
                "prompt_version": "ReportPlanning",
                "llm_args": {
                    "model": global_use_model,
                    "temperature": 0.1
                },
                "parse_arg_dict": {
                    "plan_think": ["think"],
                    "plan_result": ["result"],
                },
            },
            "update": {},
            "final_aggregate": {},  
        },
        "RETRIEVAL": {
            "execute": {
                "react_agent": True, # use Search Agent
                "prompt_version": "SearchAgentENPrompt", # see recursive.agent.prompts.search_agent.main
                "searcher_type": "SerpApiSearch", # see recursive.executor.actions.bing_browser
                "llm_args": {
                    "model": global_use_model, # set the llm
                },
                "parse_arg_dict": {
                    "result": ["result"],
                },
                "react_parse_arg_dict": { # for search agent, parse result from xml format llm response
                    "observation": ["observation"],
                    "missing_info": ["missing_info"],
                    "think": ["planning_and_think"],
                    "action_think": ["current_turn_query_think"],
                    "search_querys": ["current_turn_search_querys"],
                },
                "temperature": 0.2, # search agent
                "max_turn": 4, # search agent max turn
                "llm_merge": True, # use llm to merge search agent result, see recursive.agent.agents.regular.SimpleExcutor.search_merge, the prompt is set in config
                "only_use_react_summary": False,
                "webpage_helper_max_threads": 10, # use requests to download web page
                "search_max_thread": 4, # serpapi parallel
                "backend_engine": engine_backend, # google or bing, defined in serpapi
                "cc": "US", # search region
                "topk": 20,
                "pk_quota": 20, # search agent, pk quota, see __search
                "select_quota": 20, # search agent select quota
                "selector_max_workers": 8, # selector parallel
                "summarizier_max_workers": 8, # summarizer parallel
                "selector_model": "gpt-4o-mini",
                "summarizer_model": "gpt-4o-mini",
            },
            "search_merge": {
                "prompt_version": "MergeSearchResultVFinal", # search merge prompt
                "llm_args": {
                    "model": global_use_model,
                },
                "parse_arg_dict": {
                    "result": ["result"],
                }
            },
            "atom": {
                "prompt_version": "ReportSearchOnlyUpdate",
                "llm_args": {
                    "model": global_use_model,
                },
                "parse_arg_dict": {
                    "atom_think": ["think"],
                    "update_result": ["goal_updating"]
                },
                "all_atom": True,
                "only_on_depend": True
            },            
            "planning": {},
            "update": {},
            "final_aggregate": {},  
        },
        "REASONING": {
            "execute": {
                "prompt_version": "ReportReasoner",
                "llm_args": {
                    "model": global_use_model,
                    "temperature": 0.3
                },
                "parse_arg_dict": {
                    "think": ["think"],
                    "result": ["result"],
                },
            },
            "atom": {
                # "use_candidate_plan": True
                "all_atom": True # force to atom
            },            
            "planning": {},
            "update": {},
            "final_aggregate": {},  
        },
    }
    config["tag2task_type"] = {v: k for k,v in config["task_type2tag"].items()}
    
    
    data = read_jsonl(input_filename)
    items = data[start:end]
    
    import pathlib
    root_folder = "{}/{}".format(str(pathlib.Path(output_filename).parent.parent),
                                 "records") 
    caches["search"] = Cache("{}/../cache/{}-{}-search".format(root_folder, start, end)) # cache search and llm result
    caches["llm"] = Cache("{}/../cache/{}-{}-llm".format(root_folder, start, end))
    
    import os
    if os.path.exists(output_filename):
        done_ques = [item["prompt"]  for item in read_jsonl(output_filename)]
        filtered_items = [item for item in items if item["prompt"] not in done_ques]
        print("Has Done {} item, left {} items to run".format(len(done_ques), len(filtered_items)))
        items = filtered_items
    
    output_f = open(output_filename, "a", encoding="utf8")
    for item in items:
        question = item["prompt"]
        root_node = RegularDummyNode(
            config = config,
            nid = "",
            node_graph_info = {
                "outer_node": None,
                "root_node": None,
                "parent_nodes": [],
                "layer": 0
            },
            task_info = {
                "goal": question,
                "task_type": "write",
                "length": "You should determine itself, according to the question",
                "dependency": []
            },
            node_type = NodeType.PLAN_NODE
        )
        root_node.node_graph_info["root_node"] = root_node
        engine = GraphRunEngine(root_node, "xml", config)
        import os
        qstr = item["id"]
        folder = "{}/{}".format(root_folder, qstr)
        os.makedirs(folder, exist_ok=True)
        rf = open("{}/report.md".format(folder), "w")
        
        custom_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
        log_id = logger.add("{}/engine.log".format(folder), format=custom_format)
        try:
            result = engine.forward_one_step_untill_done(save_folder=folder, nl=True, nodes_json_file=nodes_json_file)    
        except Exception as e:
            logger.error("Encounter exception: {}\nWhen Process {}".format(traceback.format_exc(), question))
            continue
            
        
        result = get_report_with_ref(engine.root_node.to_json(), result)
        item["result"] = result
        output_f.write(json.dumps(item, ensure_ascii=False) + "\n")
        output_f.flush()
        rf.write(item["result"])
        rf.flush()
        rf.close()
        
        logger.remove(log_id)

    if done_flag_file is not None:
        with open(done_flag_file, "w") as f:
            f.write("done")
            
                  
                                 
def define_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", type=str, required=True)
    parser.add_argument("--mode", type=str, choices=["story", "report"], required=True)
    parser.add_argument("--output-filename", type=str, required=True)
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--length", type=int)
    parser.add_argument("--engine-backend", type=str)
    parser.add_argument("--nodes-json-file", type=str, help="Path to save nodes.json for real-time visualization")
    current_date = datetime.now().strftime("%b %d, %Y")  # Format: "Apr 1, 2025"
    parser.add_argument("--today-date", type=str, default=current_date, help="Today's date to use in prompts (default: current date)")
    
    parser.add_argument("--start", type=int, default=None)
    parser.add_argument("--end", type=int, default=None)
    parser.add_argument("--done-flag-file", type=str, default=None)
    parser.add_argument("--need-continue", action="store_true")
    return parser
    


if __name__ == "__main__":
    parser = define_args()
    args = parser.parse_args()
    if args.mode == "story":
        story_writing(args.filename, args.output_filename,
                      args.start, args.end, args.done_flag_file, args.model,
                      nodes_json_file=args.nodes_json_file)
    else:
        report_writing(args.filename, args.output_filename,
                       args.start, args.end, args.done_flag_file, args.model, args.engine_backend,
                       nodes_json_file=args.nodes_json_file, today_date=args.today_date)