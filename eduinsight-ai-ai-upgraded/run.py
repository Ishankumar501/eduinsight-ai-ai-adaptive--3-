"""Run the EduInsight AI app."""

import webbrowser
from threading import Timer

from app import create_app


app = create_app()


def open_browser():
    webbrowser.open("http://127.0.0.1:5000/study-sphere")


if __name__ == "__main__":
    Timer(2, open_browser).start()
    app.run(debug=True)