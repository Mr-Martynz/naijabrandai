# NaijaBrandAI

An agentic AI tool for Nigerian perfume vendors. A vendor sends a bottle photo via WhatsApp and gets back:
- 3 culturally resonant Instagram/TikTok captions in Nigerian English
- 10-15 local hashtags Nigerian perfume buyers actually search
- A flyer layout recommendation (colors, text placement, CTA)
- Best time to post for a Nigerian audience

## Why "agentic" and not just one AI call

Instead of one AI call doing everything, this is built as an agent with separate tools:
- **Color extractor** (done) — pure Python, reads the actual photo and pulls real dominant colors, so flyer suggestions are grounded in the real image, not guessed
- **Hashtag lookup** (not started) — a curated list the agent queries, more reliable than an LLM inventing hashtags
- **Caption generator** (not started) — a vision LLM, responsible only for the creative writing part
- **The agent itself** (not started) — built with smolagents, decides which tools to call and in what order

## Current status

- [x] Project environment set up (venv, requirements.txt)
- [x] Tool 1: color extractor — takes an image, returns dominant color + palette as hex codes
- [ ] Tool 2: hashtag lookup
- [ ] Vision model wired up (starting with free Hugging Face models, swapping to a paid API later for real vendors)
- [ ] Agent built with smolagents to tie tools together
- [ ] Local end-to-end test
- [ ] WhatsApp integration (Meta Cloud API)
- [ ] Vendor tracking + Paystack payment gate

## Setup

\`\`\`
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
\`\`\`