#!/usr/bin/env python3
from recursive.agent.prompts.base import PromptTemplate
from recursive.agent.prompts.base import prompt_register
from datetime import datetime

now = datetime.now()


fewshot = """
<example index=1>
User-given writing task:
{
    "id": "",
    "task_type": "write",
    "goal": "Create an excellent suspense story set in the colony on Europa (Jupiter’s moon), incorporating the real environmental characteristics of Europa. Write the story directly, skillfully integrating the background setting, characters, character relationships, and plot conflicts into the story to make it gripping. Character motivations and plot development must be logical and free of contradictions.",
    "length": "4000 words"
}

A partially complete recursive global plan is provided as a reference, represented in a recursively nested JSON structure. The `sub_tasks` field represents the DAG (Directed Acyclic Graph) of the task planning. If `sub_tasks` is empty, it indicates an atomic task or one that has not yet been further planned:

{"id":"","task_type":"write","goal":"Create an excellent suspense story set in the colony on Europa (Jupiter’s moon), incorporating the real environmental characteristics of Europa. Write the story directly, skillfully integrating the background setting, characters, character relationships, and plot conflicts into the story to make it gripping. Character motivations and plot development must be logical and free of contradictions.","dependency":[],"length":"4000 words","sub_tasks":[{"id":"1","task_type":"think","goal":"Design the main characters and core suspense elements of the story. This includes the cause, progression, and resolution of the suspense event, as well as determining the theme and ideas the story aims to express. This includes the truth behind the case, a misleading clue system, and the pacing of the truth reveal.","dependency":[],"sub_tasks":[{"id":"1.1","task_type":"think","goal":"Design the truth behind the case: determine the nature of the event, the specific individuals involved, their motivations, methods, and timeline.","dependency":[]},{"id":"1.2","task_type":"think","goal":"Design a misleading clue system: include false suspects, misleading evidence, and coincidental events.","dependency":["1.1"]},{"id":"1.3","task_type":"think","goal":"Design the pacing of the truth reveal: plan the order of key clues, methods for eliminating misleading clues, and the gradual progression of the truth.","dependency":["1.1","1.2"]},{"id":"1.4","task_type":"think","goal":"Determine the theme and ideas of the story, exploring deeper issues such as humanity, technology, and ethics.","dependency":["1.1","1.2","1.3"]}]},{"id":"2","task_type":"think","goal":"Based on the results of Task 2, further refine the character design. Create detailed settings for the main characters, including their backgrounds, personalities, motivations, and relationships with one another. This includes public relationships, hidden relationships, conflicts of interest, emotional bonds, and their psychological changes and behavioral evolution throughout the events.","dependency":["1"],"sub_tasks":[{"id":"2.1","task_type":"think","goal":"Create detailed backgrounds for the main characters, including their life experiences, professional skills, and personal goals.","dependency":[]},{"id":"2.2","task_type":"think","goal":"Detail the characters' personality traits and behavior patterns to create vivid characterizations.","dependency":["2.1"]},{"id":"2.3","task_type":"think","goal":"Design the character relationship network, including public relationships, hidden relationships, conflicts of interest, and emotional bonds.","dependency":["2.1","2.2"]},{"id":"2.4","task_type":"think","goal":"Based on the designed suspense elements and plot, plan the psychological changes and behavioral evolution of the characters during the events, reflecting their growth or downfall.","dependency":["2.1","2.2","2.3"]}]},{"id":"3","task_type":"think","goal":"Integrate the design elements and refine the story framework. This includes designing the story structure, plotting the development of events, setting up turning points, pacing the clues, and designing key scenes and atmospheres.","dependency":["1","2"],"sub_tasks":[{"id":"3.1","task_type":"think","goal":"Design the story structure: plan the main content for the beginning, development, climax, and ending.","dependency":[]},{"id":"3.2","task_type":"think","goal":"Plot the development of events, arranging the order and pacing of key events.","dependency":["3.1"]},{"id":"3.3","task_type":"think","goal":"Set up turning points and the climax to ensure the story's tension and appeal.","dependency":["3.1","3.2"]},{"id":"3.4","task_type":"think","goal":"Plan the layout and reveal of clues to maintain the suspense.","dependency":["3.1","3.2","3.3"]},{"id":"3.5","task_type":"think","goal":"Design key scenes and atmospheres to highlight the sci-fi and suspense features of the story.","dependency":["3.1","3.2","3.3","3.4"]}]},{"id":"4","task_type":"write","goal":"Based on the previous designs, write the complete story, including the opening, development, climax, and ending. Skillfully integrate Europa’s environmental characteristics and suspense elements to make it gripping.","dependency":["1","2","3"],"length":"4000 words","sub_tasks":[{"id":"4.1","task_type":"write","goal":"Write the opening part of the story. Introduce the colony environment and main characters through a specific scene and lay the groundwork for suspense.","dependency":[],"length":"800 words","sub_tasks":[{"id":"4.1.1","task_type":"think","goal":"Conceive the specific scene for the story's opening, selecting one that showcases the Europa colony's environment and main characters.","dependency":[]},{"id":"4.1.2","task_type":"think","goal":"Determine the suspenseful hints to be laid in the opening, considering how to subtly introduce suspense elements.","dependency":["4.1.1"]},{"id":"4.1.3","task_type":"write","goal":"Write the opening part of the story, incorporating the designed scene and suspenseful hints.","dependency":["4.1.1","4.1.2"],"length":"800 words"}]},{"id":"4.2","task_type":"write","goal":"Write the event outbreak and initial investigation part, describing the occurrence of the suspenseful event and the characters’ initial reactions and investigation.","dependency":[],"length":"1200 words","sub_tasks":[{"id":"4.2.1","task_type":"think","goal":"Further detail the process of the suspenseful event's occurrence, including time, location, and method, ensuring the plot is logical and engaging.","dependency":[]},{"id":"4.2.2","task_type":"think","goal":"Based on the settings, further consider the main characters' reactions and initial investigative actions after the event, reflecting their personalities and relationships.","dependency":["4.2.1"]},{"id":"4.2.3","task_type":"write","goal":"Write the event outbreak and initial investigation part, showcasing the suspenseful event and characters' reactions to advance the plot.","dependency":["4.2.1","4.2.2"],"length":"1200 words"}]},{"id":"4.3","task_type":"write","goal":"Write the in-depth investigation section, revealing character relationships through the investigation process and increasing the story's suspense.","dependency":[],"length":"1000 words","sub_tasks":[{"id":"4.3.1","task_type":"think","goal":"Based on the settings, further detail the clues and misleading information that appear during the in-depth investigation, adding complexity and suspense to the story.","dependency":[]},{"id":"4.3.2","task_type":"think","goal":"Based on the settings, further consider the interactions between the main characters during the investigation, revealing their backgrounds and hidden relationships.","dependency":["4.3.1"]},{"id":"4.3.3","task_type":"write","goal":"Write the in-depth investigation section, integrating the designed clues and character interactions to enhance the story's suspense.","dependency":["4.3.1","4.3.2"],"length":"1000 words"}]},{"id":"4.4","task_type":"write","goal":"Write the climax and ending section, resolving the mystery and showcasing the characters' fates and the story's theme.","dependency":[],"sub_tasks":[],"length":"1000 words"}]}]}
</example>
"""


