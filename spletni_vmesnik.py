from bottle import *
from model import *
import secrets
import os
from datetime import datetime, timedelta

secret_key = secrets.token_hex(42)
static_dir = os.path.join(os.path.dirname(__file__), 'static')

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

def pridobi_url_domaca_stran():
    uporabnisko_ime, vrsta = preveri_piskotek()
    if vrsta == "admin":
        return "/admin"
    elif vrsta == "učitelj":
        return f"/ucitelji/{uporabnisko_ime}"
    elif vrsta == "učenec":
        return f"/ucenci/{uporabnisko_ime}"
    return "/prijava"

def pridobi_url_odjava():
    return "/odjava"

def pridobi_url_nova_instrukcija(uporabnisko_ime):
    return f"/ucitelji/{uporabnisko_ime}/nova_instrukcija"

def pridobi_url_oceni_instrukcijo(id_instrukcije):
    return f"/oceni/{id_instrukcije}"

def pridobi_url_ucitelj_koledar(uporabnisko_ime):
    return f"/ucitelji/{uporabnisko_ime}/koledar"

def pridobi_url_ucenec_koledar(uporabnisko_ime):
    return f"/ucenci/{uporabnisko_ime}/koledar"

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
    napaka = request.query.napaka or None
    redirect("/prijava")

@get("/registracija")
def registracija():
    return template("registracija.html")

@post("/registracija")
def registracija_post():
    uporabnisko_ime = request.forms.get("uporabnisko_ime")
    geslo = request.forms.get("geslo")
    ponovi_geslo = request.forms.get("ponovi_geslo")
    if geslo != ponovi_geslo:
        return template("registracija.html")
    return template("registracija_popup.html", uporabnisko_ime=uporabnisko_ime, geslo=geslo, napaka=None)

@post("/registracija_popup")
def registracija_popup_post():
    uporabnisko_ime = request.forms.get("uporabnisko_ime")
    geslo = request.forms.get("geslo")
    vrsta = int(request.forms.get("vrsta"))
    ime = request.forms.get("ime")
    priimek = request.forms.get("priimek")
    eposta = request.forms.get("eposta")
    cena = request.forms.get("cena") if vrsta == 1 else None
    registracija_uporabnika(uporabnisko_ime, geslo, vrsta, ime, priimek, eposta, cena)
    redirect("/prijava")
    
@get("/preveri_uporabnisko_ime")
def preveri_uporabnisko_ime_v_bazi():
    uporabnisko_ime = request.query.uporabnisko_ime
    obstaja = preveri_uporabnisko_ime(uporabnisko_ime)
    response.content_type = 'application/json'
    return {"obstaja": obstaja}

@get("/admin")
def admin():
    preveri_dostop("admin")
    return template("admin.html", pridobi_domaca_stran=pridobi_url_domaca_stran)

@get("/admin/vsi_ucitelji")
def vsi_ucitelji():
    preveri_dostop("admin")
    page = int(request.query.page or 1)
    limit = 100
    offset = (page - 1) * limit
    vsi_ucitelji = Admin.vsi_ucitelji(limit, offset)
    next_page = page + 1 if len(vsi_ucitelji) == limit else None
    return template("vsi_ucitelji.html", ucitelji=vsi_ucitelji, page=page, limit=limit, next_page=next_page, pridobi_domaca_stran=pridobi_url_domaca_stran)

@get("/admin/vsi_ucenci")
def vsi_ucenci():
    preveri_dostop("admin")
    page = int(request.query.page or 1)
    limit = 100
    offset = (page - 1) * limit
    vsi_ucenci = Admin.vsi_ucenci(limit, offset)
    next_page = page + 1 if len(vsi_ucenci) == limit else None
    return template("vsi_ucenci.html", ucenci=vsi_ucenci, page=page, limit=limit, next_page=next_page, pridobi_domaca_stran=pridobi_url_domaca_stran)

