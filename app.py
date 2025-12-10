from flask import Flask, request, redirect, render_template_string
from flask_compress import Compress
import csv
import os
import datetime

app = Flask(__name__)
Compress(app)

RAW_SCORES_CSV = "raw_scores.csv"
AVERAGES_CSV = "averages.csv"

# ---------- Helper Functions ----------

def weeks_until_exam():
    today = datetime.date.today()
    exam_date = datetime.date(2025, 9, 13)  # Set your exam date here
    delta = exam_date - today
    weeks = delta.days // 7
    return str(weeks)

def load_raw_scores():
    if not os.path.exists(RAW_SCORES_CSV):
        return []
    with open(RAW_SCORES_CSV, newline="") as file:
        return list(csv.DictReader(file))

def save_raw_scores(scores):
    with open(RAW_SCORES_CSV, "w", newline="") as file:
        fieldnames = ["week", "subject", "mon", "tue", "wed", "thu", "fri"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scores)

def load_averages():
    if not os.path.exists(AVERAGES_CSV):
        return []
    with open(AVERAGES_CSV, newline="") as file:
        return list(csv.DictReader(file))

def save_averages(avgs):
    with open(AVERAGES_CSV, "w", newline="") as file:
        fieldnames = ["week", "maths_avg", "english_avg", "vr_avg", "nvr_avg"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(avgs)

def calculate_averages(raw_scores, week):
    subjects = {"Maths": [], "English": [], "VR": [], "NVR": []}
    for entry in raw_scores:
        if entry["week"] == week:
            scores = [int(entry["mon"]), int(entry["tue"]), int(entry["wed"]), int(entry["thu"]), int(entry["fri"])]
            subjects[entry["subject"]] = scores

    result = {"week": week}
    for subject, scores in subjects.items():
        if scores:
            avg = round(sum(scores) / 5, 2)
            result[f"{subject.lower()}_avg"] = avg
        else:
            result[f"{subject.lower()}_avg"] = "N/A"
    return result

# ---------- Templates ----------

TEMPLATE = '''
<!doctype html>
<html>
<head>
    <title>Weekday Subject Score Tracker</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; max-width: 900px; margin: auto; }
        h1, h2 { color: #333; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
        input, button { margin: 5px 0; padding: 5px; font-family: Arial; }
        form.inline { display: inline; }
        nav { margin-bottom: 20px; }
        a { margin-right: 15px; }

        {% if page == "view" %}
        @media screen and (orientation: portrait) {
            body::before {
                content: "🔄 Please rotate your device to landscape for better viewing!";
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: #fff;
                color: #333;
                font-size: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
                z-index: 9999;
                padding: 20px;
            }
        }
        {% endif %}
    </style>
</head>
<body>
    <h1>Weekday Subject Score Tracker</h1>
    <nav>
        <a href="/">Home</a>
        <a href="/view">View Results</a>
    </nav>

    {% if page == "home" %}
    <h2>Add Scores</h2>
    <form method="POST" action="/add">
        <label>Subject:
            <select name="subject" required>
                <option>Maths</option>
                <option>English</option>
                <option>VR</option>
                <option>NVR</option>
            </select>
        </label><br>
        <label>Monday: <input name="mon" type="number" required></label><br>
        <label>Tuesday: <input name="tue" type="number" required></label><br>
        <label>Wednesday: <input name="wed" type="number" required></label><br>
        <label>Thursday: <input name="thu" type="number" required></label><br>
        <label>Friday: <input name="fri" type="number" required></label><br>
        <input type="submit" value="Add Scores">
    </form>
    {% endif %}

    {% if page == "view" %}
    <h2>Raw Scores</h2>
    <table>
        <tr>
            <th>Weeks Left</th><th>Subject</th><th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th><th>Delete</th>
        </tr>
        {% for score in raw_scores %}
        <tr>
            <td>{{ score.week }}</td>
            <td>{{ score.subject }}</td>
            <td>{{ score.mon }}</td>
            <td>{{ score.tue }}</td>
            <td>{{ score.wed }}</td>
            <td>{{ score.thu }}</td>
            <td>{{ score.fri }}</td>
            <td>
                <form method="POST" action="/delete_raw/{{ loop.index0 }}" class="inline">
                    <button type="submit">Delete</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>

    <h2>Weekly Averages</h2>
    <table>
        <tr>
            <th>Weeks Left</th><th>Maths Avg</th><th>English Avg</th><th>VR Avg</th><th>NVR Avg</th><th>Delete</th>
        </tr>
        {% for avg in averages %}
        <tr>
            <td>{{ avg.week }}</td>
            <td>{{ avg.maths_avg }}</td>
            <td>{{ avg.english_avg }}</td>
            <td>{{ avg.vr_avg }}</td>
            <td>{{ avg.nvr_avg }}</td>
            <td>
                <form method="POST" action="/delete_avg/{{ loop.index0 }}" class="inline">
                    <button type="submit">Delete</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}
</body>
</html>
'''

# ---------- Routes ----------

@app.route('/')
def index():
    return render_template_string(TEMPLATE, page="home")

@app.route('/add', methods=["POST"])
def add():
    subject = request.form["subject"]
    mon = request.form["mon"]
    tue = request.form["tue"]
    wed = request.form["wed"]
    thu = request.form["thu"]
    fri = request.form["fri"]
    week = weeks_until_exam()
    new_entry = {
        "week": week,
        "subject": subject,
        "mon": mon,
        "tue": tue,
        "wed": wed,
        "thu": thu,
        "fri": fri
    }
    raw_scores = load_raw_scores()
    raw_scores.append(new_entry)
    save_raw_scores(raw_scores)
    return redirect('/view')

@app.route('/view')
def view():
    raw_scores = load_raw_scores()
    weeks = set(e["week"] for e in raw_scores)
    updated_averages = []
    for week in weeks:
        avg_entry = calculate_averages(raw_scores, week)
        if avg_entry:
            updated_averages.append(avg_entry)
    save_averages(updated_averages)
    averages = load_averages()
    return render_template_string(TEMPLATE, page="view", raw_scores=raw_scores, averages=averages)

@app.route('/delete_raw/<int:index>', methods=["POST"])
def delete_raw(index):
    raw_scores = load_raw_scores()
    if 0 <= index < len(raw_scores):
        del raw_scores[index]
        save_raw_scores(raw_scores)
    return redirect('/view')

@app.route('/delete_avg/<int:index>', methods=["POST"])
def delete_avg(index):
    averages = load_averages()
    if 0 <= index < len(averages):
        del averages[index]
        save_averages(averages)
    return redirect('/view')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)

