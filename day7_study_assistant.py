import json
import os
from datetime import datetime
from openai import OpenAI

client = OpenAI()
MODEL = "gpt-4o-mini"


def save_session(session, folder="sessions"):
    os.makedirs(folder, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = os.path.join(folder, f"study_session_{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(session, f, ensure_ascii=False, indent=2)
    return path


def ask_ai(system_prompt, user_prompt):
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=500,
    )
    return resp.choices[0].message.content


def print_stats(session):
    quizzes = [x for x in session["items"] if x.get("type") == "quiz_take"]

    if not quizzes:
        print("\n📊 No quiz stats yet.\n")
        return

    total_s = 0
    total_t = 0
    for q in quizzes:
        s, t = q["score"].split("/")
        total_s += int(s)
        total_t += int(t)

    print("\n📊 Session Stats")
    print(f"- Quizzes taken: {len(quizzes)} | Total: {total_s}/{total_t}\n")


def menu():
    print("\n📚 Study Assistant")
    print("1) Explain a topic")
    print("2) Summarize text")
    print("3) Make a quiz (auto graded)")
    print("4) Exit (show stats + save)")
    return input("Choose (1-4): ").strip()


def main():
    system_prompt = "You are a helpful study assistant."

    session = {
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "items": []
    }

    while True:
        choice = menu()

        if choice == "1":
            topic = input("Topic: ").strip()
            prompt = f"Explain '{topic}' simply with an example."
            out = ask_ai(system_prompt, prompt)
            print("\n", out, "\n")

        elif choice == "2":
            text = input("Paste text:\n").strip()
            prompt = "Summarize this in 5 bullet points:\n\n" + text
            out = ask_ai(system_prompt, prompt)
            print("\n", out, "\n")

        elif choice == "3":
            topic = input("Quiz topic: ").strip()
            prompt = f"""
Create a 3-question quiz about {topic}.
Return ONLY valid JSON like this:
{{
  "questions": [
    {{
      "q": "question",
      "answer": "correct answer"
    }}
  ]
}}
"""
            raw = ask_ai(system_prompt, prompt)

            try:
                quiz = json.loads(raw)
            except Exception:
                print("❌ Failed to parse quiz.")
                # print(raw)  # uncomment to debug
                continue

            score = 0
            total = len(quiz["questions"])

            for i, q in enumerate(quiz["questions"], 1):
                print(f"Q{i}: {q['q']}")
                user = input("Your answer: ").strip().lower()
                correct = q["answer"].strip().lower()

                if user and (user in correct or correct in user):
                    print("✅ Correct\n")
                    score += 1
                else:
                    print(f"❌ Correct answer: {q['answer']}\n")

            print(f"🏁 Final Score: {score}/{total}\n")

            session["items"].append({
                "type": "quiz_take",
                "topic": topic,
                "score": f"{score}/{total}",
                "quiz": quiz
            })

        elif choice == "4":
            print_stats(session)
            path = save_session(session)
            print(f"✅ Session saved to: {path}\nGoodbye 👋")
            break

        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