@get("/admin/uredi_uporabnike")
def uredi_uporabnike():
    preveri_dostop("admin")
    uporabnisko_ime = request.query.uporabnisko_ime
    ime = request.query.ime
    priimek = request.query.priimek
    eposta = request.query.eposta
    vrsta = request.query.vrsta
    cena = request.query.cena
    cena_operator = request.query.cena_operator
    page = int(request.query.page or 1)
    
    uporabniki = Uporabnik.vsi_uporabniki(uporabnisko_ime, ime, priimek, eposta, vrsta, cena, cena_operator, page, 100)
    next_page = page + 1 if len(uporabniki) == 100 else None
    return template("uredi_uporabnike.html", uporabniki=uporabniki, pridobi_domaca_stran=pridobi_url_domaca_stran, request=request, page=page, next_page=next_page)

@get("/admin/uredi_uporabnike/<uporabnisko_ime>")
def uredi_uporabnika(uporabnisko_ime):
    preveri_dostop("admin")
    uporabnik = pridobi_uporabnika(uporabnisko_ime)
    return template("uredi_uporabnika.html", uporabnik=uporabnik, pridobi_domaca_stran=pridobi_url_domaca_stran)

@post("/admin/uredi_uporabnike/<uporabnisko_ime>")
def uredi_uporabnika_post(uporabnisko_ime):
    preveri_dostop("admin")
    id_uporabnika = pridobi_id_uporabnika(uporabnisko_ime)
    novo_uporabnisko_ime = request.forms.get("geslo")
    novo_geslo = request.forms.get("geslo")
    nova_vrsta = int(request.forms.get("vrsta"))
    novo_ime = request.forms.get("ime")
    novi_priimek = request.forms.get("priimek")
    nova_eposta = request.forms.get("eposta")
    nova_cena = request.forms.get("cena") if nova_vrsta == 1 else None
    posodobi_uporabnika(id_uporabnika, novo_uporabnisko_ime, novo_geslo, nova_vrsta, novo_ime, novi_priimek, nova_eposta, nova_cena)
    redirect("/admin/uredi_uporabnike")
    
@get("/ucitelji/<uporabnisko_ime>")
def ucitelj(uporabnisko_ime):
    preveri_dostop("učitelj", uporabnisko_ime)
    id_ucitelja = Ucitelj.pridobi_id_ucitelja(uporabnisko_ime)
    ime_ucitelja = Ucitelj.ime_ucitelja(id_ucitelja)
    return template("ucitelj.html", uporabnisko_ime=uporabnisko_ime, ime_ucitelja=ime_ucitelja, pridobi_domaca_stran=pridobi_url_domaca_stran)

@get("/ucitelji/<uporabnisko_ime>/ucenci")
def vsi_ucenci(uporabnisko_ime):
    preveri_dostop("učitelj", uporabnisko_ime)
    id_ucitelja = Ucitelj.pridobi_id_ucitelja(uporabnisko_ime)
    ime_ucitelja = Ucitelj.ime_ucitelja(id_ucitelja)
    page = int(request.query.page or 1)
    limit = 100
    offset = (page - 1) * limit
    ucenci = Ucitelj.ucenci_ucitelja(id_ucitelja, limit=limit, offset=offset)
    next_page = page + 1 if len(ucenci) == limit else None
    return template("ucenci.html", ucenci=ucenci, uporabnisko_ime=uporabnisko_ime, ime_ucitelja=ime_ucitelja, pridobi_domaca_stran=pridobi_url_domaca_stran, page=page, limit=limit, next_page=next_page)

@get("/ucitelji/<uporabnisko_ime>/instrukcije")
def vsi_instrukcije(uporabnisko_ime):
    preveri_dostop("učitelj", uporabnisko_ime)
    id_ucitelja = Ucitelj.pridobi_id_ucitelja(uporabnisko_ime)
    ime_ucitelja = Ucitelj.ime_ucitelja(id_ucitelja)
    page = int(request.query.page or 1)
    limit = 100
    offset = (page - 1) * limit
    instrukcije = Instrukcije.vse_instrukcije_ucitelja(id_ucitelja, limit=limit, offset=offset)
    next_page = page + 1 if len(instrukcije) == limit else None
    return template("instrukcije.html", instrukcije=instrukcije, uporabnisko_ime=uporabnisko_ime, ime_ucitelja=ime_ucitelja, pridobi_domaca_stran=pridobi_url_domaca_stran, page=page, limit=limit, next_page=next_page)

