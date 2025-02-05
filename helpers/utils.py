import hashlib
import re

def clean_text(text) -> str:
    """Cleans the text by removing the assistant's name and any leading/trailing whitespace."""
    return re.sub(r'https*://[\w\.-]+\.com[\w/\-]+|https*://[\w\.]+\.com|[\w\.]+\.com/[\w/\-]+', lambda x:re.findall(r'(?<=\://)[\w\.]+\.com|[\w\.]+\.com', x.group())[0], text).replace("*", "").replace("_", "").replace("`", "").replace("~", "").replace(">", "").replace("<", "")

def compute_documents_hash(documents) -> str:
    """
    Computes a combined hash for a list of documents, only works for documents loaded with docstring walker.
    """
    hash_obj = hashlib.md5()

    sorted_docs: list = sorted(documents, key=lambda doc: doc.metadata.get("file_name") + doc.text) # use metadata and text incase the document is chunked

    for doc in sorted_docs:
        doc_str = f"{doc.metadata["file_name"]}-{doc.text}"
        hash_obj.update(doc_str.encode("utf-8")) # update hash

    return hash_obj.hexdigest() # return hash