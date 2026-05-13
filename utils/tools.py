from dataclasses import asdict, dataclass, field

from agents import RunContextWrapper, function_tool
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import os


@dataclass
class ResearchState:
    research_interest: str = ""
    topic: str = ""
    number_of_papers: int = 0
    source: str = ""
    similarity_method: str = ""
    email_address: str = ""
    papers: list[dict] = field(default_factory=list)
    selected_papers: list[dict] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


@function_tool
def record_research_request(
    ctx: RunContextWrapper[ResearchState],
    research_interest: str,
    topic: str,
    number_of_papers: int,
    source: str,
    similarity_method: str,
    email_address: str,
):
    """
    Record the user's research request in structured state.
    """
    ctx.context.research_interest = research_interest
    ctx.context.topic = topic
    ctx.context.number_of_papers = number_of_papers
    ctx.context.source = source
    ctx.context.similarity_method = similarity_method
    ctx.context.email_address = email_address

    return {
        "status": "recorded",
        "research_request": ctx.context.to_dict(),
    }


@function_tool
def get_research_request(ctx: RunContextWrapper[ResearchState]):
    """
    Get the structured research request recorded by the reception agent.
    """
    return ctx.context.to_dict()


@function_tool
def search_arxiv(
    ctx: RunContextWrapper[ResearchState],
    start: int = 0,
):
    """
    Search arXiv using the topic and paper count stored in research state.
    """
    query = ctx.context.topic
    max_results = ctx.context.number_of_papers + 20

    if not query:
        return {
            "error": "No topic has been recorded yet. Ask the reception agent to record the research request first."
        }

    if max_results <= 0:
        return {
            "error": "No paper count has been recorded yet. Ask the reception agent to record the research request first."
        }

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

        papers.append(
            {
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "published": published,
                "updated": updated,
                "url": paper_url,
                "source": "arXiv",
            }
        )
    ctx.context.papers = papers
    return papers, len(papers)

@function_tool
def filter_papers(ctx: RunContextWrapper[ResearchState], filtered_paper_indices: list[int]):
    """
    Filter the retrieved papers based on the indices provided by the paper filtering agent.
     The indices are based on the order of the papers returned by the search_arxiv tool.
     The filtered papers are stored in the research state and will be used by the email agent if the user wants to email them.
     The filtered papers are also returned as output of this tool, which will be presented to the user by the paper filtering agent.
    """
    papers = ctx.context.papers
    filtered_papers = [papers[i] for i in filtered_paper_indices]
    ctx.context.selected_papers = filtered_papers
    return filtered_papers

@function_tool
def send_email(ctx: RunContextWrapper[ResearchState]):
    """
    Send the selected papers to the user's email address specified in the research request.
    """
    selected_papers = ctx.context.selected_papers
    email_address = ctx.context.email_address
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))
    from_email = Email(os.environ.get("MY_EMAIL_ADDRESS"))
    to_email = To(email_address)
    subject = "Your Research Paper Recommendations on " + ctx.context.topic
    content_str = "Here are the papers we found for your research interest:\n\n"
    for i, paper in enumerate(selected_papers):
        content_str += f"{i+1}. {paper['title']}\n"
        content_str += f"   Authors: {', '.join(paper['authors'])}\n"
        content_str += f"   Published: {paper['published']}\n"
        content_str += f"   Abstract: {paper['abstract']}\n"
        content_str += f"   URL: {paper['url']}\n\n"

    content = Content("text/plain", content_str)
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return {
        "status": "email_sent",
        "response_status_code": response.status_code,
        "response_body": response.body,
        "response_headers": dict(response.headers),
    }


