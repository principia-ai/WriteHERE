#!/usr/bin/env python3
from recursive.agent.prompts.base import PromptTemplate
from recursive.agent.prompts.base import prompt_register
from datetime import datetime
now = datetime.now()
import json

@prompt_register.register_module()
class StoryWrtingNLWriterCN(PromptTemplate):
    def __init__(self) -> None:
        system_message = """
您是一位专业且富有创新性的作家，正在与其他作家合作创作一部用户要求的小说。

### 要求：
- 从故事的前一部分结尾开始，匹配现有文本的写作风格、词汇和整体氛围。根据写作要求自然地完成您的部分，不要重新诠释或重新描述已经涵盖的细节或事件。
- 密切关注现有的小说设计结论。
- 尽可能使用多种修辞、语言和文学手法（例如，模糊性、头韵等）来创造吸引人的效果。
- 避免平淡或重复的短语（除非有意使用以创造叙事、主题或语言效果）。
- 使用多样化和丰富的语言：变化句式结构、词汇选择和用词。
- 除非绝对必要，否则避免总结性、解释性或说明性的内容或句子。
- 注重对话和描述，尽量减少叙述。
- 确保情节或描述中没有断层或突兀感。您可以写一些过渡性内容以保持与现有材料的完整连续性。

### 指示：
首先，在 `<think></think>` 中思考任务。然后，在 `<article></article>` 中继续故事。
""".strip()

        
        content_template = """
需要完成的协作小说创作需求：  
**{to_run_root_question}**  

根据现有的小说设计结论和要求，继续编写故事。您需要继续写作：  
**{to_run_task}**

---
以下是现有的小说设计结论，您应当遵守：  
```
{to_run_outer_graph_dependent}

{to_run_same_graph_dependent}
```

---
已经写好的小说内容：
```
{to_run_article}
```

根据要求，继续编写 **{to_run_task}**。
"""
        super().__init__(system_message, content_template) 