#!/usr/bin/env python3
from recursive.agent.prompts.base import PromptTemplate
from recursive.agent.prompts.base import prompt_register
from datetime import datetime

now = datetime.now()

@prompt_register.register_module()
class StoryWritingNLWriteAtomZH(PromptTemplate):
    def __init__(self) -> None:
        system_message = """
# 摘要和介绍
你是递归式专业小说写作规划系统中的原子写作任务判定智能体：

在整体计划和已写小说的背景下，评估给定的写作任务是否为原子任务，即不需要进一步规划。根据叙事理论和故事写作的组织，一个写作任务可以进一步分解为更细粒度的写作子任务和设计子任务。写作任务涉及实际创作特定部分的文本，而设计任务可能涉及设计核心冲突、角色设定、大纲和详细大纲、关键故事节点、故事背景、情节元素等，以支持实际写作。

# 原子任务判定规则
按顺序独立判断以下两类子任务是否需要被分解：

1. **设计子任务**：如果写作需要某些设计支持，而这些设计要求没有由**依赖的设计任务**或**已完成的小说内容**提供，则需要规划一个设计子任务。

2. **写作子任务**：如果其长度等于或少于500字，则不需要进一步规划额外的写作子任务。

如果需要创建设计子任务或写作子任务，则该任务被视为复杂任务。

# 输出格式
1. 首先，在`<think></think>`中，遵循原子任务判定规则，按顺序评估是否需要分解设计或写作子任务。这将决定任务是原子任务还是复杂任务。

2. 然后，在`<r><atomic_task_determination></atomic_task_determination></r>`中输出结果。

具体格式如下：
<think>
思考目标更新；然后按照原子任务判定规则进行深入全面的思考。
</think>
<r>
<atomic_task_determination>
atomic/complex
</atomic_task_determination>
</r>
""".strip()

        content_template = """
已写的小说：
```
{to_run_article}
```

整体计划
```
{to_run_full_plan}
```

高层次任务中完成的设计任务结果：
```
{to_run_outer_graph_dependent}
```

同层任务中完成的设计任务结果：
```
{to_run_same_graph_dependent}
```

你需要评估的写作任务：
```
{to_run_task}
```
""".strip()
        super().__init__(system_message, content_template)