import os
from openai import OpenAI

client = OpenAI()

# ----------------------------
# 1️⃣ Read File
# ----------------------------
def read_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print("❌ File not found. Please try again.")
        return None


# ----------------------------
# 2️⃣ Show Menu
# ----------------------------
def get_user_choice():
    print("\nChoose what you want the AI to do:")
    print("1 - Summarize")
    print("2 - Extract key points")
    print("3 - Analyze tone")
    print("4 - Custom task")

    return input("Enter your choice (1-4): ")


# ----------------------------
# 3️⃣ Build Prompt
# ----------------------------
def build_prompt(choice, text):

    if choice == "1":
        return "Summarize the following text:", text

    elif choice == "2":
        return "Extract the key points from the following text:", text

    elif choice == "3":
        return "Analyze the tone of the following text:", text

    elif choice == "4":
        custom = input("Enter your custom instruction: ")
        return custom, text

    else:
        print("Invalid choice.")
        return None, None


# ----------------------------
# 4️⃣ Ask AI
# ----------------------------
def ask_ai(system_instruction, user_text):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_text}
        ]
    )

    return response.choices[0].message.content


# ----------------------------
# 5️⃣ Save Output
# ----------------------------
def save_output(result):

    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    with open("outputs/result.txt", "a", encoding="utf-8") as file:
        file.write(result)
        file.write("\n\n------------------\n\n")


# ----------------------------
# 6️⃣ Main Function
# ----------------------------
def main():

    file_path = input("Enter file name (example: notes.txt): ")
    text = read_file(file_path)

    if text is None:
        return

    choice = get_user_choice()
    system_instruction, user_text = build_prompt(choice, text)

    if system_instruction is None:
        return

    print("\n⏳ Processing...\n")

    result = ask_ai(system_instruction, user_text)

    print("\n✅ Result:\n")
    print(result)

    save_output(result)


# ----------------------------
# Run Program
# ----------------------------
if __name__ == "__main__":
    main()
