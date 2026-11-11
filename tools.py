from datetime import datetime
import requests
import json
from Utilities.utilities import log

# 1. Actual Python function definition
# This is the real code that runs locally on our machine when called.
def get_current_time():
    return datetime.now().strftime("%Y %m %d %H %M %S")

def get_city_weather(city):
    url = f"https://wttr.in/{city}?format=3"
    response = requests.get(url, timeout=5)
    response.raise_for_status() # this raises an HTTPError for bad responses (4xx or 5xx)
    return response.text
    

def search_knowledge_base(query):
    results = search(query, top_k=2)

    log(f"📚 Knowledge base search: {query}")
    for r in results:
        log(f"   {r['score']:.2f} - {r['source']} #{r['chunk_id']}")

    blocks = []
    for r in results:
        sourceFileName = r['source']
        chunkId        = r['chunk_id']
        chunkText      = r['text']

        header = f"[{sourceFileName} #{chunkId}]"
        block  = f"{header}\n{chunkText}"
        blocks.append(block)

    return "\n\n".join(blocks)



# 2. TOOLS Definition (JSON Schema for the LLM)
# The LLM cannot read Python code directly. We provide this specification (schema)
# to tell the LLM:
#   - What tools are available (name)
#   - What each tool does (description) -> The LLM uses this to decide WHEN to call the tool
#   - What inputs/parameters the tool expects (parameters schema)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get current time and date",
            "parameters": {
                "type": "object",
                "properties": {},  # Empty because get_current_time takes no arguments
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_city_weather",
            "description": "Get the weather of a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description" : "Searches the Zorvex Technologies company knowledge base: leave, medical, HR, hiring, tech, incident "
                            "reports and travel expense policies. Use it for any question about company policies or documents. "
                            "Returns the most relevant passages with their source.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's question, rewritten as a short, self-contained search query.",
                    }
                },
                "required": ["query"],
            },
        },
    },
]


# 3. Function Dispatch Map
# The LLM only returns the name of the function as a STRING (e.g., "get_current_time").
# In Python, you cannot call a string directly like "get_current_time"().
# This dictionary maps the string name to the actual Python function reference.
FUNCTION_NAME_TO_FUNCTION_MAP = {
    "get_current_time": get_current_time,
    "get_city_weather": get_city_weather,
    "search_knowledge_base" : search_knowledge_base,
}




def execute_tool_call(tool_call):
    func_name = tool_call.function.name
    func_args = {}

    try:
        func_args = json.loads(tool_call.function.arguments or "{}")
        log(f"Executing {func_name} with arguments: {func_args}")

        fn = FUNCTION_NAME_TO_FUNCTION_MAP[func_name]

        result = fn(**func_args)
    
    except Exception as e :
        result = f"Error while running {func_name} : {e}"

    log(f"Tool: '{func_name}' Execution Result: '{result}'")

    return str(result)