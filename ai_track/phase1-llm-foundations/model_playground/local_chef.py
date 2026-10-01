

import time
import json

from openai import OpenAI

from schemas import BenchMarkResult

# Point to Ollama's local server (no real API key needed)
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

MODEL = "llama3.2"

# Identical system and user prompts to the other chefs
SYSTEM_PROMPT = """You are a master AI research assistant.
Always break down your thinking logically before providing a concise final answer.
You must give your final answer by calling the record_benchmark tool."""

USER_PROMPT = "Why is sky blue during the day and red during sunset?"

# Convert Pydantic form to JSON Schema
form_schema = BenchMarkResult.model_json_schema()

print(f"Connecting to local model (Ollama / {MODEL}) with Pydantic validation...")

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
)

elapsed_time = round(time.time() - start_time, 2)

# Extract tool arguments
message = response.choices[0].message
if not message.tool_calls:
    raise RuntimeError(f"Model did not call the tool. It said: {message.content}")

raw_data = json.loads(message.tool_calls[0].function.arguments)

# Validate into Pydantic model
result = BenchMarkResult(**raw_data)

print(f"\nTime Taken: {elapsed_time} seconds")
print(f"Answer: {result.answer}")
print(f"Confidence: {result.confidence}")
print(f"Reasoning Steps: {result.reasoning_steps}")