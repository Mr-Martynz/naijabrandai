from smolagents import tool

from rag_store import find_similar_captions_text, search_catalog_text


@tool
def search_catalog(query: str, vendor_id: int) -> str:
    """Search a vendor's product catalog by meaning and return the matching products
    with their exact Naira price and stock status. Always use this tool for any question
    about a product, price or availability. Never answer those from memory.

    Args:
        query: What the person is asking about, in plain words (for example "smoky perfume for men").
        vendor_id: The numeric ID of the vendor whose catalog to search.
    """
    return search_catalog_text(query, vendor_id)


@tool
def find_similar_caption(image_description: str) -> str:
    """Find captions written earlier for similar-looking perfume photos, so new captions
    keep a consistent style. Use it once, after you have the photo description.

    Args:
        image_description: The factual description of the new photo.
    """
    return find_similar_captions_text(image_description)