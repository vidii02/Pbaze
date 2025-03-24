from model import *
import time
import getpass

statistika = {
    "stevilo_instrukcij": "Število inštrukcij",
    "stevilo_opravljenih": "Število opravljenih inštrukcij",
    "stevilo_rezerviranih": "Število rezerviranih inštrukcij",
    "stevilo_preklicanih": "Število preklicanih inštrukcij",
    "skupno_stevilo_ur": "Skupno število ur",
    "stevilo_predmetov": "Število predmetov",
    "zasluzek": "Skupni zaslužek",
    "povprecna_ocena": "Povprečna ocena",
    "stevilo_ucencev": "Število učencev",
    "stopnja_uspesnosti_rezervacij": "Stopnja uspešnosti rezervacij",
    "povprecno_trajanje": "Povprečno trajanje inštrukcije",
    "povprecen_zasluzek_na_instrukcijo": "Povprečen zaslužek na inštrukcijo",
    "najpogostejsi_predmet": "Najpogostejši predmet",
    "najpogostejsi_ucenec": "Najpogostejši učenec",
    "stevilo_uciteljev": "Število učiteljev",
    "povprecna_dolzina_instrukcije": "Povprečna dolžina inštrukcije",
    "najpogostejsi_predmet": "Največkrat izbran predmet",
    "najpogostejsi_ucitelj": "Največkrat izbran učitelj"
}

### Metode

def odjava():
    print("Uspešno si se odjavil!")
    time.sleep(1)
    print()
    glavni_meni()

def preveri_dostop(uporabnik, vrsta: list):
    """Preveri, če ima uporabnik pravico dostopa."""
    
    if uporabnik["vrsta"] not in vrsta:
        print("Nimaš pravice dostopa!")
        time.sleep(1)
        return False
    
    return True

def prikazi_moznosti(izbire, nazaj = False, glavni_meni = False, izpis = False, konec = False, vrsta = "", page_options: dict = dict()):
    """Izpiši možnosti v glavnem meniju."""
    
    barva = ""
    if vrsta == "učitelj":  # Barva za učitelja
        barva = "34"    # Modra
    elif vrsta == "učenec": # Barva za učenca
        barva = "32"    # Zelena
    elif vrsta == "page":   # Barva za strani
        barva = "36"    # Cyan
    
    if len(page_options.items()) == 0:    # Če ni strani
        i = 1
        for moznost in (izbire): # Izpišejo se možnosti od 1 naprej
            print(f"\033[1;{barva}m{i}) {moznost}\033[0m")
            i += 1
    else:
        for key, value in page_options.items():
            print(f"\033[1;{barva}m{key}) {value}\033[0m")
    
    if nazaj:   # Možnost za vrnitev nazaj
        print(f"\033[1;93m{i}) Nazaj\033[0m")
        i += 1
    
    if glavni_meni:   # Možnost za vrnitev v glavni meni
        print(f"\033[1;37m{i}) Glavni meni\033[0m")
        i += 1
    
    if izpis:   # Možnost za izpis
        print(f"\033[1;33m{i}) Odjava\033[0m")
    
    if konec:   # Možnost za končanje programa
        print(f"\033[1;31m0) Konec\033[0m")

def konec():
    """Pozdravi pred končanjem programa."""
    print("Adijo!")
    time.sleep(1)
    exit()
    
