from flask import Blueprint, redirect, render_template, request, session, url_for

from assessment.diagnostic import DiagnosticSession
from assessment.micro_assessment import get_micro_assessment, score_micro_assessment
from assessment.question_engine import get_diagnostic_set, load_questions
from intelligence.intervention import recommend_intervention
from intelligence.mastery import build_mastery_map
from intelligence.misconception import detect_misconceptions
from knowledge_graph.concepts import load_concepts
from research.learning_gain import gain_summary

student_bp = Blueprint("student", __name__)

QUESTIONS = get_diagnostic_set(load_questions())
CONCEPTS = load_concepts()


def _store():
    from app import STORE
    return STORE


# ============================================================
# AI HISTORY SAVE
# ============================================================

def _save_ai_history(student_id):
    """
    Save the current AI learning session into AI history.
    This keeps lesson + chat + test + intervention + scores.
    """

    store = _store()

    state = store["ai_sessions"].get(student_id)

    if not state:
        return

    # Create history storage if it does not exist
    if "ai_history" not in store:
        store["ai_history"] = {}

    if student_id not in store["ai_history"]:
        store["ai_history"][student_id] = {}

    topic = state.get("topic", "").strip()

    if not topic:
        return

    # Save complete AI session
    store["ai_history"][student_id][topic] = {
        "topic": topic,
        "lesson": state.get("lesson", ""),
        "history": list(state.get("history", [])),
        "test": state.get("test", []),
        "last_analysis": state.get("last_analysis"),
        "pre_score": state.get("pre_score"),
        "intervention": state.get("intervention", ""),
        "retest": state.get("retest", []),
        "post_score": state.get("post_score"),
        "post_analysis": state.get("post_analysis"),
        "learning_gain": state.get("learning_gain"),
    }


# ============================================================
# LOGIN
# ============================================================

@student_bp.route("/login", methods=["POST"])
def login():
    """Step 1: student logs in."""

    student_id = (
        request.form.get("student_id", "").strip()
        or "S000"
    )

    student_name = (
        request.form.get("student_name", "").strip()
        or "Demo Student"
    )

    session["student_id"] = student_id
    session["student_name"] = student_name

    session["answers"] = {}
    session["q_index"] = 0

    # Start AI-first learning flow
    return redirect(url_for("student.learn"))


# ============================================================
# DIAGNOSTIC
# ============================================================

@student_bp.route("/diagnostic", methods=["GET", "POST"])
def diagnostic():
    """Steps 2 + 3: diagnostic test."""

    if "student_id" not in session:
        return redirect(url_for("student.login"))

    if request.method == "POST":

        q_id = request.form["question_id"]

        session["answers"][q_id] = {
            "option": request.form["chosen_option"],
            "confidence": int(
                request.form["confidence"]
            ),
        }

        session["q_index"] += 1
        session.modified = True

    index = session["q_index"]

    if index >= len(QUESTIONS):
        return redirect(url_for("student.results"))

    question = QUESTIONS[index]

    return render_template(
        "diagnostic.html",
        question=question,
        index=index + 1,
        total=len(QUESTIONS),
    )


# ============================================================
# RESULTS
# ============================================================

@student_bp.route("/results")
def results():
    """Runs diagnostic analysis."""

    if "student_id" not in session:
        return redirect(url_for("student.login"))

    student_id = session["student_id"]

    diag = DiagnosticSession(
        student_id,
        QUESTIONS
    )

    for q_id, response in session["answers"].items():

        diag.answer(
            q_id,
            response["option"],
            response["confidence"]
        )

    mastery_map = build_mastery_map(
        diag.records,
        CONCEPTS
    )

    misconceptions = detect_misconceptions(
        diag.records
    )

    store = _store()

    store["diagnostic_records"][student_id] = diag.records

    store["mastery_maps"][student_id] = mastery_map

    store["misconceptions"][student_id] = misconceptions

    store["learning_gains"][student_id] = {
        "pre_score": diag.score()
    }

    intervention = None

    if misconceptions:

        intervention = recommend_intervention(
            misconceptions[0],
            mastery_map,
            CONCEPTS
        )

        store["interventions"][student_id] = intervention

    return render_template(
        "results.html",
        student_name=session["student_name"],
        mastery_map=mastery_map,
        concepts=CONCEPTS,
        misconceptions=misconceptions,
        intervention=intervention,
        pre_score=diag.score(),
    )


# ============================================================
# INTERVENTION
# ============================================================

@student_bp.route("/intervention")
def intervention_view():

    student_id = session.get("student_id")

    if not student_id:
        return redirect(url_for("student.login"))

    store = _store()

    intervention = store["interventions"].get(
        student_id
    )

    if not intervention or intervention.status == "recommended":

        return render_template(
            "waiting_on_teacher.html"
        )

    return render_template(
        "intervention.html",
        intervention=intervention
    )


