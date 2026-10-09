"""
RAG layer: semantic search over (1) a vendor's product catalog and (2) past captions.

Golden rule: the vector database only FINDS things. Prices and stock are always
read from SQLite by product id, so the AI can never invent them.
"""
import uuid
from datetime import datetime

import chromadb
from chromadb.utils import embedding_functions

from db import get_connection

CHROMA_PATH = "chroma_db"
CATALOG_COLLECTION = "catalog"
CAPTIONS_COLLECTION = "captions"

# Catalog matches farther away than this count as "no match".
# Tune it after looking at the distances printed by test_rag.py.
MAX_DISTANCE = 1.3

_client = None
_collections = {}
_embedding_function = None


def configure(path=None, embedding_function=None):
    """Mainly for tests: point at a different folder or embedding model."""
    global CHROMA_PATH, _client, _embedding_function
    if path:
        CHROMA_PATH = path
    _embedding_function = embedding_function
    _client = None
    _collections.clear()


def _get_collection(name):
    """Create the client and collection on first use, so importing this file stays fast."""
    global _client
    if name not in _collections:
        if _client is None:
            _client = chromadb.PersistentClient(path=CHROMA_PATH)
        ef = _embedding_function or embedding_functions.DefaultEmbeddingFunction()
        _collections[name] = _client.get_or_create_collection(name=name, embedding_function=ef)
    return _collections[name]


# ---------- Money and formatting (plain code, no AI) ----------

def format_naira(price_kobo):
    naira, kobo = divmod(price_kobo, 100)
    return f"₦{naira:,}.{kobo:02d}" if kobo else f"₦{naira:,}"


def format_product(product):
    availability = "In stock" if product["stock"] > 0 else "Out of stock"
    text = f"[product id {product['id']}] {product['name']} - {format_naira(product['price_kobo'])} - {availability}"
    if product["description"]:
        text += f"\n  {product['description']}"
    return text


# ---------- Collection 1: product catalog ----------

def sync_catalog(vendor_id):
    """Copy this vendor's products from SQLite into the search index. Safe to re-run."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, name, description FROM products WHERE vendor_id = ?", (vendor_id,)
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        return 0

    # Only name + description are searchable. Prices are NOT put in the index on purpose.
    _get_collection(CATALOG_COLLECTION).upsert(
        ids=[f"{vendor_id}-{r['id']}" for r in rows],
        documents=[f"{r['name']}. {r['description'] or ''}".strip() for r in rows],
        metadatas=[{"vendor_id": vendor_id, "product_id": r["id"]} for r in rows],
    )
    return len(rows)


def _get_products_by_ids(vendor_id, product_ids):
    """Read the real product rows (with real prices and stock) from SQLite, keeping order."""
    if not product_ids:
        return []
    placeholders = ",".join("?" * len(product_ids))
    conn = get_connection()
    try:
        rows = conn.execute(
            f"SELECT * FROM products WHERE vendor_id = ? AND id IN ({placeholders})",
            (vendor_id, *product_ids),
        ).fetchall()
    finally:
        conn.close()
    by_id = {r["id"]: r for r in rows}
    return [by_id[pid] for pid in product_ids if pid in by_id]


def search_catalog_items(query, vendor_id, n_results=3):
    """Return [{'product': row, 'distance': float}] for the best matches. Smaller distance = closer."""
    collection = _get_collection(CATALOG_COLLECTION)
    if collection.count() == 0:
        return []

    results = collection.query(
        query_texts=[query], n_results=n_results, where={"vendor_id": vendor_id}
    )
    matches = [
        (meta["product_id"], dist)
        for meta, dist in zip(results["metadatas"][0], results["distances"][0])
        if dist <= MAX_DISTANCE
    ]
    products = _get_products_by_ids(vendor_id, [pid for pid, _ in matches])
    dist_by_id = dict(matches)
    return [{"product": p, "distance": dist_by_id[p["id"]]} for p in products]


def search_catalog_text(query, vendor_id):
    items = search_catalog_items(query, vendor_id)
    if not items:
        return (
            "No matching products found in the catalog. Do not guess any product, "
            "price or stock. Tell the person you will check with the vendor."
        )
    return "\n".join(format_product(item["product"]) for item in items)


# ---------- Collection 2: past captions ----------

def season_for(month):
    if month == 12:
        return "detty_december"
    if month in (11, 1, 2):
        return "harmattan"
    if month == 3:
        return "hot_season"
    return "rainy_season"


def save_caption(vendor_id, caption, image_description, colors, hashtags, season=None):
    """Remember a caption we generated. We search by the PHOTO DESCRIPTION, because a new
    photo's description is most similar to the descriptions of similar past photos."""
    if isinstance(colors, (list, tuple)):
        colors = ",".join(colors)
    if isinstance(hashtags, (list, tuple)):
        hashtags = " ".join(hashtags)

    _get_collection(CAPTIONS_COLLECTION).add(
        ids=[f"{vendor_id}-{uuid.uuid4().hex[:12]}"],
        documents=[image_description],
        metadatas=[{
            "vendor_id": vendor_id,
            "caption": caption,
            "colors": colors,  # Chroma metadata can't hold lists, so these are plain strings
            "hashtags": hashtags,
            "season": season or season_for(datetime.now().month),
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }],
    )


def find_similar_captions(image_description, n_results=3):
    """Return the metadata (caption, colors, hashtags, season) of the closest past photos."""
    collection = _get_collection(CAPTIONS_COLLECTION)
    if collection.count() == 0:
        return []
    results = collection.query(query_texts=[image_description], n_results=n_results)
    return results["metadatas"][0]


def find_similar_captions_text(image_description):
    items = find_similar_captions(image_description)
    if not items:
        return "No past captions saved yet. Write the captions from scratch."
    lines = []
    for i, m in enumerate(items, 1):
        lines.append(f"{i}. \"{m['caption']}\" (season: {m['season']}, colors: {m['colors']}, hashtags: {m['hashtags']})")
    return "Past captions for similar photos, for style consistency only:\n" + "\n".join(lines)