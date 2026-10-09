from db import get_vendor_by_sender

NEW_PRODUCT_PHOTO = "new_product_photo"
PRICE_QUESTION = "price_question"
ORDER_REQUEST = "order_request"
CATALOG_REQUEST = "catalog_request"
GENERAL_SUPPORT = "general_support"

# Crude placeholder rules. The LLM version replaces these later.
# Checked in this order, so "I want to order, how much is it?" counts as an order.
KEYWORDS = {
    ORDER_REQUEST: ["order", "buy", "i'll take", "i will take", "purchase"],
    PRICE_QUESTION: ["price", "how much", "cost", "naira", "₦"],
    CATALOG_REQUEST: ["catalog", "catalogue", "what do you have", "what do you sell", "available"],
}


def classify_intent(message):
    """Label one WhatsApp message. Photos are decided by message type, no AI needed."""
    if message.get("type") == "image":
        return NEW_PRODUCT_PHOTO
    if message.get("type") != "text":
        return GENERAL_SUPPORT

    text = message["text"]["body"].lower()
    for intent in (ORDER_REQUEST, PRICE_QUESTION, CATALOG_REQUEST):
        if any(word in text for word in KEYWORDS[intent]):
            return intent
    return GENERAL_SUPPORT


def route_message(message):
    """Work out WHO sent it (vendor or customer) and WHAT they want."""
    vendor = get_vendor_by_sender(message["from"])
    intent = classify_intent(message)

    if vendor and vendor["is_active"]:
        return {"role": "vendor", "vendor": vendor, "intent": intent}

    # Not a whitelisted vendor: the content pipeline must never run for them.
    if intent == NEW_PRODUCT_PHOTO:
        intent = GENERAL_SUPPORT
    return {"role": "customer", "vendor": None, "intent": intent}