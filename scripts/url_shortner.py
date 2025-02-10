from tool_registry import register_tool
from .data_manager import DataManager as dm
import requests

@register_tool()
def shorten_url(long_url: str, alias: str = "") -> str:
    """
    Shorten a long URL using TinyURL API.
    
    Args:
        long_url (str): The URL to be shortened
        alias (str, optional): Custom alias for the shortened URL recommended to keep the default
        
    Returns the shortened url.
    """
    try:
        api_key = dm.url_shortner.get('api_key')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        payload = {
            "url": long_url,
            "domain": "tinyurl.com"
        }
        
        if alias:
            payload["alias"] = alias
            
        response = requests.post(
            'https://api.tinyurl.com/create',
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            return f"The shortened url is this: {response.json()['data']['tiny_url']}"
        else:
            raise Exception(f"API Error: {response.status_code}, {response.text}")
            
    except Exception as e:
        return f"Error shortening URL: {str(e)}"
