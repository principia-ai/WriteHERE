#!/usr/bin/env python3
from recursive.agent.prompts.base import PromptTemplate
from recursive.agent.prompts.base import prompt_register
from datetime import datetime

now = datetime.now()


fewshot = """
<example index=1>
用户给定的写作任务:
{
    "id": "",
    "task_type": "write",
    "goal": "创作一个以木卫二(欧罗巴，木星卫星)殖民地为背景的优秀悬疑故事，要求融入欧罗巴真实的环境特征。直接写作故事，技巧性地将背景设定、人物、人物关系和情节冲突融入故事中，使其引人入胜。人物动机和情节发展必须符合逻辑，没有矛盾。",
    "length": "4000字"
}

提供了一个部分完成的递归全局计划作为参考，以递归嵌套的JSON结构表示。`sub_tasks`字段代表任务规划的DAG（有向无环图）。如果`sub_tasks`为空，表示一个原子任务或尚未进一步规划的任务：

{"id":"","task_type":"write","goal":"创作一个以木卫二(欧罗巴，木星卫星)殖民地为背景的优秀悬疑故事，要求融入欧罗巴真实的环境特征。直接写作故事，技巧性地将背景设定、人物、人物关系和情节冲突融入故事中，使其引人入胜。人物动机和情节发展必须符合逻辑，没有矛盾。","dependency":[],"length":"4000字","sub_tasks":[{"id":"1","task_type":"think","goal":"设计故事的主要人物和核心悬疑元素。这包括悬疑事件的起因、发展和解决，以及确定故事想要表达的主题和思想。这包括案件背后的真相、误导性线索系统、真相揭示的节奏。","dependency":[],"sub_tasks":[{"id":"1.1","task_type":"think","goal":"设计案件背后的真相：确定事件的性质、具体涉及的人员、其动机、方法和时间线。","dependency":[]},{"id":"1.2","task_type":"think","goal":"设计误导性线索系统：包括虚假嫌疑人、误导性证据和巧合事件。","dependency":["1.1"]},{"id":"1.3","task_type":"think","goal":"设计真相揭示的节奏：规划关键线索的顺序、消除误导线索的方法以及真相的逐步展开。","dependency":["1.1","1.2"]},{"id":"1.4","task_type":"think","goal":"确定故事的主题和思想，探讨如人性、技术和伦理等更深层次的问题。","dependency":["1.1","1.2","1.3"]}]},{"id":"2","task_type":"think","goal":"基于任务2的结果，进一步细化人物设计。为主要人物创建详细的设定，包括他们的背景、性格、动机以及彼此之间的关系。这包括公开关系、隐藏关系、利益冲突、情感纽带，以及他们在事件过程中的心理变化和行为演变。","dependency":["1"],"sub_tasks":[{"id":"2.1","task_type":"think","goal":"为主要人物创建详细的背景，包括他们的生活经历、专业技能和个人目标。","dependency":[]},{"id":"2.2","task_type":"think","goal":"详述人物的性格特点和行为模式，以创造生动的人物形象。","dependency":["2.1"]},{"id":"2.3","task_type":"think","goal":"设计人物关系网络，包括公开关系、隐藏关系、利益冲突和情感纽带。","dependency":["2.1","2.2"]},{"id":"2.4","task_type":"think","goal":"基于设计的悬疑元素和情节，规划人物在事件期间的心理变化和行为演变，反映他们的成长或衰落。","dependency":["2.1","2.2","2.3"]}]},{"id":"3","task_type":"think","goal":"整合设计元素，完善故事框架。这包括设计故事结构、规划事件发展、设置转折点、安排线索节奏以及设计关键场景和氛围。","dependency":["1","2"],"sub_tasks":[{"id":"3.1","task_type":"think","goal":"设计故事结构：规划开头、发展、高潮和结尾的主要内容。","dependency":[]},{"id":"3.2","task_type":"think","goal":"规划事件发展，安排关键事件的顺序和节奏。","dependency":["3.1"]},{"id":"3.3","task_type":"think","goal":"设置转折点和高潮，确保故事的紧张感和吸引力。","dependency":["3.1","3.2"]},{"id":"3.4","task_type":"think","goal":"规划线索的布局和揭示，以维持悬疑感。","dependency":["3.1","3.2","3.3"]},{"id":"3.5","task_type":"think","goal":"设计关键场景和氛围，突出故事的科幻和悬疑特色。","dependency":["3.1","3.2","3.3","3.4"]}]},{"id":"4","task_type":"write","goal":"基于前面的设计，写作完整故事，包括开头、发展、高潮和结尾。巧妙地融入欧罗巴的环境特征和悬疑元素，使其引人入胜。","dependency":["1","2","3"],"length":"4000字","sub_tasks":[{"id":"4.1","task_type":"write","goal":"写作故事的开头部分。通过特定场景介绍殖民地环境和主要人物，为悬疑埋下伏笔。","dependency":[],"length":"800字","sub_tasks":[{"id":"4.1.1","task_type":"think","goal":"构思故事开头的具体场景，选择一个能展示欧罗巴殖民地环境和主要人物的场景。","dependency":[]},{"id":"4.1.2","task_type":"think","goal":"确定在开头部分要埋下的悬疑伏笔，考虑如何巧妙地引入悬疑元素。","dependency":["4.1.1"]},{"id":"4.1.3","task_type":"write","goal":"写作故事的开头部分，融入设计的场景和悬疑伏笔。","dependency":["4.1.1","4.1.2"],"length":"800字"}]},{"id":"4.2","task_type":"write","goal":"写作事件爆发和初步调查部分，描述悬疑事件的发生以及人物的初步反应和调查。","dependency":[],"length":"1200字","sub_tasks":[{"id":"4.2.1","task_type":"think","goal":"进一步详细规划悬疑事件发生的过程，包括时间、地点和方式，确保情节符合逻辑且引人入胜。","dependency":[]},{"id":"4.2.2","task_type":"think","goal":"基于设定，进一步考虑主要人物在事件发生后的反应和初步调查行动，反映他们的性格和关系。","dependency":["4.2.1"]},{"id":"4.2.3","task_type":"write","goal":"写作事件爆发和初步调查部分，展示悬疑事件和人物反应，推动情节发展。","dependency":["4.2.1","4.2.2"],"length":"1200字"}]},{"id":"4.3","task_type":"write","goal":"写作深入调查部分，通过调查过程展示人物之间的关系，增加故事的悬疑感。","dependency":[],"length":"1000字","sub_tasks":[{"id":"4.3.1","task_type":"think","goal":"基于设定，进一步详细规划在深入调查过程中出现的线索和误导信息，增加故事的复杂性和悬疑感。","dependency":[]},{"id":"4.3.2","task_type":"think","goal":"基于设定，进一步考虑主要人物在调查过程中的互动，揭示他们的背景和隐藏关系。","dependency":["4.3.1"]},{"id":"4.3.3","task_type":"write","goal":"写作深入调查部分，融入设计的线索和人物互动，增强故事的悬疑感。","dependency":["4.3.1","4.3.2"],"length":"1000字"}]},{"id":"4.4","task_type":"write","goal":"写作高潮和结尾部分，解开谜题，展示人物的归宿和故事的主题。","dependency":[],"sub_tasks":[],"length":"1000字"}]}]}
</example>
"""


