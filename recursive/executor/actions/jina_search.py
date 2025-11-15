#!/usr/bin/env python3
"""
Jina.ai Search Integration for WriteHERE

This module provides search functionality using Jina.ai's Search API and Reader API.
Jina.ai offers:
- Search API: Web search with clean, structured results
- Reader API: Extract clean content from web pages
"""

import json
import logging
import os
import warnings
from typing import List, Optional
import requests
from loguru import logger
from dotenv import load_dotenv

from recursive.executor.actions import BaseAction, tool_api
from recursive.executor.actions.parser import BaseParser, JsonParser
from recursive.executor.actions.register import tool_register
from recursive.executor.actions.selector_and_summazier import selector, summarizier
from recursive.memory import caches

load_dotenv(dotenv_path='api_key.env')


class JinaSearch:
    """
    Jina.ai Search Client

    Uses Jina.ai's Search API to perform web searches and Reader API to extract content.
    """

    def __init__(
        self,
        jina_api_key: str = None,
        topk: int = 20,
        is_valid_source=None,
        min_char_count: int = 150,
        **kwargs
    ):
        """
        Initialize Jina Search client.

        Args:
            jina_api_key: Jina.ai API key (if None, will use JINA_API_KEY from env)
            topk: Number of search results to return
            is_valid_source: Function to validate URLs
            min_char_count: Minimum character count for valid content
            **kwargs: Additional parameters
        """
        self.jina_api_key = jina_api_key or str(os.getenv('JINA_API_KEY', ''))
        self.topk = topk
        self.is_valid_source = is_valid_source if is_valid_source else lambda x: True
        self.min_char_count = min_char_count
        self.usage = 0

        # Jina.ai API endpoints
        self.search_endpoint = "https://s.jina.ai/"
        self.reader_endpoint = "https://r.jina.ai/"

        if not self.jina_api_key:
            logger.warning(
                "JINA_API_KEY not found in environment variables. "
                "Jina.ai search may not work properly without authentication."
            )

    def get_usage_and_reset(self):
        """Get usage statistics and reset counter."""
        usage = self.usage
        self.usage = 0
        return {"JinaSearch": usage}

    def search(self, query: str, exclude_urls: List[str] = [], overwrite_cache: bool = False) -> dict:
        """
        Perform a web search using Jina.ai Search API.

        Args:
            query: Search query string
            exclude_urls: List of URLs to exclude from results
            overwrite_cache: Whether to overwrite cache

        Returns:
            Dictionary of search results with position as key
        """
        search_cache = caches["search"]
        cache_name = "JinaSearch"
        call_args_dict = {
            "query": query,
            "topk": self.topk,
            "exclude_urls": exclude_urls
        }

        # Check cache first
        url_to_results = {}
        if search_cache is not None and not overwrite_cache:
            cache_result = search_cache.get_cache(
                name=cache_name,
                call_args_dict=call_args_dict
            )
            if cache_result is not None:
                logger.info(f"Cache hit for query: {query}")
                return cache_result

        # Perform search
        self.usage += 1

        try:
            headers = {
                "Accept": "application/json",
            }

            if self.jina_api_key:
                headers["Authorization"] = f"Bearer {self.jina_api_key}"

            # Jina.ai Search API
            search_url = f"{self.search_endpoint}{query}"

            response = requests.get(
                search_url,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            # Parse Jina search results
            results = []
            if "data" in data:
                for idx, item in enumerate(data["data"], start=1):
                    url = item.get("url", "")

                    # Skip invalid URLs
                    if not url or not self.is_valid_source(url) or url.endswith('.pdf') or url in exclude_urls:
                        continue

                    results.append({
                        "url": url,
                        "title": item.get("title", ""),
                        "description": item.get("description", item.get("content", "")),
                        "position": idx,
                        "publish_time": "Not Provided"
                    })

                    if len(results) >= self.topk:
                        break

        except Exception as e:
            logger.error(f"Error during Jina search for query '{query}': {e}")
            # Return empty results on error
            results = []

        # Convert to position-indexed dict
        pos2results = {i: result for i, result in enumerate(results)}

        # Save to cache
        if search_cache is not None:
            search_cache.save_cache(
                name=cache_name,
                call_args_dict=call_args_dict,
                value=pos2results
            )

        return pos2results

    def fetch_content(self, pages: List[dict]) -> List[dict]:
        """
        Fetch full content for a list of pages using Jina.ai Reader API.

        Args:
            pages: List of page dictionaries with 'url' field

        Returns:
            List of pages with added 'content' field
        """
        fetched_pages = []

        for page in pages:
            url = page["url"]

            try:
                # Use Jina Reader API to get clean content
                headers = {
                    "Accept": "application/json",
                }

                if self.jina_api_key:
                    headers["Authorization"] = f"Bearer {self.jina_api_key}"

                reader_url = f"{self.reader_endpoint}{url}"

                response = requests.get(
                    reader_url,
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()

                data = response.json()

                # Extract content from Jina Reader response
                if "data" in data:
                    content = data["data"].get("content", "")
                    title = data["data"].get("title", page.get("title", ""))

                    if len(content) >= self.min_char_count:
                        # Update page with content
                        page["snippet"] = page.get("description", "")
                        if "description" in page:
                            del page["description"]

                        # Format content
                        long_res = f"Snippet: {page['snippet']}\nContent: {content}"
                        page["content"] = long_res
                        page["title"] = title

                        fetched_pages.append(page)
                    else:
                        logger.warning(f"Content too short for URL: {url} (length: {len(content)})")

                else:
                    logger.warning(f"No data in Jina Reader response for URL: {url}")

            except Exception as e:
                logger.error(f"Error fetching content from {url}: {e}")
                continue

        return fetched_pages


@tool_register.register_module()
class JinaBrowser(BaseAction):
    """
    Jina.ai Web Browser Tool

    Provides web search and content extraction using Jina.ai APIs.
    Compatible with the existing WriteHERE framework.
    """

    def __init__(
        self,
        timeout: int = 5,
        black_list: Optional[List[str]] = None,
        topk: int = 20,
        pk_quota: int = 20,
        select_quota: int = 8,
        description: Optional[dict] = None,
        parser: type[BaseParser] = JsonParser,
        enable: bool = True,
        language: str = "en",
        selector_max_workers: int = 8,
        summarizier_max_workers: int = 8,
        selector_model: str = "gpt-4o-mini",
        summarizer_model: str = "gpt-4o-mini",
        **kwargs
    ):
        """
        Initialize Jina Browser action.

        Args:
            timeout: Request timeout in seconds
            black_list: List of domains to exclude
            topk: Number of search results to fetch
            pk_quota: Maximum number of results to process
            select_quota: Number of results to select after filtering
            description: Tool description for the agent
            parser: Parser class for output
            enable: Whether this tool is enabled
            language: Language for prompts ("en" or "zh")
            selector_max_workers: Max parallel workers for selection
            summarizier_max_workers: Max parallel workers for summarization
            selector_model: Model to use for selection
            summarizer_model: Model to use for summarization
            **kwargs: Additional parameters
        """
        self.select_quota = select_quota
        self.language = language

        # Initialize Jina searcher
        self.searcher = JinaSearch(topk=topk, **kwargs)
        self.search_results = None
        self.pk_quota = pk_quota
        self.selector_max_workers = selector_max_workers
        self.summarizier_max_workers = summarizier_max_workers

        self.selector_model = selector_model
        self.summarizer_model = summarizer_model

        super().__init__(description, parser, enable)

    def __search(self, query_list, search_N):
        """Perform parallel searches for multiple queries."""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        queries = query_list if isinstance(query_list, list) else [query_list]
        query2search_results = {}

        # Search in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_query = {
                executor.submit(self.searcher.search, q): q
                for q in queries
            }
            for future in as_completed(future_to_query):
                query = future_to_query[future]
                try:
                    results = future.result()
                except Exception as exc:
                    import traceback
                    warnings.warn(f'{query} generated an exception: {traceback.print_exc()}')
                else:
                    query2search_results[query] = results

        # Merge and deduplicate results
        N = search_N
        pk_results = []
        dedup_urls = set()
        cursors = {query: 0 for query in queries}

        while len(pk_results) < N:
            find = False
            for query in queries:
                index = cursors[query]
                if index >= len(query2search_results.get(query, {})):
                    continue
                find = True
                page = query2search_results[query][index]
                page["search_query"] = query
                cursors[query] += 1

                if page['url'].endswith(".pdf"):
                    continue
                if page['url'] in dedup_urls:
                    continue

                dedup_urls.add(page['url'])
                pk_results.append(page)
                page["pk_index"] = len(pk_results)

            if not find:
                break

        return pk_results

    def __single_fetch(self, search_results):
        """Fetch content for search results."""
        return self.searcher.fetch_content(search_results)

    def __select_and_summarize(self, search_results, question, think, N, query_list):
        """Select and summarize search results."""
        search_results = selector(
            search_results, question, think, N, query_list,
            self.language, self.selector_max_workers,
            self.selector_model
        )
        search_results = summarizier(
            search_results, question, think,
            self.language, self.summarizier_max_workers,
            self.summarizer_model
        )
        return search_results

    @tool_api()
    def full_pipeline_search(self, query_list, user_question, think, global_start_index):
        """
        Jina Web Browser Search API

        ### Specific Functions
        1. Through this API, you can search multiple search queries in parallel using Jina.ai,
           obtaining summaries of search results corresponding to each query.
        2. The content of search results will only return titles and summaries, not the full text.
           You can retrieve the full text by using this tool.
        3. Unless the summary contains all needed information, you should call this tool to get
           the full text of the search results you need.

        ### Specific Return Content
        1. Returns all search query results in XML format, within <search_results></search_results> tags.
        2. Each search result is in <result></result> tags with an index attribute.
        3. Within a single search result:
            - <title></title>: Search result title
            - <url></url>: URL of the search result
            - <snippet></snippet>: Summary of the search result
            - <publish_time></publish_time>: Webpage publication time

        Args:
            query_list ({"type":"array","items":{"type":"string"}}): Search queries to search in parallel
            user_question ({"type": "string"}): User question
            think ({"type": "string"}): Thinking process
            global_start_index ({"type": "int"}): Starting index

        Returns:
            Dict[str, str]: dict of search results
        """
        search_N = self.pk_quota  # 20
        select_N = max(len(query_list), self.select_quota)  # 8
        search_cache = caches["search"]

        # Load Cache
        cache_name = "JinaBrowser.full_pipeline_search"
        call_args_dict = {
            "search_N": search_N,
            "query_list": query_list,
            "user_question": user_question,
            "think": think,
            "global_start_index": global_start_index,
            "searcher": "JinaSearch",
        }

        cache_result = search_cache.get_cache(
            name=cache_name,
            call_args_dict=call_args_dict
        )
        if cache_result is not None:
            logger.info("Cache hit for full pipeline search")
            return cache_result

        # Search
        pk_search_results = self.__search(query_list, search_N)

        ori_cnt = len(pk_search_results)
        ori_urls = [res["url"] for res in pk_search_results]

        # Fetch web page content
        pk_search_results = self.__single_fetch(pk_search_results)

        logger.info(
            f"Queries {str(query_list)} after pk get {ori_cnt} results, "
            f"fetched {len(pk_search_results)} results, "
            f"succ urls: \n" + "\n".join([res["url"] for res in pk_search_results]) + "\n"
            f"failed urls: \n" + "\n".join(list(set(ori_urls) - set([res["url"] for res in pk_search_results])))
        )

        # Check if we have any valid results
        if not pk_search_results:
            logger.warning("No web_pages found in search results")
            default_result = {
                "web_pages": [],
                "result": "No web pages could be retrieved.",
                "juege_and_summarized_search_results": [],
                "exclude_search_results": []
            }
            search_cache.save_cache(
                name=cache_name,
                call_args_dict=call_args_dict,
                value=default_result
            )
            return default_result

        logger.info("Start Select and Summarize")

        # Select and summarize
        juege_and_summarized_search_results = self.__select_and_summarize(
            pk_search_results, user_question, think, select_N, query_list
        )

        # Format results
        FORMAT_STRING_TEMPLATE = """
<search_result index={index}>
<title>
{title}
</title>
<url>
{url}
</url>
<page_time>
{publish_time}
</page_time>
<summary>
{content}
</summary>
</search_result>
"""

        results = []
        for idx, page in enumerate(juege_and_summarized_search_results, start=global_start_index):
            page["global_index"] = idx
            results.append(FORMAT_STRING_TEMPLATE.format(
                index=idx,
                title=page["title"],
                url=page["url"],
                publish_time=page["publish_time"],
                content=page["summary"]
            ))
        results = "\n\n".join(results)
        select_urls = set([page["url"] for page in juege_and_summarized_search_results])

        search_result = {
            "web_pages": juege_and_summarized_search_results,
            "result": results,
            "juege_and_summarized_search_results": juege_and_summarized_search_results,
            "exclude_search_results": [res for res in pk_search_results if res["url"] not in select_urls]
        }

        # Save cache
        search_cache.save_cache(
            name=cache_name,
            call_args_dict=call_args_dict,
            value=search_result
        )

        return search_result


if __name__ == "__main__":
    # Test Jina Search
    from recursive.cache import Cache
    caches["search"] = Cache("temp/search")
    caches["web_page"] = Cache("temp/web_page")
    caches["llm"] = Cache("temp/llm")

    browser = JinaBrowser(
        pk_quota=20,
        select_quota=4,
        language="en"
    )

    # Test search
    result = browser.full_pipeline_search(
        query_list=["artificial intelligence"],
        user_question="What is artificial intelligence?",
        think="Need to understand the basics of AI",
        global_start_index=0
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))
