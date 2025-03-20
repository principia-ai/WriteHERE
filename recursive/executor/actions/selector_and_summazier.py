import requests
import json
import tqdm
from concurrent.futures import ThreadPoolExecutor
import threading
from recursive.llm.llm import OpenAIApiProxy
import time
from recursive.utils.file_io import parse_hierarchy_tags_result
from loguru import logger

VERBOSE=False
# VERBOSE=True  
    
class EvidenceSelectorAPIClientOpenAI:
    def __init__(
        self,
        model,
        max_parralel_requests=10,
        language = "en"
    ):
        """
        Initialize the API client.

        :param url: URL of the API server
        """
        self.model = model
        self.language = language
        assert language in ("zh", "en")
        # self.llm = OpenAIApiProxy(verbose=False)
        self.llm = OpenAIApiProxy(verbose=VERBOSE)
        self.max_parralel_requests = max_parralel_requests
        self.en_sys_pe = "You are an intelligent assistant specializing in information retrieval, equipped with powerful text analysis and logical reasoning abilities."
        
        self.zh_sys_pe = (
            "您是一位专注于信息检索的智能助手，具备强大的文本分析和逻辑推理能力。"
        )
        self.en_prompt = """
The Agent is solving user problems through multiple rounds of searches. You will evaluate **the results of one search round**. You will be provided with the Agent's thinking, judgment, and purpose for initiating this round of search, as well as a webpage obtained from this search round.

Your task includes the following steps:
1. Analyze the webpage:
    - Carefully examine every sentence in the webpage
    - Based on your knowledge, carefully reason about possible connections between the webpage and the purpose of this search round.
2. Determine whether the webpage content can fulfill the purpose of this search round, categorizing it as "rich and fully satisfy", "fully satisfy", "partially satisfy", or "not satisfy"
Please first think in <think></think>, then make your judgment in <answer></answer>, as follows:
<think>
thinking
</think>
<answer>
rich and fully satisfy/fully satisfy/partially satisfy/not satisfy
</answer>

--
The thinking for initiating this search round is: **{to_run_think}**

--
Here is the webpage content:
{passage}

Make your judgment and output according to the requirements, determining whether the webpage content can fulfill the purpose of this search round
"""
        self.zh_prompt = """
Agent正在通过多轮的搜索解决用户问题，你将对**其中一轮搜索的结果**进行评估。会提供给你Agent发起该轮搜索的思考、判断和目的，以及该轮搜索得到的一条网页。

您的任务包括以下步骤：
1. 分析网页：
    - 仔细检查网页中的每一句话
    - 根据你的知识，认真推理网页与该轮搜索的目的之间的可能联系。
2. 判断网页内容能否满足该轮搜索目的，判定属于“非常丰富且完全满足”， “完全满足”，或“部分满足”，或“不满足”
请首先在<think></think>中进行思考，然后在<answer></answer>中进行判断，如下：
<think>
思考
</think>
<answer>
非常丰富且完全满足/完全满足/部分满足/不满足
</answer>

--
发起该轮搜索的思考为：**{to_run_think}**

--
以下是网页内容：
{passage}

按照要求进行判断和输出，判断网页内容能否满足该轮搜索目的
""".strip()

    # def predict_with_cache(self, *args, **kwargs):
    #     return es_cache.call_with_cache(self.predict, *args, **kwargs)

    def predict(self, page, temperature=0.01, max_new_tokens=10, do_sample=False):

        # 发送 POST 请求
        cnt = 0
        cnt2 = 0
        while cnt2 < 5:
            try:
                msg = [
                    {"role": "system", "content": self.zh_sys_pe if self.language == "zh" else self.en_sys_pe},
                    {"role": "user", "content": page["to_run_prompt"]},
                    
                ]
                response = self.llm.call(messages=msg, model=self.model, overwrite_cache = (cnt > 0 or cnt2 > 0))
                if response is None:
                    page["select_response"] = ""
                    page["judgement"] =  0
                    return page
                
                judgement = parse_hierarchy_tags_result(response[0]["message"]["content"],
                                                        ["answer"])
                
                score = 0
                # print(judgement)
                if "非常丰富" in judgement or "rich and fully satisfy" in judgement.lower():
                    score = 3
                elif "完全满足" in judgement or "fully satisfy" in judgement.lower():
                    score = 2
                elif "部分满足" in judgement or "partially satisfy" in judgement.lower():
                    score = 1
                elif "不满足" in judgement or "not satisfy" in judgement.lower():
                    score = 0
                else:
                    raise Exception(f"模型未能给出纳排的判断结果：[{response}]\n The Message is :\n{msg}")
                page["select_response"] = response[0]["message"]["content"]
                page["judgement"] = score
                return page
            
            except requests.exceptions.RequestException as e:
                cnt += 1
                print(f"请求失败: {e}, 重试 {cnt} 次 ...")
                time.sleep(1)
            except Exception as e:
                cnt2 += 1
                print("Failed: {}".format(e), flush=True)
                
                

    def compute_score(
        self, web_pages, question, think, batch_size=30, max_length=None, normalize=False
    ):
        """
        sentences_pairs=[[query,title],[query1,title1],...]
        """
        if batch_size > self.max_parralel_requests:
            batch_size = self.max_parralel_requests
            
        for page in web_pages:
            if self.language == "en":
                page["to_run_prompt"] = self.en_prompt.format(query=question, passage=format_web_page(page), to_run_think=think)
            else:
                page["to_run_prompt"] = self.zh_prompt.format(query=question, passage=format_web_page(page), to_run_think=think)
                
        
        # document_scores = [self.predict(input) for input in inputs]
        with ThreadPoolExecutor(
            max_workers=batch_size,
            thread_name_prefix=f"pid={threading.get_ident()}_evidence_selector",
        ) as executor:
            # exe_map = executor.map(self.predict_with_cache, inputs)
            judged_web_pages = executor.map(self.predict, web_pages)
            judged_web_pages = list(judged_web_pages)
        for web_page in judged_web_pages:
            if "to_run_prompt" in web_page:
                del web_page["to_run_prompt"]
        return judged_web_pages
    
 
