#!/usr/bin/env python3
from recursive.agent.prompts.base import PromptTemplate
from recursive.agent.prompts.base import prompt_register
from datetime import datetime
now = datetime.now()


@prompt_register.register_module()
class SearchCombineAtomUpdateAndPlanningEN(PromptTemplate):
    def __init__(self) -> None:
        system_message = """
# Summary and Introduction
Today is {today_date}, You are the goal refining Agent in a recursive professional report-writing planning system:

- Based on the overall plan, the already-written report, existing search results and analysis conclusions, update, revise or correct the current search tasks goal as needed to make them more aligned with demands, reasonable, and detailed. 
- Directly output the refined goal. If no refines are needed, output the original goal.

# Output Format
1. First, think through the goal update in `<think></think>`
2. Then, directly output the refined goal in `<result><goal_updating></goal_updating></result>`.

The specific format is as follows:
<think>
Think about the goal update;
</think>
<result>
<goal_updating>
[Updated goal]
</goal_updating>
</result>

# Examples
## Example1

""".strip().format("02.13.2025")

        
        content_template = """
already-written report:
```
{to_run_article}
```

overall plan
```
{to_run_full_plan}
```

results of search and analysis tasks completed:
```
{to_run_outer_graph_dependent}

{to_run_same_graph_dependent}
```

The search task you need to update/correct/update:
```
{to_run_task}
```
""".strip()
        super().__init__(system_message, content_template)