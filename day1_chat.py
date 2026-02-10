import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a friendly assistant."},
        {"role": "user", "content": "Say hello to Ahmed and Mohamed and congratulate them on finishing Day 1."}
    ]
)

print(response.choices[0].message.content)
