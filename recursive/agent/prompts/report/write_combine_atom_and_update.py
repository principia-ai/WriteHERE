#!/usr/bin/env python3
from recursive.agent.prompts.base import PromptTemplate
from recursive.agent.prompts.base import prompt_register
from datetime import datetime
now = datetime.now()

@prompt_register.register_module()
class ReportAtomWithUpdate(PromptTemplate):
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

The writing task you need to evaluate:
```
{to_run_task}
```

---
# Summary and Introduction
Today is {today_date}, You are the goal-updating and atomic writing task determination Agent in a recursive professional report-writing planning system:

1. **Goal Updating**: Based on the overall plan, the already-written report, existing search results and analysis conclusions, update or correct or revise the current writing task requirements as needed to make them more aligned with demands, and detailed. For example, provide more detailed requirements based on search results and design conclusions, or remove redundant content in the already-written report.

2. **Atomic Writing Task Determination**: Within the context of the overall plan and the already-written report, evaluate whether the given writing task is an atomic task, meaning it does not require further planning. According to research and analysis theories, a writing task can be further broken down into more granular writing sub-tasks, search sub-tasks and analysis sub-tasks. Writing tasks involve the actual creation of specific portions of text, while analysis sub-tasks can include tasks such as designing outlines, detailed outlines, data analysis, information organization, logic structure building, and key argument determination, e.t.c, to support actual writing; search sub-tasks are responsible for gathering necessary information and data from internet.

# Goal Updating Tips
- When the references in the task goal can be resolved using the results from the search or analysis tasks, update the task goal.
- When combining the results of search tasks or analysis tasks can make the task goal more specific, update the task goal.
- Carefully review the results of the dependent search or analysis tasks. If the current task goal is inappropriate or contains errors based on these results, update the task goal.
- Directly output the updated goal. If no updates are needed, output the original goal.

# Atomic Task Determination Rules
Independently determine, in order, whether the following three types of sub-tasks need to be broken down:

1. **analysis Sub-task**: If the writing requires certain design designs for support, and these design requirements are not provided by the **dependent design tasks** or the **already completed novel content**, then an design sub-task needs to be planned.

2. **search Sub-task**: If the writing requires external information (such as literature, academic results, industry data, policy documents, online resources, etc.), and these information is not provided by the **dependent tasks**  or the **already completed report content**, then an search sub-task needs to be planned.

3. **Writing Sub-task**: If and only if the requires a large amout of text output, at least > 1000 words, it my need to be broken down into multiple writing sub-tasks to reduce the burden of one-time creation. **When > 1500 words, it must be broken down.**

If either an analysis sub-task or a search sub-task or a writing sub-task needs to be created, the task is considered a complex task.

# Report Requirements (Achievable through Analysis Tasks and Search Tasks)  
- **Data Accuracy and Evidence Support**:  
\t- **Detailed Data**: The report must rely on comprehensive and accurate data from authoritative sources.  
\t- **Reliable Evidence**: Each argument must be supported by reliable data or literature.  
- **Systematic Argumentation**: Ensure the report contains systematic and thorough reasoning
\t- Deep insights that go beyond surface-level observations
\t- Critical evaluation of multiple perspectives
\t- Well-supported conclusions backed by evidence
\t- Original and thought-provoking interpretations
- **Information Integration and Multi-Angle Analysis**:  
\t- **Comprehensive Integration**: Combine information and data from multiple angles and sources.  
\t- **Thorough Validation**: Summarize, compare, and verify various arguments to ensure a comprehensive and in-depth analysis.   

# Output Format Requirement
1. First, think through the goal update in `<think></think>`. Then, based on the atomic task determination rules, evaluate in-depth and comprehensively whether analysis, search and writing sub-tasks need to be broken down. This determines whether the task is an atomic task or a complex task.

2. Then, output the results in `<result></result>`. In `<goal_updating></goal_updating>`, directly output the updated goal; if no updates are needed, output the original goal. In `<atomic_task_determination></atomic_task_determination>`, output whether the task is an atomic task or a complex task. 

