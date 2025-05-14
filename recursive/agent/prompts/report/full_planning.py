#!/usr/bin/env python3
from recursive.agent.prompts.base import PromptTemplate
from recursive.agent.prompts.base import prompt_register
from datetime import datetime

now = datetime.now()

@prompt_register.register_module()
class ReportPlanning(PromptTemplate):
    def __init__(self) -> None:
        system_message = ""
        content_template = """
Writing tasks that require further planning:
{to_run_task}

Reference planning:
{to_run_candidate_plan}

Reference thinking:
{to_run_candidate_think}
---

Overall plan:
```
{to_run_full_plan}
```
---

Results of analysis tasks completed:
```
{to_run_outer_graph_dependent}

{to_run_same_graph_dependent}
```
---


Already-written report content:
```
{to_run_article}
```
---

# Overall Introduction
You are a recursive professional report-writing and information seeking planning expert, specializing in planning professional report writing based on in-depth research、search and analysis. A high-level plan tailored to the user's knowledge problem-solving needs is already in place, and your task is to further recursively plan the specified writing sub-tasks within this framework. Through your planning, the resulting report will strictly adhere to user requirements and achieve perfection in terms of analysis, logic, and content depth.

1. Continue the recursive planning for the specified professional report-writing sub-tasks. According to research and analysis theories, break down the organization of report writing and the results of analysis tasks into more granular writing sub-tasks, specifying their scope and specific writing content.
2. Plan analysis sub-tasks and search sub-tasks as needed to assist and support specific writing. Analysis sub-tasks can include tasks such as designing outlines, detailed outlines, data analysis, information organization, logic structure building, and key argument determination to support actual writing. Search sub-tasks are responsible for gathering necessary information and data from internet.
3. For each task, plan a Directed Acyclic Graph (DAG) of sub-tasks, where the edges represent dependency relationships between search and analysis tasks within the same layer of the DAG. Recursively plan each sub-task until all sub-tasks become atomic tasks.

# Task Types
## Writing (Core, Actual Writing)
- **Function**: Perform actual report-writing tasks in sequence according to the plan. Based on specific writing requirements and already written content, continue writing in conjunction with the conclusions of analysis tasks and search tasks.
- **All writing tasks are continuation tasks**: Ensure continuity and logical consistency with the preceding content during planning. Writing tasks should flow smoothly and seamlessly with one another, maintaining the overall coherence and unity of the report.
- **Breakable tasks**: Writing, Analysis, Search
- Unless necessary, each writing sub-task should be > 500 words.

## Analysis  
- **Function**: Analyze and design any requirements outside of actual report writing. This includes but is not limited to research plan design, designing outlines, detailed outlines, data analysis, information organization, logic structure building, key argument determination, etc., to support actual writing.
- **Breakable tasks**: Analysis, Search

## Search  
- **Function**: Perform information-gathering tasks, including collecting necessary data, materials, and information from internet to support analysis and writing tasks.
- **Breakable tasks**: Search

# Planning Tips  
1. The last sub-task derived from a writing task must always be a writing task.  
2. Reasonably control the number of sub-tasks in each layer of the DAG, **generally 3–5 sub-tasks**. If the number of tasks exceeds this range, aim to plan recursively. **Do not planning over 8 sub-tasks in one layer.**
3. **Analysis tasks** and **search tasks** can serve as **sub-tasks of writing tasks**, more analysis sub-tasks and search sub-tasks should be generated to enhance the quality of writing.  
4. Use `dependency` to list the IDs of analysis tasks and search tasks within the same-layer DAG. List all potential dependencies as comprehensively as possible.
5. **When an analysis sub-task involves designing specific writing structures, subsequent dependent writing tasks should not be flatten, it should be recursived. e.g., write xxx acorrding to the structure.**. Never forget it.
6. **Do not redundantly plan tasks already covered in the `overall plan` or duplicate content already present in the `already written report content`, and previous analysis tasks.**  
7. Follow the results of analysis tasks and search tasks.
8. search tasks goal only specify the information requirements, do not specify the source or specify how to search.
**9**. Unless specified by user, the length of each writing task should be > 500 words.

# Task Attributes (Required)  
1. **id**: The unique identifier for the sub-task, indicating its level and task number.  
2. **goal**: A precise and complete description of the sub-task goal in string format.  
3. **dependency**: A list of IDs of search and analysis tasks tasks within the same-layer DAG that this task depends on. List all potential dependencies as comprehensively as possible. If there are no dependent sub-tasks, this should be empty.  
4. **task_type**: A string indicating the type of task. Writing tasks are labeled as `write`, analysis tasks are labeled as `think`, and search tasks are labeled as `search`.  
5. **length**: For writing tasks, this attribute specifies the scope. It is required for writing tasks. Analysis tasks and search tasks do not require this attribute.  
6. **sub_tasks**: A JSON list representing the sub-task DAG. Each element in the list is a JSON object representing a task.

# Example
<example index=1>
User-given writing task:
{{
    "id": "",
    "task_type": "write",
    "goal": "Generate a detailed business biography to document DeepSeek's rise",
    "length": "8600 words"
}}

A partially complete recursive global plan is provided as a reference, represented in a recursively nested JSON structure. The `sub_tasks` field represents the DAG (Directed Acyclic Graph) of the task planning. If `sub_tasks` is empty, it indicates an atomic task or one that has not yet been further planned:

{{"id":"root","task_type":"write","goal":"Generate a detailed business biography to document DeepSeek's rise","dependency":[],"length":"8600 words","sub_tasks":[{{"id":"1","task_type":"search","goal":"Briefly collect DeepSeek's company information, including: founding team background, establishment time, financing history, product development history, technological breakthroughs, market performance and other key information, to determine the overall article structure","dependency":[],"sub_tasks":[]}},{{"id":"2","task_type":"think","goal":"Analyze DeepSeek's development trajectory and success factors, identify key milestone events, design the overall structure and key content of the biography","dependency":["1"],"sub_tasks":[]}},{{"id":"3","task_type":"write","goal":"Write biography content based on search results and designed overall structure and key content","length":"8600 words","dependency":["1","2"],"sub_tasks":[{{"id":"3.1","task_type":"write","goal":"Write the founder and team background chapter, focusing on Liang Wenfeng's quantitative investment experience and team characteristics","length":"1200 words","dependency":[],"sub_tasks":[{{"id":"3.1.1","task_type":"search","goal":"Collect detailed information about Liang Wenfeng's experience at Ubiquant, including entrepreneurial process, quantitative investment achievements, technical accumulation, etc.","dependency":[]}},{{"id":"3.1.2","task_type":"search","goal":"Collect detailed background information of DeepSeek's founding team, collect Ubiquant's AI technology reserve information, especially details of the 'Firefly' series supercomputing platform","dependency":[]}},{{"id":"3.1.3","task_type":"write","goal":"Complete the writing of founder background and team characteristics sections, highlighting Liang Wenfeng's quantitative investment achievements and AI layout, as well as the young team composition and technical strength","length":"1200 words","dependency":["3.1.1","3.1.2"]}}]}},{{"id":"3.2","task_type":"write","goal":"Write the company founding and initial vision chapter, describing the 2023 entrepreneurial background and positioning","length":"1000 words","dependency":[],"sub_tasks":[{{"id":"3.2.1","task_type":"search","goal":"Collect 2023 AI industry background materials, Search for deep reasons why Liang Wenfeng chose the AI track, especially DeepSeek's differentiated positioning","dependency":[],"sub_tasks":[]}},{{"id":"3.2.1","task_type":"write","goal":"Write about entrepreneurial background and era opportunities, as well as initial strategic positioning and technical route choices, especially the deep reasons for Liang Wenfeng choosing the AI track, and DeepSeek's differentiated positioning","length":"1000 words","dependency":["3.2.1"],"sub_tasks":[]}}]}},{{"id":"3.3","task_type":"write","goal":"Write key development nodes chapter, detailing the release and impact of three important products: V2, V3, and R1","length":"1800 words","dependency":[],"sub_tasks":[{{"id":"3.3.1","task_type":"search","goal":"Collect detailed information about DeepSeek V2, V3 and R1 releases, and their impact on the industry","dependency":[]}},{{"id":"3.3.2","task_type":"think","goal":"Analyze the technical progress path of the three products and their impact on the industry","dependency":["3.3.1"]}},{{"id":"3.3.3","task_type":"write","goal":"Write the chapter, including three sections: V2 triggering price war, V3's shocking release and R1's inference breakthrough","length":"1800 words","dependency":["3.3.1","3.3.2"],"sub_tasks":[]}}]}},{{"id":"3.4","task_type":"write","goal":"Based on the written releases and impacts of V2, V3, and R1, further write core technology and product advantages chapter, analyzing sources of competitiveness","length":"1500 words","dependency":[],"sub_tasks":[{{"id":"3.4.1","task_type":"search","goal":"Collect information about DeepSeek's technical innovations, computing power optimization solutions and engineering innovations","dependency":[],"sub_tasks":[]}},{{"id":"3.4.2","task_type":"write","goal":"Based on collected materials and analysis conclusions, write about model architecture innovation, hardware-software coordination optimization, and model optimization and distillation strategies","length":"1500 words","dependency":["3.4.1"],"sub_tasks":[]}}]}},{{"id":"3.5","task_type":"write","goal":"Write market competition pattern and business strategy chapter, analyzing the game with domestic and foreign competitors","length":"1200 words","dependency":[],"sub_tasks":[{{"id":"3.5.1","task_type":"search","goal":"Collect product strategies and market performance of major domestic and foreign large model companies (Baidu, Alibaba, etc.)","dependency":[],"sub_tasks":[]}},{{"id":"3.5.2","task_type":"search","goal":"Collect and analysis DeepSeek's differentiated competition strategy compared with other large model companies","dependency":["3.5.1","3.5.2"],"sub_tasks":[]}},{{"id":"3.5.3","task_type":"write","goal":"Based on collected materials and analysis conclusions, write about domestic competition pattern, international competitiveness and influence analysis, and business strategy innovation analysis","length":"1200 words","dependency":["3.5.1","3.5.2"],"sub_tasks":[]}}]}},{{"id":"3.6","task_type":"write","goal":"Further write industry influence and external response chapter, summarizing DeepSeek's social influence","length":"1000 words","dependency":[],"sub_tasks":[]}},{{"id":"3.7","task_type":"write","goal":"Write future outlook chapter, predicting DeepSeek's development direction and challenges","length":"900 words","dependency":[],"sub_tasks":[{{"id":"3.7.1","task_type":"search","goal":"Collect future development plans and goals revealed by DeepSeek officially","dependency":[],"sub_tasks":[]}},{{"id":"3.7.2","task_type":"write","goal":"Based on collected materials and analysis conclusions, write future outlook chapter, including future plans, technology innovation outlook, ecosystem building outlook, talent strategy outlook and internationalization outlook","length":"900 words","dependency":["3.7.1"],"sub_tasks":[]}}]}}]}}]}}
</example>

# Output Format
In `<result></result>`, output the planning results in the JSON format as shown in the example. The top-level object should represent the given task, with its `sub_tasks` as the results of the planning. The specific format is as follows:
<result>
write here
</result>

---
Writing tasks that require further planning, follow the requirements as before, and output as # Output Format, directly give the result in format in <result></result>, Do not forget recursive planning: 
**{to_run_task}**
"""
        super().__init__(system_message, content_template)