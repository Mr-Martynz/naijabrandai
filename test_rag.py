from db import init_db
from rag_store import (
    CAPTIONS_COLLECTION, CATALOG_COLLECTION, MAX_DISTANCE, _get_collection,
    find_similar_captions, search_catalog_items, search_catalog_text, sync_catalog,
)

VENDOR_ID = 1
init_db()
print(f"Indexed {sync_catalog(VENDOR_ID)} products.\n")

failed = 0


def check(label, ok):
    global failed
    failed += not ok
    print("PASS" if ok else "FAIL", "-", label)


def show(query):
    items = search_catalog_items(query, VENDOR_ID)
    print(f'\nQuery: "{query}"')
    for item in items:
        print(f'   {item["product"]["name"]}  (distance {item["distance"]:.2f})')
    return [item["product"]["name"] for item in items]


# 1-3: meaning-based search finds the right product (expected one should be in the top 2)
names = show("strong smoky woody scent for men")
check("smoky woody -> Oud Royale", "Oud Royale" in names[:2])

names = show("floral perfume for a wedding")
check("floral wedding -> Velvet Rose", "Velvet Rose" in names[:2])

names = show("fresh light scent for hot weather")
check("fresh and light -> Citrus Splash", "Citrus Splash" in names[:2])

# 4: the answer text carries exact prices and stock, straight from SQLite
text = search_catalog_text("how much is Oud Royale", VENDOR_ID)
print("\nTool output for 'how much is Oud Royale':\n" + text + "\n")
check("price shown exactly as ₦45,000", "₦45,000" in text)
check("stock status shown", "In stock" in text or "Out of stock" in text)

text = search_catalog_text("Citrus Splash", VENDOR_ID)
check("zero stock shows 'Out of stock'", "Citrus Splash" in text and "Out of stock" in text)

# 5: prices must NOT live in the search index
docs = _get_collection(CATALOG_COLLECTION).get()["documents"]
check("no prices inside the search index", all("₦" not in d and "000" not in d for d in docs))

# 6: unrelated query (informational: if this lists products, lower MAX_DISTANCE)
names = show("laptop charger")
print(f"   (MAX_DISTANCE is {MAX_DISTANCE}; an unrelated query ideally returns nothing)")

# 7: similar-caption lookup
similar = find_similar_captions("a dark glass bottle with a gold lid on a black background")
print("\nClosest past caption:", similar[0]["caption"] if similar else None)
check("dark/gold bottle -> the Oud Royale caption", bool(similar) and "Oud Royale" in similar[0]["caption"])
check("caption metadata includes season and hashtags", bool(similar) and similar[0]["season"] and similar[0]["hashtags"])

print("\nAll good!" if failed == 0 else f"\n{failed} check(s) failed.")