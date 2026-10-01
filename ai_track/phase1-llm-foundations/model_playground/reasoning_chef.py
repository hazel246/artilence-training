import time
import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from schemas import BenchMarkResult

# Load API keys from .env
load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)

MODEL = "openai/gpt-oss-120b"  # was deepseek-r1-distill-llama-70b (decommissioned)

SYSTEM_PROMPT = """You are a master AI research assistant.
Always break down your thinking logically before providing a concise final answer."""

USER_PROMPT = "Why is sky blue during the day and red during sunset?"

# Convert Pydantic model to JSON Schema for tool calling
form_schema = BenchMarkResult.model_json_schema()

print(f"Connecting to Groq ({MODEL}) with Pydantic validation...")

start_time = time.time()

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT},
    ],
    tools=[{
        "type": "function",
        "function": {
            "name": "record_benchmark",
            "description": "Fill out the benchmark response form",
            "parameters": form_schema,
        },
    }],
    tool_choice={"type": "function", "function": {"name": "record_benchmark"}},
    max_completion_tokens=2000,
)

elapsed_time = round(time.time() - start_time, 2)

# Extract the tool call arguments
message = response.choices[0].message
if not message.tool_calls:
    raise RuntimeError(f"No tool call returned. finish_reason: {response.choices[0].finish_reason}")

raw_data = json.loads(message.tool_calls[0].function.arguments)

# Validate into the Pydantic object
result = BenchMarkResult(**raw_data)

print(f"\nTime Taken: {elapsed_time} seconds")
print(f"Answer: {result.answer}")
print(f"Confidence: {result.confidence}")
print(f"Reasoning Steps: {result.reasoning_steps}")