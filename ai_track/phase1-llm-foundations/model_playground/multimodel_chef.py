import base64
import mimetypes
import time

import anthropic
from dotenv import load_dotenv

from schemas import MultimodalResult

load_dotenv()

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from your .env

MODEL = "claude-sonnet-5-5"

# IMAGE_SOURCE = IMAGE_URL
IMAGE_SOURCE = "images.png"

SYSTEM_PROMPT = """You are a careful vision assistant.
You must give your final answer by calling the record_image_analysis tool. Do not reply with plain text only."""

USER_PROMPT = "Describe this image in detail and extract key observable visual elements or fields."


def build_image_block(source: str) -> dict:
    """Return an image content block from either a URL or a local file path."""
    if source.startswith("http"):
        return {"type": "image", "source": {"type": "url", "url": source}}

    mime, _ = mimetypes.guess_type(source)
    with open(source, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")
    return {
        "type": "image",
        "source": {"type": "base64", "media_type": mime or "image/jpeg", "data": data},
    }


form_schema = MultimodalResult.model_json_schema()

print(f"Connecting to multimodal model ({MODEL})...")
start_time = time.time()

response = client.messages.create(
    model=MODEL,
    max_tokens=1500,
    system=SYSTEM_PROMPT,
    messages=[
        {
            "role": "user",
            "content": [
                build_image_block(IMAGE_SOURCE),  # image first, then the text
                {"type": "text", "text": USER_PROMPT},
            ],
        }
    ],
    tools=[{
        "name": "record_image_analysis",
        "description": "Record the structured analysis of the image",
        "input_schema": form_schema,
    }],
    tool_choice={"type": "auto"},  # forced tool_choice was rejected earlier
)

elapsed_time = round(time.time() - start_time, 2)

# Find the tool_use block (with "auto", content[0] may be plain text)
raw_data = None
for block in response.content:
    if block.type == "tool_use" and block.name == "record_image_analysis":
        raw_data = block.input
        break

if raw_data is None:
    raise RuntimeError(f"Model did not call the tool. stop_reason: {response.stop_reason}")

result = MultimodalResult(**raw_data)

print(f"\nTime Taken: {elapsed_time} seconds")
print(f"Description: {result.image_description}")
print(f"Extracted Fields: {result.extracted_fields}")
print(f"Confidence: {result.confidence}")