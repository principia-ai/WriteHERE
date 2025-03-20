#!/usr/bin/env python3
from recursive.agent.prompts.base import PromptTemplate
from recursive.agent.prompts.base import prompt_register
from datetime import datetime

now = datetime.now()

@prompt_register.register_module()
class StoryWritingReasonerFinalAggregateZH(PromptTemplate):
    def __init__(self) -> None:
        system_message = """
你是一位专业且富有创意的小说评价者，正在与其他小说专家合作评估一部新完成的小说。

你的任务是仔细评估提供的小说，并提供专业分析和改进建议。你的反馈将帮助作者改进作品。

### 评估维度：
1. **总体质量和文学价值**
2. **情节和结构**
3. **人物塑造**
4. **世界建构和背景设定**
5. **语言风格和写作技巧**
6. **主题和思想深度**
7. **读者体验和情感共鸣**
8. **原创性和创新点**

### 输出格式：
提供你的评价，包含以下部分：
1. **总体评价**：总结小说的总体质量、优点和不足
2. **详细分析**：按以上评估维度提供具体分析
3. **改进建议**：为每一维度提供针对性的改进建议
4. **结论**：最终评价和对作品潜力的看法

使用`<article_evaluation></article_evaluation>`标签包裹你的评价。
""".strip()

        content_template = """
请评价以下小说：

## 原始用户需求：
{to_run_root_question}

## 小说内容：
```
{to_run_article}
```

请提供你的专业评价。
""".strip()
        super().__init__(system_message, content_template)