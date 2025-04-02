#!/usr/bin/env python3
from recursive.agent.prompts.base import PromptTemplate
from recursive.agent.prompts.base import prompt_register
from datetime import datetime
now = datetime.now()

@prompt_register.register_module()
class ReportSearchOnlyUpdate(PromptTemplate):
    def __init__(self) -> None:
        system_message = ""
        
        content_template = """
results of search and analysis tasks completed:
```
{to_run_outer_graph_dependent}

{to_run_same_graph_dependent}
```

already-written report:
```
{to_run_article}
```

overall plan
```
{to_run_full_plan}
```

The search task you need to update/correct/update:
```
{to_run_task}
```

---
# Summary and Introduction
Today is {today_date}, You are the goal updating Agent in a recursive professional report-writing planning system:

- Based on the overall plan, the already-written report, existing search results and analysis conclusions, update, or correct the current search tasks goal (information requirements) as needed.
\t- When the references in the task goal can be resolved using the results from the search or analysis tasks, update the task goal.
\t- When combining the results of search tasks or analysis tasks can make the task goal more specific, update the task goal.
\t- Carefully review the results of the dependent search or analysis tasks. If the current task goal is inappropriate or contains errors based on these results, update the task goal.
\t- Don't make goals overly detailed

# Output Format
directly output the updated goal in `<result><goal_updating></goal_updating></result>`. If theres no need to update, output the original goal directly and simply.

The specific format is as follows:
<result>
<goal_updating>
[Updated goal]
</goal_updating>
</result>

# Examples
## Example1
Task: Find Yao Ming's birth year and ensure the information is accurate.
-> There's no need to update
## Example2
Task: Find Yao Ming's birth year
-> There's no need to update
## Example 3
Task1: Find Yao Ming's birth year => Result is 1980
Task2 (depend Task1): Based on the determined year, look up the NBA Finals of that year, focusing on the runner-up team and its head coach information
Update the Task2 to: look up the NBA Finals of 1080, focusing on the runner-up team and its head coach information

--
The search task you need to update/correct/update:
```
{to_run_task}
```

Do your job as I told you, and output the answer follow the # Output Format.
""".strip()
        super().__init__(system_message, content_template)