"""EduInsight AI demo app factory."""

from pathlib import Path

from flask import Flask, render_template, session, redirect
import markdown

APP_DIR = Path(__file__).resolve().parent

# In-memory database for demo
STORE = {
    "diagnostic_records": {},
    "mastery_maps": {},
    "misconceptions": {},
    "interventions": {},
    "micro_scores": {},
    "learning_gains": {},
    "ai_sessions": {},
}


def create_app():

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    app = Flask(
        __name__,
        template_folder=str(APP_DIR / "templates"),
        static_folder=str(APP_DIR / "static"),
    )

    app.secret_key = "eduinsight-demo-secret"

    # -------------------------------------------------
    # MARKDOWN RENDERER
    # -------------------------------------------------
    @app.template_filter("markdown")
    def markdown_filter(text):
        if not text:
            return ""

        return markdown.markdown(
            str(text),
            extensions=[
                "extra",
                "nl2br",
                "sane_lists",
            ],
        )

    # -------------------------------------------------
    # BLUEPRINTS
    # -------------------------------------------------
    from app.student.routes import student_bp
    from app.teacher.routes import teacher_bp
    from app.researcher.routes import researcher_bp

    app.register_blueprint(
        student_bp,
        url_prefix="/student"
    )

    app.register_blueprint(
        teacher_bp,
        url_prefix="/teacher"
    )

    app.register_blueprint(
        researcher_bp,
        url_prefix="/researcher"
    )

    # -------------------------------------------------
    # HOME
    # Directly open Study Sphere
    # -------------------------------------------------
    @app.route("/")
    def login():
        return redirect("/study-sphere")

    # -------------------------------------------------
    # STUDY SPHERE DASHBOARD
    # -------------------------------------------------
    @app.route("/study-sphere")
    def study_sphere():

        session["student_id"] = "S100"
        session["student_name"] = "Aisha Khan"

        return render_template(
            "dashboard.html"
        )

    return app