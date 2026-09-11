"""Load and serve diagnostic questions."""

import csv
from dataclasses import dataclass
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass
class Question:
    question_id: str
    concept_id: str
    text: str
    options: dict  # {"A": "...", "B": "...", ...}
    correct_option: str
    misconception_option: str
    misconception_name: str
    difficulty: int

    def is_correct(self, chosen_option: str) -> bool:
        return chosen_option.strip().upper() == self.correct_option

    def is_misconception_choice(self, chosen_option: str) -> bool:
        return bool(self.misconception_name) and \
            chosen_option.strip().upper() == self.misconception_option


def load_questions(path: str = None) -> list:
    """Return all questions from questions.csv, in file order."""
    path = path or (DATA_DIR / "questions.csv")
    questions = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            options = {
                "A": row["option_a"],
                "B": row["option_b"],
                "C": row["option_c"],
                "D": row["option_d"],
            }
            questions.append(Question(
                question_id=row["question_id"],
                concept_id=row["concept_id"],
                text=row["question_text"],
                options=options,
                correct_option=row["correct_option"].strip().upper(),
                misconception_option=row["misconception_option"].strip().upper(),
                misconception_name=row["misconception_name"].strip(),
                difficulty=int(row["difficulty"]),
            ))
    return questions


def get_diagnostic_set(questions: list, n: int = 10) -> list:
    """Return the first n questions as the diagnostic set.

    The bundled bank has exactly 10 questions spanning the concept graph,
    so by default this simply returns all of them in order.
    """
    return questions[:n]


def get_question(questions: list, question_id: str) -> Question:
    for q in questions:
        if q.question_id == question_id:
            return q
    raise KeyError(f"Unknown question_id: {question_id}")
