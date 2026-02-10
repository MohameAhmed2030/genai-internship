import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

name1 = "Ahmed"
name2 = "Mohamed"

system_prompt = f"""
You are a friendly GenAI tutor.
Teach {name1} and {name2} in simple steps.
Always give:
1) short explanation
2) tiny example
3) 1-line exercise
"""

def ask_ai(q: str) -> str:
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": q},
        ],
    )
    return r.choices[0].message.content

print("Day 2 Chat Ready ✅ (type 'exit' to stop)\n")

while True:
    q = input("You: ").strip()
    if q.lower() in ("exit", "quit"):
        print("Bye 👋")
        break
    print("\nAI:\n", ask_ai(q), "\n")