@prompt_register.register_module()
class StoryWritingNLPlanningEN(PromptTemplate):
    def __init__(self) -> None:
        system_message = """
# Overall Introduction
You are a recursive professional novel-writing planning expert adept at planning professional novel writing based on narrative theory. A high-level plan tailored to the user's novel-writing needs is already in place, and your task is to further recursively plan the specified writing sub-tasks within this framework. Through your planning, the resulting novel will strictly adhere to user requirements and achieve perfection in terms of plot, creativity (ideas, themes, and topics), and development.

1. Continue the recursive planning for the specified professional novel-writing sub-tasks. According to narrative theory, the organization of story writing and the result of the design tasks, break the tasks down into more granular writing sub-tasks, specifying their scope and specific writing content.  
2. Plan design sub-tasks as needed to assist and support specific writing. Design sub-tasks are for designing elements including outlines, character, Writing style, Narrative techniques, viewpoint, setting, theme, tone and scene construction, etc., to support the actual writing.
3. For each task, plan a sub-task DAG (Directed Acyclic Graph), where the edges represent dependency relationships between design tasks within the same layer of the DAG. Recursively plan each sub-task until all sub-tasks are atomic tasks.

# Task Types
## Writing (Core, actual writing)
- **Function**: Perform actual novel-writing tasks in sequence according to the plan. Based on specific writing requirements and already-written content, continue writing in conjunction with the conclusions of design tasks.  
- **All writing tasks are continuation tasks**: Ensure continuity with the preceding content during planning. Writing tasks should flow smoothly and seamlessly with one another.  
- **Breakable tasks**: Writing, Design
- Unless necessary, each writing sub-task should be more than 500 words. Do not break down a writing task less than 500 words into sub- writing tasks.

## Design
- **Function**: Analyze and design any novel-writing needs other than actual writing. This may include outlines, character, Writing style, Narrative techniques, viewpoint, setting, theme, tone and scene construction, etc., to support the actual writing.  
- **Breakable tasks**: Design  

# Information Provided to You
- **`Already-written novel content`**: Content from previous writing tasks that has already been written.  
- **`Overall plan`**: The overall writing plan, which specifies the task you need to plan through the `is_current_to_plan_task` key.  
- **`Results of design tasks completed in higher-level tasks`**  
- **`Results of design tasks dependent on the same-layer DAG tasks`**  
- **`Writing tasks that require further planning`**  
- **`Reference planning`**: A planning sample is provided, which you may cautiously reference.  

# Planning Tips
1. The last sub-task derived from a writing task must always be a writing task.  
2. Reasonably control the number of sub-tasks in each layer of the DAG, generally **2 to 5** sub-tasks. If the number of tasks exceeds this, plan recursively.  
3. **Design tasks** can serve as **sub-tasks of writing tasks**, and as many design sub-tasks as possible should be generated to enhance the quality of writing.  
4. Use `dependency` to list the IDs of design tasks within the same-layer DAG. List all potential dependencies as comprehensively as possible.  
5. When a design sub-task involves designing specific writing structures (e.g., plot design), subsequent dependent writing tasks should not be laid out flat but should await recursive planning in subsequent rounds.  
6. **Do not redundantly plan tasks already covered in the `overall plan` or duplicate content already present in the `already-written novel content`, and previous design tasks. ** 
7. Writing tasks should flow smoothly and seamlessly, ensuring continuity in the narrative.
8. Following the Results of design tasks
**9**. Unless specified by user, the length of each writing task should be > 500 words. Do not break a writing task less than 500 words into sub-writing tasks.

# Task Attributes
1. **id**: The unique identifier for the sub-task, indicating its level and task number.  
2. **goal**: A precise and complete description of the sub-task goal in string format.  
3. **dependency**: A list of design task IDs from the same-layer DAG that this task depends on. List all potential dependencies as comprehensively as possible. If there are no dependent sub-tasks, this should be empty.  
4. **task_type**: A string indicating the type of task. Writing tasks are labeled as `write`, and design tasks are labeled as `think`.  
5. **length**: For writing tasks, this attribute specifies the scope, it is required for writing task. Design tasks do not require this attribute.  
6. **sub_tasks**: A JSON list representing the sub-task DAG. Each element in the list is a JSON object representing a task.


# Example
{}

# Output Format
1. First, conduct in-depth and comprehensive thinking in `<think></think>`.  
2. Then, in `<result></result>`, output the planning results in the JSON format as shown in the example. The top-level object should represent the given task, with its `sub_tasks` as the results of the planning.  
```
""".strip().format(fewshot)
        
        content_template = """
Writing tasks that require further planning:
{to_run_task}

Reference planning: 
{to_run_candidate_plan}

Reference thinking:
{to_run_candidate_think}
---

Already-written novel content: 
```
{to_run_article}
```

Overall plan: 
```
{to_run_full_plan}
```

Results of design tasks completed in higher-level tasks: 
```
{to_run_outer_graph_dependent}
```

Results of design tasks dependent on the same-layer DAG tasks: 
```
{to_run_same_graph_dependent}
```

Plan the writing task according to the aforementioned requirements and examples.  
""".strip()
        super().__init__(system_message, content_template)
    
