import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
hf_token = os.getenv("HF_TOKEN")
client = InferenceClient(api_key=hf_token, provider="featherless-ai")


def generate_headline(description: str) -> str:
    """
    Generates a short, catchy flyer headline (not a caption) from a product description.
    """
    prompt = f"""Product description: {description}

Write ONE short, catchy flyer headline for this product — 3 to 6 words max.

Rules:
- Sell a FEELING or BENEFIT (confidence, attraction, luxury, status) — NOT a literal description of the product
- Do NOT repeat the brand name, bottle color, or packaging details from the description
- Think like an advertising slogan, not a product label

Examples of the right style: "Smell Like Royalty", "Your Signature Scent", "Confidence In A Bottle", "Turn Heads Everywhere"
Examples of the WRONG style (too literal): "Black Gold Perfume Bottle", "100ml Eau de Parfum"

Return ONLY the headline, nothing else."""

    completion = client.chat_completion(
        model="Qwen/Qwen3-VL-8B-Instruct",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=20,
    )
    return completion.choices[0].message.content.strip()


def recommend_flyer(colors: dict, description: str) -> dict:
    """
    Given extracted colors and a product description, suggests a flyer layout:
    background, accent, headline, text placement, and CTA.
    """
    dominant = colors["dominant_hex"]
    accent = colors["palette_hex"][0]
    headline = generate_headline(description)

    return {
        "background_color": dominant,
        "accent_color": accent,
        "headline": headline,
        "text_placement": f'"{headline}" top-center in bold, product photo centered, price bottom-left',
        "cta_placement": "Bottom-right, in accent color, bold text",
        "cta_example": "DM to order 📩 / Tap link in bio",
    }


if __name__ == "__main__":
    test_colors = {"dominant_hex": "#1d1d1c", "palette_hex": ["#d8c38f", "#1e1d1c", "#786338"]}
    test_description = "A 100ml black and gold Eau de Parfum bottle with Arabic calligraphy and a gold lion medallion."
    print(recommend_flyer(test_colors, test_description))