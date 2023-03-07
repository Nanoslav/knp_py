from flask import Flask, render_template, request, redirect, url_for, json
import sqlite3
import time
import random

app = Flask(__name__)
app.debug = True

conn = sqlite3.connect("knp.sqlite", check_same_thread=False)
conn.row_factory = sqlite3.Row

options = ["kámen", "nůžky", "papír"]
win = {"kámen": "nůžky", "nůžky": "papír", "papír": "kámen"}
htmlText = {
    "Výhra": "<span style='color: green;'>Výhra</span>",
    "Prohra": "<span style='color: red;'>Prohra</span>",
    "Nerozhodně": "<span style='color: yellow;'>Nerozhodně</span>",
}


def getScore():
    cursor = conn.cursor()
    win = cursor.execute(
        f'SELECT COUNT(id) FROM knp WHERE vysledek = "Výhra"'
    ).fetchone()
    loss = cursor.execute(
        f'SELECT COUNT(id) FROM knp WHERE vysledek = "Prohra"'
    ).fetchone()
    return [win[0], loss[0]]


def game(choice, choicePC):
    if choice == choicePC:
        return "Nerozhodně"
    if win[choice] == choicePC:
        return "Výhra"
    else:
        return "Prohra"


@app.route("/", methods=["GET", "POST"], strict_slashes=False)
def hra():
    score = getScore()
    if request.method == "POST":
        choice = request.form.get("select")
        choicePC = random.choice(options)

        vysledek = game(choice, choicePC)

        cursor = conn.cursor()
        cursor.execute(
            f'INSERT INTO knp(vyberUZ, vyberPC, vysledek, date) VALUES ("{choice}", "{choicePC}", "{vysledek}", "{time.time()}")'
        )
        conn.commit()
        cursor.close()

        score = getScore()

        return render_template(
            "index.html",
            choice=choice,
            choicePC=choicePC,
            vysledek=htmlText[vysledek],
            score=score,
        )

    return render_template("index.html", score=score)


@app.route("/data", strict_slashes=False)
def data():
    cursor = conn.cursor()
    data = cursor.execute(f"SELECT * FROM knp ORDER BY date DESC LIMIT 50").fetchall()

    score = getScore()

    return render_template("data.html", data=data, htmlText=htmlText, score=score)


@app.route("/data/remove", strict_slashes=False)
def removeData():
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM knp")
    conn.commit()

    return redirect(url_for("data"))


@app.template_filter("ctime")
def timectime(s):
    return time.strftime("%d. %m. %Y - %H:%M:%S", time.localtime(s))


if __name__ == "__main__":
    app.run()
