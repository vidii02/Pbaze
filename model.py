import baza
import sqlite3
import os

if not os.path.exists("baza.db"):
    povezava = sqlite3.connect("baza.db")
    baza.ustvari_bazo_ce_ne_obstaja(povezava)
    povezava.execute("PRAGMA foreign_keys = ON")
    ucitelji = baza.pripravi_tabele(povezava)
    baza.pripravi_tabele(povezava)
    povezava.commit()
    povezava.close()

povezava = sqlite3.connect("baza.db")
povezava.execute("PRAGMA foreign_keys = ON")
baza.ustvari_bazo(povezava)

class Ucitelji:
    """Razred za ucitelje"""
    def __init__(self, id, ime, priimek, eposta, cena):
        self.id = id
        self.ime = ime
        self.priimek = priimek
        self.eposta = eposta
        self.cena = cena
    
    def __str__(self):
        return f"Učitelj {self.ime} {self.priimek}, ID: {self.id}, E-pošta: {self.eposta}, Cena: {self.cena} EUR"
    
    @staticmethod
    def vsi_ucitelji():
        """Vrne vse ucitelje"""
        sql = """
            SELECT * FROM ucitelji
            """
        results = []
        test = povezava.execute(sql)
        for id, ime, priimek, eposta, cena in test:
            results.append(Ucitelji(id, ime, priimek, eposta, cena))
        return results