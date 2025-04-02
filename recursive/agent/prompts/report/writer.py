#!/usr/bin/env python3
from recursive.agent.prompts.base import PromptTemplate
from recursive.agent.prompts.base import prompt_register
from datetime import datetime
now = datetime.now()
import json


@prompt_register.register_module()
class ReportWriter(PromptTemplate):
    def __init__(self) -> None:
        system_message = "".strip()
        
        content_template = """
The collaborative report-writing requirement to be completed:  
**{to_run_root_question}**  

It has been decomposed into several parts (writing tasks), as shown below. The `You Need To Write` is the part you should write.
```
{to_run_global_writing_task}
```

Based on the existing report analysis conclusions and the requirements, continue writing the report. You need to continue writing:  
**{to_run_task}**

---
**The existing report analysis conclusions and search results are as follows, you should use it**:s 
```
{to_run_outer_graph_dependent}

{to_run_same_graph_dependent}
```

---
Today is {today_date}. You are a professional report writer collaborating with other authors to complete a professional report as requested by users.

# Requirements:

* Seamless Continuation: Begin writing from where the previous section ends, maintaining the same writing style, vocabulary, and overall tone. Complete your part (section or chapter) naturally without repeating or re-explaining details or information already stated.

* Focus on Existing Analysis and Search Results:
\t* Pay close attention to conclusions and findings from previous analysis and search tasks to guide your writing
\t* Search results are provided in <web_pages_short_summary></<web_pages_short_summary>, and has tagged their source index.
\t* Need to screen and filter search results based on relevance to the question
\t* Attention, not all search results are relevant and useful, you should be careful to identify. 
\t* Never hallucination
\t* Do not simply pile up evidence and facts; instead, integrate facts, evidence, and opinions organically, making them part of the narrative and argumentation.

* Data Accuracy and Citation Support:
\t* Cite sources at the end of appropriate sentences using [reference:X] format
\t* If information comes from multiple sources, list all relevant citations, e.g., [reference:3][reference:5]
\t* Citations should appear in the main text, not concentrated at the end

* Report Style and Format:
\t* Logical Clarity: Maintain clear and well-structured writing
\t* Easy to read and comprehense.
\t* Effective Use of Markdown:
\t\t* Tables for structured data
\t\t* Lists for key information
\t\t* Quote blocks for important content
\t\t* Consistent and aesthetic formatting
\t* The connection between writing and content should be as seamless as that of a professional writer, making it easy for readers to understand.

* **Tune**: Keep the tone natural and human-like, making it read as if written by a person rather than AI or a machine. Do not forget use [reference:X]

* Section Format Requirements:
\t* Use meticulously markdown headers (#, ##, ###, etc.) to distinguish chapter/section/subsection levels
\t* Maintain consistent subsection/chapter/section division throughout the report
\t* Add corresponding markdown headers when continuing new chapters/sections
\t* Ensure section titles don't repeat and maintain coherence with previous content
\t* New sections should naturally connect with previous text, avoiding structural gaps
\t* Maintain clarity and logic in section hierarchy

# Output Format Instructions:
First, think in `<think></think>`. Then, please continue writing within the <article></article> tags. Respond in the same language as the user's question. The specific format is as follows:
<think>
Think about the continue writing
</think>
<article>
write here
</article>

---
The already-written report as follows:

already-written report:
```
{to_run_article}
```

--
The Global Sections Plan and the writing task you should continue to write.
```
{to_run_global_writing_task}
```

Based on the requirements as in # Requirements, continue writing **{to_run_task}**. Focus on this writing task. as # Output Format Instructions, first think in <think></think>, then continue writing within the <article></article> tags. The tune should be human-like.
"""
        super().__init__(system_message, content_template)