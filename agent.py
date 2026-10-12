from dotenv import load_dotenv
from smolagents import tool, ToolCallingAgent, OpenAIModel

from color_extractor import get_colors
from hashtag_lookup import get_hashtags
from vision_tool import describe_image
from rag_tools import find_similar_caption
from llm_client import BASE_URL, GEMINI_API_KEY, get_model_name


# These three tools are kept so the agent CAN fetch the facts itself if we ever want it to.
# Today build_package.py fetches them in plain code (always needed, no judgment required),
# so they are not registered below. That saves several paid round trips per photo.
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

model = OpenAIModel(
    model_id=get_model_name(),
    api_base=BASE_URL,
    api_key=GEMINI_API_KEY,
)

# The caption agent's real job: look up past captions for style, then write the new ones.
# max_steps stops a confused run from looping, since every step is a paid model call.
agent = ToolCallingAgent(
    tools=[find_similar_caption],
    model=model,
    max_steps=4,
)


if __name__ == "__main__":
    result = agent.run(
        "A bottle of perfume in black and gold packaging with a lion emblem. "
        "Call find_similar_caption once with that description, then write 2 short captions in "
        "Nigerian English that match the style of the past captions."
    )
    print(result)