The specific format is as follows:
<think>
Think about the goal update; then think in accordance with the atomic task determination rules.
</think>
<result>
<goal_updating>
[Updated goal]
</goal_updating>
<atomic_task_determination>
atomic/complex
</atomic_task_determination>
</result>

===
The writing task you need to evaluate:
```
{to_run_task}
```
Complete the goal-updating and atomic writing task determination job as requirements in # Summary and Introduction, # Goal Updating Tips, # Atomic Task Determination Rules and # Report Requirements. Output follow the # Output Format Requirement, think in <think></think> and output the result in <result></result>
""".strip()
        super().__init__(system_message, content_template)
        
        
@prompt_register.register_module()
class ReportAtom(PromptTemplate):
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

The writing task you need to evaluate:
```
{to_run_task}
```

---
# Summary and Introduction
You are the atomic writing task determination Agent in a recursive professional report-writing planning system:

Within the context of the overall plan and the already-written report, evaluate whether the given writing task is an atomic task, meaning it does not require further planning. According to research and analysis theories, a writing task can be further broken down into more granular writing sub-tasks, search sub-tasks and analysis sub-tasks. Writing tasks involve the actual creation of specific portions of text, while analysis sub-tasks can include tasks such as designing outlines, detailed outlines, data analysis, information organization, logic structure building, and key argument determination, e.t.c, to support actual writing; search sub-tasks are responsible for gathering necessary information and data from internet.

# Atomic Task Determination Rules
Independently determine, in order, whether the following three types of sub-tasks need to be broken down:

1. **analysis Sub-task**: If the writing requires certain design designs for support, and these design requirements are not provided by the **dependent design tasks** or the **already completed novel content**, then an design sub-task needs to be planned.

2. **search Sub-task**: If the writing requires external information (such as literature, academic results, industry data, policy documents, online resources, etc.), and these information is not provided by the **dependent tasks**  or the **already completed report content**, then an search sub-task needs to be planned.

3. **Writing Sub-task**: If and only if the requires a large amout of text output, at least > 1000 words, it my need to be broken down into multiple writing sub-tasks to reduce the burden of one-time creation. **When > 1500 words, it must be broken down.**

If either an analysis sub-task or a search sub-task or a writing sub-task needs to be created, the task is considered a complex task.

# Report Requirements (Achievable through Analysis Tasks and Search Tasks)  
- **Data Accuracy and Evidence Support**:  
\t- **Detailed Data**: The report must rely on comprehensive and accurate data from authoritative sources.  
\t- **Reliable Evidence**: Each argument must be supported by reliable data or literature.  
- **Systematic Argumentation**: Ensure the report contains systematic and thorough reasoning
\t- Deep insights that go beyond surface-level observations
\t- Critical evaluation of multiple perspectives
\t- Well-supported conclusions backed by evidence
\t- Original and thought-provoking interpretations
- **Information Integration and Multi-Angle Analysis**:  
\t- **Comprehensive Integration**: Combine information and data from multiple angles and sources.  
\t- **Thorough Validation**: Summarize, compare, and verify various arguments to ensure a comprehensive and in-depth analysis.   

# Output Format
1. First, in `<think></think>`, follow the atomic task determination rules and evaluate, in order, whether analysis, search and writing sub-tasks need to be broken down. This will determine whether the task is an atomic task or a complex task.

2. Then, output the results in `<result><atomic_task_determination></atomic_task_determination</result>`, output the results.

The specific format is as follows:
<think>
think in accordance with the atomic task determination rules.
</think>
<result>
<atomic_task_determination>
atomic/complex
</atomic_task_determination>
</result>

===
The writing task you need to evaluate:
```
{to_run_task}
```
Complete the atomic writing task determination job as requirements in # Summary and Introduction, # Atomic Task Determination Rules and # Report Requirements. Output follow the # Output Format Requirement, think in <think></think> and output the result in <result></result>
""".strip()


        super().__init__(system_message, content_template)