@get("/ucitelji/<uporabnisko_ime>/statistika")
def statistika_ucitelja(uporabnisko_ime):
    preveri_dostop("učitelj", uporabnisko_ime)
    id_ucitelja = Ucitelj.pridobi_id_ucitelja(uporabnisko_ime)
    ime_ucitelja = Ucitelj.ime_ucitelja(id_ucitelja)
    statistika = Ucitelj.pridobi_statistiko(id_ucitelja)
    return template("statistika_ucitelja.html", uporabnisko_ime=uporabnisko_ime, ime_ucitelja=ime_ucitelja, statistika=statistika, pridobi_domaca_stran=pridobi_url_domaca_stran)

@get("/ucitelji/<uporabnisko_ime>/koledar")
def koledar_ucitelj(uporabnisko_ime):
    preveri_dostop("učitelj", uporabnisko_ime)
    id_ucitelja = Ucitelj.pridobi_id_ucitelja(uporabnisko_ime)
    instrukcija_status = request.query.get('instrukcija_status').split(",") if request.query.get('instrukcija_status') else []
    ucenec = request.query.ucenec or None

    week_start_str = request.query.get('week_start')
    if week_start_str:
        current_week_start = datetime.strptime(week_start_str, "%Y-%m-%d")
    else:
        current_week_start = datetime.now()
        current_week_start = current_week_start - timedelta(days=current_week_start.weekday())

    current_week_end = current_week_start + timedelta(days=6)

    instrukcije = Instrukcije.filtrirane_instrukcije_ucitelj(id_ucitelja, instrukcija_status, current_week_start, current_week_end, ucenec)
    return template("koledar.html", 
                    instrukcije=instrukcije, 
                    zacetni_datum=datetime(1970,1,1), 
                    uporabnisko_ime=uporabnisko_ime, 
                    vrsta="učitelj", 
                    pridobi_domaca_stran=pridobi_url_domaca_stran, 
                    pridobi_odjava=pridobi_url_odjava, 
                    pridobi_nova_instrukcija=pridobi_url_nova_instrukcija, 
                    pridobi_oceni_instrukcijo=pridobi_url_oceni_instrukcijo,
                    pridobi_url_ucitelj_koledar = pridobi_url_ucitelj_koledar,
                    pridobi_url_ucenec_koledar = pridobi_url_ucenec_koledar,
                    current_week_start=current_week_start, 
                    current_week_end=current_week_end)

@get("/ucitelji/<uporabnisko_ime>/nova_instrukcija")
def nova_instrukcija(uporabnisko_ime):
    preveri_dostop("učitelj", uporabnisko_ime)
    return template("nova_instrukcija.html", 
                    uporabnisko_ime=uporabnisko_ime, 
                    pridobi_domaca_stran=pridobi_url_domaca_stran, 
                    pridobi_odjava=pridobi_url_odjava, 
                    pridobi_nova_instrukcija=pridobi_url_nova_instrukcija, 
                    pridobi_oceni_instrukcijo=pridobi_url_oceni_instrukcijo,
                    pridobi_url_ucitelj_koledar = pridobi_url_ucitelj_koledar,
                    pridobi_url_ucenec_koledar = pridobi_url_ucenec_koledar)

@post("/ucitelji/<uporabnisko_ime>/nova_instrukcija")
def nova_instrukcija_post(uporabnisko_ime):
    preveri_dostop("učitelj", uporabnisko_ime)
    id_ucitelja = Ucitelj.pridobi_id_ucitelja(uporabnisko_ime)
    ime_predmeta = request.forms.get("ime_predmeta")
    datum = request.forms.get("datum")
    trajanje = request.forms.get("trajanje")
    status = request.forms.get("status")

    Instrukcije.dodaj_instrukcijo(id_ucitelja, ime_predmeta, datum, trajanje, status)
    
    redirect(f"/ucitelji/{uporabnisko_ime}/koledar")

