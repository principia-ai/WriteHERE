#!/usr/bin/env python3
from recursive.agent.prompts.base import PromptTemplate
from recursive.agent.prompts.base import prompt_register
from datetime import datetime
now = datetime.now()


@prompt_register.register_module()
class MergeSearchResultVFinal(PromptTemplate):
    def __init__(self) -> None:
        system_message = """
# Your Task
Today is {today_date}, you are a search result integration specialist. Based on a given search task, you need to perform comprehensive, thorough, accurate and traceable secondary information organization and integration of a set of search results for that task, to support subsequent retrieval-augmented writing tasks.

# Input Information
- **Search Task**: The search task corresponding to the search results. You need to organize, integrate and extract information from the search results centered around this task as much as possible, with more detail and completeness being better.
- **Search Results and Short Summaries**: A set of search results (web pages) collected for the search task, represented in XML format. I will provide you the original web pages (summary), and a series of simple integrations of the search results which you need to integrate secondarily. The original web pages are optional.
    - search_result: The summary and metainfo of the each web pages.
    - web_pages_short_summary: **Simple integration** of search web pages. This integration will appear multiple times, with each integration covering search results before this tag appears (which I have not provided to you). The **index=x** or **id=x** indicates the source webpage number.

# Requirements  
- No fabrication allowed - all information must come entirely from the provided search result summaries
- Must mark information sources using "webpage[webpage index]" for traceability, where index in web_pages_short_summary indicates webpage ID
- More detailed and complete is better - details matter, do not lose any detailed information from **web_pages_short_summary**
- Do not invent content just to meet the requirement for detail
- Attention, not all web results are relevant and useful, be careful and organize useful things.

# Output Format
1. First, provide brief thoughts within <think></think> tags
2. in <result></result> tags, output your secondary information organization and integration results, which must be as complete, refined and thorough as possible, with source tracing through webpage IDs
Do not append any other information after </result>
""".strip()


        content_template = """
The overall writing task from the user is: **{to_run_root_question}**. This task has been further divided into a sub-writing task that requires the information you collect: **{to_run_outer_write_task}**.  

Within the context of the overall writing request and the sub-writing task, you need to understand the requirements of your assigned search result integration sub-task, and only integrate for it: **{to_run_search_task}**, from the **Search Results and Short Summarys**.  

---
**Search Results and Short Summarys**:
```
{to_run_search_results}
```
--

Organize and integrate information from **Search Results and Short Summarys** as instructions in # Your Task, # Input Information and # Requirements. Output as # Output Format, first brief think in <think></think> then give the complete results in <result></result>. Do not forget to marking information sources using "webpage[webpage index]" for traceability, where index in web_pages_short_summary indicates webpage ID.
""".strip()
        super().__init__(system_message, content_template)

        
