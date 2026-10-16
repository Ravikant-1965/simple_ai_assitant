from openai import OpenAI
from dotenv import load_dotenv
import json

from tools import TOOLS, FUNCTION_NAME_TO_FUNCTION_MAP

import os

load_dotenv() #by default looks for .env file

client = OpenAI(   # if the module is kept empty then it will automatically start calling a model
    base_url=os.getenv("BASE_URL"),  # here we specidied to call OLLAMA model
    api_key=os.getenv("API_KEY"),
)


messages = []

messages.append(
    {
        "role":"system",
        "content":"You are humble assitant. Resopond within 20 words"
    }
)

while True:
    user_input = input("Ravi: ")

    if user_input.lower() in ["exit", "bye", "quit"]:
        break

    messages.append(
        {
            "role":"user",
            "content":user_input
        }
    )

    # --- STEP 1: First call to the LLM (with tools schema provided) ---
    # We pass `tools=TOOLS` so the LLM is aware of available external tools.
    # The LLM doesn't execute the code itself; it only decides IF a tool is needed.
    response = client.chat.completions.create( 
        model=os.getenv("MODEL"),
        messages=messages,
        tools=TOOLS
    )

    msg = response.choices[0].message

    # --- STEP 2: Check if the LLM decided to call any tools ---
    # If the user asks a normal question ("Hello"), msg.tool_calls is None.
    # If the LLM needs external data, msg.tool_calls will contain a list of tool calls.
    if msg.tool_calls:
        # Why append msg?
        # In the OpenAI/Ollama API protocol, whenever you return tool outputs,
        # the conversation history MUST include the assistant message that requested those tools.
        # Otherwise, the API throws an error: "Invalid message: tool response without matching tool call".
        messages.append(msg)

        # Why a for-loop?
        # 1. Models support "Parallel Tool Calling" - the LLM may decide to call
        #    multiple tools at the same time (e.g., getting weather for two cities).
        # 2. `msg.tool_calls` is always a list, so iterating ensures we execute every tool requested.
        for tool_call in msg.tool_calls:
            # The model gives us the function name as a string (e.g. "get_current_time")
            func_name = tool_call.function.name

            # Why json.loads()?
            # The LLM returns arguments as a serialized JSON string (e.g. '{"city": "Paris"}').
            # `json.loads` parses that string into a real Python dictionary.
            # Why `or "{}"`?
            # If the tool has no parameters, the model may return None or an empty string `""`.
            # Calling `json.loads("")` causes a JSONDecodeError crash, so `or "{}"` acts as a safe fallback.
            func_args = json.loads(tool_call.function.arguments or "{}")

            # Look up the actual Python function using the dispatch dictionary
            fn = FUNCTION_NAME_TO_FUNCTION_MAP[func_name]

            # Why `**` before func_args?
            # `**` is Python's dictionary unpacking operator (keyword argument unpacking).
            # It takes `{ "param1": val1, "param2": val2 }` and passes them as `fn(param1=val1, param2=val2)`.
            # For functions with no arguments (empty dict `{}`), `fn(**{})` simply executes `fn()`.
            # Without `**`, calling `fn(func_args)` would pass the dictionary as a single positional parameter,
            # causing a TypeError: fn() takes 0 positional arguments but 1 was given.
            result = fn(**func_args)

            # --- STEP 3: Return the tool execution result back to the conversation ---
            messages.append(
                {
                    # "role": "tool" tells the model this message contains output from a tool execution
                    "role": "tool",
                    # "tool_call_id" links this result back to the specific tool request ID from the LLM
                    "tool_call_id": tool_call.id,
                    # Why str(result)? The API expects `content` to be a string.
                    # Functions can return ints, datetimes, objects, or lists; str() safely turns it to text.
                    "content": str(result)
                }
            )

        # --- STEP 4: Second call to the LLM API ---
        # Why a second call?
        # The first call only decided *which* tool to call.
        # Now that we've run the tool locally and appended the tool's result to `messages`,
        # this second call gives the LLM the answer so it can formulate a natural conversational reply.
        response_2 = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messages
        )

        # Overwrite `msg` with the final response from the second call
        msg = response_2.choices[0].message

    # Save the final assistant answer into the conversation history
    messages.append(
        {
            "role": "assistant",
            "content": msg.content
        }
    )

    # Print the final assistant response to the user
    print(f"AI: {msg.content}")

        
