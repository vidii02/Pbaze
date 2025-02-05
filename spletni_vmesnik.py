from bottle import *
from model import Admin, Ucitelj, Ucenec, Predmet, Instrukcije, UciteljPredmet
import secrets
import sqlite3
import os

secret_key = secrets.token_hex(42)
static_dir = os.path.join(os.path.dirname(__file__), 'static')

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

def preveri_piskotek():
    uporabnisko_ime_cookie = request.get_cookie("uporabnisko_ime", secret=secret_key)
    vrsta_cookie = request.get_cookie("vrsta", secret=secret_key)
    if not uporabnisko_ime_cookie or not vrsta_cookie:
        redirect("/prijava")
    return uporabnisko_ime_cookie, vrsta_cookie

def izbrisi_piskotke():
    cookies = ["uporabnisko_ime", "geslo", "vrsta"]
    for cookie in cookies:
        response.delete_cookie(cookie)

def preveri_dostop(zahtevana_vrsta, uporabnisko_ime=None):
    prijavljen_uporabnisko_ime, vrsta = preveri_piskotek()
    if vrsta != zahtevana_vrsta or (uporabnisko_ime and prijavljen_uporabnisko_ime != uporabnisko_ime):
        if vrsta == "učitelj":
            redirect(f"/ucitelji/{prijavljen_uporabnisko_ime}")
        elif vrsta == "učenec":
            redirect(f"/ucenci/{prijavljen_uporabnisko_ime}")
        elif vrsta == "admin":
            redirect("/admin")
        else:
            redirect("/prijava?napaka=Dostop zavrnjen: Nimate pravic za dostop do te strani.")
    return prijavljen_uporabnisko_ime

def pridobi_domaca_stran():
    uporabnisko_ime, vrsta = preveri_piskotek()
    if vrsta == "admin":
        return "/admin"
    elif vrsta == "učitelj":
        return f"/ucitelji/{uporabnisko_ime}"
    elif vrsta == "učenec":
        return f"/ucenci/{uporabnisko_ime}"
    return "/prijava"

@get('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root=static_dir)

@get("/")
def naslovna_stran():
    izbrisi_piskotke()
    redirect("/prijava")

@get("/prijava")
def prijava():
    izbrisi_piskotke()
    napaka = request.query.napaka or None
    return template("prijava.html", napaka=napaka)

@post("/prijava")
def prijava_post():
    uporabnisko_ime = request.forms.get("uporabnisko_ime")
    geslo = request.forms.get("geslo")
    uporabnik = preveri_uporabnika(uporabnisko_ime, geslo)
    if uporabnik:
        response.set_cookie("uporabnisko_ime", uporabnisko_ime, secret=secret_key)
        response.set_cookie("geslo", geslo, secret=secret_key)
        response.set_cookie("vrsta", uporabnik["vrsta"], secret=secret_key)
        if uporabnik["vrsta"] == "učitelj":
            redirect(f"/ucitelji/{uporabnisko_ime}")
        elif uporabnik["vrsta"] == "učenec":
            redirect(f"/ucenci/{uporabnisko_ime}")
        elif uporabnik["vrsta"] == "admin":
            redirect("/admin")
        else:
            return template("prijava.html", napaka="Napaka pri prijavi")
    else:
        print("Napačno uporabniško ime ali geslo")
        return template("prijava.html", napaka="Napačno uporabniško ime ali geslo")

@get("/odjava")
def odjava():
    izbrisi_piskotke()
    redirect("/prijava")

@get("/admin")
def admin():
    preveri_dostop("admin")
    return template("admin.html", pridobi_domaca_stran=pridobi_domaca_stran)

@get("/admin/vsi_ucitelji")
def vsi_ucitelji():
    preveri_dostop("admin")
    page = int(request.query.page or 1)
    limit = 100
    offset = (page - 1) * limit
    vsi_ucitelji = Admin.vsi_ucitelji(limit, offset)
    next_page = page + 1 if len(vsi_ucitelji) == limit else None
    return template("vsi_ucitelji.html", ucitelji=vsi_ucitelji, page=page, limit=limit, next_page=next_page, pridobi_domaca_stran=pridobi_domaca_stran)

@get("/admin/vsi_ucenci")
def vsi_ucenci():
    preveri_dostop("admin")
    page = int(request.query.page or 1)
    limit = 100
    offset = (page - 1) * limit
    vsi_ucenci = Admin.vsi_ucenci(limit, offset)
    next_page = page + 1 if len(vsi_ucenci) == limit else None
    return template("vsi_ucenci.html", ucenci=vsi_ucenci, page=page, limit=limit, next_page=next_page, pridobi_domaca_stran=pridobi_domaca_stran)

@get("/ucitelji/<uporabnisko_ime>")
def ucitelj(uporabnisko_ime):
    preveri_dostop("učitelj", uporabnisko_ime)
    ime_ucitelja = Ucitelj.ime_ucitelja(Ucitelj.pridobi_id_ucitelja(uporabnisko_ime))
    return template("ucitelj.html", uporabnisko_ime=uporabnisko_ime, ime_ucitelja=ime_ucitelja, pridobi_domaca_stran=pridobi_domaca_stran)

@get("/ucitelji/<uporabnisko_ime>/ucenci")
def vsi_ucenci(uporabnisko_ime):
    preveri_dostop("učitelj", uporabnisko_ime)
    ucenci = Ucitelj.ucenci_ucitelja(Ucitelj.pridobi_id_ucitelja(uporabnisko_ime))
    return template("ucenci.html", ucenci=ucenci, uporabnisko_ime=uporabnisko_ime, pridobi_domaca_stran=pridobi_domaca_stran)

@get("/ucitelji/<uporabnisko_ime>/koledar")
def koledar_ucitelj(uporabnisko_ime):
    preveri_dostop("učitelj", uporabnisko_ime)
    instrukcije = Instrukcije.vse_instrukcije_ucitelja(Ucitelj.pridobi_id_ucitelja(uporabnisko_ime))
    return template("koledar.html", instrukcije=instrukcije, uporabnisko_ime=uporabnisko_ime, vrsta="učitelj", pridobi_domaca_stran=pridobi_domaca_stran)

@get("/ucenci/<uporabnisko_ime>")
def ucenec(uporabnisko_ime):
    preveri_dostop("učenec", uporabnisko_ime)
    ime_ucenca = Ucenec.ime_ucenca(Ucenec.pridobi_id_ucenca(uporabnisko_ime))
    return template("ucenec.html", uporabnisko_ime=uporabnisko_ime, ime_ucenca=ime_ucenca, pridobi_domaca_stran=pridobi_domaca_stran)

@get("/ucenci/<uporabnisko_ime>/koledar")
def koledar_ucenec(uporabnisko_ime):
    preveri_dostop("učenec", uporabnisko_ime)
    instrukcije = Instrukcije.vse_instrukcije_ucenca(Ucenec.pridobi_id_ucenca(uporabnisko_ime))
    return template("koledar.html", instrukcije=instrukcije, uporabnisko_ime=uporabnisko_ime, vrsta="učenec", pridobi_domaca_stran=pridobi_domaca_stran)

run(host="127.0.0.1", port=8080, debug=True, reloader=True)