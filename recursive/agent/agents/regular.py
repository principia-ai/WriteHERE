#coding:utf8

from typing import Dict, List
from abc import ABC, abstractmethod
from overrides import overrides
import random
import json
from recursive.utils.register import Register
from recursive.executor.actions.register import executor_register, tool_register
from recursive.executor.actions import ActionExecutor
from recursive.utils.file_io import make_mappings
from recursive.llm.llm import OpenAIApiProxy
from recursive.utils.file_io import parse_hierarchy_tags_result
from copy import deepcopy
from pprint import pprint
from loguru import logger
from recursive.agent.agent_base import agent_register, Agent
from recursive.agent.prompts.base import prompt_register
from recursive.executor.agents.claude_fc_react import SearchAgent
from recursive.executor.actions.bing_browser import BingBrowser
import re
    

def get_llm_output(node, agent, memory, agent_type, overwrite_cache=False, *args, **kwargs):
    memory_info = memory.collect_node_run_info(node)
    task_type = node.task_info.get("task_type", "")
    
    if task_type == "":
        inner_kwargs = node.config[task_type]
    else:
        task_type = node.task_type_tag
        inner_kwargs = node.config[task_type][agent_type]
        
    if agent_type == "planning":
        if not inner_kwargs.get("depth_diff", False):
            prompt_version = inner_kwargs["prompt_version"]
        else:
            if node.node_graph_info["outer_node"] is None:
                prompt_version = inner_kwargs["depth_1_prompt_version"]
            else:
                prompt_version = inner_kwargs["depth_N_prompt_version"]      
    elif agent_type == "atom":
        if inner_kwargs.get("update_diff", False):
            if len(node.node_graph_info["parent_nodes"]) > 0:
                prompt_version = inner_kwargs["with_update_prompt_version"]
            else:
                prompt_version = inner_kwargs["without_update_prompt_version"]
        else:
            prompt_version = inner_kwargs["prompt_version"]
    else:
        prompt_version = inner_kwargs["prompt_version"]
        
    to_run_check_str = kwargs.get("to_run_check_str", None)
    
    system_message = prompt_register.module_dict[prompt_version]().construct_system_message(
        to_run_check_str = to_run_check_str
    )
    to_run_task = deepcopy(node.task_info)
    for k in ("candidate_plan", "candidate_think"):
        if k in to_run_task:
            del to_run_task[k]
            
    if kwargs.get("nl", False) and agent_type in ("execute", "final_aggregate"):
        to_run_task = node.task_info["goal"]
        if "length" in node.task_info:
            if node.config.get("language", "") == "en":
                to_run_task += " Word count requirement: approximately {}".format(node.task_info["length"])
            else:
                to_run_task += " 要求字数：约{}".format(node.task_info["length"])
        to_run_outer_graph_dependent = []
        for layer_tasks in memory_info["upper_graph_precedents"]:
            for t in layer_tasks:
                to_run_outer_graph_dependent.append("【{}】:\n {}".format(t["goal"], t["result"]))
        to_run_outer_graph_dependent = "\n\n".join(to_run_outer_graph_dependent) 
        to_run_same_graph_dependent = "\n\n".join(["【{}】: \n{}".format(t["goal"], t["result"]) for t in memory_info["same_graph_precedents"]])
    else:
        to_run_task = json.dumps(to_run_task, ensure_ascii=False)
        to_run_outer_graph_dependent = []
        for layer_tasks in memory_info["upper_graph_precedents"]:
            for t in layer_tasks:
                to_run_outer_graph_dependent.append("【{}】:\n {}".format(t["goal"], t["result"]))
        to_run_outer_graph_dependent = "\n\n".join(to_run_outer_graph_dependent) 
        to_run_same_graph_dependent = "\n\n".join(["【{}】: \n{}".format(t["goal"], t["result"]) for t in memory_info["same_graph_precedents"]])

    to_run_target_write_tasks = ""
    if task_type == "RETRIEVAL":
        depend_write_task = node.get_direct_depend_write_task()
        if node.config["language"] == "zh":
            to_run_target_write_tasks = "\n".join(
                "COMPOSITION任务{}，字数：{}".format(idx, node.task_info["length"]) for idx, node in enumerate(depend_write_task, start=1)
            ) if (depend_write_task is not None and len(depend_write_task) > 0) else "Not Provided"
        else:
            to_run_target_write_tasks = "\n".join(
                "Write Task{}，word count requirements：{}".format(idx, node.task_info["length"]) for idx, node in enumerate(depend_write_task, start=1)
            ) if (depend_write_task is not None and len(depend_write_task) > 0) else "Not Provided"
        
    
    # Prepare prompt arguments
    prompt_args = {
        'to_run_root_question': memory.root_node.task_info["goal"],
        'to_run_article': memory.article,
        'to_run_full_plan': node.get_all_layer_plan(),
        'to_run_outer_graph_dependent': to_run_outer_graph_dependent,
        'to_run_same_graph_dependent': to_run_same_graph_dependent,
        'to_run_task': to_run_task,
        'to_run_candidate_plan': node.task_info.get("candidate_plan", "Missing"),
        'to_run_candidate_think': node.task_info.get("candidate_think", "Missing"),
        'to_run_final_aggregate': kwargs.get("to_run_final_aggregate", ""),
        'to_run_target_write_tasks': to_run_target_write_tasks,
        'to_run_global_writing_task': node.get_all_previous_writing_plan(),
        'today_date': node.config.get('today_date', 'Mar 26, 2025')  # Add today_date from config
    }
    
    prompt = prompt_register.module_dict[prompt_version]().construct_prompt(**prompt_args)
    llm_result = agent.call_llm(
        system_message = system_message,
        prompt = prompt,
        parse_arg_dict = inner_kwargs["parse_arg_dict"],
        overwrite_cache = overwrite_cache,
        **inner_kwargs.get("llm_args", {})
    ) 
    return llm_result


