from db import init_db, add_vendor, get_vendor_by_sender, normalize_number

init_db()

name = input("Business name: ").strip()
number = normalize_number(input("Vendor WhatsApp number with country code (e.g. 2348012345678): "))
delivery = input("Delivery info, one line (can leave blank): ").strip()

if get_vendor_by_sender(number):
    print("That number is already registered.")
else:
    vendor_id = add_vendor(name, number, delivery_info=delivery or None)
    print(f"Vendor saved with id {vendor_id}")