@get("/ucenci/<uporabnisko_ime>")
def ucenec(uporabnisko_ime):
    preveri_dostop("učenec", uporabnisko_ime)
    id_ucenca = Ucenec.pridobi_id_ucenca(uporabnisko_ime)
    ime_ucenca = Ucenec.ime_ucenca(id_ucenca)
    return template("ucenec.html", uporabnisko_ime=uporabnisko_ime, ime_ucenca=ime_ucenca, pridobi_domaca_stran=pridobi_url_domaca_stran)

@get("/ucenci/<uporabnisko_ime>/statistika")
def statistika_ucitelja(uporabnisko_ime):
    preveri_dostop("učenec", uporabnisko_ime)
    id_ucenca = Ucenec.pridobi_id_ucenca(uporabnisko_ime)
    ime_ucenca = Ucenec.ime_ucenca(id_ucenca)
    statistika = Ucenec.pridobi_statistiko(id_ucenca)
    return template("statistika_ucenca.html", uporabnisko_ime=uporabnisko_ime, ime_ucenca=ime_ucenca, statistika=statistika, pridobi_domaca_stran=pridobi_url_domaca_stran)

@get("/ucenci/<uporabnisko_ime>/koledar")
def koledar_ucenec(uporabnisko_ime):
    preveri_dostop("učenec", uporabnisko_ime)
    id_ucenca = Ucenec.pridobi_id_ucenca(uporabnisko_ime)
    instrukcija_status = request.query.get('instrukcija_status').split(",") if request.query.get('instrukcija_status') else []
    ucitelj = request.query.ucitelj or None

    week_start_str = request.query.get('week_start')
    if week_start_str:
        current_week_start = datetime.strptime(week_start_str, "%Y-%m-%d")
    else:
        current_week_start = datetime.now()
        current_week_start = current_week_start - timedelta(days=current_week_start.weekday())

    current_week_end = current_week_start + timedelta(days=6)

    instrukcije = Instrukcije.filtrirane_instrukcije_ucenec(id_ucenca, instrukcija_status, current_week_start, current_week_end, ucitelj)
    return template("koledar.html",
                    instrukcije=instrukcije,
                    zacetni_datum=datetime(1970,1,1),
                    uporabnisko_ime=uporabnisko_ime,
                    vrsta="učenec",
                    pridobi_domaca_stran=pridobi_url_domaca_stran,
                    pridobi_odjava=pridobi_url_odjava,
                    pridobi_nova_instrukcija=pridobi_url_nova_instrukcija,
                    pridobi_oceni_instrukcijo=pridobi_url_oceni_instrukcijo,
                    pridobi_url_ucitelj_koledar = pridobi_url_ucitelj_koledar,
                    pridobi_url_ucenec_koledar = pridobi_url_ucenec_koledar,
                    current_week_start=current_week_start,
                    current_week_end=current_week_end)

@get("/oceni/<id_instrukcije>")
def oceni_instrukcijo(id_instrukcije):
    preveri_dostop("učenec")
    instrukcija = Instrukcije.pridobi_instrukcijo(id_instrukcije)
    return template("oceni_instrukcijo.html", instrukcija=instrukcija, pridobi_domaca_stran=pridobi_url_domaca_stran)

@post("/oceni/<id_instrukcije>")
def oceni_instrukcijo_post(id_instrukcije):
    preveri_dostop("učenec")
    ocena = int(request.forms.get("ocena"))
    komentar = request.forms.get("komentar")
    if ocena and komentar:
        Instrukcije.posodobi_oceno_in_komentar(id_instrukcije, ocena, komentar)
        redirect(f"/ucenci/{request.get_cookie('uporabnisko_ime', secret=secret_key)}/koledar")
    else:
        return template("oceni_instrukcijo.html", instrukcija=Instrukcije.pridobi_instrukcijo(id_instrukcije), pridobi_domaca_stran=pridobi_url_domaca_stran)

run(host="127.0.0.1", port=8080, debug=True, reloader=True)