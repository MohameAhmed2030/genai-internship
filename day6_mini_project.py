import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def ask_ai(task: str, text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that works with documents."},
            {"role": "user", "content": f"{task}\n\nTEXT:\n{text}"}
        ],
        max_tokens=250
    )
    return response.choices[0].message.content

print("📄 Day 6 Mini Project – Document Tool")
file_path = input("Enter text file name (example: notes.txt): ").strip()

text = read_file(file_path)

print("\nChoose an action:")
print("1 - Summarize")
print("2 - Extract key points")
print("3 - Rewrite in simple language")
print("4 - Translate to swedish")
print("5 - Is it written b human or AI")

choice = input("Your choice: ").strip()

if choice == "1":
    task = "Summarize this document."
elif choice == "2":
    task = "Extract 5 key bullet points from this document."
elif choice == "3":
    task = "Rewrite this document in very simple language."
elif choice == "4":
    task = "Translate to swedish."
elif choice == "5":
    task = "Check if this text is written by human or AI."



else:
    print("Invalid choice")
    exit()

result = ask_ai(task, text)
print("\n=== AI OUTPUT ===\n")
print(result)
