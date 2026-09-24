from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "una_frase_qualsiasi_a_caso"


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
        # Lettura delle credenziali inviate dal form HTML
        username = request.form["username"]
        password = request.form["password"]

        # Connessione al database ed esecuzione della query parametrizzata
        connessione = connetti_al_database()
        cursore = connessione.cursor()

        cursore.execute(
            "SELECT * FROM utente WHERE username = %s AND password = %s",
            (username, password)
        )

        utente_trovato = cursore.fetchone()

        # Chiusura delle risorse
        cursore.close()
        connessione.close()

        # Verifica dell'esito della query
        if utente_trovato is None:
            # Login fallito: ricarica il form passando il messaggio d'errore
            return render_template("login.html", errore="Credenziali errate")
        else:
            # Login riuscito: salva lo stato in sessione e reindirizza alla route 'elenco'
            session["loggato"] = True
            return redirect(url_for("elenco"))
    else:
        # Metodo GET: mostra il form vuoto senza errori
        return render_template("login.html", errore=None)

@app.route("/logout")
def logout():
    # Svuota tutti i dati salvati nella sessione corrente
    session.clear()
    # Reindirizza l'utente alla pagina di login
    return redirect(url_for("login"))


# Esempio di come si usa il "cancello" in una pagina protetta
# (lo scriveranno gli Studenti 2, 3 e 4 nelle rispettive route)
@app.route("/esempio-pagina-protetta")
def esempio_pagina_protetta():
    # Controllo di sicurezza: se l'utente non è autenticato, rimanda al login
    if not session.get("loggato"):
        return redirect(url_for("login"))

    return "Questa pagina si vede solo se hai fatto login"