def extract_json_content(text):
    pattern = r'```json\s*(.*?)\s*```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None



@agent_register.register_module()
class UpdateAtomPlanningAgent(Agent):
    @overrides
    def forward(self, node, memory, *args, **kwargs) -> str:
        """
        {
            atom: {
                prompt_version: xxx,
                llm_args: {xxx},
                parse_arg_dict: {},
                "atom_result_flag": "原子任务"
            }
            planning: {
                prompt_version: xxx,
                llm_args: {xxx},
                parse_arg_dict: {}
            }
        }
        """
        return_result = {}
        # Check Atom
        task_type = node.task_info.get("task_type", "")
        if task_type == "":
            inner_kwargs = node.config[task_type]
        else:
            task_type = node.task_type_tag
            inner_kwargs = node.config[task_type]["atom"]
            
        if inner_kwargs.get("all_atom", False):
            if not "prompt_version" in inner_kwargs:
                plan_result = []
                return_result["result"] = plan_result
            else:
                # update, but is atom task
                # judge only_on_depend
                if (not inner_kwargs.get("only_on_depend", False)) or (
                    len(node.node_graph_info["parent_nodes"]) > 0
                ):
                    atom_llm_result = get_llm_output(
                        node, self, memory, "atom", *args, **kwargs
                    )
                    atom_llm_result["atom_original"] = atom_llm_result.pop("original")
                    if atom_llm_result.get("update_result", ""):
                        ori_goal = node.task_info["goal"]
                        node.task_info["goal"] = atom_llm_result.get("update_result", "").replace("\n", "; ")
                        logger.info("Update goal from {} to {}".format(
                            ori_goal, node.task_info["goal"] 
                        )) 
                    return_result.update(atom_llm_result)
                plan_result = []
                return_result["result"] = plan_result     
                
        elif inner_kwargs.get("use_candidate_plan", False):
            candidate_plan = node.task_info["candidate_plan"]
            plan_result = []
            if not isinstance(candidate_plan, list):
                logger.info("Candidate Plan Missing: {}".format(candidate_plan))                
            else:
                plan_result = candidate_plan
            return_result["result"] = plan_result
            logger.info("Use Candidate Plan for: {}, the candidate plan is \n{}".format(
                node.task_info["goal"],
                return_result["result"]
            ))
        elif "force_atom_layer" in inner_kwargs and node.node_graph_info["layer"] >= inner_kwargs["force_atom_layer"]:
            plan_result = []
            return_result["result"] = plan_result
            logger.info("Current Node: {}, Layer = {}, >= force atom layer(), force to atom".format(
                node, node.node_graph_info["layer"], inner_kwargs["force_atom_layer"]
            ))
        else:
            succ = False
            retry_cnt = 0
            while not succ and retry_cnt < 10:
                atom_llm_result = get_llm_output(
                    node, self, memory, "atom", retry_cnt > 0, *args, **kwargs
                )
            # Determine if it failed. If atom_result is not one of "atomic" or "complex" then it's a failure, otherwise it's successful
                succ = (atom_llm_result["atom_result"].strip() in ("atomic", "complex"))
                if not succ:
                    logger.error("ATOM Judgement for {} is failed, Get Response: {}, retry_cnt={}".format(node, 
                                                                                                          atom_llm_result["original"],
                                                                                                          retry_cnt))
                    retry_cnt += 1

            atom_llm_result["atom_original"] = atom_llm_result.pop("original")
            return_result.update(atom_llm_result)
            # Use atom's thinking as candidate_think for recursive planning
            node.task_info["candidate_think"] = atom_llm_result["atom_think"]
            if atom_llm_result.get("update_result", ""):
                node.task_info["goal"] = atom_llm_result.get("update_result", "").replace("\n", "; ")
        
            if atom_llm_result["atom_result"] == inner_kwargs["atom_result_flag"]:
                plan_result = []
                return_result["result"] = plan_result
            else: # Need Recursive Planning
                succ = False
                retry_cnt = 0
                plan_result = []
                while not succ and retry_cnt < 10:
                    plan_llm_result = get_llm_output(
                        node, self, memory, "planning", retry_cnt > 0, *args, **kwargs
                    )
                    try:
                        plan_result = self.parse_result(plan_llm_result["plan_result"])
                    except Exception as e: 
                        # Incorrect format, cannot get plan_result, first check if planning can be extracted directly from the response
                        source = plan_llm_result["plan_result"].strip() if plan_llm_result["plan_result"].strip() != "" else plan_llm_result["original"]
                        plan_llm_result["plan_result"] = extract_json_content(source) # If fail to fetch, return None
                        try: 
                            plan_result = self.parse_result(plan_llm_result["plan_result"])
                        except Exception as e:
                            logger.error("Planning for {} failed, original is {}, retry {}".format(
                                node, plan_llm_result["original"], retry_cnt
                            ))
                            retry_cnt += 1
                            continue 
                    succ = True
                        
                plan_llm_result["result"] = plan_result
                return_result.update(plan_llm_result)
            
        return return_result

    @overrides
    def parse_result(self, agent_output, *args, **kwargs) -> Dict:
        return json.loads(agent_output.strip().strip('`').replace('json', '').strip())["sub_tasks"]


