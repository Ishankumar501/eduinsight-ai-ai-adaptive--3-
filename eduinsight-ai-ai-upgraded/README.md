# EduInsight AI

A demo repository for an adaptive assessment system that builds a concept
mastery map from a diagnostic, detects a specific misconception (not just a
wrong answer), recommends a targeted intervention, and measures the
learning gain after the student completes it.

## The demo story

1. Student logs in.
2. Takes a 10-question diagnostic assessment.
3. Rates confidence after each answer.
4. EduInsight constructs the concept mastery map.
5. System detects one misconception.
6. AI recommends an intervention.
7. Teacher accepts or modifies it.
8. Student completes the intervention.
9. System runs a micro-assessment.
10. Dashboard calculates the learning gain.
11. Teacher sees class-level concept gaps.
12. Research mode exports anonymized evidence.

The bundled question bank covers fractions and proportions. Two questions
share a "denominator addition error" distractor and two share a
"cross-multiplication error" distractor, so a student who picks the same
type of wrong answer twice triggers a detected misconception instead of a
one-off mistake.

## Run it two ways

### 1. Command line, no browser

```
pip install -r requirements.txt
python demo.py
```

Runs all 12 steps with scripted answers and prints each stage's output,
including the anonymized research export written to `research/exports/`.

### 2. Web app

```
pip install -r requirements.txt
python run.py
```

Open `http://127.0.0.1:5000`, log in as a student, and click through the
diagnostic, results, teacher review, intervention, micro-assessment, and
both dashboards yourself.

State lives in an in-memory store (`app/STORE`) for this demo — it resets
whenever the process restarts. Swap it for a real database before using
this beyond a demo.

## Repository layout

```
eduinsight-ai/
├── app/                 Flask app: student, teacher, and researcher routes
│   ├── student/         Login, diagnostic, results, intervention, micro-assessment
│   ├── teacher/         Intervention review, class dashboard
│   ├── researcher/      Anonymized export
│   ├── templates/       Server-rendered HTML
│   └── static/          Stylesheet
│
├── assessment/          Diagnostic delivery and confidence capture
│   ├── question_engine.py
│   ├── diagnostic.py
│   ├── confidence.py
│   └── micro_assessment.py
│
├── intelligence/        Mastery, misconception detection, risk, intervention
│   ├── mastery.py
│   ├── misconception.py
│   ├── risk_model.py
│   └── intervention.py
│
├── knowledge_graph/      Concept graph and prerequisite reasoning
│   ├── concepts.py
│   └── prerequisites.py
│
├── research/             Learning gain, statistics, anonymized export
│   ├── experiment.py
│   ├── learning_gain.py
│   ├── statistics.py
│   └── anonymizer.py
│
├── dashboard/             Data shaping for each dashboard view
│   ├── student.py
│   ├── teacher.py
│   └── researcher.py
│
├── data/
│   ├── questions.csv       10-question diagnostic bank
│   ├── concepts.csv        Concept graph with prerequisites
│   └── sample_students.csv Pre-recorded classmates for the class dashboard
│
├── models/                 Placeholder for a trained risk model, if one gets added
├── tests/
│   └── test_pipeline.py
├── demo.py                 12-step CLI walkthrough
├── run.py                  Flask app entry point
└── requirements.txt
```

## Design notes

- **Misconception vs. mistake.** `intelligence/misconception.py` only flags
  a misconception once the same tagged wrong answer shows up at least
  twice. One wrong answer is treated as noise.
- **Learning gain.** `research/learning_gain.py` uses Hake's normalized
  gain, `(post - pre) / (1 - pre)`, which is the standard way education
  research compares gains across students with different starting scores.
- **Anonymization.** `research/anonymizer.py` hashes the student ID with a
  fixed salt and drops every direct identifier before export — only
  mastery scores, misconception labels, intervention type, and gain
  numbers leave the system.
- **No real auth or database.** Login is a name field, and state lives in
  memory. Both are fine for a classroom demo and both are the first things
  to replace before this goes near real student data.

## Tests

```
pip install -r requirements.txt
python -m pytest tests/
```

## AI Adaptive Learning mode

The upgraded demo adds a topic-first flow:
`AI Topic Tutor -> AI Test -> AI Analysis -> Personalized Intervention -> Fresh Reassessment -> Learning Gain`.

### Enable live AI
1. Install requirements: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env`
3. Put your API key in `.env` as `OPENAI_API_KEY=...`
4. Run `python run.py`
5. Open `http://127.0.0.1:5000`
6. Click **AI Topic Tutor**.

The app uses the Google Gemini Developer API for live tutoring, assessment generation,
analysis, and personalized intervention when `GEMINI_API_KEY` is configured. The default
model is `gemini-3.1-flash-lite`, which currently has a free tier. Without a key, the
adaptive screens remain navigable in DEMO mode with local fallback content.

### Enable free-tier Gemini AI
1. Install requirements: `pip install -r requirements.txt`
2. Get a Gemini API key from Google AI Studio: https://aistudio.google.com/apikey
3. Copy `.env.example` to `.env`
4. Put your key in `.env` as `GEMINI_API_KEY=...`
5. Run `python run.py`
6. Open `http://127.0.0.1:5000` and click **AI Topic Tutor**.

The free tier has usage limits; if the quota is exhausted, the app falls back to demo
content instead of crashing.
