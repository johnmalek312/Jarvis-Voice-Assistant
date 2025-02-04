from .data_manager import DataManager as dm
from tool_registry import register_tool
import os
import requests
import json
import websocket
from selenium import webdriver
from selenium.webdriver.chromium.webdriver import ChromiumDriver
if dm.browser["browser"].lower() == "chrome":
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
elif dm.browser["browser"].lower() == "edge":
    from selenium.webdriver.edge.options import Options
    from selenium.webdriver.edge.service import Service
else:
    raise Exception("Browser not supported")

from llama_index.tools.google import GoogleSearchToolSpec
from pydantic import Field
from logger import app_logger as logging
from llama_index.readers.web import BeautifulSoupWebReader
from llama_index.core.schema import TextNode
from llama_index.core.node_parser import TextSplitter
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import VectorStoreIndex
import re

debugging_port = 10001  # You can choose any available port

driver: ChromiumDriver | None = None  # Global variable to hold the driver instance

def check_driver():
    """Checks if the current driver session is still active."""
    global driver
    try:
        # Accessing window_handles will fail if the browser is closed.
        driver.switch_to.window(driver.current_window_handle)
        return True
    except Exception:
        try:
            driver = get_driver()
            return False
        except Exception as e:
            raise Exception(f"Failed to reconnect to browser: {e}")

def get_driver():
    """Initializes the driver if not already initialized and returns it."""
    global driver
    if driver is not None:
        return driver

    driver_path = 'driver/browser_driver.exe'
    options = Options()
    options.add_argument(f'--remote-debugging-port={debugging_port}')
    username = os.getenv('USERNAME')  # Gets Windows username

    if dm.browser["browser"].lower() == "chrome":
        options.add_argument(f"user-data-dir=C:/Users/{username}/AppData/Local/Google/Chrome/User Data")  # Chrome user data
    elif dm.browser["browser"].lower() == "edge":
        options.add_argument(f"user-data-dir=C:/Users/{username}/AppData/Local/Microsoft/Edge/User Data")  # Edge user data

    service = Service(driver_path)

    try:
        if dm.browser["browser"].lower() == "chrome":
            driver = webdriver.Chrome(service=service, options=options)
        elif dm.browser["browser"].lower() == "edge":
            driver = webdriver.Edge(service=service, options=options)
        return driver
    except Exception as e:
        raise Exception(f"Failed to connect to browser: {e}")

# @register_tool()
def open_new_tab(url: str = None) -> None | str:
    """Opens a new tab in the browser."""
    try:
        if url is None:
            url = "https://"
        # browser is opened
        if check_driver():
            driver.execute_script("window.open(arguments[0], '_blank');", url)
        else:
            driver.get(url=url)
        result = "New tab opened in browser"
        logging.info("open_new_tab successful: %s", result)
        return result
    except Exception as e:
        logging.error("open_new_tab error: %s", e)
        return f"Error while opening new tab: {e}"

# @register_tool()
def open_google(query: str = Field("", description="The search query to open google with.")) -> None | str:
    """Opens a new tab with a Google search query."""
    try:
        check_driver()
        if query:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        else:
            search_url = "https://www.google.com"
        open_new_tab(search_url)
        result = "Google search opened in browser"
        logging.info("open_google successful: %s", result)
        return result
    except Exception as e:
        logging.error("open_google error: %s", e)
        return f"Error while searching Google: {e}"

# @register_tool()
def open_youtube(search_query: str = Field(None, description="The query to search for on youtube.")) -> None | str:
    """Opens YouTube, optionally with a search query."""
    try:
        check_driver()
        if search_query:
            url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
        else:
            url = "https://www.youtube.com"
        open_new_tab(url)
        result = "YouTube opened in browser"
        logging.info("open_youtube successful: %s", result)
        return result
    except Exception as e:
        logging.error("open_youtube error: %s", e)
        return f"Error while opening YouTube: {e}"

google_spec = GoogleSearchToolSpec(dm.google_search["api_key"], dm.google_search["search_engine_id"], 3)

# @register_tool()
def google_search(query: str = Field(description="The search query to perform on Google.")) -> list[dict] | str:
    """
    Searches Google for a query using the Google API and returns the top 3 links by default.
    Calls the fetch_link_result function to obtain the actual content of these links.
    This function is useful in conjunction with the get_url_markdown function to extract the most relevant text from the search results.
    """
    try:
        res = google_spec.google_search(query)
        items = json.loads(res[0].text)["items"]
        keys = ["title", "link", "snippet"]
        # get the links and make them in a list
        links = [item["link"] for item in items]
        logging.info("google_search returned links: %s", links)
        result = [{k: v for k, v in item.items() if k in keys} for item in items]
        logging.info("google_search successful")
        return result
    except Exception as e:
        logging.error("google_search error: %s", e)
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

# @register_tool()
def fetch_link_content(url: str = Field(description="The link to fetch"), query: str = Field(description="The retrieval query for similarity search."), minimum_characters: int = 20) -> list[str] | str:
    """Try to use this only once per request. Sends a get request to the url or link, then formats the html response and returns the most relevant chunk based on the query.
    This can be used to scrape data from websites and to get more detailed search results by passing list of links with a query to the function.

    Example:
        url_to_web_markdown("https://www.w3schools.com/python/python_intro.asp", "what is python")
        would return the most relevant chunk of text from the w3schools python introduction page.
    """
    try:
        logging.info("Getting content from: %s with query: %s", url, query)
        first_splitter.minimum_characters = minimum_characters
        loader = BeautifulSoupWebReader()
        markdown_list = load_data(soup_reader=loader, urls=[url])
        nodes = two_step_chunking(markdown_list)
        results = VectorStoreIndex(nodes=nodes).as_retriever().retrieve(query)
        result_texts = [result.node.text for result in results]
        logging.info("fetch_link_content successful, received result: %s", result_texts)
        return result_texts
    except Exception as e:
        logging.error("fetch_link_content error: %s", e)
        return "Error while fetching url: " + str(e)

# @register_tool()
def get_active_tab_url() -> str:
    """Returns the current URL of the browser."""
    try:
        check_driver()
        switch_to_visible_tab()
        current_url = driver.current_url
        logging.info("get_active_tab_url successful: %s", current_url)
        return current_url
    except Exception as e:
        logging.error("get_active_tab_url error: %s", e)
        return f"Error while getting current URL: {e}"

# @register_tool()
def open_browser() -> str:
    """Opens the browser."""
    try:
        get_driver()
        result = "Browser opened"
        logging.info("open_browser successful: %s", result)
        return result
    except Exception as e:
        logging.error("open_browser error: %s", e)
        return f"Error while opening browser: {e}"

def switch_to_visible_tab():
    """Switches to the first visible tab in the browser."""
    check_driver()
    tabs = requests.get(f"http://127.0.0.1:{debugging_port}/json/list").json()
    tabs = filter(
        lambda x: (x["url"].startswith("https://") or x["url"].startswith("http://")) and x["type"] == "page", tabs)
    for tab in tabs:
        ws_url = tab["webSocketDebuggerUrl"]
        ws = websocket.create_connection(ws_url, suppress_origin=True)
        ws.send(json.dumps(
            {"id": 1, "method": "Runtime.evaluate", "params": {"expression": "document.visibilityState"}}))
        message_json = ws.recv()
        if json.loads(message_json)['result']["result"]['value'] == "visible":
            driver.switch_to.window(tab["id"])
            ws.close()
            return
    raise Exception("No visible tabs found")