FORMAT_STRING_TEMPLATE = """
<web_page index={index}>
<title>
{title}
</title>
<url>
{url}
</url>
<page_time>
{publish_time}
</page_time>
<summary>
{content}
</summary>
</web_page>
"""



@agent_register.register_module()
class SimpleExcutor(Agent):
    @overrides
    def forward(self, node, memory, *args, **kwargs) -> str:
        """
        {
            executor: {
                prompt_version: xxx,
                llm_args: {xxx},
                parse_arg_dict: {},
            }
        }
        """
        task_type = node.task_type_tag
        inner_kwargs = node.config[task_type]["execute"]
        if task_type == "RETRIEVAL" and inner_kwargs.get("react_agent", False):
            react_agent = SearchAgent(
                prompt_version = inner_kwargs["prompt_version"],
                action_executor = ActionExecutor(
                    actions = [BingBrowser(searcher_type=inner_kwargs["searcher_type"],
                                           language = node.config["language"],
                                           search_max_thread=inner_kwargs["search_max_thread"],
                                           selector_max_workers = inner_kwargs["selector_max_workers"],
                                           summarizier_max_workers = inner_kwargs["summarizier_max_workers"],
                                           selector_model = inner_kwargs["selector_model"],
                                           summarizer_model = inner_kwargs["summarizer_model"],
                                           webpage_helper_max_threads=inner_kwargs["webpage_helper_max_threads"],
                                           backend_engine=inner_kwargs["backend_engine"],
                                           cc=inner_kwargs["cc"])]),
                model = inner_kwargs["llm_args"]["model"],
                max_turn = inner_kwargs["max_turn"],
                action_memory = True,
                remove_history = True,
                parse_arg_dict = inner_kwargs["react_parse_arg_dict"]
            )
            
            depend_write_task = node.get_direct_depend_write_task()
            to_run_root_question = memory.root_node.task_info["goal"]
            if node.config["language"] == "zh":
                to_run_target_write_tasks = "\n".join(
                    "COMPOSITION任务{}，字数：{}".format(idx, node.task_info["length"]) for idx, node in enumerate(depend_write_task, start=1)
                ) if (depend_write_task is not None and len(depend_write_task) > 0) else "Not Provided"  
                outer_write_task = node.get_outer_write_task()
                to_run_outer_write_task = "COMPOSITION任务{}，字数：{}".format(outer_write_task["goal"], 
                                                                outer_write_task["length"])
            else:
                to_run_target_write_tasks = "\n".join(
                    "Write Task{}, word count requirements: {}".format(idx, node.task_info["length"]) for idx, node in enumerate(depend_write_task, start=1)
                ) if (depend_write_task is not None and len(depend_write_task) > 0) else "Not Provided"
                outer_write_task = node.get_outer_write_task()
                to_run_outer_write_task = "Write Task {}, word count requirements: {}".format(outer_write_task.task_info["goal"], outer_write_task.task_info["length"])
                
            react_agent_result = react_agent.chat(message=node.task_info["goal"], 
                                                  global_start_index = memory.global_start_index,
                                                  to_run_target_write_tasks = to_run_target_write_tasks,
                                                  to_run_root_question = to_run_root_question,
                                                  to_run_outer_write_task = to_run_outer_write_task,
                                                  today_date = node.config.get('today_date', 'Mar 26, 2025'),
                                                  temperature=inner_kwargs.get("temperature", None))
            
            execute_result = []
            for turn_result in react_agent_result["result"]:
                for page in turn_result["web_pages"]:
                    memory.add_search_result(page)
                    if not inner_kwargs.get("only_use_react_summary", False):
                        execute_result.append(FORMAT_STRING_TEMPLATE.format(
                            index = page["global_index"],
                            title=page["title"],
                            url=page["url"],
                            publish_time=page["publish_time"],
                            content=page["summary"]
                        ))
                execute_result.append("<web_pages_short_summary>\n{}\n</web_pages_short_summary>".format(
                    turn_result["observation"]
                ))
            execute_result = "\n\n".join(execute_result)
            
            if inner_kwargs.get("llm_merge", False):
                merge_result = self.search_merge(node, memory, execute_result,
                                                 to_run_outer_write_task)
                llm_result = {
                    "ori": react_agent_result["ori"],
                    "agent_result": execute_result,
                    "merge_result": merge_result,
                    "result": merge_result["result"]
                }
            else: 
                llm_result = {
                    "ori": react_agent_result["ori"],
                    "result": execute_result
                }
        else:
            succ = False 
            retry_cnt = 0
            while not succ and retry_cnt < 50:
                llm_result = get_llm_output(
                    node, self, memory, "execute", retry_cnt > 0, *args, **kwargs
                )
                # 判定是否失败，如果result不为空则为成功
                succ = (llm_result["result"].strip() != "")
                if not succ:
                    logger.error("Execute for {} is failed, Get Response: {}, retry_cnt={}".format(node, 
                                                                                                   llm_result["original"],
                                                                                                   retry_cnt))
                    retry_cnt += 1
                
            # for write
            if node.task_type_tag == "COMPOSITION":
                memory.article += "\n\n" + llm_result["result"]
        
        return llm_result

    @overrides
    def parse_result(self, agent_output, *args, **kwargs) -> Dict:
        return agent_output
    
    def search_merge(self, node, memory, search_results, to_run_outer_write_task, *args, **kwargs):
        inner_kwargs = node.config["RETRIEVAL"]["search_merge"]
        prompt_version = inner_kwargs["prompt_version"]

        system_message = prompt_register.module_dict[prompt_version]().construct_system_message()
        
        to_run_search_task = node.task_info["goal"]
        to_run_search_results = search_results

        to_run_root_question = memory.root_node.task_info["goal"]
            
        # to_run_target_write_tasks
        depend_write_task = node.get_direct_depend_write_task()
        if node.config["language"] == "zh":
            to_run_target_write_tasks = "\n".join(
                "写作任务{}，字数：{}".format(idx, node.task_info["length"]) for idx, node in enumerate(depend_write_task, start=1)
            ) if (depend_write_task is not None and len(depend_write_task) > 0) else "Not Provided"
        else:
            to_run_target_write_tasks = "\n".join(
                "Write Task{}, word count requirements：{}".format(idx, node.task_info["length"]) for idx, node in enumerate(depend_write_task, start=1)
            ) if (depend_write_task is not None and len(depend_write_task) > 0) else "Not Provided"
        # Prepare prompt arguments
        prompt_args = {
            'to_run_search_task': to_run_search_task,
            'to_run_search_results': to_run_search_results,
            'to_run_target_write_tasks': to_run_target_write_tasks,
            'to_run_outer_write_task': to_run_outer_write_task,
            'to_run_root_question': to_run_root_question,
            'today_date': node.config.get('today_date', 'Mar 26, 2025')  # Add today_date from config
        }
        
        prompt = prompt_register.module_dict[prompt_version]().construct_prompt(**prompt_args)
        
        succ = False 
        retry_cnt = 0
        while not succ and retry_cnt < 50:
            llm_result = self.call_llm(
                system_message = system_message,
                prompt = prompt,
                parse_arg_dict = inner_kwargs["parse_arg_dict"],
                overwrite_cache = True if retry_cnt > 0 else False,
                **inner_kwargs.get("llm_args", {})
            )
            # 判定是否失败，如果result不为空则为成功
            succ = (llm_result["result"].strip() != "")
            if not succ:
                logger.error("Search Merge for {} is failed, Get Response: {}, retry_cnt={}".format(node, 
                                                                                                    llm_result["original"],
                                                                                                    retry_cnt))
                retry_cnt += 1
        if not succ:
            logger.error("Search Merge for {} after retry fail, return the original as result".format(node))
            llm_result = {"result": search_results}
            
        return llm_result
        

