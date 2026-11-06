import os

def log(text):
    if os.getenv("DEBUG") == "True":
        print(f"  LOG: {text}")
    return None
