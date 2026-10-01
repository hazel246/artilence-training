import time

import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from .env

MODEL = "claude-sonnet-5-5"


def get_weather(location: str) -> str:
    """Mock weather service returning weather details for a location."""
    mock_database = {
        "Tokyo": "Sunny, 22°C (72°F), Wind: 8 km/h",
        "New York": "Rainy, 14°C (57°F), Wind: 15 km/h",
        "London": "Cloudy, 16°C (61°F), Wind: 10 km/h",
    }
    return mock_database.get(location, f"Weather data unavailable for {location}.")


TOOL_FUNCTIONS = {"get_weather": get_weather}

# Claude uses "input_schema" instead of OpenAI's "function" wrapper
tools = [
    {
        "name": "get_weather",
        "description": "Get current weather conditions for a given city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city name, e.g., Tokyo, London",
                }
            },
            "required": ["location"],
        },
    }
]

USER_PROMPT = "What's the weather like in Tokyo right now?"
messages = [{"role": "user", "content": USER_PROMPT}]

start_time = time.time()

print("Step 1: Sending user query to model...")
response = client.messages.create(
    model=MODEL,
    max_tokens=1000,
    tools=tools,
    tool_choice={"type": "auto"},
    messages=messages,
)

if response.stop_reason != "tool_use":
    # The model answered directly without using the tool
    for block in response.content:
        if block.type == "text":
            print("Model did not request a tool. Answer:", block.text)
else:
    print("Model requested tool call(s)!")

    # Add the model's full response (including tool_use blocks) to history
    messages.append({"role": "assistant", "content": response.content})

    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            print(f"Function requested: {block.name}({block.input})")

            func = TOOL_FUNCTIONS.get(block.name)
            if func is None:
                tool_output = f"Unknown tool: {block.name}"
            else:
                tool_output = func(**block.input)
            print(f"Executed python function result: {tool_output}")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": tool_output,
            })

    # Tool results go back as a USER message
    messages.append({"role": "user", "content": tool_results})

    print("\nStep 2: Sending tool result back to model for final answer...")
    final_response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        tools=tools,  # must be included again because history contains tool blocks
        messages=messages,
    )
    for block in final_response.content:
        if block.type == "text":
            print(f"\nFinal Answer: {block.text}")

print(f"\nTotal time: {round(time.time() - start_time, 2)} seconds")