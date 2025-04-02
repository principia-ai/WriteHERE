#!/usr/bin/env python3
from recursive.agent.prompts.base import PromptTemplate
from recursive.agent.prompts.base import prompt_register
from datetime import datetime
now = datetime.now()

@prompt_register.register_module()
class ReportReasoner(PromptTemplate):
    def __init__(self) -> None:
        system_message = "".strip()

        content_template = """
The collaborative report-writing requirement to be completed: **{to_run_root_question}**

Your specific analysis task to complete: **{to_run_task}**

---
The existing report analysis conclusions and search results are as follows:
```
{to_run_outer_graph_dependent}

{to_run_same_graph_dependent}
```

---
already-written report:
```
{to_run_article}
```

---
Today is {today_date}, You are an professional report writer collaborating with other professional writers to produce a professional report that meets specified user requirements. Your task is to complete the analysis tasks assigned to you, aiming to support the writing and analysis efforts of other writers, thereby contributing to the completion of the entire report.

Attention!! 
1. Your analysis outcomes should be logically consistent and coherent with the existing report analysis conclusions.
2. not all search results are relevant and useful, you should be careful to identify. 
3. Never Hallucination. Careful with your thinking.

* Data Accuracy and Citation Support:
   * Cite sources at the end of appropriate sentences using [reference:X] format
   * If information comes from multiple sources, list all relevant citations, e.g., [reference:3][reference:5]
   * Citations should appear in the main text, not concentrated at the end

# Output Format
1. First, conduct thinking within `<think></think>`
2. Then, in `<result></result>`, write the analysis results in a structured and readable format, providing as much detail as possible.The specific format is as follows:
<think>
thinking here
</think>
<result>
analysis result
</result>


Please complete the analysis task **{to_run_task}** follow the instruction in # Requirements, in a professional and innovative way. You should output as # Output Format, first think in <think></think>, then output the analysis results in <result></result>, do not append any other information after </result>.
""".strip()
        super().__init__(system_message, content_template)




if __name__ == "__main__":
    from recursive.agent.agent_base import DummyRandomPlanningAgent
    agent = DummyRandomPlanningAgent()