# Curated Nigerian perfume/beauty hashtags, grouped by category.
# This is a starting list — expand it over time as you learn what real vendors use.

HASHTAGS = {
    "general": ["#PerfumeNigeria", "#PerfumesInLagos", "#SmellGood", "#FragranceLovers"],
    "event": ["#OwambeReady", "#DettyDecember", "#OwambeSeason", "#WeddingSeasonNG"],
    "buyer_intent": ["#PerfumeForSale", "#AffordablePerfume", "#PerfumeDeals", "#BuyPerfumeOnline"],
    "brand_style": ["#ArabianPerfume", "#LattafaNigeria", "#ArmafPerfume", "#UnisexFragrance"],
    "location": ["#LagosBusiness", "#AbujaFragrance", "#NigerianSmallBusiness", "#LagosPerfumeVendor", "#AbujaPerfumeStore", "#PortHarcourtPerfume", "#LekkiPerfumePlug", "#PerfumeInNigeria"],
    "business_focused": ["#NaijaBusiness", "#NaijaPerfumePlug", "#PerfumeVendorsInNigeria", "#AffordableLuxuryNigeria", "#LagosBigBoys"]
}

def get_hashtags(categories=None, limit=15):
    """
    Returns a flat list of hashtags.
    If categories is given (a list of category names), only pull from those.
    Otherwise, pull from all categories.
    """
    if categories is None:
        categories = HASHTAGS.keys()

    result = []
    for cat in categories:
        result.extend(HASHTAGS.get(cat, []))

    return result[:limit]


if __name__ == "__main__":
    tags = get_hashtags()
    print(f"Got {len(tags)} hashtags:")
    print(tags)