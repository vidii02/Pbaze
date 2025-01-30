import baza
import sqlite3
import os

if not os.path.exists("baza.db"):
    try:
        with sqlite3.connect("baza.db") as povezava:
            baza.pripravi_bazo(povezava)
            povezava.execute("PRAGMA foreign_keys = ON")
            ucitelji, ucenci, uporabniki, predmeti, instrukcije, uciteljiPredmeti = baza.pripravi_tabele(povezava)
            povezava.commit()
    except sqlite3.DatabaseError as e:
        print(f"Napaka pri ustvarjanju baze: {e}")

class Ucitelji:
    """Razred za učitelje"""
    def __init__(self, id, ime, priimek, eposta, cena, id_uporabnika):
        self.id = id
        self.ime = ime
        self.priimek = priimek
        self.eposta = eposta
        self.cena = cena
        self.id_uporabnika = id_uporabnika
    
    def __str__(self):
        return f"Učitelj {self.ime} {self.priimek}, ID: {self.id}, E-pošta: {self.eposta}, Cena: {self.cena} EUR"
    
    @staticmethod
    def vsi_ucitelji():
        """Vrne vse učitelje"""
        sql = """
            SELECT * FROM ucitelji
            """
        results = []
        try:
            with sqlite3.connect("baza.db") as povezava:
                for id, ime, priimek, eposta, cena, id_uporabnika in povezava.execute(sql):
                    results.append(Ucitelji(id, ime, priimek, eposta, cena, id_uporabnika))
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri dostopu do baze: {e}")
        return results

class Ucenci:
    """Razred za učence"""
    def __init__(self, id, ime, priimek, eposta, id_uporabnika):
        self.id = id
        self.ime = ime
        self.priimek = priimek
        self.eposta = eposta
        self.id_uporabnika = id_uporabnika
    
    def __str__(self):
        return f"Učenec {self.ime} {self.priimek}, ID: {self.id}, E-pošta: {self.eposta}"
    
    @staticmethod
    def vsi_ucenci():
        """Vrne vse učence"""
        sql = """
            SELECT * FROM ucenci
            """
        results = []
        try:
            with sqlite3.connect("baza.db") as povezava:
                for id, ime, priimek, eposta, id_uporabnika in povezava.execute(sql):
                    results.append(Ucenci(id, ime, priimek, eposta, id_uporabnika))
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri dostopu do baze: {e}")
        return results

class Uporabniki:
    """Razred za uporabnike"""
    def __init__(self, id, uporabnisko_ime, geslo, vrsta):
        self.id = id
        self.uporabnisko_ime = uporabnisko_ime
        self.geslo = geslo
        self.vrsta = vrsta
    
    def __str__(self):
        return f"Uporabnik {self.uporabnisko_ime}, ID: {self.id}, Vrsta: {self.vrsta}"
    
    @staticmethod
    def vsi_uporabniki():
        """Vrne vse uporabnike"""
        sql = """
            SELECT * FROM uporabniki
            """
        results = []
        try:
            with sqlite3.connect("baza.db") as povezava:
                for id, uporabnisko_ime, geslo, vrsta in povezava.execute(sql):
                    results.append(Uporabniki(id, uporabnisko_ime, geslo, vrsta))
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri dostopu do baze: {e}")
        return results

class Predmeti:
    """Razred za predmete"""
    def __init__(self, id, ime_predmeta):
        self.id = id
        self.ime_predmeta = ime_predmeta
    
    def __str__(self):
        return f"Predmet {self.ime_predmeta}"
    
    @staticmethod
    def vsi_predmeti():
        """Vrne vse predmete"""
        sql = """
            SELECT * FROM predmeti
            """
        results = []
        try:
            with sqlite3.connect("baza.db") as povezava:
                for id, ime_predmeta in povezava.execute(sql):
                    results.append(Predmeti(id, ime_predmeta))
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri dostopu do baze: {e}")
        return results

class Instrukcije:
    """Razred za inštrukcije"""
    def __init__(self, id, datum, cas, trajanje, status, id_ucitelja, id_ucenca):
        self.id = id
        self.datum = datum
        self.cas = cas
        self.trajanje = trajanje
        self.status = status
        self.id_ucitelja = id_ucitelja
        self.id_ucenca = id_ucenca
    
    def __str__(self):
        return f"Inštrukcije ID: {self.id}, Datum: {self.datum}, Čas: {self.cas}, Trajanje: {self.trajanje} minut, Status: {self.status}, Učitelj ID: {self.id_ucitelja}, Učenec ID: {self.id_ucenca}"
    
    @staticmethod
    def vse_instrukcije():
        """Vrne vse inštrukcije"""
        sql = """
            SELECT * FROM instrukcije
            """
        results = []
        try:
            with sqlite3.connect("baza.db") as povezava:
                for id, datum, cas, trajanje, status, id_ucitelja, id_ucenca in povezava.execute(sql):
                    results.append(Instrukcije(id, datum, cas, trajanje, status, id_ucitelja, id_ucenca))
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri dostopu do baze: {e}")
        return results

class UciteljiPredmeti:
    """Razred za povezovanje učiteljev in predmetov"""
    def __init__(self, id_ucitelja, id_predmeta):
        self.id_ucitelja = id_ucitelja
        self.id_predmeta = id_predmeta
    
    def __str__(self):
        return f"Učitelj ID: {self.id_ucitelja}, Predmet ID: {self.id_predmeta}"
    
    @staticmethod
    def vsi_ucitelji_predmeti():
        """Vrne vse povezave med učitelji in predmeti"""
        sql = """
            SELECT * FROM uciteljiPredmeti
            """
        results = []
        try:
            with sqlite3.connect("baza.db") as povezava:
                for id_ucitelja, id_predmeta in povezava.execute(sql):
                    results.append(UciteljiPredmeti(id_ucitelja, id_predmeta))
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri dostopu do baze: {e}")
        return results