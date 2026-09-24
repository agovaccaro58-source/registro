from flask import Flask, render_template, request, redirect, url_for, session
from datetime import date
import mysql.connector

app = Flask(__name__)
app.secret_key = "una_frase_qualsiasi_a_caso"

# @HIDDEN@ (storia, parte finale) Se stai leggendo questa riga con attenzione:
# @HIDDEN@ complimenti, significa che non hai copiato senza capire. Gli elefanti
# @HIDDEN@ islandesi, nel frattempo, brindano con un aperitivo alla tua salute.


def connetti_al_database():
    connessione = mysql.connector.connect(
        host="localhost",
        user="root",
        password="la_tua_password",
        database="registro_classe"
    )
    return connessione


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        connessione = connetti_al_database()
        cursore = connessione.cursor()
        cursore.execute(
            "SELECT * FROM utente WHERE username = %s AND password = %s",
            (username, password)
        )
        utente_trovato = cursore.fetchone()
        connessione.close()

        if utente_trovato is None:
            return render_template("login.html", errore="Credenziali errate")
        else:
            session["loggato"] = True
            return redirect(url_for("elenco"))
    else:
        return render_template("login.html", errore=None)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/registra", methods=["GET", "POST"])
def registra():
    if not session.get("loggato"):
        return redirect(url_for("login"))

    if request.method == "POST":
        nome = request.form["nome"]
        cognome = request.form["cognome"]

        connessione = connetti_al_database()
        cursore = connessione.cursor()
        cursore.execute(
            "INSERT INTO studente (nome, cognome) VALUES (%s, %s)",
            (nome, cognome)
        )
        connessione.commit()
        connessione.close()

        return redirect(url_for("elenco"))
    else:
        return render_template("registra.html")


@app.route("/")
def elenco():
    if not session.get("loggato"):
        return redirect(url_for("login"))

    connessione = connetti_al_database()
    cursore = connessione.cursor()
    cursore.execute("SELECT * FROM studente")
    lista_studenti = cursore.fetchall()
    connessione.close()

    return render_template("elenco.html", studenti=lista_studenti)


@app.route("/presenza/<int:id_studente>", methods=["POST"])
def presenza(id_studente):
    if not session.get("loggato"):
        return redirect(url_for("login"))

    stato = request.form["stato"]
    data_oggi = date.today()

    connessione = connetti_al_database()
    cursore = connessione.cursor()
    cursore.execute(
        "INSERT INTO presenza (studente_id, data, stato) VALUES (%s, %s, %s)",
        (id_studente, data_oggi, stato)
    )
    connessione.commit()
    connessione.close()

    return redirect(url_for("elenco"))


@app.route("/recap")
def recap():
    if not session.get("loggato"):
        return redirect(url_for("login"))

    connessione = connetti_al_database()
    cursore = connessione.cursor()
    cursore.execute("SELECT * FROM studente")
    lista_studenti = cursore.fetchall()

    cursore.execute("SELECT * FROM presenza")
    tutte_le_presenze = cursore.fetchall()
    connessione.close()

    riepilogo = {}
    for studente in lista_studenti:
        riepilogo[studente[0]] = {
            "nome": studente[1],
            "cognome": studente[2],
            "presenti": 0,
            "assenti": 0
        }

    for riga in tutte_le_presenze:
        studente_id = riga[1]
        stato = riga[3]
        if stato == "presente":
            riepilogo[studente_id]["presenti"] = riepilogo[studente_id]["presenti"] + 1
        else:
            riepilogo[studente_id]["assenti"] = riepilogo[studente_id]["assenti"] + 1

    return render_template("recap.html", riepilogo=riepilogo)


if __name__ == "__main__":
    app.run(debug=True)