#!/usr/bin/env python3
from recursive.agent.prompts.base import PromptTemplate
from recursive.agent.prompts.base import prompt_register
from datetime import datetime

now = datetime.now()

@prompt_register.register_module()
class StoryWrtingNLReasonerCN(PromptTemplate):
    def __init__(self) -> None:
        system_message = ""

        content_template = """
需要完成的协作小说创作需求: **{to_run_root_question}**

您需要完成的具体小说设计任务: **{to_run_task}**

---
已有的小说设计结论如下:
```
{to_run_outer_graph_dependent}

{to_run_same_graph_dependent}
```

---
已经写好的小说内容:
```
{to_run_article}
```

---
您是一位创新型专业作家，正与其他专业作家合作创作一个符合特定用户需求的创意故事。您的任务是完成分配给您的故事设计任务，旨在创新性地支持其他作家的写作和设计工作，从而为整个小说的完成做出贡献。

注意!! 您的设计成果应当与现有的小说设计结论在逻辑上保持一致和连贯。

# 输出格式
1. 首先，在 `<think></think>` 标签内进行思考
2. 然后，在 `<r></r>` 标签内以结构化且易读的格式写出设计结果，提供尽可能详细的内容。

请根据需求，以合理且创新的方式完成故事设计任务 **{to_run_task}**。
""".strip()
        super().__init__(system_message, content_template)

 
@prompt_register.register_module()
class StoryWritingReasonerFinalAggregateCN(PromptTemplate):
    def __init__(self) -> None:
        system_message = ""

        content_template = """
需要完成的协作小说创作需求: **{to_run_root_question}**

您需要完成的具体小说设计任务: **{to_run_task}**

---
已有的小说设计结论如下:
```
{to_run_outer_graph_dependent}

{to_run_same_graph_dependent}
```

---
已经写好的小说内容:
```
{to_run_article}
```

---
**您需要整合和完善的小说设计结论**，以给出最终的故事设计任务: **{to_run_task}**:
```
{to_run_final_aggregate}
```

---
您是一位创新型专业作家，正与其他专业作家合作创作一个符合特定用户需求的创意故事。您的任务是**整合和完善**多位小说设计师提供的故事设计结果，并完成分配给您的故事设计任务，确保最终设计是**创新的**、逻辑一致的和连贯的。您需要解决潜在的冲突，增强各元素之间的联系，并在必要时填补空白，以产生一个统一且引人入胜的故事等。

注意!! 您的设计成果应与小说设计所提供的结论保持**逻辑一致性**和**连贯性**，同时提升整体小说设计的质量。

# 整合与完善要求
- **整合**:
  - 合并和综合多位小说设计师的输入，确保所有元素（如情节、人物、主题）统一为一个连贯的整体。
  - 识别并解决各推理者结果之间的逻辑不一致或矛盾。
  - 确保没有遗漏关键的设计元素，并且所有方面都有助于故事的推进和深度。

- **完善**:
  - 增强组合设计的清晰度、深度和情感共鸣。
  - 填补空白或详细阐述缺乏足够细节或发展的领域。
  - 确保故事的语调、节奏和风格始终保持一致。

- **创新和影响**:
  - 验证整体故事设计保持原创性并避免陈词滥调。
  - 深化普遍或深刻的主题，确保它们能引起读者的共鸣。
  - 引入微妙的改进或创意增强，提升故事的整体影响力。

# 输出格式
1. 首先，在 `<think></think>` 标签内进行深入思考，在思考过程中考虑各种可能性。确保审核和评估所有推理者的输入，解决不一致问题，并确定需要完善或增强的领域。
2. 然后，在 `<r></r>` 标签内以**结构化且易读的格式**写出**最终**设计结果。

请根据需求，以合理且创新的方式完成故事设计任务 **{to_run_task}**。
""".strip()
        super().__init__(system_message, content_template) 