@agent_register.register_module()
class FinalAggregateAgent(Agent):
    @overrides
    def forward(self, node, memory, *args, **kwargs) -> str:
        return_result = {}
        task_type = node.task_type_tag
        if task_type == "RETRIEVAL":
            # Aggregate All Child Result
            results = []
            for child in node.topological_task_queue:
                results.append("【{}】:\n {}".format(child.task_info["goal"],
                                                child.get_node_final_result()["result"]))
            results = "\n\n".join(results)
            return_result["result"] = results
    
        elif task_type == "REASONING":
            inner_kwargs = node.config[task_type]["final_aggregate"]
            results = []
            for child in node.topological_task_queue:
                results.append("【{}】:\n {}".format(child.task_info["goal"],
                                                child.get_node_final_result()["result"]))
            results = "\n\n".join(results)
            if inner_kwargs.get("mode", "concat") == "concat":
                return_result["result"] = results
            else:
                assert inner_kwargs.get("mode", "concat") == "llm"
                fa_llm_result = get_llm_output(
                    node, self, memory, "final_aggregate", to_run_final_aggregate = results,
                    *args, **kwargs
                )
                return_result = fa_llm_result
                    
        elif task_type == "COMPOSITION":
            return_result["result"] = memory.article
        return return_result 

    @overrides
    def parse_result(self, agent_output, *args, **kwargs) -> Dict:
        return agent_output