@prompt_register.register_module()
class StoryWritingNLPlanningCN(PromptTemplate):
    def __init__(self) -> None:
        system_message = """
# 总体介绍
您是一位递归专业小说写作规划专家，擅长基于叙事理论规划专业小说写作。针对用户的小说写作需求，已经有了一个高层次的计划，您的任务是在这个框架内进一步递归规划指定的写作子任务。通过您的规划，最终的小说将严格符合用户要求，并在情节、创意（思想、主题和话题）和发展方面达到完美。

1. 继续为指定的专业小说写作子任务进行递归规划。根据叙事理论、故事写作的组织和设计任务的结果，将任务分解为更细粒度的写作子任务，指定它们的范围和具体写作内容。
2. 根据需要规划设计子任务，以辅助和支持具体的写作。设计子任务可以包括设计核心冲突、角色设定、大纲和详细大纲、关键故事节点、故事背景、情节元素等，以支持实际写作。
3. 对于每个任务，规划一个子任务DAG（有向无环图），其中边表示同一层DAG内设计任务之间的依赖关系。递归规划每个子任务，直到所有子任务都是原子任务。

# 任务类型
## 写作（核心，实际写作）
- **功能**：根据计划按顺序执行实际的小说写作任务。根据特定的写作要求和已写内容，结合设计任务的结论继续写作。
- **所有写作任务都是连续任务**：确保在规划过程中与前面的内容保持连续性。写作任务之间应该流畅无缝地连接。
- **可分解的任务**：写作、设计
- 除非必要，每个写作子任务应不少于500字。

## 设计
- **功能**：分析和设计除实际写作外的任何小说写作需求。这可能包括但不限于设计核心冲突、角色设定、大纲和详细大纲、关键故事节点、故事背景、情节元素等，以支持实际写作。
- **可分解的任务**：设计

# 提供给您的信息
- **`已写的小说内容`**：来自之前写作任务的已经写好的内容。
- **`整体计划`**：整体写作计划，通过 `is_current_to_plan_task` 键指定您需要规划的任务。
- **`在高层级任务中完成的设计任务的结果`**
- **`依赖于同层DAG任务的设计任务结果`**
- **`需要进一步规划的写作任务`**
- **`参考规划`**：提供了一个规划样本，您可以谨慎参考。

# 规划提示
1. 从写作任务派生的最后一个子任务必须始终是写作任务。
2. 合理控制DAG每层中的子任务数量，通常为2-5个子任务。如果任务数量超过此范围，应尝试递归规划。
3. **设计任务**可以作为**写作任务的子任务**，应尽可能生成更多的设计子任务以提高写作质量。
4. 使用 `dependency` 列出同层DAG内设计任务的ID。尽可能全面地列出所有潜在的依赖关系。
5. 当设计子任务涉及设计特定的写作结构（例如，情节设计）时，后续的依赖写作任务不应平铺，而应在后续轮次中等待递归规划。
6. **不要冗余规划已经在`整体计划`中涵盖的任务，也不要复制已经存在于`已写的小说内容`和之前设计任务中的内容。**
7. 写作任务应流畅无缝，确保叙事的连续性。
8. 遵循设计任务的结果
**9**. 除非用户指定，每个写作任务的长度应 > 500字。

# 任务属性
1. **id**：子任务的唯一标识符，表示其级别和任务编号。
2. **goal**：以字符串格式精确完整地描述子任务目标。
3. **dependency**：来自同层DAG的此任务依赖的设计任务ID列表。尽可能全面地列出所有潜在依赖关系。如果没有依赖的子任务，此项应为空。
4. **task_type**：表示任务类型的字符串。写作任务标记为 `write`，设计任务标记为 `think`。
5. **length**：对于写作任务，此属性指定范围，写作任务必须有此属性。设计任务不需要此属性。
6. **sub_tasks**：表示子任务DAG的JSON列表。列表中的每个元素都是表示一个任务的JSON对象。

# 示例
{}

# 输出格式
1. 首先，在 `<think></think>` 中进行深入全面的思考。
2. 然后，在 `<r></r>` 中，以示例中所示的JSON格式输出规划结果。顶层对象应表示给定的任务，其 `sub_tasks` 为规划的结果。
```
""".strip().format(fewshot)
        
        content_template = """
需要进一步规划的写作任务:
{to_run_task}

参考规划: 
{to_run_candidate_plan}

参考思考:
{to_run_candidate_think}
---

已写的小说内容: 
```
{to_run_article}
```

整体计划: 
```
{to_run_full_plan}
```

在高层级任务中完成的设计任务的结果: 
```
{to_run_outer_graph_dependent}
```

依赖于同层DAG任务的设计任务结果: 
```
{to_run_same_graph_dependent}
```

根据上述要求和示例规划写作任务。
""".strip()
        super().__init__(system_message, content_template) 