import os
import base64
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from color_extractor import get_colors
from hashtag_lookup import get_hashtags
from vision_tool import describe_image

load_dotenv()
hf_token = os.getenv("HF_TOKEN")
client = InferenceClient(api_key=hf_token, provider="featherless-ai")

def generate_package(image_path):
    # Gather real data from our three tools
    colors = get_colors(image_path)
    hashtags = get_hashtags(limit=15)
    description = describe_image(image_path)

    prompt = f"""You are a Nigerian social media assistant for perfume vendors.

Photo description: {description}
Dominant colors: {colors['dominant_hex']} (palette: {', '.join(colors['palette_hex'])})

Write 3 short Instagram/TikTok captions in natural Nigerian English for this product. Use authentic Nigerian phrases naturally (like "Owambe," "Detty December," "you go love it," "smell good") — don't force all of them into every caption. Number them 1-3."""

    completion = client.chat_completion(
        model="Qwen/Qwen3-VL-8B-Instruct",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    captions = completion.choices[0].message.content

    return {
        "description": description,
        "colors": colors,
        "hashtags": hashtags,
        "captions": captions,
    }

if __name__ == "__main__":
    result = generate_package("test.jpg")
    print("\n--- CAPTIONS ---")
    print(result["captions"])
    print("\n--- HASHTAGS ---")
    print(" ".join(result["hashtags"]))
    print("\n--- COLORS ---")
    print(result["colors"])