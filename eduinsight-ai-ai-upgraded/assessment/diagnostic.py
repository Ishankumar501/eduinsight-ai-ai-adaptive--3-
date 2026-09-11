"""Runs the 10-question diagnostic assessment for one student."""

from dataclasses import dataclass, field

from assessment.confidence import valid_confidence


@dataclass
class AnswerRecord:
    question_id: str
    concept_id: str
    chosen_option: str
    correct: bool
    is_misconception_choice: bool
    misconception_name: str
    confidence: int


class DiagnosticSession:
    """Step 2 + 3 of the demo story: take the diagnostic, rate confidence
    after every answer."""

    def __init__(self, student_id: str, questions: list):
        self.student_id = student_id
        self.questions = questions
        self.records: list = field(default_factory=list)
        self.records = []

    def answer(self, question_id: str, chosen_option: str, confidence: int) -> AnswerRecord:
        question = next(q for q in self.questions if q.question_id == question_id)
        confidence = valid_confidence(confidence)
        record = AnswerRecord(
            question_id=question.question_id,
            concept_id=question.concept_id,
            chosen_option=chosen_option.strip().upper(),
            correct=question.is_correct(chosen_option),
            is_misconception_choice=question.is_misconception_choice(chosen_option),
            misconception_name=question.misconception_name if question.is_misconception_choice(chosen_option) else "",
            confidence=confidence,
        )
        self.records.append(record)
        return record

    def is_complete(self) -> bool:
        return len(self.records) == len(self.questions)

    def score(self) -> float:
        if not self.records:
            return 0.0
        correct = sum(1 for r in self.records if r.correct)
        return round(correct / len(self.records), 3)
