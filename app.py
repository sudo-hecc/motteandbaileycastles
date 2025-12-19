from flask import Flask, render_template_string
import logging
import os

# INITIALISE WEB APPLICATION (use default `static/` folder)
app = Flask(__name__)

# SETUP HTML TEMPLATE
HERE = os.path.dirname("static/pages/")

with open(os.path.join(HERE, "main_page.html"), "r") as f:
    TEMPLATE = f.read()

# DEFINE ROUTES
@app.route("/")
def index():
    return render_template_string(TEMPLATE)

# RUN WEB APPLICATION
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)