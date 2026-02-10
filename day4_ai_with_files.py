import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 1) Read file content
with open("notes.txt", "r") as f:
    file_text = f.read()

# 2) Send file content to AI
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Extracts 3 key bullet points, Then give one recommendation."},
        {"role": "user", "content": f"Summarize the following text:\n\n{file_text}"}
    ],
    max_tokens=150
)

# 3) Print AI output
print("=== AI Summary ===\n")
print(response.choices[0].message.content)
