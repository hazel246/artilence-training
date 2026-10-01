import time
import anthropic
from schemas import BenchMarkResult
from dotenv import load_dotenv

load_dotenv()

# 1. Initialize the claude client (phone line to anthropic)
client = anthropic.Anthropic()

# 2. System prompt and User prompt
SYSTEM_PROMPT = """You are a master AI research assistant.
Always break down your thinking logically before providing a concise final answer.
You must give your final answer by calling the record_benchmark tool. Do not reply with plain text only."""

USER_PROMPT = "Why is sky blue during the day and red during sunset?"

# 3. Convert our Pydantic magic form into JSON form for Claude
form_schema = BenchMarkResult.model_json_schema()

# 4. Start the timer!
start_time = time.time()

# 5. Send the order to chef 1
response = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=1000,
    system=SYSTEM_PROMPT,
    messages=[{"role": "user", "content": USER_PROMPT}],
    tools=[{
        "name": "record_benchmark",
        "description": "Fill out the benchmark response form",
        "input_schema": form_schema,
    }],
    tool_choice={"type": "auto"},  # was {"type": "tool", "name": "record_benchmark"}
)

# 6. Stop the timer!
elapsed_time = round(time.time() - start_time, 2)

# 7. Extract the filled-out form from Claude's response
# With "auto", content[0] might be a text block, so search for the tool_use block
raw_data = None
for block in response.content:
    if block.type == "tool_use" and block.name == "record_benchmark":
        raw_data = block.input  # a raw python dictionary {}
        break

if raw_data is None:
    raise RuntimeError(f"Model did not call the tool. stop_reason: {response.stop_reason}")

# Convert the raw dictionary back into our pydantic object!
result = BenchMarkResult(**raw_data)

# 8. Print our clean results!
print(f"Time Taken: {elapsed_time} seconds")
print(f"Answer: {result.answer}")
print(f"Confidence: {result.confidence}")
print(f"Reasoning Steps: {result.reasoning_steps}")