class Summarizier:
    def __init__(
        self,
        model,
        max_parralel_requests=10,
        language = "en",
    ):
        """
        Initialize the API client.

        :param url: URL of the API server
        """
        self.language = language
        assert language in ("zh", "en")
        self.llm = OpenAIApiProxy(verbose=VERBOSE)
        self.max_parralel_requests = max_parralel_requests
        self.model = model
        
        self.en_sys_pe = """
You are an expert in web search and information understanding. The Agent is solving the user's problem through multiple rounds of searching. You will be provided with a search result, and you need to thoroughly and comprehensively organize/extract content from the result that is relevant to both the **user's original question** and the **purpose of this round of search**. The content you organize and extract will replace the original webpage content and will be used by the Agent to answer the user's question and conduct subsequent searches. Therefore, you must ensure **accuracy** and **completeness**.

- Do not omit any relavant information, Do not omit details from important content.  
- **Specify details, subjects, and qualifying conditions as much as possible to prevent your summarized content from being taken out of context**
- Relevant content may not exist on the webpage; do not fabricate any nonexistent information.  
- Focus on finding and completely organizing relevant information from the webpage.  
- Only organize and extract content; do not provide suggestions for the next search. Any content with relevance or indicative value can also be organized.  
- If there is absolutely no relevant content, output "no content"  
- Pay attention to the timeliness of the content and clearly identify the described entities to avoid misunderstandings.  

Output format:  
Please first provide a brief analysis within `<think></think>`, then organize and extract content within `<content></content>`, as follows:

```
<think>
Your analysis
</think>
<content>
Specific content
</content>
```
""".strip()


        self.en_prompt = """
The user's original question is: **{to_run_question}**

The thought behind initiating this round of search (you need to understand the purpose of this round of search) is: **{to_run_think}**

--
The following is the webpage content:  
{passage}

Organize and extract as required, focusing solely on the webpage content itself. Do not provide suggestions, follow the instructions I told you before, briefly think in <think></think>, and give the summary in <content></content>.
""".strip()
        
        self.zh_sys_pe = """
你是网页搜索和信息理解专家，Agent正在通过多轮的搜索解决用户问题，你将被给到一条搜索结果，你需要对该条搜索结果的内容，完整且详尽地整理/抽取出与**用户原始问题**，以及**该轮搜索目的**相关的内容。你所整理和抽取的内容将替代原始网页内容提供给Agent用于回答用户问题和进行之后的搜索，因此需要保证 **正确性** 和 **完整性**。

- 不要遗漏任何信息
- 网页中很可能并不存在相关内容，不要虚构任何不存在的内容
- 专注于在网页中找到相关的信息，并完整地进行整理
- 只要做内容整理和抽取，不要给出下一步搜索建议，有任何存在相关性或提示性的内容也可以进行整理
- 若完全无相关内容，直接输出 无内容
- 注意内容的时效性，并需要清晰指出描述的实体防止误解。


输出格式：
请首先在<think></think>中进行简要的思考，然后在<content></content>中进行整理和内容抽取，具体如下：
<think>
思考
</think>
<content>
具体内容
</content>
""".strip()
        
        
        self.zh_prompt = """
用户原始问题为：**{to_run_question}**

发起该轮搜索的思考为（你需要理解该轮搜索的目的）：**{to_run_think}**

--
以下是网页内容：
{passage}

按照要求进行整理和抽取，关注于网页内容本身，不要给出建议：
""".strip()

    # def predict_with_cache(self, *args, **kwargs):
    #     return es_cache.call_with_cache(self.predict, *args, **kwargs)

    def predict(self, page, temperature=0.01, max_new_tokens=10, do_sample=False):

        # 发送 POST 请求
        cnt = 0
        while True:
            try:
                msg = [
                    {"role": "system", "content": self.en_sys_pe if self.language == "en" else self.zh_sys_pe},
                    {"role": "user", "content": page["to_run_prompt"]},
                ]
                response = self.llm.call(messages=msg, model=self.model, overwrite_cache=(cnt > 0))
                
                if response is None:
                    page["summarizier_response"] = ""
                    page["summary"] = ""
                
                summary = parse_hierarchy_tags_result(response[0]["message"]["content"],
                                                        ["content"])
                page["summarizier_response"] = response[0]["message"]["content"]
                page["summary"] = summary
                return page
            
            except requests.exceptions.RequestException as e:
                cnt += 1
                print(f"请求失败: {e}, 重试 {cnt} 次 ...")
                time.sleep(1)

    def summarize(
        self, web_pages, question, think, batch_size=30, max_length=None, normalize=False
    ):
        """
        sentences_pairs=[[query,title],[query1,title1],...]
        """
        if batch_size > self.max_parralel_requests:
            batch_size = self.max_parralel_requests
            
        for page in web_pages:
            if self.language == "zh":
                page["to_run_prompt"] = self.zh_prompt.format(
                    to_run_question=question, 
                    passage=format_web_page(page), 
                    to_run_think=think)
            else:
                page["to_run_prompt"] = self.en_prompt.format(
                    to_run_question=question, 
                    passage=format_web_page(page), 
                    to_run_think=think)
        
        # document_scores = [self.predict(input) for input in inputs]
        with ThreadPoolExecutor(
            max_workers=batch_size,
            thread_name_prefix=f"pid={threading.get_ident()}_evidence_summarizer",
        ) as executor:
            # exe_map = executor.map(self.predict_with_cache, inputs)
            summarizied_web_pages = executor.map(self.predict, web_pages)
            summarizied_web_pages = list(summarizied_web_pages)
        for web_page in summarizied_web_pages:
            if "to_run_prompt" in web_page:
                del web_page["to_run_prompt"]
                
        summarizied_web_pages = [page for page in summarizied_web_pages if (page["summary"].strip().lower() not in ("无内容", "“无内容”", "无内容。", "无内容，", "无", "无。", "no content", "no content."))]
                
        return summarizied_web_pages


