import os
import base64
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
hf_token = os.getenv("HF_TOKEN")

client = InferenceClient(api_key=hf_token, provider="featherless-ai")

def describe_image(image_path):
    # Read the image file and convert it to base64 text,
    # since we're sending a local file, not a web URL
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:image/jpeg;base64,{base64_image}"

    completion = client.chat_completion(
        model="Qwen/Qwen3-VL-8B-Instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this product photo in one factual sentence — what it is, its color, and its packaging style."},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
        max_tokens=100,
    )
    return completion.choices[0].message.content

if __name__ == "__main__":
    description = describe_image("test.jpg")
    print("Image description:", description)