@student_bp.route(
    "/intervention/complete",
    methods=["POST"]
)
def complete_intervention():

    student_id = session.get("student_id")

    intervention = _store()["interventions"].get(
        student_id
    )

    if intervention:
        intervention.status = "completed"

    return redirect(
        url_for("student.micro_assessment")
    )


# ============================================================
# MICRO ASSESSMENT
# ============================================================

@student_bp.route(
    "/micro-assessment",
    methods=["GET", "POST"]
)
def micro_assessment():

    student_id = session.get("student_id")

    if not student_id:
        return redirect(url_for("student.login"))

    store = _store()

    intervention = store["interventions"].get(
        student_id
    )

    if not intervention:
        return redirect(
            url_for("student.results")
        )

    concept_id = intervention.concept_ids[0]

    questions = get_micro_assessment(
        concept_id
    )

    if request.method == "POST":

        answers = {
            q.question_id:
                request.form.get(
                    q.question_id,
                    ""
                )
            for q in questions
        }

        post_score = score_micro_assessment(
            questions,
            answers
        )

        store["micro_scores"][student_id] = post_score

        pre_score = store["learning_gains"][
            student_id
        ]["pre_score"]

        store["learning_gains"][student_id] = (
            gain_summary(
                pre_score,
                post_score
            )
        )

        return redirect(
            url_for("student.dashboard")
        )

    return render_template(
        "micro_assessment.html",
        questions=questions
    )


# ============================================================
# OLD DASHBOARD
# ============================================================

@student_bp.route("/dashboard")
def dashboard():

    student_id = session.get("student_id")

    if not student_id:
        return redirect(
            url_for("student.login")
        )

    store = _store()

    gain = store["learning_gains"].get(
        student_id
    )

    if not gain or "post_score" not in gain:
        return redirect(
            url_for("student.results")
        )

    return render_template(
        "student_dashboard.html",
        student_name=session.get("student_name"),
        gain=gain,
        mastery_map=store[
            "mastery_maps"
        ].get(student_id, {}),
        concepts=CONCEPTS,
    )


# ============================================================
# AI ADAPTIVE LEARNING
# ============================================================

@student_bp.route(
    "/learn",
    methods=["GET", "POST"]
)
def learn():
    """Topic-first AI learning flow."""

    if "student_id" not in session:
        return redirect(
            url_for("student.login")
        )

    if request.method == "POST":

        topic = request.form.get(
            "topic",
            ""
        ).strip()

        if not topic:

            return render_template(
                "topic.html",
                error="Enter a topic first."
            )

        from services.ai import explain_topic

        store = _store()

        student_id = session["student_id"]

        # Save previous session before starting new topic
        _save_ai_history(student_id)

        # Create new AI session
        store["ai_sessions"][student_id] = {

            "topic": topic,

            "lesson": explain_topic(topic),

            "history": [],

            "test": [],

            "last_analysis": None,

            "pre_score": None,

            "post_score": None,

            "post_analysis": None,

            "intervention": "",

            "retest": [],

            "learning_gain": 0.0,
        }

        return redirect(
            url_for("student.tutor")
        )

    return render_template(
        "topic.html"
    )


# ============================================================
# AI TUTOR / CHAT
# ============================================================

@student_bp.route(
    "/tutor",
    methods=["GET", "POST"]
)
def tutor():

    if "student_id" not in session:
        return redirect(
            url_for("student.login")
        )

    student_id = session["student_id"]

    state = _store()["ai_sessions"].get(
        student_id
    )

    if not state:
        return redirect(
            url_for("student.learn")
        )

    from services.ai import tutor_reply

    reply = None

    if request.method == "POST":

        message = request.form.get(
            "message",
            ""
        ).strip()

        if message:

            # User message
            state["history"].append({
                "role": "user",
                "content": message
            })

            # AI reply
            reply = tutor_reply(
                state["topic"],
                message,
                state["history"]
            )

            # AI message
            state["history"].append({
                "role": "assistant",
                "content": reply
            })

            # IMPORTANT:
            # Save chat immediately
            _save_ai_history(student_id)

    return render_template(
        "tutor.html",
        state=state,
        reply=reply
    )


# ============================================================
# AI HISTORY LIST
# ============================================================

@student_bp.route("/history")
def history():

    if "student_id" not in session:
        return redirect(
            url_for("student.login")
        )

    student_id = session["student_id"]

    # Save current AI session
    _save_ai_history(student_id)

    history_store = _store().get(
        "ai_history",
        {}
    )

    student_history = history_store.get(
        student_id,
        {}
    )

    return render_template(
        "history.html",
        history=student_history
    )


# ============================================================
# AI HISTORY DELETE
# ============================================================

@student_bp.route(
    "/history/delete/<path:topic>",
    methods=["POST"]
)
def delete_history(topic):

    if "student_id" not in session:
        return redirect(
            url_for("student.login")
        )

    student_id = session["student_id"]

    history_store = _store().get(
        "ai_history",
        {}
    )

    if student_id in history_store:

        history_store[student_id].pop(
            topic,
            None
        )

    return redirect(
        url_for("student.history")
    )


