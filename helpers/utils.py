import re

def clean_text(text) -> str:
    """Cleans the text by removing the assistant's name and any leading/trailing whitespace."""
    return re.sub(r'https*://[\w\.-]+\.com[\w/\-]+|https*://[\w\.]+\.com|[\w\.]+\.com/[\w/\-]+', lambda x:re.findall(r'(?<=\://)[\w\.]+\.com|[\w\.]+\.com', x.group())[0], text).replace("*", "").replace("_", "").replace("`", "").replace("~", "").replace(">", "").replace("<", "")