def vsi_ucitelji(page, limit, st_uciteljov):
    skupno_strani = st_uciteljov // limit + 1 if st_uciteljov % limit != 0 else st_uciteljov // limit
    zacetni_indeks = (page - 1) * limit
    koncni_indeks = min(zacetni_indeks + limit, st_uciteljov)
    
    offset = (page - 1) * limit
    ucitelji = Admin.vsi_ucitelji(limit, offset)
    
    print("-" * 100)
    
    elements = ["", "Ime učenca: ", "Priimek učenca: ", "E-pošta: ", "Cena: "]
    spacing = [6, 45, 45, 45, 45]
    dolzina = 55
    velika_dolzina = 61
    big_padding_left = "║" + " " * ((velika_dolzina - dolzina) // 2)
    big_padding_right = " " * ((velika_dolzina - dolzina) // 2) + "║"
    padding_left = "║ "
    padding_right = "   ║"
    row = "║" + " " * (velika_dolzina + 2) + "║"
    header = f"Vsi učitelji (Stran {page} od {skupno_strani})"
    header_padding = " " * ((velika_dolzina - 4 - len(header)) // 2)
    
    print("╔" + "═" * (velika_dolzina + 2) + "╗")
    print(f"{row}\n{big_padding_left}{header_padding}{header}{header_padding}{' ' if len(header) % 2 == 0 else ''}{big_padding_right}\n{row}")
    
    ind = 0
    for i in range(zacetni_indeks, koncni_indeks):
        print(f"{big_padding_left}╔{'═' * dolzina}╗{big_padding_right}")
        
        ucitelj: Ucitelj = ucitelji[ind]
        
        elements[0] = f"#{i+1}"
        
        data = ["", ucitelj.ime, ucitelj.priimek, ucitelj.eposta, str(ucitelj.cena) + " €"]
        
        formated_data = [elements[i] + str(data[i]) + " " * (spacing[i] - len(elements[i]) - len(str(data[i]))) for i in range(len(data))]
        
        print(f"{big_padding_left}{padding_left}{formated_data[0]}{formated_data[1]}{padding_right}{big_padding_right}\n" + 
              f"{big_padding_left}{padding_left}{' ' * 6}{formated_data[2]}{padding_right}{big_padding_right}\n" + 
              f"{big_padding_left}{padding_left}{' ' * 6}{formated_data[3]}{padding_right}{big_padding_right}\n" + 
              f"{big_padding_left}{padding_left}{' ' * 6}{formated_data[4]}{padding_right}{big_padding_right}")
        
        print(f"{big_padding_left}╚{'═' * dolzina}╝{big_padding_right}")
        
        if ind < len(ucitelji):
            print("║" + " " * (velika_dolzina + 2) + "║")
        
        ind += 1
    
    print("╚" + "═" * (velika_dolzina + 2) + "╝") 

    print("-" * 100)

def vsi_ucenci(page, limit, st_ucencev):
    skupno_strani = st_ucencev // limit + 1 if st_ucencev % limit != 0 else st_ucencev // limit
    zacetni_indeks = (page - 1) * limit
    koncni_indeks = min(zacetni_indeks + limit, st_ucencev)
    
    offset = (page - 1) * limit
    ucenci = Admin.vsi_ucenci(limit, offset)
    
    print("-" * 100)    
    
    elements = ["", "Ime učenca: ", "Priimek učenca: ", "E-pošta: "]
    spacing = [6, 45, 45, 45]
    dolzina = 55
    velika_dolzina = 61
    big_padding_left = "║" + " " * ((velika_dolzina - dolzina) // 2)
    big_padding_right = " " * ((velika_dolzina - dolzina) // 2) + "║"
    padding_left = "║ "
    padding_right = "   ║"
    row = "║" + " " * (velika_dolzina + 2) + "║"
    header = f"Vsi učenci (Stran {page} od {skupno_strani})"
    header_padding = " " * ((velika_dolzina - 4 - len(header)) // 2)
    
    print("╔" + "═" * (velika_dolzina + 2) + "╗")
    print(f"{row}\n{big_padding_left}{header_padding}{header}{header_padding}{' ' if len(header) % 2 == 0 else ''}{big_padding_right}\n{row}")
    
    ind = 0
    for i in range(zacetni_indeks, koncni_indeks):
        print(f"{big_padding_left}╔{'═' * dolzina}╗{big_padding_right}")
        
        ucenec: Ucenec = ucenci[ind]
        
        elements[0] = f"#{i+1}"
        
        data = ["", ucenec.ime, ucenec.priimek, ucenec.eposta]
        
        formated_data = [elements[i] + str(data[i]) + " " * (spacing[i] - len(elements[i]) - len(str(data[i]))) for i in range(len(data))]
        
        print(f"{big_padding_left}{padding_left}{formated_data[0]}{formated_data[1]}{padding_right}{big_padding_right}\n" + 
              f"{big_padding_left}{padding_left}{' ' * 6}{formated_data[2]}{padding_right}{big_padding_right}\n" + 
              f"{big_padding_left}{padding_left}{' ' * 6}{formated_data[3]}{padding_right}{big_padding_right}")
        
        print(f"{big_padding_left}╚{'═' * dolzina}╝{big_padding_right}")
        
        if ind < len(ucenci):
            print("║" + " " * (velika_dolzina + 2) + "║")
        
        ind += 1
    
    print("╚" + "═" * (velika_dolzina + 2) + "╝") 

    print("-" * 100)

def uciteljevi_ucenci(id_ucitelja, page, limit, st_ucencev):
    skupno_strani = st_ucencev // limit + 1 if st_ucencev % limit != 0 else st_ucencev // limit
    zacetni_indeks = (page - 1) * limit
    koncni_indeks = min(zacetni_indeks + limit, st_ucencev)
    ucitelj = Ucitelj.ime_ucitelja(id_ucitelja)
    
    offset = (page - 1) * limit
    ucenci: list = Ucitelj.ucenci_ucitelja(id_ucitelja, limit=limit, offset=offset)
    
    print("-" * 100)

    elements = ["", "Ime učenca: ", "Priimek učenca: ", "E-pošta: "]
    spacing = [6, 45, 45, 45]
    dolzina = 55
    velika_dolzina = 61
    big_padding_left = "║" + " " * ((velika_dolzina - dolzina) // 2)
    big_padding_right = " " * ((velika_dolzina - dolzina) // 2) + "║"
    padding_left = "║ "
    padding_right = "   ║"
    row = "║" + " " * (velika_dolzina + 2) + "║"
    header = f"Vsi učenci od {ucitelj} (Stran {page} od {skupno_strani})"
    header_padding = " " * ((velika_dolzina - 4 - len(header)) // 2)
    
    print("╔" + "═" * (velika_dolzina + 2) + "╗")
    print(f"{row}\n{big_padding_left}{header_padding}{header}{header_padding}{' ' if len(header) % 2 == 0 else ''}{big_padding_right}\n{row}")
    
    ind = 0
    for i in range(zacetni_indeks, koncni_indeks):
        print(f"{big_padding_left}╔{'═' * dolzina}╗{big_padding_right}")

        ucenec: Ucenec = ucenci[ind]
        
        elements[0] = f"#{i+1}"
        
        data = ["", ucenec.ime, ucenec.priimek, ucenec.eposta]
        
        formated_data = [elements[i] + str(data[i]) + " " * (spacing[i] - len(elements[i]) - len(str(data[i]))) for i in range(len(data))]
        
        print(f"{big_padding_left}{padding_left}{formated_data[0]}{formated_data[1]}{padding_right}{big_padding_right}\n" + 
              f"{big_padding_left}{padding_left}{' ' * 6}{formated_data[2]}{padding_right}{big_padding_right}\n" + 
              f"{big_padding_left}{padding_left}{' ' * 6}{formated_data[3]}{padding_right}{big_padding_right}")
        
        print(f"{big_padding_left}╚{'═' * dolzina}╝{big_padding_right}")
        
        if ind < len(ucenci):
            print("║" + " " * (velika_dolzina + 2) + "║")
        
        ind += 1
    
    print("╚" + "═" * (velika_dolzina + 2) + "╝") 
    
    print("-" * 100)

def uciteljeve_instrukcije(id_ucitelja, page, limit, st_instrukcij):
    skupno_strani = st_instrukcij // limit + 1 if st_instrukcij % limit != 0 else st_instrukcij // limit
    zacetni_indeks = (page - 1) * limit
    koncni_indeks = min(zacetni_indeks + limit, st_instrukcij)
    ucitelj = Ucitelj.ime_ucitelja(id_ucitelja)
    
    offset = (page - 1) * limit
    instrukcije = Instrukcije.vse_instrukcije_ucitelja(id_ucitelja, limit, offset)
    
    print("-" * 100)
    
    status = {"Opravljeno": "\033[0;32mOpravljeno\033[0m", "Rezervirano": "\033[0;93mRezervirano\033[0m", "Preklicano": "\033[0;31mPreklicano\033[0m"}
    ocena = {None: "Ni ocene", 1: "\033[0;31m1\033[0m" + " " * 27, 2: "\033[0;31m2\033[0m" + " " * 27, 3: "\033[0;93m3\033[0m" + " " * 27, 4: "\033[0;32m4\033[0m" + " " * 27, 5: "\033[0;32m5\033[0m" + " " * 27}
    elements = ["", "Ime učenca: ", "Priimek učenca: ", "E-pošta: ", "Predmet: ", "Datum: ", "Trajanje: ", "Status: ", "Ocena: ", "Mnenje: "]
    spacing = [6, 45, 35, 45, 35, 45, 35, 56, 35, 80]
    dolzina = 90
    velika_dolzina = 96
    big_padding_left = "║" + " " * ((velika_dolzina - dolzina) // 2)
    big_padding_right = " " * ((velika_dolzina - dolzina) // 2) + "║"
    padding_left = "║ "
    padding_right = "   ║"
    row = "║" + " " * (velika_dolzina + 2) + "║"
    header = f"Vse inštrukcije {ucitelj} (Stran {page} od {skupno_strani})"
    header_padding = " " * ((velika_dolzina - 4 - len(header)) // 2)
    
    print("╔" + "═" * (velika_dolzina + 2) + "╗")
    print(f"{row}\n{big_padding_left}{header_padding}{header}{header_padding}{' ' if len(header) % 2 == 1 else ''}{big_padding_right}\n{row}")
    
    ind = 0
    for i in range(zacetni_indeks, koncni_indeks):
        print(f"{big_padding_left}╔{'═' * dolzina}╗{big_padding_right}")
        
        instrukcija: Instrukcije = instrukcije[ind]
        ucenec = podatki_ucenca(instrukcija.id_ucenca)
        
        elements[0] = f"#{i+1}"
        
        mnenje = instrukcija.mnenje if len(instrukcija.mnenje) < 72 else instrukcija.mnenje[:70] + "..." 
        data = ["", ucenec[0], ucenec[1], ucenec[2], instrukcija.ime_predmeta, instrukcija.datum, instrukcija.trajanje, status[instrukcija.status], ocena[instrukcija.ocena], mnenje]
        
        formated_data = [elements[i] + str(data[i]) + " " * (spacing[i] - len(elements[i]) - len(str(data[i]))) for i in range(len(data))]

        vrstica_1 = (f"{formated_data[0]}" +
                     f"{formated_data[1]}" +
                     f"{formated_data[2]}")

        vrstica_2 = (f"{formated_data[3]}" +
                     f"{formated_data[4]}")

        vrstica_3 = (f"{formated_data[5]}" +
                     f"{formated_data[6]}")

        vrstica_4 = (f"{formated_data[7]}" +
                     f"{formated_data[8]}")
        
        vrstica_5 = (f"{formated_data[9]}")
        
        print(f"{big_padding_left}{padding_left}{vrstica_1}{padding_right}{big_padding_right}\n" + 
              f"{big_padding_left}╠{'═' * dolzina}╣{big_padding_right}\n" +
              f"{big_padding_left}{padding_left}{' ' * 6}{vrstica_2}{padding_right}{big_padding_right}\n" + 
              f"{big_padding_left}{padding_left}{' ' * 6}{vrstica_3}{padding_right}{big_padding_right}\n" + 
              f"{big_padding_left}{padding_left}{' ' * 6}{vrstica_4}{padding_right}{big_padding_right}\n" + 
              f"{big_padding_left}{padding_left}{' ' * 6}{vrstica_5}{padding_right}{big_padding_right}")
        
        print(f"{big_padding_left}╚{'═' * dolzina}╝{big_padding_right}")
        
        if ind < len(instrukcije):
            print("║" + " " * (velika_dolzina + 2) + "║")
        
        ind += 1
    
    print("╚" + "═" * (velika_dolzina + 2) + "╝") 
    
    print("-" * 100)

def izpisi_statistiko(ime_priimek, statistika_data: dict):
    print("-" * 100)
    
    elements = []
    data = []
    for key, value in statistika_data.items():
        vrednost = value
        if isinstance(vrednost, float):
            vrednost = f"{vrednost:.2f}"
        if key in ["zasluzek", "povprecen_zasluzek_na_instrukcijo"]:
            vrednost = f"{vrednost} €"
        elif key == "stopnja_uspesnosti_rezervacij":
            vrednost = f"{vrednost} %"
        
        elements.append(f"{statistika[key]}: ")
        data.append(vrednost)
    
    dolzina = 50
    padding_left = "║  "
    padding_right = "  ║"
    row = "║" + " " * dolzina + "║"
    header = f"Statistika za {ime_priimek}"
    header_padding = " " * ((dolzina - 4 - len(header)) // 2)
    
    formated_data = [elements[i] + str(data[i]) + " " * (dolzina - 4 - len(elements[i]) - len(str(data[i]))) for i in range(len(data))]
    
    print("╔" + "═" * dolzina + "╗")
    print(f"{row}\n{padding_left}{header_padding}{header}{header_padding}{' ' if len(header) % 2 == 1 else ''}{padding_right}\n{row}")
    
    print("╠" + "═" * dolzina + "╣")
    
    for i in range(len(statistika_data)):
        print(f"{padding_left}{formated_data[i]}{padding_right}")
    
    print("╚" + "═" * dolzina + "╝") 

    print("-" * 100)

def koledar(uporabnik, current_week_start: datetime, current_week_end: datetime, filtrirane_instrukcije):
    print("-" * 100)
    
    elements = []
    data = []
    
    ocena = {None: "Ni ocene", 1: "\033[0;31m1\033[0m" + " " * 54, 2: "\033[0;31m2\033[0m" + " " * 54, 3: "\033[0;93m3\033[0m" + " " * 54, 4: "\033[0;32m4\033[0m" + " " * 54, 5: "\033[0;32m5\033[0m" + " " * 54}
    status = {"Opravljeno": "\033[0;32mOpravljeno\033[0m" + " " * 44, "Rezervirano": "\033[0;93mRezervirano\033[0m" + " " * 43, "Preklicano": "\033[0;31mPreklicano\033[0m" + " " * 44}
    elements = ["Učitelj: ", "Učenec: ", "Predmet: ", "", "Status: ", "Ocena: ", "Mnenje: "]
    dolzina = 70
    spacing = [dolzina - 8 for _ in range(len(elements))]
    srednja_dolzina = dolzina + 6
    velika_dolzina = srednja_dolzina + 6
    padding_left = "║   "
    padding_right = "   ║"
    middle_padding_left = "║" + " " * ((srednja_dolzina - dolzina) // 2)
    middle_padding_right = " " * ((srednja_dolzina - dolzina) // 2) + "║"
    big_padding_left = "║" + " " * ((velika_dolzina - srednja_dolzina) // 2)
    big_padding_right = " " * ((velika_dolzina - srednja_dolzina) // 2) + "║"
    middle_row = big_padding_left + "║" + " " * srednja_dolzina + "║" + big_padding_right
    big_row = "║" + " " * (velika_dolzina + 2) + "║"
    zacetek = current_week_start.date()
    konec = current_week_end.date()
    date_start = f"{zacetek.day}-{zacetek.month}-{zacetek.year}"
    date_end = f"{konec.day}-{konec.month}-{konec.year}"
    header = f'Koledar {Ucitelj.ime_ucitelja(Ucitelj.pridobi_id_ucitelja(uporabnik["uporabnisko_ime"])) if uporabnik["vrsta"] == "učitelj" else Ucenec.ime_ucenca(Ucenec.pridobi_id_ucenca(uporabnik["uporabnisko_ime"]))} od {date_start} do {date_end}'
    header_padding = " " * ((velika_dolzina - 4 - len(header)) // 2)
    if len(filtrirane_instrukcije) != 0:
        zacetni_datum = datetime.strptime(filtrirane_instrukcije[0].datum, "%Y-%m-%d %H:%M").date()
    new_day = False
    
    print("╔" + "═" * (velika_dolzina + 2) + "╗")
    print(f"{big_row}\n{big_padding_left}{header_padding}{header}{header_padding}{' ' if len(header) % 2 == 1 else ''}{big_padding_right}\n{big_row}")
    
    for i in range(len(filtrirane_instrukcije)):
        instrukcija: Instrukcije = filtrirane_instrukcije[i]
          
        datum = datetime.strptime(instrukcija.datum, "%Y-%m-%d %H:%M").date()
        if zacetni_datum < datum or i == 0:
            zacetni_datum = datum
            if new_day:
                new_day = False
                print(f"{middle_padding_left}╚{'═' * srednja_dolzina}╝{middle_padding_right}")
                print(big_row)
            new_day = True
            print(f"{big_padding_left}╔{'═' * srednja_dolzina}╗{big_padding_right}")
            current_date = f"{datum.day}-{datum.month}-{datum.year}"
            padding = " " * ((dolzina - len(current_date)) // 2)
            print(f"{big_padding_left}{middle_padding_left}{padding}{current_date}{padding}{' ' if len(current_date) % 2 == 1 else ''}{middle_padding_right}{big_padding_right}")
            print(middle_row)
        
        mnenje = instrukcija.mnenje if len(instrukcija.mnenje) < dolzina - 15 else instrukcija.mnenje[:dolzina - 19] + "..." 
        data = [Ucitelj.ime_ucitelja(instrukcija.id_ucitelja), Ucenec.ime_ucenca(instrukcija.id_ucenca), instrukcija.ime_predmeta, f'Od {instrukcija.datum.split(" ")[1]} do {(datetime.strptime(instrukcija.datum.split(" ")[1], "%H:%M") + timedelta(minutes=int(instrukcija.trajanje))).strftime("%H:%M")}', status[instrukcija.status], ocena[instrukcija.ocena], mnenje]
        
        formated_data = [elements[i] + str(data[i]) + " " * (spacing[i] - len(elements[i]) - len(str(data[i]))) for i in range(len(data))]
        
        print(f"{middle_padding_left}{padding_left}╔{'═' * (dolzina - 2)}╗{padding_right}{middle_padding_right}")
        
        for j in range(len(formated_data)):
            print(f"{big_padding_left}{middle_padding_left}{padding_left}{formated_data[j]}{padding_right}{middle_padding_right}{big_padding_right}")
        
        print(f"{middle_padding_left}{padding_left}╚{'═' * (dolzina - 2)}╝{padding_right}{middle_padding_right}")
    
    if len(filtrirane_instrukcije) != 0:
        print(f"{middle_padding_left}╚{'═' * srednja_dolzina}╝{middle_padding_right}")
    
    print("╚" + "═" * (velika_dolzina + 2) + "╝") 
    
    print("-" * 100)

def podatki_ucenca(id_ucenca):
    with sqlite3.connect("baza.db") as povezava:
        cursor = povezava.cursor()
        sql_ucenec = f"SELECT ime, priimek, eposta FROM ucenci WHERE id = {id_ucenca};"
        cursor.execute(sql_ucenec)
        ucenec = cursor.fetchone()
    return ucenec

def st_vseh_ucencev():
    with sqlite3.connect("baza.db") as povezava:
        cursor = povezava.cursor()
        sql_ucenci = "SELECT COUNT(*) AS stevilo_ucencev FROM ucenci;"
        cursor.execute(sql_ucenci)
        st_ucencev = cursor.fetchone()[0]
    return st_ucencev

def st_vseh_uciteljov():
    with sqlite3.connect("baza.db") as povezava:
        cursor = povezava.cursor()
        sql_ucitelji = "SELECT COUNT(*) AS stevilo_uciteljev FROM ucitelji;"
        cursor.execute(sql_ucitelji)
        st_uciteljov = cursor.fetchone()[0]
    return st_uciteljov

def st_uciteljevih_instrukcij(id_ucitelja):
    with sqlite3.connect("baza.db") as povezava:
        cursor = povezava.cursor()
        sql_instrukcije = f"SELECT COUNT(*) AS stevilo_instrukcij FROM instrukcije WHERE id_ucitelja = {id_ucitelja};"
        cursor.execute(sql_instrukcije)
        st_instrukcij = cursor.fetchone()[0]
    return st_instrukcij

### Meniji

def glavni_meni():
    """Prikaže glavni meni."""
    
    izbire = ["Prijava", "Registracija"]
    prikazi_moznosti(izbire, konec = True)
    
    match input("Izberi možnost: "):
        case "1":
            meni_prijava()
        case "2":
            meni_registracija()
        case "0":
            konec()
        case _: 
            print("Napačna izbira!")
            time.sleep(1)
            glavni_meni()

def meni_prijava():
    """Prikaže meni za prijavo."""
    
    up_ime = input("Vnesi uporabniško ime: ")
    geslo = getpass.getpass("Vnesi geslo: ")
    
    uporabnik = Uporabnik.preveri_uporabnika(up_ime, geslo)
    
    if not uporabnik:
        print("Uporabnik ne obstaja!")
        time.sleep(1)
        print()
        glavni_meni()
    
    if uporabnik["vrsta"] == "učitelj":
        ime_ucitelja = Ucitelj.ime_ucitelja(Ucitelj.pridobi_id_ucitelja(uporabnik["uporabnisko_ime"]))
        print(f"\nPozdravljen/a, \033[1m{ime_ucitelja}!\033[0m")
        glavni_meni_ucitelj(uporabnik)
    elif uporabnik["vrsta"] == "učenec":
        ime_ucenca = Ucenec.ime_ucenca(Ucenec.pridobi_id_ucenca(uporabnik["uporabnisko_ime"]))
        print(f"\nPozdravljen/a, \033[1m{ime_ucenca}!\033[0m")
        glavni_meni_ucenec(uporabnik)
    else:
        glavni_meni_admin(uporabnik)
    
    return

def meni_registracija():
    while True:
        uporabnisko_ime = input("Vnesi uporabniško ime: ")
        if not Uporabnik.preveri_uporabnisko_ime(uporabnisko_ime):
            break
        print("Uporabniško ime že obstaja! Poskusi znova.")
    geslo = getpass.getpass("Vnesi geslo: ")
    while True:
        izbira = input("Izberi vrsto uporabnika:\n1) Učitelj\n2) Učenec\n")
        if izbira in ["1", "2"]:
            break
        print("Napačna izbira! Poskusi znova.")
    vrsta = "učitelj" if izbira == "1" else "učenec"
    ime = input("Vnesi ime: ")
    priimek = input("Vnesi priimek: ")
    email = input("Vnesi e-pošto: ")
    if vrsta == "učitelj":
        while True:
            cena = float(input("Vnesi ceno inštrukcij: "))
            if 0 < cena < 50:
                break
            print("Cena mora biti med 0 in 50!")
        Uporabnik.registracija_uporabnika(uporabnisko_ime, geslo, vrsta, ime, priimek, email, cena) 
    else:
        Uporabnik.registracija_uporabnika(uporabnisko_ime, geslo, vrsta, ime, priimek, email)
    
    print("Uspešno si se registriral!")
    time.sleep(1)    
    glavni_meni()

def glavni_meni_ucitelj(uporabnik):
    if not preveri_dostop(uporabnik, ["učitelj"]):
        return
    
    moznosti = ["Vsi učenci", "Vsi termini inštrukcij", "Statistika", "Koledar"]
    prikazi_moznosti(moznosti, izpis = True, konec = True, vrsta = "učitelj")
    
    match input("Izberi možnost: "):
        case "1":
            meni_uciteljevi_ucenci(uporabnik)
        case "2":
            meni_uciteljeve_instrukcije(uporabnik)
        case "3":
            meni_statistika(uporabnik)
        case "4":
            meni_koledar(uporabnik)
        case "5":
            odjava()
        case "0":
            konec()
        case _: 
            print("Napačna izbira!")
            time.sleep(1)
    
    glavni_meni_ucitelj(uporabnik)

def glavni_meni_ucenec(uporabnik):
    if not preveri_dostop(uporabnik, ["učenec"]):
        return
    
    moznosti = ["Statistika", "Koledar"]
    prikazi_moznosti(moznosti, izpis = True, konec = True, vrsta = "učenec")
    
    match input("Izberi možnost: "):
        case "1":
            meni_statistika(uporabnik)
        case "2":
            meni_koledar(uporabnik)
        case "3":
            odjava()
        case "0":
            konec()
        case _: 
            print("Napačna izbira!")
            time.sleep(1)
    
    glavni_meni_ucenec(uporabnik)

def glavni_meni_admin(uporabnik):
    if not preveri_dostop(uporabnik, ["admin"]):
        return
    
    moznosti = ["Vsi učitelji", "Vsi učenci"]
    prikazi_moznosti(moznosti, izpis = True, konec = True)
    
    match input("Izberi možnost: "):
        case "1":
            meni_vsi_ucitelji(uporabnik)
        case "2":
            meni_vsi_ucenci(uporabnik)
        case "0":
            konec()
        case _: 
            print("Napačna izbira!")
            time.sleep(1)
    glavni_meni_admin(uporabnik)
        
def meni_uciteljevi_ucenci(uporabnik, page=1, limit=10):
    if not preveri_dostop(uporabnik, ["učitelj"]):
        return
    
    id_ucitelja = Ucitelj.pridobi_id_ucitelja(uporabnik["uporabnisko_ime"])
    st_ucencev = len(Ucitelj.ucenci_ucitelja(id_ucitelja))
    
    while True:
        uciteljevi_ucenci(id_ucitelja, page, limit, st_ucencev)
        
        st_strani = st_ucencev // limit + 1
        moznosti = []
        page_options = dict()
        if page < st_strani and page * limit < st_ucencev:
            moznosti.append("+")
            page_options["+"] = "Naprej"
        if page > 1:
            moznosti.append("-")
            page_options["-"] = "Nazaj"
        prikazi_moznosti(moznosti, konec=True, vrsta = "page", page_options = page_options)
        
        izbira = input("Izberi možnost: ")
        
        if izbira == "+" and "+" in moznosti:
            page += 1
        elif izbira == "-" and "-" in moznosti:
            page -= 1
        elif izbira == "0":
            break
        else:
            print("Napačna izbira!")
            time.sleep(1)

def meni_vsi_ucitelji(uporabnik, page = 1, limit = 5):
    if not preveri_dostop(uporabnik, ["admin"]):
        return
    
    st_uciteljev = st_vseh_uciteljov()
    
    while True:
        vsi_ucitelji(page, limit, st_uciteljev)
        
        st_strani = st_uciteljev // limit + 1
        moznosti = []
        page_options = dict()
        if page - 1 < st_strani and page * limit < st_uciteljev:
            moznosti.append("+")
            page_options["+"] = "Naprej"
        if page > 1:
            moznosti.append("-")
            page_options["-"] = "Nazaj"
        prikazi_moznosti(moznosti, konec = True, vrsta = "page", page_options = page_options)
        
        izbira = input("Izberi možnost: ")
        
        if izbira == "+" and "+" in moznosti:
            page += 1
        elif izbira == "-" and "-" in moznosti:
            page -= 1
        elif izbira == "0":
            break
        else:
            print("Napačna izbira!")
            time.sleep(1)
            meni_vsi_ucitelji(uporabnik, page, limit)

def meni_vsi_ucenci(uporabnik, page = 1, limit = 5):
    if not preveri_dostop(uporabnik, ["admin"]):
        return
    
    st_ucencev = st_vseh_ucencev()
    
    while True:
        vsi_ucenci(page, limit, st_ucencev)
        
        st_strani = st_ucencev // limit + 1
        moznosti = []
        page_options = dict()
        if page - 1 < st_strani and page * limit < st_ucencev:
            moznosti.append("+")
            page_options["+"] = "Naprej"
        if page > 1:
            moznosti.append("-")
            page_options["-"] = "Nazaj"
        prikazi_moznosti(moznosti, konec = True, vrsta = "page", page_options = page_options)
        
        izbira = input("Izberi možnost: ")
        
        if izbira == "+" and "+" in moznosti:
            page += 1
        elif izbira == "-" and "-" in moznosti:
            page -= 1
        elif izbira == "0":
            break
        else:
            print("Napačna izbira!")
            time.sleep(1)
            meni_vsi_ucenci(uporabnik, page, limit)

def meni_uciteljeve_instrukcije(uporabnik,  page = 1, limit = 10):
    if not preveri_dostop(uporabnik, ["učitelj"]):
        return
    
    id_ucitelja = Ucitelj.pridobi_id_ucitelja(uporabnik["uporabnisko_ime"])
    st_instrukcij = st_uciteljevih_instrukcij(id_ucitelja)
    
    while True:
        uciteljeve_instrukcije(id_ucitelja, page, limit, st_instrukcij)
        
        st_strani = st_instrukcij // limit + 1
        moznosti = []
        page_options = dict()
        if page - 1 < st_strani and page * limit < st_instrukcij:
            moznosti.append("+")
            page_options["+"] = "Naprej"
        if page > 1:
            moznosti.append("-")
            page_options["-"] = "Nazaj"
        prikazi_moznosti(moznosti, konec = True, vrsta = "page", page_options = page_options)
        
        izbira = input("Izberi možnost: ")
        
        if izbira == "+" and "+" in moznosti:
            page += 1
        elif izbira == "-" and "-" in moznosti:
            page -= 1
        elif izbira == "0":
            break
        else:
            print("Napačna izbira!")
            time.sleep(1)
            meni_vsi_ucenci(uporabnik, page, limit)

def meni_statistika(uporabnik):
    if uporabnik["vrsta"] not in ["učitelj", "učenec"]:
        return
    
    if uporabnik["vrsta"] == "učitelj":
        id_ucitelja = Ucitelj.pridobi_id_ucitelja(uporabnik["uporabnisko_ime"])
        ime_priimek = Ucitelj.ime_ucitelja(id_ucitelja)
        statistika_data = Ucitelj.pridobi_statistiko(id_ucitelja)
        izpisi_statistiko(ime_priimek, statistika_data)
    else:
        id_ucenca = Ucenec.pridobi_id_ucenca(uporabnik["uporabnisko_ime"])
        ime_priimek = Ucenec.ime_ucenca(id_ucenca)
        statistika_data = Ucenec.pridobi_statistiko(id_ucenca)
        izpisi_statistiko(ime_priimek, statistika_data)
    
    return

def meni_koledar(uporabnik):
    if not preveri_dostop(uporabnik, ["učitelj", "učenec"]):
        return
    
    current_week_start = datetime.now()
    current_week_start = current_week_start - timedelta(days=current_week_start.weekday())
    current_week_end = current_week_start + timedelta(days=6)
    
    while True:
        vrsta_instrukcije = ["Opravljeno", "Rezervirano", "Preklicano"]
        if uporabnik["vrsta"] == "učitelj":
            filtrirane_instrukcije = Instrukcije.filtrirane_instrukcije_ucitelj(Ucitelj.pridobi_id_ucitelja(uporabnik["uporabnisko_ime"]), vrsta_instrukcije, current_week_start, current_week_end, "")
        else:
            filtrirane_instrukcije = Instrukcije.filtrirane_instrukcije_ucenec(Ucenec.pridobi_id_ucenca(uporabnik["uporabnisko_ime"]), vrsta_instrukcije, current_week_start, current_week_end, "")
        
        koledar(uporabnik, current_week_start, current_week_end, filtrirane_instrukcije)
        
        moznosti = ["Naslednji teden", "Prejšnji teden"]
        prikazi_moznosti(moznosti, konec = True, vrsta = "page", page_options = {"+": "Naslednji teden", "-": "Prejšnji teden"})
        
        izbira = input("Izberi možnost: ")
        
        if izbira == "+":
            current_week_start = current_week_start + timedelta(days=7)
            current_week_end = current_week_end + timedelta(days=7)
        elif izbira == "-":
            current_week_start = current_week_start - timedelta(days=7)
            current_week_end = current_week_end - timedelta(days=7)
        elif izbira == "0":
            break
        else:
            print("Napačna izbira!")
            time.sleep(1)
            koledar(uporabnik, current_week_start, current_week_end, filtrirane_instrukcije)

glavni_meni()