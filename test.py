import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

def search_arxiv(query: str, start: int = 0, max_results: int = 20):
    base_url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": query,
        "start": start,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    url = base_url + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)

    namespace = {
        "atom": "http://www.w3.org/2005/Atom"
    }

    papers = []

    for entry in root.findall("atom:entry", namespace):
        title = entry.find("atom:title", namespace).text.strip()
        abstract = entry.find("atom:summary", namespace).text.strip()
        published = entry.find("atom:published", namespace).text.strip()
        updated = entry.find("atom:updated", namespace).text.strip()
        paper_url = entry.find("atom:id", namespace).text.strip()
        authors = [
            author.find("atom:name", namespace).text.strip()
            for author in entry.findall("atom:author", namespace)
        ]

        papers.append({
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "published": published,
            "updated": updated,
            "url": paper_url,
            "source": "arXiv",
        })

    return papers

# papers = search_arxiv("all:LLM", max_results=10)

# for paper in papers:

#     print("Title:", paper["title"])

#     print("Authors:", ", ".join(paper["authors"]))

#     print("Published:", paper["published"])

#     print("URL:", paper["url"])

#     print("Abstract:", paper["abstract"][:300], "...")

#     print("-" * 80)