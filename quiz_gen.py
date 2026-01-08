# =======================================================
# QuizBee 🐝 – Interactive Quiz App 
# Features:
# - LLM generates MCQ quiz in JSON
# - Interactive radio buttons
# - Auto evaluation
# - Student attempt history
# - Leaderboard
# - PDF export (questions + answers)
# =======================================================

import streamlit as st
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

# ---------------- ENV SETUP ----------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

HISTORY_FILE = "quiz_history.json"

def extract_json(text):
    """
    Safely extract JSON from LLM output
    """
    if not text:
        return None

    # Remove code fences if present
    text = text.strip()
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    # Extract first JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        return None

    json_text = text[start:end+1]

    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        return None

# ---------------- LLM FUNCTION ----------------

def request_quiz_json(name, age, topic, difficulty, num_q):
    prompt = f"""
Generate a quiz for a {age}-year-old child named {name}.

STRICT RULES:
- Output ONLY valid JSON
- No explanations
- No markdown
- No extra text
- No code blocks
- Explanation must be simple and child-friendly

JSON format:
{{
  "quiz_title": "string",
  "questions": [
    {{
      "id": 1,
      "question": "string",
      "options": {{
        "A": "string",
        "B": "string",
        "C": "string",
        "D": "string"
      }},
      "correct_answer": "A",
      "explanation": "string"
    }}
  ]
}}

Topic: {topic}
Difficulty: {difficulty}
Number of questions: {num_q}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=3000
    )

    raw_output = response.choices[0].message.content

    quiz_json = extract_json(raw_output)

    if quiz_json is None:
        raise ValueError("LLM did not return valid JSON")

    return quiz_json

# ---------------- PDF GENERATOR ----------------

def generate_pdf(title, questions):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'title', parent=styles['Title'], alignment=1,
        textColor=colors.HexColor('#1A237E')
    )
    body = ParagraphStyle('body', parent=styles['Normal'], fontSize=11)

    story = [Paragraph(title, title_style), Spacer(1, 14)]

    for q in questions:
        story.append(Paragraph(f"Q{q['id']}. {q['question']}", body))
        for opt, txt in q['options'].items():
            story.append(Paragraph(f"{opt}. {txt}", body))
       ## story.append(Paragraph(f"Correct Answer: {q['correct_answer']}", body))
        story.append(Spacer(1, 10))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ---------------- HISTORY FUNCTIONS ----------------

def save_attempt(name, age, score, total):
    attempt = {
        "name": name,
        "age": age,
        "score": score,
        "total": total,
        "percentage": round((score / total) * 100, 2),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    try:
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []

    data.append(attempt)

    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_history():
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# ---------------- STREAMLIT APP ----------------

def app():
    st.set_page_config(page_title="QuizBee 🐝", layout="centered")

    st.title("QuizBee 🐝")
    st.caption("Fun quizzes • Instant results • Leaderboard")

    name = st.text_input("👦👧 Student Name")
    age = st.text_input("🎂 Age")
    topic = st.text_input("📘 Topic")
    difficulty = st.radio("⚡ Difficulty", ["Easy", "Medium", "Hard"], horizontal=True)
    num_q = st.selectbox("❓ Number of Questions", [10, 20, 30, 50, 100])

    if not name or not age or not topic:
        st.info("Please fill all details to start")
        st.stop()

    if "quiz" not in st.session_state:
        st.session_state.quiz = None

    # ---------- SESSION STATE INIT ----------
    if "quiz_run_id" not in st.session_state:
        st.session_state.quiz_run_id = 0

    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    if "wrong_answers" not in st.session_state:
        st.session_state.wrong_answers = []

  #------------------Submit-----------------#
    if st.button("🚀 Generate Quiz"):
        with st.spinner("Creating quiz..."):
            try:
                st.session_state.quiz = request_quiz_json(
                    name, age, topic, difficulty, num_q
                )
                st.session_state.submitted = False #reset
                st.session_state.quiz_run_id = 0
                st.session_state.wrong_answers = []
                st.success("🎉 Quiz generated successfully!")
            except Exception as e:
                st.error("⚠️ Failed to generate quiz. Please try again.")
                st.code(str(e))
                st.session_state.quiz = None
                st.stop()

    if st.session_state.quiz:
        quiz = st.session_state.quiz
        st.subheader(quiz["quiz_title"])

    # -------- QUESTIONS (FIRST) --------
        answers = {}
        for q in quiz["questions"]:
            answers[q["id"]] = st.radio(
            f"Q{q['id']}. {q['question']}",
            options=list(q["options"].keys()),
            format_func=lambda x: f"{x}. {q['options'][x]}",
            index=None,
            disabled=st.session_state.submitted,
            key=f"q_{st.session_state.quiz_run_id}_{q['id']}"
        )

    # -------- SUBMIT --------
        if st.button("📤 Submit Quiz") and not st.session_state.submitted:

            if None in answers.values():
                st.warning("⚠️ Please answer all questions")
                st.stop()

            wrong_answers = []
            score = 0

            for q in quiz["questions"]:
                selected = answers[q["id"]]
                correct = q["correct_answer"]

                if selected == correct:
                    score += 1
                else:
                    wrong_answers.append({
                        "question": q["question"],
                        "selected": f"{selected}. {q['options'][selected]}",
                        "correct": f"{correct}. {q['options'][correct]}",
                        "explanation": q["explanation"]
                    })

            st.session_state.wrong_answers = wrong_answers
            st.session_state.submitted = True

            total = len(quiz["questions"])
            save_attempt(name, age, score, total)

            st.success(f"🎉 Your Score: {score}/{total}")
            st.progress(score / total)

        # -------- REVIEW --------
        if st.session_state.submitted and st.session_state.wrong_answers:
            st.divider()
            st.subheader("❌ Questions to Review")
            for i, item in enumerate(st.session_state.wrong_answers, start=1):
                st.markdown(f"### ❌ Question {i}")
                st.write(f"**Question:** {item['question']}")
                st.error(f"Your Answer: {item['selected']}")
                st.success(f"Correct Answer: {item['correct']}")
                st.info(f"💡 Explanation: {item['explanation']}")

        # -------- POST-RESULT ACTIONS --------
        if st.session_state.submitted:
            st.divider()

            pdf = generate_pdf("QuizBee ", quiz["questions"])
            st.download_button(
                "📄 Download Quiz PDF",
                data=pdf,
                file_name="quizbee_quiz.pdf",
                mime="application/pdf"
            )

            if st.button("🔁 Retake Quiz (Same Questions)"):
                st.session_state.submitted = False
                st.session_state.wrong_answers = []
                st.session_state.quiz_run_id += 1
                st.rerun()

    # ---------------- LEADERBOARD ----------------
    st.divider()
    st.subheader("🏆 Leaderboard")

    history = load_history()
    if history:
        history = sorted(history, key=lambda x: x["percentage"], reverse=True)
        st.table(history[:10])
    else:
        st.info("Leaderboard will appear after attempts")


if __name__ == "__main__":
    app()
