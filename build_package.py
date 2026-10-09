import time
from agent import agent
from flyer_recommender import recommend_flyer
from posting_time import recommend_posting_time
from color_extractor import get_colors
from vision_tool import describe_image


def build_package(image_path):
    """
    Runs the full pipeline on one photo.
    Returns a list of text sections (captions, flyer, timing), or None if the AI failed.
    """
    # Step 1: let the agent gather colors, description, and hashtags, then write captions.
    # Retry loop since free-tier providers occasionally hit capacity limits.
    caption_result = None
    for attempt in range(3):
        try:
            caption_result = agent.run(
                f"Look at the product photo at '{image_path}'. Use your tools to get its dominant colors, "
                "a factual description, and relevant hashtags.\n\n"
                "Then write 3 short Instagram/TikTok captions in natural Nigerian English. "
                "Each caption must reference a specific real detail from the photo description "
                "(like the exact product name, bottle color, or packaging design) — do not write "
                "generic lines. Use Nigerian phrases like 'Owambe', 'Detty December', 'smell good', "
                "'you go love it' naturally, spread across the captions, not forced into every line.\n\n"
                "Give me a final answer with: the 3 captions, the hashtags, and the color palette, clearly labeled."
            )
            break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                print("Retrying in 10 seconds...")
                time.sleep(10)

    if caption_result is None:
        return None

    # Step 2: clean structured data for the flyer tool
    colors = get_colors(image_path)
    description = describe_image(image_path)

    # Step 3: flyer and timing tools, always needed
    flyer = recommend_flyer(colors, description)
    timing = recommend_posting_time()

    flyer_text = "\n".join(f"{key}: {value}" for key, value in flyer.items())
    timing_text = "\n".join(f"{key}: {value}" for key, value in timing.items())

    return [
        f"CAPTIONS, HASHTAGS & COLORS\n\n{caption_result}",
        f"FLYER RECOMMENDATION\n\n{flyer_text}",
        f"BEST POSTING TIME\n\n{timing_text}",
    ]


# This block only runs when you type `python build_package.py` yourself,
# never when main.py imports the file.
if __name__ == "__main__":
    sections = build_package("test.jpg")
    if sections is None:
        print("All attempts failed. Try running again in a few minutes.")
    else:
        print("\n\n".join(sections))