def format_web_page(page):
    format_template = """
<title>
{title}
</title>
<url>
{url}
</url>
<publish_time>
{publish_time}
</publish_time>
<content>
{content}
</content>
""".strip()
    return format_template.format(
        title=page["title"],
        url=page["url"],
        publish_time=page["publish_time"],
        content=page["content"]
    )


def selector(web_pages, question, think, N, query_list, language, max_workers, model):    
    web_pages = EvidenceSelectorAPIClientOpenAI(max_parralel_requests=max_workers, language = language, model=model).compute_score(web_pages, question, think, batch_size=max_workers)
    logger.info(
        "Get {} web_pages to select, the result is {}".format(
            len(web_pages), ", ".join(map(str, [page["judgement"] for page in web_pages]))
        )
    )
    web_pages = [page for page in web_pages if page["judgement"] != 0]
    web_pages = sorted(web_pages, key=lambda x: (x["judgement"], -x["pk_index"]), reverse=True)
    

    # select_web_pages = []
    web_page_group_by_query = {q: [] for q in query_list}
    for page in web_pages:
        web_page_group_by_query[page["search_query"]].append(page)
    selected_pages = []
    cursors = {query: 0 for query in query_list}
    
    while len(selected_pages) < N:
        find = False
        for query in query_list:
            index = cursors[query]
            if index >= len(web_page_group_by_query.get(query, [])):
                continue
            find = True
            page = web_page_group_by_query[query][index]
            cursors[query] += 1
            selected_pages.append(page)
        if not find: break
    
    from collections import Counter
    logger.info("After Sort, the Left Result is {}; Each Query Stat: {}".format(
        ", ".join(["{}: {}".format(page["pk_index"], page["judgement"]) for page in web_pages]),
        Counter([page["search_query"] for page in selected_pages]).most_common(1000))
    )
    return selected_pages
    
    

