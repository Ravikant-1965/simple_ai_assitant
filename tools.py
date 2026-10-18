from datetime import datetime
import requests

# 1. Actual Python function definition
# This is the real code that runs locally on our machine when called.
def get_current_time():
    return datetime.now().strftime("%Y %m %d %H %M %S")

def get_city_weather(city):
    url = f"https://wttr.in/{city}?format=3"
    response = requests.get(url, timeout=5)
    return response.text
    

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
                }
            }
        }
    }
]


# 3. Function Dispatch Map
# The LLM only returns the name of the function as a STRING (e.g., "get_current_time").
# In Python, you cannot call a string directly like "get_current_time"().
# This dictionary maps the string name to the actual Python function reference.
FUNCTION_NAME_TO_FUNCTION_MAP = {
    "get_current_time": get_current_time,
    "get_city_weather": get_city_weather,
}