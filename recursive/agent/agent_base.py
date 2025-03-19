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


agent_register = Register('agent_register')
    
class Agent(ABC):
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.args = args
 
    @abstractmethod
    def forward(self, node, memory, *args, **kwargs):
        raise NotImplementedError()
    
    @abstractmethod
    def parse_result(self, agent_output, *args, **kwargs):
        raise NotImplementedError()

    def call_llm(self, system_message, prompt, parse_arg_dict, history_message = None, **other_inner_args):
        llm = OpenAIApiProxy()
        
        if system_message.strip() == "":
            message = []
        else:
            message = [
                {"role": "system", "content": system_message},
            ]
        if history_message is not None:
            message.append(history_message)
        message.append({"role": "user", "content": prompt})
        logger.info(message[-1]["content"])
        
        model = other_inner_args.pop("model", "gpt-4o")
        
        resp = llm.call(messages = message,
                        model=model,
                        **other_inner_args)[0]
        if "r1" in model:
            reason = resp["message"]["reasoning_content"]
        else:
            reason = ""
        content = resp["message"]["content"]
        logger.info("Get REASONING: {}\n\nResult: {}".format(
            reason, content
        ))

        assert isinstance(parse_arg_dict, dict)
        result = {
            "original": content,
            "result": content,
            "reason": reason
        }
        
        """  
        The following code extracts structured information from an LLM's textual response by looking for content within specific XML-like tags. It works by:

        1. Iterating through each key-value pair in parse_arg_dict which maps output keys to tag patterns
        2. For each pair, it calls parse_hierarchy_tags_result() which extracts text enclosed in those specific XML-like tags
        3. The extracted content is stripped of whitespace and stored in the result dictionary under the corresponding key

        For example, if the LLM response contains <reasoning>Some analysis here</reasoning> and parse_arg_dict has {"thought": "reasoning"}, the function would extract "Some
        analysis here" and store it under result["thought"].
        """
        for key, value in parse_arg_dict.items():
            result[key] = parse_hierarchy_tags_result(content, value).strip()
        return result
                    
        
        

@agent_register.register_module()
class DummyRandomPlanningAgent(Agent):
    @overrides
    def forward(self, node, memory, *args, **kwargs) -> str:
        # layer_cnt = random.randint(1, 3)
        layer = node.node_graph_info["layer"]
        if layer == 2:
            result = {
                "original": "",
                "result": [],
                "thought": ""
            }
            return result
            
        # layer_cnt = random.randint(1, 2) 
        layer_cnt = 3 if layer == 1 else 1
        plans = []
        current = []
        cnt = 0
        for layer_idx in range(layer_cnt):
            parent = current
            current = []
            # node_cnt = random.randint(1, 3)
            node_cnt = random.randint(1, 2) if layer_idx < 2 else 1
            for nidx in range(node_cnt):
                if layer_idx == 0:
                    depend_cnt = 0
                    dependency = []
                else:
                    dependency = random.sample(parent, random.randint(1, len(parent)))
                    dependency = sorted([node["id"]  for node in dependency])
                task = {
                    "goal": "random_dummy",
                    "id": cnt,
                    "dependency": dependency
                }
                cnt += 1
                current.append(task)
            plans.extend(current)
        
        result = {
            "original": "",
            "result": plans,
            "thought": ""
        }
        return result

    @overrides
    def parse_result(self, agent_output, *args, **kwargs) -> Dict:
        return agent_output
      
@agent_register.register_module()
class SinglePlanningAgent(Agent):
    @overrides
    def forward(self, node, memory, *args, **kwargs) -> str:
        layer = node.node_graph_info["layer"]
        if layer == 1:
            result = {
                "original": "",
                "result": [],
                "thought": ""
            }
            return result
        
        plans = [{
            "id": 0,
            "dependency": [],
            "goal": node.task_info["goal"]
        }]
        
        result = {
            "original": "",
            "result": plans,
            "thought": ""
        }
        return result

    @overrides
    def parse_result(self, agent_output, *args, **kwargs) -> Dict:
        return agent_output



@agent_register.register_module()           
class DummyRandomExecutorAgent(Agent):
    @overrides
    def forward(self, node, memory, *args, **kwargs) -> str:
        result = {
            "original": "",
            "process": [],
            "thought": "",
            "result": "Random Fake Result"
        }
        return result

    @overrides
    def parse_result(self, agent_output, *args, **kwargs) -> Dict:
        return agent_output


@agent_register.register_module() 
class DummyRandomUpdateAgent(Agent):
    @overrides
    def forward(self, node, memory, *args, **kwargs) -> str:
        return None

    @overrides
    def parse_result(self, agent_output, *args, **kwargs) -> Dict:
        return json.loads(agent_output)
    
@agent_register.register_module()
class DummyRandomPriorReflectionAgent(Agent):
    @overrides
    def forward(self, node, memory, *args, **kwargs) -> str:
        return None

    @overrides
    def parse_result(self, agent_output, *args, **kwargs) -> Dict:
        return json.loads(agent_output)
   
@agent_register.register_module()     
class DummyRandomPlanningPostReflectionAgent(Agent):
    @overrides
    def forward(self, node, memory, *args, **kwargs) -> str:
        return None

    @overrides
    def parse_result(self, agent_output, *args, **kwargs) -> Dict:
        return json.loads(agent_output)
    
@agent_register.register_module()     
class DummyRandomExecutorPostReflectionAgent(Agent):
    @overrides
    def forward(self, node, memory, *args, **kwargs) -> str:
        result = {
            "thought": "",
            "original": "",
            "status": "success",
            "result": node.raw_plan
        }
        return result

    @overrides
    def parse_result(self, agent_output, *args, **kwargs) -> Dict:
        return json.loads(agent_output)

@agent_register.register_module()  
class DummyRandomFinalAggregateAgent(Agent):
    @overrides
    def forward(self, node, memory, *args, **kwargs) -> str:
        result = {
            "thought": "",
            "original": "",
            "status": "success",
            "result": node.topological_task_queue[-1].get_node_final_result()
        }
        return result

    @overrides
    def parse_result(self, agent_output, *args, **kwargs) -> Dict:
        return json.loads(agent_output)




if __name__ == "__main__":
    agent = DummyRandomExecutorAgent("", "")
    output = agent.forward({}, {}, {}, {}, {})
    from pprint import pprint
    pprint(agent.parse_result(output))