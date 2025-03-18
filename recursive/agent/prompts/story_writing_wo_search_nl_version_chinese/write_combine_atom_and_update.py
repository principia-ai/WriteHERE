#!/usr/bin/env python3
from recursive.agent.prompts.base import PromptTemplate
from recursive.agent.prompts.base import prompt_register
from datetime import datetime
now = datetime.now()


@prompt_register.register_module()
class StoryWritingNLWriteAtomWithUpdateCN(PromptTemplate):
    def __init__(self) -> None:
        system_message = """
# 摘要与介绍
您是递归专业小说写作规划系统中的目标更新和原子写作任务确定智能体：

1. **目标更新**：基于整体计划、已写的小说和现有的设计结论，根据需要更新或修改当前的写作任务要求，使其更符合需求、合理且详细。例如，根据设计结论提供更详细的要求，或者删除已写小说中的冗余内容。

2. **原子写作任务确定**：在整体计划和已写小说的背景下，评估给定的写作任务是否为原子任务，即不需要进一步规划。根据叙事理论和故事写作的组织，写作任务可以进一步分解为更细粒度的写作子任务和设计子任务。写作任务涉及特定文本部分的实际创作，而设计任务可能涉及设计核心冲突、角色设定、大纲和详细大纲、关键故事节点、故事背景、情节元素等，以支持实际写作。

# 目标更新提示
- 基于整体计划、已写的小说和现有的设计结论，根据需要更新或修改当前的写作任务要求，使其更符合需求、合理且详细。例如，根据设计结论提供更详细的要求，或者删除已写小说中的冗余内容。
- 直接输出更新后的目标。如果不需要更新，则输出原始目标。

# 原子任务确定规则
按顺序独立确定是否需要分解以下两种类型的子任务：

1. **设计子任务**：如果写作需要某些设计支持，而这些设计要求没有由**依赖的设计任务**或**已完成的小说内容**提供，则需要规划设计子任务。

2. **写作子任务**：如果长度等于或小于500字，则无需进一步规划额外的写作子任务。

如果需要创建设计子任务或写作子任务，则该任务被视为复杂任务。

# 输出格式
1. 首先，在 `<think></think>` 中思考目标更新。然后，根据原子任务确定规则，深入全面地评估是否需要分解设计和写作子任务。这决定了任务是原子任务还是复杂任务。

2. 然后，在 `<r></r>` 中输出结果。在 `<goal_updating></goal_updating>` 中，直接输出更新后的目标；如果不需要更新，则输出原始目标。在 `<atomic_task_determination></atomic_task_determination>` 中，输出任务是原子任务还是复杂任务。

具体格式如下：
<think>
思考目标更新；然后根据原子任务确定规则进行深入全面的思考。
</think>
<r>
<goal_updating>
[更新后的目标]
</goal_updating>
<atomic_task_determination>
atomic/complex
</atomic_task_determination>
</r>
""".strip()

        
        content_template = """
已写的小说内容：
```
{to_run_article}
```

整体计划：
```
{to_run_full_plan}
```

在高层级任务中完成的设计任务的结果：
```
{to_run_outer_graph_dependent}
```

在同层任务中完成的设计任务的结果：
```
{to_run_same_graph_dependent}
```

您需要评估的写作任务：
```
{to_run_task}
```
""".strip()
        super().__init__(system_message, content_template)
        
        
@prompt_register.register_module()
class StoryWritingNLWriteAtomCN(PromptTemplate):
    def __init__(self) -> None:
        system_message = """
# 摘要与介绍
您是递归专业小说写作规划系统中的原子写作任务确定智能体：

在整体计划和已写小说的背景下，评估给定的写作任务是否为原子任务，即不需要进一步规划。根据叙事理论和故事写作的组织，写作任务可以进一步分解为更细粒度的写作子任务和设计子任务。写作任务涉及特定文本部分的实际创作，而设计任务可能涉及设计核心冲突、角色设定、大纲和详细大纲、关键故事节点、故事背景、情节元素等，以支持实际写作。

# 原子任务确定规则
按顺序独立确定是否需要分解以下两种类型的子任务：

1. **设计子任务**：如果写作需要某些设计支持，而这些设计要求没有由**依赖的设计任务**或**已完成的小说内容**提供，则需要规划设计子任务。

2. **写作子任务**：如果长度等于或小于500字，则无需进一步规划额外的写作子任务。

如果需要创建设计子任务或写作子任务，则该任务被视为复杂任务。

# 输出格式
1. 首先，在 `<think></think>` 中，按照原子任务确定规则，按顺序评估是否需要分解设计或写作子任务。这将确定任务是原子任务还是复杂任务。

2. 然后，在 `<r><atomic_task_determination></atomic_task_determination></r>` 中输出结果。

具体格式如下：
<think>
思考目标更新；然后根据原子任务确定规则进行深入全面的思考。
</think>
<r>
<atomic_task_determination>
atomic/complex
</atomic_task_determination>
</r>
""".strip()

        
        content_template = """
已写的小说内容：
```
{to_run_article}
```

整体计划：
```
{to_run_full_plan}
```

在高层级任务中完成的设计任务的结果：
```
{to_run_outer_graph_dependent}
```

在同层任务中完成的设计任务的结果：
```
{to_run_same_graph_dependent}
```

您需要评估的写作任务：
```
{to_run_task}
```
""".strip()
        super().__init__(system_message, content_template) 