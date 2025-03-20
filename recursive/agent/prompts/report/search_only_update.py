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
Today is Mar 17 2025, You are the goal updating Agent in a recursive professional report-writing planning system:

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



@prompt_register.register_module()
class ReportSearchOnlyUpdateZH(PromptTemplate):
    def __init__(self) -> None:
        system_message = ""
        
        content_template = """
已完成的搜索和分析任务结果:
```
{to_run_outer_graph_dependent}

{to_run_same_graph_dependent}
```

已撰写的报告:
```
{to_run_article}
```

总体计划
```
{to_run_full_plan}
```

您需要更新/纠正/更新的搜索任务:
```
{to_run_task}
```

---
# 摘要与介绍
今天是2025年3月17日，你是递归专业报告写作计划系统中的目标更新代理：

- 根据整体计划、已经编写的报告、现有搜索结果和分析结论，按需更新或纠正当前搜索任务目标（信息需求）。
	- 当任务目标中的引用可以使用搜索或分析任务的结果解决时，更新任务目标。
	- 当结合搜索任务或分析任务的结果可以使任务目标更具体时，更新任务目标。
	- 仔细审查依赖的搜索或分析任务的结果。如果当前任务目标基于这些结果不当或包含错误，请更新任务目标。
	- 不要使目标过于详细

# 输出格式
直接在`<result><goal_updating></goal_updating></result>`中输出更新后的目标。如果不需要更新，直接简单地输出原始目标。

具体格式如下：
<result>
<goal_updating>
[更新后的目标]
</goal_updating>
</result>

# 示例
## 示例1
任务：查找姚明的出生年份并确保信息准确。
-> 无需更新
## 示例2
任务：查找姚明的出生年份
-> 无需更新
## 示例3
任务1：查找姚明的出生年份 => 结果是1980
任务2（依赖任务1）：基于确定的年份，查询那一年的NBA总决赛，重点关注亚军球队及其主教练信息
将任务2更新为：查询1980年的NBA总决赛，重点关注亚军球队及其主教练信息

--
你需要更新/纠正/更新的搜索任务：
```
{to_run_task}
```

按照我告诉你的执行你的工作，并按照#输出格式输出答案。
""".strip()
        super().__init__(system_message, content_template)