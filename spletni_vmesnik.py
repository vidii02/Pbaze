from bottle import *
from model import Ucitelj, Ucenec, Predmet, Instrukcije, UciteljPredmet
import secrets
import sqlite3

secret_key = secrets.token_hex(42)

def preveri_uporabnika(uporabnisko_ime, geslo):
    # Preveri uporabniško ime in geslo v tabeli uporabniki
    with sqlite3.connect("baza.db") as povezava:
        cursor = povezava.cursor()
        cursor.execute("SELECT Uporabnisko_ime, Geslo, Vrsta FROM uporabniki WHERE Uporabnisko_ime = ? AND Geslo = ?", (uporabnisko_ime, geslo))
        uporabnik = cursor.fetchone()
        if uporabnik:
            vrsta = "učitelj" if uporabnik[2] == 1 else "učenec" if uporabnik[2] == 0 else "admin"
            return {"uporabnisko_ime": uporabnik[0], "geslo": uporabnik[1], "vrsta": vrsta}
        return None

def preveri_piskotek(uporabnisko_ime):
    uporabnisko_ime_cookie = request.get_cookie("uporabnisko_ime", secret=secret_key)
    if not uporabnisko_ime_cookie or uporabnisko_ime_cookie != uporabnisko_ime:
        redirect("/prijava")
    return uporabnisko_ime_cookie

@get("/")
def naslovna_stran():
    cookies = ["uporabnisko_ime", "geslo"]
    for cookie in cookies:
        response.delete_cookie(cookie)
    redirect("/prijava")

@get("/prijava")
def prijava():
    return template("prijava.html")

@post("/prijava")
def prijava_post():
    up_ime = request.forms.get("uporabnisko_ime")
    geslo = request.forms.get("geslo")
    uporabnik = preveri_uporabnika(up_ime, geslo)
    if uporabnik:
        response.set_cookie("uporabnisko_ime", up_ime, secret=secret_key)
        response.set_cookie("geslo", geslo, secret=secret_key)
        if uporabnik["vrsta"] == "učitelj":
            redirect(f"/ucitelji/{up_ime}")
        elif uporabnik["vrsta"] == "učenec":
            redirect(f"/ucenci/{up_ime}")
        elif uporabnik["vrsta"] == "admin":
            redirect("/admin")
        else:
            return template("prijava.html", napaka="Napaka pri prijavi")
    else:
        print("Napačno uporabniško ime ali geslo")
        return template("prijava.html", napaka="Napačno uporabniško ime ali geslo")

@get("/odjava")
def odjava():
    cookies = ["uporabnisko_ime", "geslo"]
    for cookie in cookies:
        response.delete_cookie(cookie)
    redirect("/prijava")

@get("/admin")
def admin():
    uporabnisko_ime = request.get_cookie("uporabnisko_ime", secret=secret_key)
    if not uporabnisko_ime:
        redirect("/prijava")
    return template("admin.html")

@get("/ucitelji/<uporabnisko_ime>")
def ucitelj(uporabnisko_ime):
    preveri_piskotek(uporabnisko_ime)
    return template("ucitelj.html", uporabnisko_ime=uporabnisko_ime)

@get("/ucitelji/<uporabnisko_ime>/vsi_ucenci")
def vsi_ucenci(uporabnisko_ime):
    preveri_piskotek(uporabnisko_ime)
    ucenci = Ucitelj.ucenci_ucitelja(Ucitelj.pridobi_id_ucitelja(uporabnisko_ime))
    return template("vsi_ucenci.html", ucenci=ucenci, uporabnisko_ime=uporabnisko_ime)

@get("/ucenci/<uporabnisko_ime>")
def ucenec(uporabnisko_ime):
    preveri_piskotek(uporabnisko_ime)
    return template("ucenec.html", uporabnisko_ime=uporabnisko_ime)

run(host="127.0.0.1", port=8080, debug=True, reloader=True)