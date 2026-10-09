from db import init_db
from router import (
    classify_intent, route_message,
    NEW_PRODUCT_PHOTO, PRICE_QUESTION, ORDER_REQUEST, CATALOG_REQUEST, GENERAL_SUPPORT,
)

STRANGER = "2340000000000"  # a number that is not a vendor


def text(body):
    return {"from": STRANGER, "type": "text", "text": {"body": body}}


photo = {"from": STRANGER, "type": "image", "image": {"id": "abc"}}

init_db()

checks = [
    ("photo", classify_intent(photo), NEW_PRODUCT_PHOTO),
    ("How much is this?", classify_intent(text("How much is this?")), PRICE_QUESTION),
    ("I want to order 2 bottles", classify_intent(text("I want to order 2 bottles")), ORDER_REQUEST),
    ("What do you have?", classify_intent(text("What do you have?")), CATALOG_REQUEST),
    ("Do you deliver to Abuja?", classify_intent(text("Do you deliver to Abuja?")), GENERAL_SUPPORT),
    ("order + price together", classify_intent(text("I will take it, how much?")), ORDER_REQUEST),
    ("stranger's photo is NOT a pipeline trigger", route_message(photo)["intent"], GENERAL_SUPPORT),
    ("stranger is a customer", route_message(photo)["role"], "customer"),
]

failed = 0
for label, got, expected in checks:
    ok = got == expected
    failed += not ok
    print(("PASS" if ok else "FAIL"), "-", label, "->", got)

print("\nAll good!" if failed == 0 else f"\n{failed} check(s) failed.")