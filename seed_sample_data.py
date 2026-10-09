"""
Loads SAMPLE (made-up) products and past captions so we can test the RAG layer.
Replace these with the vendor's real catalog later. Safe to re-run: it skips what exists.
"""
from db import get_connection, init_db
from rag_store import save_caption, sync_catalog, _get_collection, CAPTIONS_COLLECTION

VENDOR_ID = 1

# (name, description, price in KOBO (100 kobo = ₦1), stock)
SAMPLE_PRODUCTS = [
    ("Oud Royale", "Deep smoky oud with amber and leather. A bold, long-lasting scent for men, great for evenings and owambe nights.", 4_500_000, 12),
    ("Velvet Rose", "Soft floral perfume with rose, peony and vanilla. Feminine and romantic, perfect for weddings and date nights.", 3_850_000, 8),
    ("Citrus Splash", "Fresh lemon, bergamot and mint. A light, cooling everyday scent that works in Lagos heat.", 2_200_000, 0),
    ("Vanilla Musk", "Sweet vanilla with warm musk and caramel. A cozy unisex scent that lasts all day.", 3_000_000, 5),
    ("Midnight Amber", "Warm amber, spice and sandalwood. A rich unisex scent, great for Detty December.", 5_200_000, 3),
]

SAMPLE_CAPTIONS = [
    {
        "image_description": "A tall black glass perfume bottle with a gold cap on a dark background",
        "caption": "Smell good, no wahala. Oud Royale don land - you go love it. Owambe don set, your scent must match.",
        "colors": ["#111111", "#c9a227"],
        "hashtags": ["#naijaperfume", "#smellgood", "#oud"],
        "season": "harmattan",
    },
    {
        "image_description": "A pink frosted glass perfume bottle surrounded by rose petals on a soft pastel background",
        "caption": "Soft girl era, but make it fragrant. Velvet Rose for the wedding season. Smell good, feel good.",
        "colors": ["#f4c2c2", "#ffffff"],
        "hashtags": ["#weddingseason", "#rosescent", "#lagosgirls"],
        "season": "rainy_season",
    },
    {
        "image_description": "A clear perfume bottle with lemon slices and green leaves on a bright white background",
        "caption": "Lagos sun no dey carry last. Citrus Splash keeps you fresh from morning till night.",
        "colors": ["#f5e642", "#3a7d44"],
        "hashtags": ["#freshscent", "#lagoslife", "#perfumeNG"],
        "season": "hot_season",
    },
]


def main():
    init_db()

    conn = get_connection()
    try:
        vendor = conn.execute("SELECT id FROM vendors WHERE id = ?", (VENDOR_ID,)).fetchone()
        if vendor is None:
            print(f"No vendor with id {VENDOR_ID}. Run seed_vendor.py first.")
            return
        existing = conn.execute("SELECT COUNT(*) FROM products WHERE vendor_id = ?", (VENDOR_ID,)).fetchone()[0]
        if existing == 0:
            conn.executemany(
                "INSERT INTO products (vendor_id, name, description, price_kobo, stock) VALUES (?, ?, ?, ?, ?)",
                [(VENDOR_ID, *p) for p in SAMPLE_PRODUCTS],
            )
            conn.commit()
            print(f"Added {len(SAMPLE_PRODUCTS)} sample products to SQLite.")
        else:
            print(f"Vendor already has {existing} products, leaving them alone.")
    finally:
        conn.close()

    print(f"Indexed {sync_catalog(VENDOR_ID)} products for search.")

    if _get_collection(CAPTIONS_COLLECTION).count() == 0:
        for c in SAMPLE_CAPTIONS:
            save_caption(VENDOR_ID, c["caption"], c["image_description"], c["colors"], c["hashtags"], c["season"])
        print(f"Saved {len(SAMPLE_CAPTIONS)} sample past captions.")
    else:
        print("Captions collection already has entries, leaving it alone.")


if __name__ == "__main__":
    main()