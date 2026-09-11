"""AI service for EduInsight AI using Google Gemini.

Uses the Gemini Developer API when GEMINI_API_KEY is configured. The
free-tier-friendly Gemini 3.1 Flash-Lite model is used by default. If no key
is configured, the app remains usable in DEMO mode.
"""
import json
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# Load the project .env even when the app is launched from another folder.
if load_dotenv:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)
from typing import Any

try:
    from google import genai
except ImportError:
    genai = None

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")


def ai_enabled() -> bool:
    return bool(os.getenv("GEMINI_API_KEY")) and genai is not None


def _client():
    if not ai_enabled():
        return None
    return genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def _call(prompt: str) -> str:
    client = _client()
    if not client:
        return ""
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return (getattr(response, "text", "") or "").strip()


DEMO_CONTENT = {
    "fractions": """Fractions describe equal parts of a whole. The denominator tells
how many equal parts make the whole; the numerator tells how many of those parts
we have. Example: 3/4 means 3 of 4 equal parts. To add fractions with the same
denominator, add the numerators and keep the denominator.""",
    "python": """Python is a high-level programming language. Variables store values,
if/elif/else controls decisions, loops repeat work, functions package reusable
logic, and lists store ordered collections. Example: for x in [1,2,3]: print(x).""",
    "c++": """C++ is a compiled programming language. A variable has a type, functions
group reusable logic, classes define objects, and vectors provide dynamic arrays.
Example: vector<int> a = {1,2,3};""",
    "dsa": """Data structures organize data and algorithms solve problems. Arrays give
fast indexed access, stacks are LIFO, queues are FIFO, and linked lists connect
nodes. Always consider time and space complexity.""",
    "dbms": """A DBMS stores and retrieves structured data. Tables contain rows and
columns, primary keys identify rows, foreign keys connect tables, and SQL is used
to query data. Normalization reduces redundant data."""
}


def explain_topic(topic: str, level: str = "beginner") -> str:
    if ai_enabled():
        return _call(f"""You are EduInsight AI, a patient adaptive tutor.
Teach the student the topic "{topic}" at {level} level.
Give: (1) simple explanation, (2) one worked example, (3) a common mistake,
(4) two quick checks. Use clear student-friendly language. Do not assume
knowledge that was not stated.""")
    key = topic.lower().strip()
    for name, content in DEMO_CONTENT.items():
        if name in key or key in name:
            return content + "\n\nQuick checks:\n1) Explain the key idea in your own words.\n2) Solve one small example."
    return (f"Let's learn {topic}. Start with the definition, then work through "
            "one simple example and one practice question. In AI mode, EduInsight "
            "will personalize this lesson to the student's answers.")


def tutor_reply(topic: str, message: str, history: list[dict[str, str]] | None = None) -> str:
    if ai_enabled():
        context = "\n".join(f"{m.get('role','user')}: {m.get('content','')}" for m in (history or [])[-8:])
        return _call(f"""You are EduInsight AI, an adaptive tutor.
Topic: {topic}
Conversation:
{context}
Student's latest message: {message}
Answer the student directly. If they are confused, explain with a simpler
example. Ask one short check-for-understanding question at the end.""")
    return (f"About {topic}: {message}\n\n"
            "In DEMO mode I can demonstrate the adaptive tutor flow. Add a "
            "GEMINI_API_KEY to enable live AI explanations and personalized replies.")


def _parse_json(raw: str):
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        if raw.endswith("```"):
            raw = raw[:-3]
    try:
        return json.loads(raw.strip())
    except Exception:
        start = raw.find("[")
        end = raw.rfind("]")
        if start >= 0 and end > start:
            try:
                return json.loads(raw[start:end+1])
            except Exception:
                return None
        return None


def generate_test(topic: str, difficulty: str = "adaptive", count: int = 5) -> list[dict[str, Any]]:
    count = max(3, min(int(count), 10))
    if ai_enabled():
        prompt = f"""Create {count} multiple-choice assessment questions for the topic "{topic}".
Difficulty: {difficulty}. Return ONLY valid JSON as an array, with no markdown.
Each item must have exactly these fields:
question: string
options: object containing A, B, C, D
answer: one of A/B/C/D
concept: the specific sub-concept tested
explanation: short explanation of the correct answer
Make the questions distinct, educational, and appropriate for a student.
Include a mix of basic understanding and application questions."""
        data = _parse_json(_call(prompt))
        if isinstance(data, list) and data:
            clean=[]
            for q in data[:count]:
                if isinstance(q, dict) and q.get("question") and isinstance(q.get("options"), dict) and q.get("answer") in {"A","B","C","D"}:
                    clean.append(q)
            if len(clean) >= 3:
                return clean
    return [
        {"question": f"Which statement best describes {topic}?", "options": {"A": f"It is a core concept used when learning {topic}.", "B": "It is unrelated to the subject.", "C": "It can never be practiced.", "D": "It has no measurable learning outcome."}, "answer": "A", "concept": topic, "explanation": f"The best choice identifies a useful concept in {topic}."},
        {"question": f"What is a good way to learn {topic}?", "options": {"A": "Memorize every answer without understanding.", "B": "Learn the idea, work examples, then practice.", "C": "Avoid questions.", "D": "Skip feedback."}, "answer": "B", "concept": topic, "explanation": "Understanding followed by practice and feedback is the useful approach."},
        {"question": f"After making a mistake in {topic}, what should a learner do?", "options": {"A": "Ignore it.", "B": "Repeat the same answer.", "C": "Identify the misconception and try a targeted example.", "D": "Stop learning."}, "answer": "C", "concept": topic, "explanation": "Targeted feedback helps correct the underlying misconception."}
    ][:count]


def analyze_test(topic: str, questions: list[dict[str, Any]], answers: dict[str, str]) -> dict[str, Any]:
    results=[]
    correct=0
    for i,q in enumerate(questions):
        chosen=answers.get(str(i),"")
        ok=chosen.upper()==str(q.get("answer","")).upper()
        correct += int(ok)
        results.append({"question": q.get("question",""), "chosen": chosen, "correct": ok, "concept": q.get("concept",topic)})
    score=round(correct/len(questions),3) if questions else 0
    weak=[r["concept"] for r in results if not r["correct"]]
    if ai_enabled():
        summary=_call(f"""Analyze this student's {topic} assessment.
Score: {score:.0%}
Incorrect concepts: {weak}
Give a concise student-friendly analysis with: strengths, weak concepts,
likely misconception patterns, and a targeted next step. Do not invent evidence.""")
    else:
        summary=(f"Score: {score:.0%}. Weak areas from this attempt: {', '.join(dict.fromkeys(weak)) or 'none detected'}. The next step is targeted practice and a fresh reassessment.")
    return {"score":score,"correct":correct,"total":len(questions),"weak_concepts":list(dict.fromkeys(weak)),"summary":summary,"results":results}


def personalized_intervention(topic: str, weak_concepts: list[str], score: float) -> str:
    weak=", ".join(weak_concepts) if weak_concepts else topic
    if ai_enabled():
        return _call(f"""Create a short adaptive intervention for a student learning {topic}.
Score was {score:.0%}. Weak concepts: {weak}.
Teach only the weak concepts. Include a simple explanation, a worked example,
a common mistake, and 3 practice prompts. Finish by telling the student to take
a fresh reassessment. Keep it clear and encouraging.""")
    return (f"Targeted intervention for {weak}:\n\n1. Revisit the core idea in {topic}.\n2. Work one simple example step-by-step.\n3. Explain why the common wrong answer is wrong.\n4. Try three new practice questions.\n\nThen take a fresh reassessment.")