# ============================================================
# AI HISTORY DETAIL / CHATGPT STYLE
# ============================================================

@student_bp.route(
    "/history/<path:topic>"
)
def history_detail(topic):

    if "student_id" not in session:
        return redirect(
            url_for("student.login")
        )

    student_id = session["student_id"]

    # Save latest chat before opening history
    _save_ai_history(student_id)

    history_store = _store().get(
        "ai_history",
        {}
    )

    student_history = history_store.get(
        student_id,
        {}
    )

    data = student_history.get(
        topic
    )

    if not data:
        return redirect(
            url_for("student.history")
        )

    return render_template(
        "history_detail.html",
        data=data
    )


# ============================================================
# AI TEST
# ============================================================

@student_bp.route(
    "/ai-test",
    methods=["GET", "POST"]
)
def ai_test():

    if "student_id" not in session:
        return redirect(
            url_for("student.login")
        )

    student_id = session["student_id"]

    state = _store()["ai_sessions"].get(
        student_id
    )

    if not state:
        return redirect(
            url_for("student.learn")
        )

    from services.ai import (
        generate_test,
        analyze_test
    )

    # Generate test once
    if not state["test"]:

        state["test"] = generate_test(
            state["topic"]
        )

    if request.method == "POST":

        answers = {
            str(i):
                request.form.get(
                    str(i),
                    ""
                )
            for i in range(
                len(state["test"])
            )
        }

        analysis = analyze_test(
            state["topic"],
            state["test"],
            answers
        )

        state["last_analysis"] = analysis

        state["pre_score"] = analysis["score"]

        # Save updated session
        _save_ai_history(student_id)

        return redirect(
            url_for("student.ai_results")
        )

    return render_template(
        "ai_test.html",
        state=state
    )


# ============================================================
# AI RESULTS
# ============================================================

@student_bp.route("/ai-results")
def ai_results():

    if "student_id" not in session:
        return redirect(
            url_for("student.login")
        )

    student_id = session["student_id"]

    state = _store()["ai_sessions"].get(
        student_id
    )

    if (
        not state
        or not state.get("last_analysis")
    ):
        return redirect(
            url_for("student.ai_test")
        )

    return render_template(
        "ai_results.html",
        state=state
    )


# ============================================================
# AI INTERVENTION
# ============================================================

@student_bp.route("/ai-intervention")
def ai_intervention():

    if "student_id" not in session:
        return redirect(
            url_for("student.login")
        )

    student_id = session["student_id"]

    state = _store()["ai_sessions"].get(
        student_id
    )

    if (
        not state
        or not state.get("last_analysis")
    ):
        return redirect(
            url_for("student.ai_test")
        )

    from services.ai import (
        personalized_intervention
    )

    analysis = state["last_analysis"]

    lesson = personalized_intervention(
        state["topic"],
        analysis["weak_concepts"],
        analysis["score"]
    )

    state["intervention"] = lesson

    # Save intervention
    _save_ai_history(student_id)

    return render_template(
        "ai_intervention.html",
        state=state
    )


# ============================================================
# AI RETEST
# ============================================================

@student_bp.route(
    "/ai-retest",
    methods=["GET", "POST"]
)
def ai_retest():

    if "student_id" not in session:
        return redirect(
            url_for("student.login")
        )

    student_id = session["student_id"]

    state = _store()["ai_sessions"].get(
        student_id
    )

    if (
        not state
        or not state.get("last_analysis")
    ):
        return redirect(
            url_for("student.ai_test")
        )

    from services.ai import (
        generate_test,
        analyze_test
    )

    # Generate adaptive retest only once
    if (
        "retest" not in state
        or not state["retest"]
    ):

        state["retest"] = generate_test(
            state["topic"],
            difficulty="adaptive",
            count=5
        )

    if request.method == "POST":

        answers = {
            str(i):
                request.form.get(
                    str(i),
                    ""
                )
            for i in range(
                len(state["retest"])
            )
        }

        post = analyze_test(
            state["topic"],
            state["retest"],
            answers
        )

        state["post_score"] = post["score"]

        pre = state["pre_score"] or 0

        if pre < 1:
            gain = round(
                (post["score"] - pre)
                / (1 - pre),
                3
            )
        else:
            gain = 0.0

        state["post_analysis"] = post

        state["learning_gain"] = gain

        # Save completed retest
        _save_ai_history(student_id)

        return redirect(
            url_for("student.ai_final")
        )

    return render_template(
        "ai_retest.html",
        state=state
    )


# ============================================================
# AI FINAL
# ============================================================

@student_bp.route("/ai-final")
def ai_final():

    if "student_id" not in session:
        return redirect(
            url_for("student.login")
        )

    student_id = session["student_id"]

    state = _store()["ai_sessions"].get(
        student_id
    )

    if (
        not state
        or "post_score" not in state
    ):
        return redirect(
            url_for("student.ai_retest")
        )

    # Save COMPLETE AI session
    _save_ai_history(student_id)

    return render_template(
        "ai_final.html",
        state=state
    )