def summarizier(web_pages, question, think, language, max_workers, model):
    web_pages = Summarizier(max_parralel_requests=max_workers, language = language, model=model).summarize(web_pages, question, think, batch_size=max_workers)
    return web_pages
    
    
    
    
if __name__ == "__main__":
    web_page = {
        "title": "姚明是几年出生的 - 百度知道",
        "url": "https://zhidao.baidu.com/question/28268647.html",
        "publish_time": "未提供",
        "content": "1980年9月12日，姚明出生于上海市第六医院。 他的父母都是篮球运动员，父亲姚志源身高2.08米，曾效力于上海男篮；母亲方凤娣身高1.88米，是70年代中国女篮的主力队员。1980年NBA亚军队伍教练是Charlie Altman",
        "pk_index": 1
    }
    web_page = {
        "title": "姚明是几年出生的 - 百度知道",
        "url": "https://zhidao.baidu.com/question/28268647.html",
        "publish_time": "未提供",
        "content": "姚明出生于上海市第六医院。 他的父母都是篮球运动员，父亲姚志源身高2.08米，曾效力于上海男篮；母亲方凤娣身高1.88米，是70年代中国女篮的主力队员。该年NBA亚军队伍教练是Charlie Altman",
        "pk_index": 1
    }
    
    think1 = """
<planning_and_think>首先需要获取姚明的出生年份，然后根据该年份确定当年NBA亚军的教练是谁。初始步骤可以分为两个主要搜索维度：1. 姚明的出生年份；2. 对应年份的NBA亚军教练。</planning_and_think>
<search_query_think>生成两个初始搜索词，一个用于查找姚明的出生年份，另一个用于查找对应年份的NBA亚军教练信息。</search_query_think>""".strip()

    think2 = """
<planning_and_think>
要回答这个问题，我需要找到姚明的出生年份，然后查找相应年份NBA总决赛亚军球队的教练。因此，我需要将问题拆解为以下几个核心步骤：
1. 找到姚明的出生年份。
2. 找到该年份NBA总决赛的亚军球队。
3. 找到该亚军球队的教练名字。

这将是一个两步搜索策略：首先找到姚明的出生年份，然后查找该年份的NBA亚军及其教练。
</planning_and_think>

<search_query_think>
首先需要确认姚明的出生年份，因此初始搜索词将围绕姚明的出生信息。
</search_query_think>
""".strip()
    summarizier(
        [web_page], "姚明出生那年NBA亚军教练是谁？", think2    
    )
    