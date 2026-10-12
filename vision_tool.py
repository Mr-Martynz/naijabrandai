import os

from llm_client import chat, image_to_data_url

# Remember descriptions so the same photo is never described twice.
# The key includes the file's last-modified time, so a replaced file gets a fresh description.
_description_cache = {}


def _ask_model(image_path):
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this product photo in one factual sentence — what it is, its color, and its packaging style."},
                {"type": "image_url", "image_url": {"url": image_to_data_url(image_path)}},
            ],
        }
    ]
    return chat(messages, max_tokens=1024)


def describe_image(image_path):
    key = (os.path.abspath(image_path), os.path.getmtime(image_path))
    if key not in _description_cache:
        _description_cache[key] = _ask_model(image_path)
    return _description_cache[key]


if __name__ == "__main__":
    description = describe_image("test.jpg")
    print("Image description:", description)