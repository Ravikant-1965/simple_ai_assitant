from openai import OpenAI

client = OpenAI(   # if the module is kept empty then it will automatically start calling a model
    base_url="http://127.0.0.1:11434/v1",  # here we specidied to call OLLAMA model
    api_key="dummy_key",
)


response = client.chat.completions.create( 
    model="qwen3:4b",
    messages=[
        {
            "role":"user",
            "content":"Hello LLM!"
        }
    ]
)

print("LLM response")
print(response)