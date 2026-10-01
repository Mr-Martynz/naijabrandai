import os
from dotenv import load_dotenv
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
    # Simple standalone test of just the agent + its 3 tools.
    # The full package (adding flyer + posting time) lives in build_package.py
    result = agent.run(
        "Look at the product photo at 'test.jpg'. Use your tools to get its colors, "
        "a description, and relevant hashtags. Give me a final answer with all three, clearly labeled."
    )
    print(result)