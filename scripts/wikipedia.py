import wikipedia
from tool_registry import register_tool



@register_tool()
def wikipedia_search(query: str) -> list[str]:
    """This function returns the search results titles based on the input query. The titles can be used to get the Wikipedia page."""
    return wikipedia.search(query)

@register_tool()
def wikipedia_page_url(title: str) -> str:
    """This function returns the Wikipedia page url based on the title."""
    return wikipedia.page(title).url


@register_tool()
def wikipedia_summary(title: str, auto_suggest: bool = True, sentences: int = 3) -> str:
    """This function returns the summary of the Wikipedia page based on the title. The auto_suggest parameter is set to True by default. If the auto_suggest parameter is set to True, the function will suggest the valid search query based on the input query. If the auto_suggest parameter is set to False, the function will return the summary of the Wikipedia page based on the input query without suggesting the valid search query."""
    return wikipedia.summary(title, auto_suggest=auto_suggest, sentences=sentences)


@register_tool()
def wikipedia_suggest(query: str) -> list[str]:
    """A function that returns the suggested valid search query based on the input query."""
    return wikipedia.suggest(query)
