"""Step 9 of the demo story: a short micro-assessment after the intervention,
targeted at the concept behind the detected misconception.
"""

from dataclasses import dataclass

MICRO_BANK = {
    "C3": [
        {"id": "M1", "text": "What is 2/5 + 1/5?", "options": {"A": "3/5", "B": "3/10", "C": "2/10", "D": "1/5"}, "correct": "A"},
        {"id": "M2", "text": "What is 1/3 + 1/6?", "options": {"A": "1/2", "B": "2/9", "C": "2/18", "D": "1/9"}, "correct": "A"},
        {"id": "M3", "text": "What is 3/8 + 1/8?", "options": {"A": "4/16", "B": "1/2", "C": "4/8", "D": "3/8"}, "correct": "B"},
    ],
    "C6": [
        {"id": "M4", "text": "Solve for x: 3/4 = x/8", "options": {"A": "6", "B": "5", "C": "11", "D": "24"}, "correct": "A"},
        {"id": "M5", "text": "Solve for x: 5/6 = x/12", "options": {"A": "10", "B": "17", "C": "7", "D": "60"}, "correct": "A"},
        {"id": "M6", "text": "Solve for x: 2/7 = x/14", "options": {"A": "4", "B": "9", "C": "16", "D": "2"}, "correct": "A"},
    ],
}


@dataclass
class MicroQuestion:
    question_id: str
    text: str
    options: dict
    correct: str


def get_micro_assessment(concept_id: str) -> list:
    bank = MICRO_BANK.get(concept_id, [])
    return [MicroQuestion(q["id"], q["text"], q["options"], q["correct"]) for q in bank]


def score_micro_assessment(questions: list, answers: dict) -> float:
    """answers: {question_id: chosen_option}"""
    if not questions:
        return 0.0
    correct = sum(1 for q in questions if answers.get(q.question_id, "").strip().upper() == q.correct)
    return round(correct / len(questions), 3)
