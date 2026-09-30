from smolagents import tool, ToolCallingAgent, InferenceClientModel

from color_extractor import get_colors
from hashtag_lookup import get_hashtags
from vision_tool import describe_image


@tool
def extract_colors(image_path: str) -> dict:
    """
    Extracts the dominant color and a 5-color palette from a product photo, as hex codes.

    Args:
        image_path: The file path to the product photo.
    """
    return get_colors(image_path)


@tool
def lookup_hashtags(limit: int = 15) -> list:
    """
    Returns a curated list of Nigerian perfume-buyer hashtags.

    Args:
        limit: Maximum number of hashtags to return.
    """
    return get_hashtags(limit=limit)


@tool
def describe_photo(image_path: str) -> str:
    """
    Uses a vision AI model to describe what's in a product photo — the item, its color, and packaging style.

    Args:
        image_path: The file path to the product photo.
    """
    return describe_image(image_path)

import os
from dotenv import load_dotenv

load_dotenv()
hf_token = os.getenv("HF_TOKEN")

model = InferenceClientModel(
    model_id="Qwen/Qwen3-VL-8B-Instruct",
    provider="featherless-ai",
    token=hf_token,
)

agent = ToolCallingAgent(
    tools=[extract_colors, lookup_hashtags, describe_photo],
    model=model,
)

if __name__ == "__main__":
    result = agent.run(
        "You are creating a social media package for a Nigerian perfume vendor. "
        "Look at the product photo at 'test.jpg'. Use your tools to get its dominant colors, "
        "a factual description, and relevant hashtags.\n\n"
        "Then write 3 short Instagram/TikTok captions in natural Nigerian English. "
        "Each caption must reference a specific real detail from the photo description "
        "(like the exact product name, bottle color, or packaging design) — do not write "
        "generic lines. Use Nigerian phrases like 'Owambe', 'Detty December', 'smell good', "
        "'you go love am' naturally, spread across the captions, not forced into every line.\n\n"
        "Give me a final answer with: the 3 captions, the hashtags, and the color palette."
    )
    print(result)