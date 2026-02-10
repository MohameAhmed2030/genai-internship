import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
Explains like you are 12

Always returns bullet points

Ends with one quiz question.

Rules:
- Be concise
- Use numbered steps
- If asked for code, return code only
- If asked for a table, return a markdown table
"""

def ask_ai(user_task: str) -> str:
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_task},
        ],
        max_tokens=300,
    )
    return r.choices[0].message.content

print("Day 5 Ready ✅ (type 'exit' to stop)\n")

while True:
    task = input("Task: ").strip()
    if task.lower() in ("exit", "quit"):
        print("Nice work today 👋")
        break
    print("\nAI:\n")
    print(ask_ai(task))
    print("\n" + "-"*40 + "\n")
