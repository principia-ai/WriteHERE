from recursive.utils.file_io import auto_read, auto_write
from collections import defaultdict
import sys

def traverse(data, web_pages):
    if isinstance(data, dict):
        if "global_index" in data:
            for k in ("url", "title", "position"):
                if k not in data:
                    print("error")
                    break
            else:
                web_pages[data["global_index"]] = data
        else:
            for k, v in data.items():
                traverse(v, web_pages)
    elif isinstance(data, list):
        for v in data:
            traverse(v, web_pages)
    
import re
import re
from typing import Dict, List, Tuple

def extract_and_renumber_citations(text: str, citation_urls):
    """
    Extract citation numbers, renumber them sequentially, and update both text and URLs.
    
    Args:
        text (str): Original text with citations
        citation_urls (dict): Original citation ID to URL mapping
        
    Returns:
        tuple: (Updated text, New citation ID to URL mapping)
    """
    # Extract all citation numbers
    pattern = r'\[reference:(\d+)\]'
    citation_numbers = re.findall(pattern, text)
    citation_numbers = [int(n) for n in citation_numbers]
    
    # Get unique URLs while maintaining order of first appearance
    seen_urls = {}  # url -> first citation number that referenced it
    for num in citation_numbers:
        if num in citation_urls:
            url = citation_urls[num]["url"]
            if url not in seen_urls:
                seen_urls[url] = num

    # Create mapping from URL to new citation number
    url_to_new_num = {url: i+1 for i, url in enumerate(seen_urls.keys())}

    # Create old to new number mapping
    old_to_new = {}
    for old_num in citation_numbers:
        if old_num in citation_urls:
            url = citation_urls[old_num]
            old_to_new[old_num] = url_to_new_num[url]

    # Create new URL mapping
    new_citation_urls = {
        new_num: url
        for url, new_num in url_to_new_num.items()
    }
    
    # Replace citations in text and remove consecutive duplicates
    def replace_match(match):
        old_num = match.group(1)
        new_num = old_to_new[old_num]
        return f'[reference:{old_to_new[old_num]}]' if old_num in old_to_new else match.group(0)
    
    # First replace all citations
    updated_text = re.sub(pattern, replace_match, text)
    
    # Then remove consecutive duplicate citations
    pattern_consecutive = r'(\[reference:\d+\])(\1)+'
    while re.search(pattern_consecutive, updated_text):
        updated_text = re.sub(pattern_consecutive, r'\1', updated_text)
    
    return updated_text, new_citation_urls

def process_citations(text, citation_to_url):
    # 步骤1: 找出文章中所有引用
    citation_pattern = r'\[(?:reference|ref):(\d+)\]'
    citations_in_text = re.findall(citation_pattern, text)
    used_ids = [int(cid) for cid in citations_in_text]
    # Find positions using regex to match both formats
    old2id_2_pos = {}
    for idx in used_ids:
        matches = list(re.finditer(r'\[(?:reference|ref):{}]'.format(idx), text))
        if matches:
            old2id_2_pos[idx] = matches[0].start()
    # old2id_2_pos = {idx: text.index("[reference:{}]".format(idx)) for idx in used_ids}
    url2page = {page["url"]: page  for page in citation_to_url.values()}
    
    # 步骤2: 创建URL到引用ID的映射，合并相同URL的引用
    url_to_old_ids = {}
    for cid in sorted(set(used_ids)):
        if cid in citation_to_url:
            url = citation_to_url[cid]["url"]
            if url not in url_to_old_ids:
                url_to_old_ids[url] = []
            # url_to_old_ids[url].append(cid)
            url_to_old_ids[url].append((cid, old2id_2_pos[cid])) # add ori position to sort
            
    
    # 步骤3: 创建新旧ID的映射并重新编号
    old_to_new_id = {}
    new_citation_to_url = {}
    new_id = 1
    
    for url, old_id_and_pos in sorted(url_to_old_ids.items(), key=lambda x: x[1][0][1]):
        # 为每个唯一URL分配一个新ID
        for old_id, pos in old_id_and_pos:
            old_to_new_id[old_id] = new_id
        # new_citation_to_url[new_id] = url
        new_citation_to_url[new_id] = url2page[url]
        
        new_id += 1
    
    # 步骤4: 更新文章中的引用
    def replace_citation(match):
        old_id = int(match.group(1))
        if old_id in old_to_new_id:
            new_id = old_to_new_id[old_id]
            url = new_citation_to_url[new_id]["url"]
            return f'[[reference:{new_id}]]({url})'
        return ""  # 如果找不到映射，删除这个引用
    
    updated_text = re.sub(citation_pattern, replace_citation, text)

    
    # Then remove consecutive duplicate citations
    pattern_consecutive = r'(\[reference:\d+\])(\1)+'
    while re.search(pattern_consecutive, updated_text):
        updated_text = re.sub(pattern_consecutive, r'\1', updated_text)

    # Replace by [\d]
    updated_text = re.sub(r'\[reference:(\d+)\]', r'[\1]', updated_text)
        
    return updated_text, new_citation_to_url


def get_report_with_ref(data, article):
    web_pages = {}
    traverse(data, web_pages)
    article, web_pages = process_citations(article, web_pages)
    bib = []
    for index, page in sorted(web_pages.items()):
        bib.append("[{}] [{}]({}) ".format(index, page["title"], page["url"]))
    article += "\n\n# References\n{}".format("\n\n".join(bib))
    return article


if __name__ == "__main__":
    web_pages = {}
    folder = sys.argv[1]
    data = auto_read("{}/nodes.json".format(folder))
    traverse(data, web_pages)
    # print(len(web_pages))
    # print(sorted(web_pages.keys()))
    # article = open("{}/report.md".format(folder)).read()
    article = open("{}/article.txt".format(folder)).read()
    
    article, web_pages = process_citations(article, web_pages)
    
    bib = []
    for index, page in sorted(web_pages.items()):
        bib.append("- [{}]({}). {} ".format(index, page["url"], page["title"]))
    article += "\n\n# References\n{}".format("\n\n".join(bib))
    open("{}/report_with_ref.md".format(folder), "w").write(article.strip())
    