from flask import Flask, render_template_string
import logging

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Motte and Bailey</title>
  </head>
  <body>
    <h1>Motte and Bailey</h1>
    <p>Motte and Bailey Castles were introduceced by King William of Englan after the Battle of Hastings (14 October 1066).</p>
  </body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(TEMPLATE)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting Waitress on 0.0.0.0:10000")
    print("Starting Waitress on 0.0.0.0:10000")
    try:
        from waitress import serve
        serve(app, host="0.0.0.0", port=10000)
    except Exception:
        logging.exception("Failed to start Waitress")
        raise