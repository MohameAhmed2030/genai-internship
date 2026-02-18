import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_chat(system_prompt: str):
    return [{"role": "system", "content": system_prompt}]

def chat_with_ai(messages, user_input):
    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=300
    )

    ai_reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": ai_reply})

    return ai_reply

def main():
    print("🤖 Day 7 Smart Chat Assistant")
    print("Type 'reset' to restart conversation.")
    print("Type 'exit' to quit.\n")

    system_prompt = """
You are a helpful AI tutor.

If a question depends on current events or information after 2023,
clearly state that your knowledge may be outdated and suggest verifying online.
Be honest about knowledge limits.
"""

    messages = create_chat(system_prompt)

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Goodbye, Ha det bra 👋 !!")
            break

        if user_input.lower() == "reset":
            messages = create_chat(system_prompt)
            print("🔄 Conversation reset!\n")
            continue

        reply = chat_with_ai(messages, user_input)
        print("AI:", reply, "\n")

if __name__ == "__main__":
    main()
