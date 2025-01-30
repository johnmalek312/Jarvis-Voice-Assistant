from theguardian import theguardian_content
from .data_manager import DataManager as dm


def search_news(q, section=None, page_size=10, order_by="newest"):
    """
    Searches for news articles from The Guardian API.

    Args:
        api_key: Your Guardian API key.
        q: The search query.
        section: (Optional) Filter by section.
        page_size: (Optional) Number of results per page (default: 10).
        order_by: (Optional) Order results by (default: "newest").

    Returns:
        A list of dictionaries, where each dictionary represents a news article,
        or None if there's an error.
    """
    try:
        content = theguardian_content.Content(api=api_key, q=q, section=section, page_size=page_size, order_by=order_by)
        response = content.get_content_response()
        return content.get_results(response)
    except Exception as e:
        print(f"Error searching news: {e}")
        return None


def get_news_content(api_key, article_id):
    """
    Retrieves the full content of a news article.

    Args:
        api_key: Your Guardian API key.
        article_id: The ID of the article.

    Returns:
        A dictionary containing the article content (including the body),
        or None if the article is not found or there's an error.
    """
    return get_item_by_id(api_key, article_id, show_fields="body")  # Reuse get_item_by_id


def get_news_summary(api_key, article_id):
    """
    Retrieves a summary of a news article.

    Args:
        api_key: Your Guardian API key.
        article_id: The ID of the article.

    Returns:
        A dictionary containing the article summary (headline, standfirst, thumbnail),
        or None if the article is not found or there's an error.
    """
    return get_item_by_id(api_key, article_id, show_fields="headline,standfirst,thumbnail")


# Helper function (reused from previous example)
def get_item_by_id(api_key, item_id, show_fields=None):
    try:
        params = {}
        if show_fields:
            params["show-fields"] = show_fields
        content = theguardian_content.Content(api=api_key)
        response = content.find_by_id(item_id, **params)
        results = content.get_results(response)
        return results[0] if results else None
    except Exception as e:
        print(f"Error retrieving item by ID: {e}")
        return None