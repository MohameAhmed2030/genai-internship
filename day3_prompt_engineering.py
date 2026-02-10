import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ===== Prompt engineering rules =====
SYSTEM_PROMPT = """
You are a professional AI tutor.

Rules:
- Be concise
- Use bullet points
- Give ONE example only
- End with ONE short exercise
"""

def ask_ai(topic: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Teach this topic: {topic}"}
        ],
        max_tokens=200
    )
    return response.choices[0].message.content

print("Day 3 – Prompt Engineering Ready ✅")
print("Type a topic (or 'exit')\n")

while True:
    topic = input("Topic: ").strip()
    if topic.lower() in ("exit", "quit"):
        print("Good work today 👋")
        break

    print("\nAI Response:\n")
    print(ask_ai(topic))
    print("\n" + "-"*40 + "\n")
