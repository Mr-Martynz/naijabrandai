import os
import requests
from fastapi import FastAPI, Request, BackgroundTasks
from dotenv import load_dotenv

from build_package import build_package
from db import init_db
from router import route_message, NEW_PRODUCT_PHOTO

load_dotenv()
init_db()  # creates the database tables the first time

app = FastAPI()

VERIFY_TOKEN = "naijabrandai_verify_123"

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
GRAPH_URL = "https://graph.facebook.com/v21.0"

# Message IDs we've already handled, so Meta's resends are ignored
processed_ids = set()


def send_text(to, text):
    """Send a plain WhatsApp text message."""
    url = f"{GRAPH_URL}/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text[:4000]},  # WhatsApp rejects messages over ~4096 characters
    }
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    print("Send status:", r.status_code, r.text)


def download_image(media_id):
    """Two steps: ask Meta for the download link, then download the file."""
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    info = requests.get(f"{GRAPH_URL}/{media_id}", headers=headers, timeout=30).json()
    file_bytes = requests.get(info["url"], headers=headers, timeout=60).content

    os.makedirs("incoming", exist_ok=True)
    extension = info.get("mime_type", "image/jpeg").split("/")[-1]
    path = os.path.join("incoming", f"{media_id}.{extension}")
    with open(path, "wb") as f:
        f.write(file_bytes)
    return path


def handle_vendor_message(message, vendor, intent):
    """Vendor side: the existing content pipeline, now only for new product photos."""
    sender = message["from"]

    if intent == NEW_PRODUCT_PHOTO:
        send_text(sender, "Got your photo! Give me a minute to work on it...")
        path = download_image(message["image"]["id"])
        print("Saved photo to:", path)

        sections = build_package(path)
        if sections is None:
            send_text(sender, "Sorry, my AI helper is busy right now. Please send your photo again in a few minutes.")
        else:
            for section in sections:
                send_text(sender, section)
    else:
        send_text(sender, f"Hi {vendor['business_name']}! Send me a photo of your perfume bottle and I'll create your captions, hashtags and flyer tips.")


def handle_customer_message(message, intent):
    """Customer side: placeholder until the customer agent is built."""
    print(f"Customer message from {message['from']} (intent: {intent}) - customer agent not built yet")
    send_text(message["from"], "Hi! This number is still being set up for orders. Please check back soon.")


def handle_message(message):
    """Runs in the background, AFTER Meta has already got its 200 OK."""
    sender = message["from"]
    try:
        route = route_message(message)
        print(f"Router: role={route['role']} intent={route['intent']}")

        if route["role"] == "vendor":
            handle_vendor_message(message, route["vendor"], route["intent"])
        else:
            handle_customer_message(message, route["intent"])
    except Exception as e:
        print("Error handling message:", e)
        send_text(sender, "Sorry, something went wrong. Please try again.")


@app.get("/webhook")
def verify_webhook(request: Request):
    """
    Meta calls this once, when you first connect your webhook, to confirm
    you actually control this URL. It sends a challenge code, and we must
    echo it back exactly to prove ownership.
    """
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)
    return {"error": "Verification failed"}


@app.post("/webhook")
async def receive_message(request: Request, background_tasks: BackgroundTasks):
    """
    Meta calls this every time a message arrives on your WhatsApp number.
    We answer 200 OK straight away, then do the slow work in the background.
    """
    data = await request.json()

    try:
        value = data["entry"][0]["changes"][0]["value"]
    except (KeyError, IndexError):
        return {"status": "ignored"}

    # Status notices (delivered/read) have no "messages", so this loop skips them
    for message in value.get("messages", []):
        msg_id = message["id"]
        if msg_id in processed_ids:
            continue
        processed_ids.add(msg_id)
        background_tasks.add_task(handle_message, message)

    return {"status": "received"}


@app.get("/")
def home():
    return {"status": "NaijaBrandAI is running"}