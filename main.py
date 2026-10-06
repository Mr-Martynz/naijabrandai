import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

VERIFY_TOKEN = "naijabrandai_verify_123"  # we'll explain this below

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")


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
async def receive_message(request: Request):
    """
    Meta calls this every time a message arrives on your WhatsApp number.
    For now, we just print what we receive so we can see the shape of the data.
    """
    data = await request.json()
    print("Received webhook data:")
    print(data)
    return {"status": "received"}


@app.get("/")
def home():
    return {"status": "NaijaBrandAI is running"}