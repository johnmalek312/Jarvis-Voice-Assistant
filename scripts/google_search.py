import json

from llama_index.tools.google import GoogleSearchToolSpec
from pydantic import Field
import logging
from .data_manager import DataManager as dm
from tool_registry import register_tool
from llama_index.readers.web import BeautifulSoupWebReader
from llama_index.core.schema import TextNode
from llama_index.core.node_parser import TextSplitter
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import VectorStoreIndex
import re

google_spec = GoogleSearchToolSpec(dm.google_search["api_key"], dm.google_search["search_engine_id"], 3)


@register_tool()
def google_search(query: str) -> list[dict] | str:
    """Searches Google for a query and returns the top 3 links by default, call fetch link result function for the actual content of the links.
    This is useful to use with the get_url_markdown function to get the most relevant chunk of text from the search results, it's recommended."""
    try:
        logging.warning(f"Searching Google for: {query}")
        res = google_spec.google_search(query)
        items = json.loads(res[0].text)["items"]
        keys = ["title", "link", "snippet"]
        # get the links and make them in a list
        links = [item["link"] for item in items]
        logging.warning(f"returned links: {links}")
        return [{k: v for k, v in item.items() if k in keys} for item in items]
    except Exception as e:
        return "Error while searching Google: " + str(e)

def load_data(
    soup_reader,
    urls: list[str],
    custom_hostname = None,
    include_url_in_text = True,
) -> list[str]:
    """Load data from the urls.

    Args:
        urls (List[str]): List of URLs to scrape.
        custom_hostname (Optional[str]): Force a certain hostname in the case
            a website is displayed under custom URLs (e.g. Substack blogs)
        include_url_in_text (Optional[bool]): Include the reference url in the text of the document

    Returns:
        List[Document]: List of documents.

    """
    from urllib.parse import urlparse

    import requests
    from bs4 import BeautifulSoup

    documents = []
    for url in urls:
        try:
            page = requests.get(url)
        except Exception:
            raise ValueError(f"One of the inputs is not a valid url: {url}")

        hostname = custom_hostname or urlparse(url).hostname or ""

        soup = BeautifulSoup(page.content, "html.parser")

        data = ""
        extra_info = {"URL": url}
        if hostname in soup_reader._website_extractor:
            data, metadata = soup_reader._website_extractor[hostname](
                soup=soup, url=url, include_url_in_text=include_url_in_text
            )
            extra_info.update(metadata)

        else:
            data = soup.getText()

            documents.append(data)

    return documents


logging.basicConfig(level=logging.WARNING)
class ParagraphSplitter(TextSplitter):
    minimum_characters: int = Field(20, ge=1)
    def __init__(self):
        super().__init__()

    def split_text(self, text: str) -> list[str]:
        if not text:
            return []

        chunks = re.split(r'\n\s*\n\s*\n', text)
        # Remove empty chunks and strip whitespace
        chunks = [chunk.strip() for chunk in chunks if chunk.strip() and len(chunk.strip()) > self.minimum_characters]
        return chunks


# set up the two-step chunking
first_splitter = ParagraphSplitter()
second_splitter = SentenceSplitter()


# Function to apply two-step chunking
def two_step_chunking(texts: list[str]):
    # First chunking
    initial_split = first_splitter.split_texts(texts)

    # Second chunking
    final_nodes = []
    for text in initial_split:
        # Apply default chunking to this document
        chunks = second_splitter.split_text(text)
        final_nodes.extend([TextNode(text=chunk) for chunk in chunks])
    return final_nodes

@register_tool()
def fetch_link_content(url: str, query: str, minimum_characters: int = 20) -> list[str] | str:
    """Try to use this only once per requestSends a get request to a list of urls or link, then formats the html response and returns the most relevant chunk based on the query.
    This can be used to scrape data from websites and to get more detailed search results by passing list of links with a query to the function.

    Example:
        url_to_web_markdown(["https://www.w3schools.com/python/python_intro.asp"], "what is python")
        would return the most relevant chunk of text from the w3schools python introduction page.
    """
    try:
        logging.warning(f"Getting content from: {url}\nquery: {query}")
        first_splitter.minimum_characters = minimum_characters
        loader = BeautifulSoupWebReader()
        markdown_list = load_data(soup_reader=loader, urls=[url])
        nodes = two_step_chunking(markdown_list)
        results = VectorStoreIndex(nodes=nodes).as_retriever().retrieve(query)
        logging.warning(f"Received {[result.node.text for result in results]}")
        return [result.node.text for result in results]
    except Exception as e:
        return "Error while fetching url: " + str(e)

