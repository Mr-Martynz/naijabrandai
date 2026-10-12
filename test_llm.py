import sys

from llm_client import chat, get_client, get_model_name, image_to_data_url

if len(sys.argv) > 1 and sys.argv[1] == "models":
    # Lists every model your key can use. Pick one and put it in .env as GEMINI_MODEL
    for m in get_client().models.list():
        print(m.id)
else:
    print("Model:", get_model_name())

    print("\n1) Text test...")
    print("   Answer:", chat([{"role": "user", "content": "Reply with exactly one word: ready"}], max_tokens=200))

    print("\n2) Vision test with test.jpg...")
    answer = chat([{
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this product photo in one short sentence."},
            {"type": "image_url", "image_url": {"url": image_to_data_url("test.jpg")}},
        ],
    }])
    print("   Answer:", answer)

    print("\nAll good!")