#standard library Imports
import os
from types import SimpleNamespace
# Third party imports
from openai import OpenAI
from dotenv import load_dotenv
# Local Module imports
from tools import TOOLS, execute_tool_call
from Utilities.utilities import log


load_dotenv() #by default looks for .env file

client = OpenAI(   # if the module is kept empty then it will automatically start calling a model
    base_url=os.getenv("BASE_URL"),  # here we specidied to call OLLAMA model
    api_key=os.getenv("API_KEY"),
)

messages = []

messages.append(
    {
        "role":"system",
        "content":"You are humble assitant. Resopond within 100 words"
    }
)


def stream_chat(history):
    
    stream = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=history,
        tools=TOOLS,
        stream=True,
    )
    
    full_response = ""
    calls = {}
    label_printed = False

    for chunk in stream:
        if not chunk:
            continue

        delta = chunk.choices[0].delta
        
        #1. Content Streaming : Do we have content from the LLM
        if delta.content:

            if not label_printed:
                print("AI: ", end="", flush=True)
                label_printed = True

            print(delta.content, end="", flush=True)
            full_response += delta.content


        #2. Tool Calls : Is the LLM asking you to call a tool
        for tc in (delta.tool_calls or []):
            obj = calls.setdefault(
                tc.index,
                SimpleNamespace(id=None, function=SimpleNamespace(name="", arguments="")),
            )
            if tc.id:
                obj.id = tc.id
            if tc.function and tc.function.name:
                obj.function.name += tc.function.name
            if tc.function and tc.function.arguments:
                obj.function.arguments += tc.function.arguments


    if label_printed:
        print()

    calls_list = []
    for key in sorted(calls):
        calls_list.append(calls[key])
    return full_response, calls_list


def build_tool_calls_payload(tool_calls):
    
    """
    builds are collected tool calls into the dict format
    that the API expexts inside an assitant message.
    """
    payload = []
    for tool_call in tool_calls:

        payload.append(
            {
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                }
            }
        )
    return payload



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

    MAX_STEPS = 5

    #chained tool calling
    try :
        for steps in range(MAX_STEPS):

            full_response, tool_calls = stream_chat(messages)

            if not tool_calls:
                break


            log(f"Step {steps+1}: model requested {len(tool_calls)} tool calls")
            

            messages.append({
                "role": "assistant",
                "content": full_response,
                "tool_calls": build_tool_calls_payload(tool_calls)
            })

            for tool_call in tool_calls:

                result = execute_tool_call(tool_call)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)
                    }
                )
        else:
            fallback = "Sorry i couldn't finish this within the steps limit"
            messages.append({
                "role":"assistant",
                "content":fallback
            })

            print(f"AI:{fallback}")
            continue

    except KeyboardInterrupt:
        print("\nAI: Exiting...(Stopped by User)")
        calls = {}
        break

    
