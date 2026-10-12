import time

from agent import agent
from color_extractor import get_colors
from flyer_recommender import recommend_flyer
from hashtag_lookup import get_hashtags
from llm_client import is_retryable
from posting_time import recommend_posting_time
from vision_tool import describe_image


def build_package(image_path):
    """
    Runs the full pipeline on one photo.
    Returns a list of text sections (captions, flyer, timing), or None if the AI failed.
    """
    # Step 1: gather the facts in plain code. They are needed for every photo, so no AI
    # decision is involved, and doing it here saves several paid round trips.
    colors = get_colors(image_path)
    hashtags = get_hashtags(limit=15)
    description = describe_image(image_path)  # one AI call, remembered for later steps

    # Step 2: the agent's real job: look up past captions for style, then write the new ones.
    task = f"""Product photo description: {description}
Dominant colors: {colors['dominant_hex']} (palette: {', '.join(colors['palette_hex'])})

First, call find_similar_caption once with the description above, to see how captions for similar photos were written.

Then write 3 short Instagram/TikTok captions in natural Nigerian English. Each caption must reference a specific real detail from the description (like the exact product name, bottle color, or packaging design) — do not write generic lines. Use Nigerian phrases like 'Owambe', 'Detty December', 'smell good', 'you go love it' naturally, spread across the captions, not forced into every line. Match the style of the past captions, but do not copy them or mention their product names.

Do not put hashtags inside the captions. Your final answer must be ONLY the 3 numbered captions, nothing else."""

    # Retry only on temporary errors (429 slow down, 5xx server trouble, network hiccups).
    # Billing, bad key and forbidden errors would fail again, so we stop straight away.
    caption_result = None
    for attempt in range(3):
        try:
            caption_result = agent.run(task)
            break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if not is_retryable(e):
                print("This error would fail again, so I'm not retrying.")
                break
            if attempt < 2:
                delay = 5 * 2 ** attempt  # 5 seconds, then 10
                print(f"Temporary error. Retrying in {delay} seconds...")
                time.sleep(delay)

    if caption_result is None:
        return None

    # Step 3: flyer and timing, always needed
    flyer = recommend_flyer(colors, description)
    timing = recommend_posting_time()

    flyer_text = "\n".join(f"{key}: {value}" for key, value in flyer.items())
    timing_text = "\n".join(f"{key}: {value}" for key, value in timing.items())

    # Hashtags and colors come straight from our own tools, so they are always correct,
    # and the AI only has to write the captions.
    captions_text = (
        f"CAPTIONS\n\n{str(caption_result).strip()}\n\n"
        f"HASHTAGS\n{' '.join(hashtags)}\n\n"
        f"COLOR PALETTE\nDominant: {colors['dominant_hex']}\nPalette: {', '.join(colors['palette_hex'])}"
    )

    return [
        captions_text,
        f"FLYER RECOMMENDATION\n\n{flyer_text}",
        f"BEST POSTING TIME\n\n{timing_text}",
    ]


# This block only runs when you type `python build_package.py` yourself,
# never when main.py imports the file.
if __name__ == "__main__":
    sections = build_package("test.jpg")
    if sections is None:
        print("The AI step failed. See the messages above for why.")
    else:
        print("\n\n".join(sections))