import re
import os
import inspect
import requests
from urllib.parse import urlparse
from tqdm import tqdm
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from googleapiclient.discovery import build
from typing import List, Tuple
from .color_logger import get_logger
from .settings import Settings
from ._types import ToolsDefType


_GOOGLE_SEARCH_API_KEY = os.environ.get('GOOGLE_SEARCH_API_KEY', None)
_GOOGLE_SEARCH_CSE_ID = os.environ.get('GOOGLE_SEARCH_CSE_ID', None)


def handle_tool_error(e: Exception) -> None:
    get_logger().error(f'ERROR [{e.__class__.__name__} in {inspect.stack()[1].function}]: {str(e)}', color='red')


### TOOLS ###

def web_search(query: str, max_results: int = 10) -> str:
    """
    Search the web for the provided query, and returns the title, URL and description of the results.
    Search results are separated by: =====

    Example of two search results:

    Title: Welcome to My Site
    URL: http://www.mysite.xyz
    Description: This is my private website, see my stuff here
    =====
    Title: Grapes Online
    URL: http://www.grapes.com
    Description: This is the number one site for grapes fans and lovers
    """
    if max_results < 1: max_results = 1
    elif max_results > 10: max_results = 10

    def duckduckgo_search(query: str, max_results: int) -> List[Tuple[str, str, str]]:
        results = []
        ddgs = DDGS() 
        results = ddgs.text(query, max_results=max_results)
        for result in tqdm(results):
            url = result['href']
            if url is None:
                continue
            body = result['body']
            title = result['title'] or ''
            results.append((title, url, body))
        return results
    
    def google_search(query: str, max_results: int, api_key: str, cse_id: str) -> List[Tuple[str, str, str]]:
        results = []
        service = build("customsearch", "v1", developerKey=api_key)
        response = service.cse().list(q=query, cx=cse_id, num=max_results).execute()
        for result in tqdm(response['items']):
            results.append((result['title'], result['link'], result['snippet']))
        return results

    try:
        if _GOOGLE_SEARCH_API_KEY and _GOOGLE_SEARCH_CSE_ID:
            get_logger().debug('Searching the web with Google')
            results = google_search(query=query, max_results=max_results, api_key=_GOOGLE_SEARCH_API_KEY, cse_id=_GOOGLE_SEARCH_CSE_ID)
        else:
            get_logger().debug('Searching the web with DuckDuckGo')
            results = duckduckgo_search(query=query, max_results=max_results)
        
        if results:
            return '\n=====\n'.join(f"Title: {title}\nURL: {url}\nDescription: {body}\n" for (title, url, body) in results)
        else:
            return "No results"

    except Exception as e:
        handle_tool_error(e)
        return f"Error while searching the web: {e}"


def visit_website(url: str) -> str:
    """
    Goes to the provided URL and returns a simple version of the page text. Images and styling are excluded.
    """
    try:
        headers = {'User-Agent': Settings().web.user_agent}
        response = requests.get(url, timeout=Settings().web.surf_timeout_seconds, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()

            # Clean whitespaces
            text = re.sub(pattern=r'[ \t]+', repl=' ', string=text)  # Replace multiple spaces and tabs with a single space
            text = re.sub(pattern=r'\n{3,}', repl='\n\n', string=text)  # Replace more than two newlines with two newlines
            text = text.strip()

            return text 
        else:
            raise RuntimeError(f"ERROR: Failed to retrieve the webpage. Status code: {response.status_code}")
    except Exception as e:
        handle_tool_error(e)
        return f"ERROR: {e}"


#######
    

def tool_display_message(tool_name: str, **arguments) -> str:
    match tool_name:
        case 'web_search':
            return f'Searching the web: {arguments["query"]}'
        case 'visit_website':
            domain = urlparse(arguments['url']).netloc
            return f'Visiting website: {domain}'
        case _:
            capitalized_name = ' '.join([s.capitalize() for s in tool_name.split(' ')])
            return f'Running tool: {capitalized_name}'
            

tools_params_definitions: ToolsDefType = {
    web_search: [("query", {"type": "string", "description": "The query to search on the web"}, True),
                 ("max_results", {"type": "number", "description": "Maximal number of results to retrieve. Must be between 1 and 10, default is 10."}, False)],
    visit_website: [("url", {"type": "string", "description": "The URL of the page to scrape"}, True)],
}