import time
from agent import agent
from flyer_recommender import recommend_flyer
from posting_time import recommend_posting_time
from color_extractor import get_colors
from vision_tool import describe_image

IMAGE_PATH = "test.jpg"

# Step 1: let the agent gather colors, description, and hashtags, then write captions.
# Wrapped in a retry loop since free-tier providers occasionally hit capacity limits.
caption_result = None
for attempt in range(3):
    try:
        caption_result = agent.run(
            f"Look at the product photo at '{IMAGE_PATH}'. Use your tools to get its dominant colors, "
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
    print("All attempts failed. Try running again in a few minutes.")
    exit()

# Step 2: get colors and description again directly, so we have clean structured
# data to feed the flyer tool (rather than parsing it back out of agent text).
colors = get_colors(IMAGE_PATH)
description = describe_image(IMAGE_PATH)

# Step 3: call flyer and timing tools directly — always needed, no judgment required.
flyer = recommend_flyer(colors, description)
timing = recommend_posting_time()

print("\n" + "=" * 50)
print("CAPTIONS, HASHTAGS & COLORS (from agent):")
print("=" * 50)
print(caption_result)

print("\n" + "=" * 50)
print("FLYER RECOMMENDATION:")
print("=" * 50)
for key, value in flyer.items():
    print(f"{key}: {value}")

print("\n" + "=" * 50)
print("BEST POSTING TIME:")
print("=" * 50)
for key, value in timing.items():
    print(f"{key}: {value}")