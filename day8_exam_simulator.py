import json
import os
import time
from datetime import datetime
from openai import OpenAI

client = OpenAI()
MODEL = "gpt-4o-mini"

# ===============================
# Save Report
# ===============================
def save_report(report, folder="exam_reports"):
    os.makedirs(folder, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = os.path.join(folder, f"exam_report_{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return path


# ===============================
# OpenAI Call
# ===============================
def ask_ai(system_prompt, user_prompt, max_tokens=900):
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content


# ===============================
# Generate Exam
# ===============================
def generate_exam(topic: str, n: int, mcq_ratio: float):
    system_prompt = "You create strict JSON only. No extra text."

    prompt = f"""
Create an exam on: {topic}

Return ONLY valid JSON exactly like:
{{
  "topic": "{topic}",
  "questions": [
    {{
      "type": "mcq",
      "q": "question text",
      "choices": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "answer": "A",
      "skill": "concepts"
    }},
    {{
      "type": "short",
      "q": "question text",
      "answer": "short correct answer",
      "skill": "definitions"
    }},
    {{
      "type": "essay",
      "q": "essay question",
      "answer": "model answer",
      "skill": "examples"
    }}
  ]
}}

Rules:
- Total questions = {n}
- MCQ ratio approx = {mcq_ratio}
- If ratio = 0 → generate exactly ONE essay question
- skill must be one of: concepts, definitions, examples, problem_solving
"""

    raw = ask_ai(system_prompt, prompt)

    try:
        return json.loads(raw), raw
    except Exception:
        raise ValueError("Model returned invalid JSON.\n\nRAW:\n" + raw[:1500])


# ===============================
# Grading Functions
# ===============================
def grade_mcq(user, correct):
    return user.strip().upper() == correct.strip().upper()


def grade_short(user, correct):
    user = user.strip().lower()
    correct_l = correct.strip().lower()

    if not user:
        return False

    keywords = [w for w in correct_l.split() if len(w) > 3][:4]
    return all(k in user for k in keywords) if keywords else (user == correct_l)


def grade_essay_with_ai(question, student_answer):
    system_prompt = "You are a strict academic writing examiner. Return strict JSON only."

    prompt = f"""
Evaluate this essay using IELTS-style rubric (0-9 scale).

Question:
{question}

Student Essay:
{student_answer}

Return ONLY valid JSON like:
{{
  "band_score": 0,
  "task_response": 0,
  "coherence": 0,
  "lexical_resource": 0,
  "grammar": 0,
  "feedback": "Detailed feedback"
}}
"""

    raw = ask_ai(system_prompt, prompt, max_tokens=700)

    try:
        return json.loads(raw)
    except:
        return {
            "band_score": 0,
            "task_response": 0,
            "coherence": 0,
            "lexical_resource": 0,
            "grammar": 0,
            "feedback": "Failed to parse evaluation."
        }


# ===============================
# Run Exam
# ===============================
def run_exam(exam, minutes: int):
    start = time.time()
    deadline = start + minutes * 60

    results = []
    score = 0

    print(f"\n🧪 EXAM STARTED: {exam.get('topic','')}")
    print(f"⏳ Time limit: {minutes} minutes")
    print("Type 'skip' to skip a question.\n")

    for i, q in enumerate(exam["questions"], 1):

        if time.time() > deadline:
            print("\n⏰ Time is up!\n")
            break

        print(f"Q{i}: {q['q']}")
        qtype = q["type"]

        essay_feedback = None
        correct_flag = False

        if qtype == "mcq":
            for c in q["choices"]:
                print(" ", c)

            user = input("Answer (A/B/C/D or skip): ").strip()

            if user.lower() != "skip":
                correct_flag = grade_mcq(user, q["answer"])

        elif qtype == "short":
            user = input("Answer (or skip): ").strip()

            if user.lower() != "skip":
                correct_flag = grade_short(user, q["answer"])

        elif qtype == "essay":
            user = input("Write your essay (or skip):\n").strip()

            if user.lower() != "skip":
                essay_feedback = grade_essay_with_ai(q["q"], user)
                correct_flag = True  # Essay doesn't use right/wrong

        else:
            user = input("Answer: ").strip()

        if qtype != "essay":
            if correct_flag:
                score += 1
                print("✅ Correct\n")
            else:
                print(f"❌ Correct answer: {q['answer']}\n")
        else:
            print("📝 Essay submitted for AI evaluation...\n")

        results.append({
            "q": q["q"],
            "type": qtype,
            "skill": q.get("skill", "unknown"),
            "user_answer": user,
            "correct_answer": q["answer"],
            "correct": correct_flag,
            "essay_evaluation": essay_feedback
        })

    total = len(results)
    return score, total, results


# ===============================
# Skill Breakdown
# ===============================
def skill_breakdown(results):
    stats = {}

    for r in results:
        skill = r["skill"]
        stats.setdefault(skill, {"correct": 0, "total": 0})
        stats[skill]["total"] += 1

        if r["correct"]:
            stats[skill]["correct"] += 1

    return stats


# ===============================
# MAIN
# ===============================
def main():
    print("\nSelect Exam Mode:")
    print("1) Reading Mode (Mostly MCQ)")
    print("2) Mixed Mode (MCQ + Short)")
    print("3) Writing Mode (Essay)")

    mode = input("Choose (1-3): ").strip()
    topic = input("Exam topic: ").strip()

    if mode == "1":
        n = 10
        mcq_ratio = 0.8
    elif mode == "2":
        n = 10
        mcq_ratio = 0.5
    elif mode == "3":
        n = 1
        mcq_ratio = 0
    else:
        print("Invalid mode. Defaulting to Mixed.")
        n = 10
        mcq_ratio = 0.5

    minutes = input("Time limit in minutes (default 10): ").strip()
    minutes = int(minutes) if minutes.isdigit() else 10

    exam, raw = generate_exam(topic, n, mcq_ratio)
    score, total, results = run_exam(exam, minutes)
    stats = skill_breakdown(results)

    report = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "topic": exam.get("topic", topic),
        "mode": mode,
        "time_limit_minutes": minutes,
        "score": f"{score}/{total}",
        "skill_breakdown": stats,
        "results": results
    }

    print("\n📊 EXAM REPORT")
    print("Score:", report["score"])

    for skill, s in stats.items():
        print(f"- {skill}: {s['correct']}/{s['total']}")

    # Show essay evaluation
    for r in results:
        if r["type"] == "essay" and r["essay_evaluation"]:
            print("\n📝 Essay Evaluation:")
            for k, v in r["essay_evaluation"].items():
                print(f"{k}: {v}")

    path = save_report(report)
    print(f"\n✅ Report saved: {path}")


if __name__ == "__main__":
    main()