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

povezava = sqlite3.connect("baza.db")
povezava.execute("PRAGMA foreign_keys = ON")

class Ucitelj:
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
    def pridobi_id_ucitelja(uporabnisko_ime):
        """Vrne ID učitelja na podlagi uporaniškega imena"""
        sql = """
            SELECT ucitelji.id FROM ucitelji
            JOIN uporabniki ON ucitelji.id_uporabnika = uporabniki.id
            WHERE uporabniki.uporabnisko_ime = ?
            """
        id = povezava.execute(sql, [uporabnisko_ime]).fetchone()
        if id:
            return id[0]
        return id
    
    @staticmethod
    def ucenci_ucitelja(id_ucitelja):
        """Vrne vse učence, ki jih poučuje določen učitelj, skupaj z datumom termina in statusom"""
        sql = """
            SELECT ucenci.ime, ucenci.priimek, ucenci.eposta, 
            CAST(CAST(strftime('%d', instrukcije.Datum) AS INTEGER) || '/' ||
            CAST(strftime('%m', instrukcije.Datum) AS INTEGER) || '/' ||
            strftime('%Y', instrukcije.Datum) AS TEXT) AS prikaz_datum,
            instrukcije.Status
            FROM ucenci
            JOIN instrukcije ON ucenci.ID = instrukcije.ID_ucenca
            WHERE instrukcije.ID_ucitelja = ?
            ORDER BY instrukcije.Datum;
            """
        results = []
        for ime, priimek, eposta, datum, status in povezava.execute(sql, [id_ucitelja]):
            results.append({
                "ime": ime,
                "priimek": priimek,
                "eposta": eposta,
                "datum": datum,
                "status": status
            })
        return results
    
    @staticmethod
    def ime_ucitelja(id_ucitelja):
        """Vrne ime učitelja na podlagi njegovega ID-ja"""
        sql = """
            SELECT ime, priimek FROM ucitelji WHERE id = ?
            """
        ime_priimek = povezava.execute(sql, [id_ucitelja]).fetchone()
        if ime_priimek:
            return f"{ime_priimek[0]} {ime_priimek[1]}"
        return None

class Ucenec:
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
    def pridobi_id_ucenca(uporabnisko_ime):
        """Vrne ID učenca na podlagi uporaniškega imena"""
        sql = """
            SELECT ucenci.id FROM ucenci
            JOIN uporabniki ON ucenci.id_uporabnika = uporabniki.id
            WHERE uporabniki.uporabnisko_ime = ?
            """
        id = povezava.execute(sql, [uporabnisko_ime]).fetchone()
        if id:
            return id[0]
        return id
    
    @staticmethod
    def ime_ucenca(id_ucenca):
        """Vrne ime učenca na podlagi njegovega ID-ja"""
        sql = """
            SELECT ime, priimek FROM ucenci WHERE id = ?
            """
        ime_priimek = povezava.execute(sql, [id_ucenca]).fetchone()
        if ime_priimek:
            return f"{ime_priimek[0]} {ime_priimek[1]}"
        return None

class Admin:
    """Razred za administratorje"""
    def __init__(self, up_ime, geslo):
        self.up_ime = up_ime
        self.geslo = geslo
    
    def __str__(self):
        return f"Admin: {self.up_ime}"
    
    @staticmethod
    def vsi_ucitelji(limit, offset):
        """Vrne vse učitelje z omejitvijo in zamikom"""
        sql = """
            SELECT * FROM ucitelji
            ORDER BY priimek
            LIMIT ? OFFSET ?
            """
        results = []
        for id, ime, priimek, eposta, cena, id_uporabnika in povezava.execute(sql, (limit, offset)):
            results.append(Ucitelj(id, ime, priimek, eposta, cena, id_uporabnika))
        return results
    
    @staticmethod
    def vsi_ucenci(limit, offset):
        """Vrne vse učence z omejitvijo in zamikom"""
        sql = """
            SELECT * FROM ucenci
            ORDER BY priimek
            LIMIT ? OFFSET ?
            """
        results = []
        for id, ime, priimek, eposta, id_uporabnika in povezava.execute(sql, (limit, offset)):
            results.append(Ucenec(id, ime, priimek, eposta, id_uporabnika))
        return results

class Uporabnik:
    """Razred za uporabnike"""
    def __init__(self, id, uporabnisko_ime, geslo, vrsta):
        self.id = id
        self.uporabnisko_ime = uporabnisko_ime
        self.geslo = geslo
        self.vrsta = vrsta
    
    def __str__(self):
        return f"Uporabnik {self.uporabnisko_ime}, ID: {self.id}, Vrsta: {self.vrsta}"
    
    @staticmethod
    def vsi_uporabniki(uporabnisko_ime="", ime="", priimek="", eposta="", vrsta="", cena="", cena_operator="eq"):
        sql = """
            SELECT 
                u.ID AS id_uporabnika,
                u.Uporabnisko_ime,
                COALESCE(uc.Ime, ut.Ime) AS Ime,
                COALESCE(uc.Priimek, ut.Priimek) AS Priimek,
                COALESCE(uc.Eposta, ut.Eposta) AS Eposta,
                u.Vrsta,
                COALESCE(ut.Cena, '') AS Cena,
                'Uredi' AS Dejanje
            FROM uporabniki u
            LEFT JOIN ucenci uc ON u.ID = uc.ID_uporabnika
            LEFT JOIN ucitelji ut ON u.ID = ut.ID_uporabnika
            WHERE u.Uporabnisko_ime LIKE ?
              AND COALESCE(uc.Ime, ut.Ime) LIKE ?
              AND COALESCE(uc.Priimek, ut.Priimek) LIKE ?
              AND COALESCE(uc.Eposta, ut.Eposta) LIKE ?
              AND (u.Vrsta = ? OR ? = '')
        """
        params = [
            f"{uporabnisko_ime}%", 
            f"{ime}%", 
            f"{priimek}%", 
            f"{eposta}%", 
            vrsta, vrsta
        ]
        if cena:
            sql += " AND u.Vrsta = 1"
            if cena_operator == "gte":
                sql += " AND COALESCE(ut.Cena, 0) >= ?"
            elif cena_operator == "lte":
                sql += " AND COALESCE(ut.Cena, 0) <= ?"
            else:
                sql += " AND COALESCE(ut.Cena, 0) = ?"
            params.append(float(cena))
        results = []
        for id_uporabnika, uporabnisko_ime, ime, priimek, eposta, vrsta, cena, dejanje in povezava.execute(sql, params):
            results.append({
                "id_uporabnika": id_uporabnika,
                "uporabnisko_ime": uporabnisko_ime,
                "ime": ime,
                "priimek": priimek,
                "eposta": eposta,
                "vrsta": vrsta,
                "cena": cena,
                "dejanje": dejanje
            })
        return results

class Predmet:
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
        for id, ime_predmeta in povezava.execute(sql):
            results.append(Predmet(id, ime_predmeta))
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
    def vse_instrukcije_ucitelja(id_ucitelja):
        """Vrne vse inštrukcije za določenega učitelja"""
        sql = """
            SELECT * FROM instrukcije WHERE id_ucitelja = ?
            """
        results = []
        for id, datum, cas, trajanje, status, id_ucitelja, id_ucenca in povezava.execute(sql, [id_ucitelja]):
            results.append(Instrukcije(id, datum, cas, trajanje, status, id_ucitelja, id_ucenca))
        return results

    @staticmethod
    def vse_instrukcije_ucenca(id_ucenca):
        """Vrne vse inštrukcije za določenega učenca"""
        sql = """
            SELECT * FROM instrukcije WHERE id_ucenca = ?
            """
        results = []
        for id, datum, cas, trajanje, status, id_ucitelja, id_ucenca in povezava.execute(sql, [id_ucenca]):
            results.append(Instrukcije(id, datum, cas, trajanje, status, id_ucitelja, id_ucenca))
        return results

class UciteljPredmet:
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
        for id_ucitelja, id_predmeta in povezava.execute(sql):
            results.append(UciteljPredmet(id_ucitelja, id_predmeta))
        return results

def preveri_uporabnika(uporabnisko_ime, geslo):
    cursor = povezava.cursor()
    cursor.execute("SELECT Uporabnisko_ime, Geslo, Vrsta FROM uporabniki WHERE Uporabnisko_ime = ? AND Geslo = ?", (uporabnisko_ime, geslo))
    uporabnik = cursor.fetchone()
    if uporabnik:
        vrsta = "učitelj" if uporabnik[2] == 1 else "učenec" if uporabnik[2] == 0 else "admin"
        return {"uporabnisko_ime": uporabnik[0], "geslo": uporabnik[1], "vrsta": vrsta}
    return None

def preveri_uporabnisko_ime(uporabnisko_ime):
    cursor = povezava.cursor()
    cursor.execute("SELECT Uporabnisko_ime FROM uporabniki WHERE Uporabnisko_ime = ?", (uporabnisko_ime,))
    return cursor.fetchone() is not None

def registracija_uporabnika(uporabnisko_ime, geslo, vrsta, ime, priimek, eposta, cena=None):
    cursor = povezava.cursor()
    cursor.execute("INSERT INTO uporabniki (Uporabnisko_ime, Geslo, Vrsta) VALUES (?, ?, ?)",
                    (uporabnisko_ime, geslo, vrsta))
    uporabnik_id = cursor.lastrowid
    if vrsta == 1:
        cursor.execute("INSERT INTO ucitelji (Ime, Priimek, Eposta, Cena, ID_uporabnika) VALUES (?, ?, ?, ?, ?)",
                        (ime, priimek, eposta, cena, uporabnik_id))
    elif vrsta == 0:
        cursor.execute("INSERT INTO ucenci (Ime, Priimek, Eposta, ID_uporabnika) VALUES (?, ?, ?, ?)",
                        (ime, priimek, eposta, uporabnik_id))
    povezava.commit()

def pridobi_id_uporabnika(uporabnisko_ime):
    cursor = povezava.cursor()
    cursor.execute("SELECT ID FROM uporabniki WHERE Uporabnisko_ime = ?", (uporabnisko_ime,))
    uporabnik = cursor.fetchone()
    if uporabnik:
        return uporabnik[0]
    return None

def pridobi_uporabnika(uporabnisko_ime):
    cursor = povezava.cursor()
    cursor.execute("""
        SELECT 
            u.ID, u.Uporabnisko_ime, 
            u.Geslo, COALESCE(uc.Ime, ut.Ime) AS Ime, 
            COALESCE(uc.Priimek, ut.Priimek) AS Priimek, 
            COALESCE(uc.Eposta, ut.Eposta) AS Eposta
        FROM uporabniki u
        LEFT JOIN ucenci uc ON u.ID = uc.ID_uporabnika
        LEFT JOIN ucitelji ut ON u.ID = ut.ID_uporabnika
        WHERE u.Uporabnisko_ime = ?
        """, (uporabnisko_ime,))
    uporabnik = cursor.fetchone()
    if uporabnik:
        uporabnik_id, uporabnisko_ime, geslo, ime, priimek, eposta = uporabnik
        return {
            "id": uporabnik_id,
            "uporabnisko_ime": uporabnisko_ime,
            "geslo": geslo,
            "ime": ime,
            "priimek": priimek,
            "eposta": eposta
        }
    return None

def posodobi_uporabnika(id_uporabnika, novo_uporabnisko_ime, novo_geslo, nova_vrsta, novo_ime, novi_priimek, nova_eposta, nova_cena):
    cursor = povezava.cursor()
    cursor.execute("""
        UPDATE uporabniki
        SET Uporabnisko_ime = ?, Geslo = ?, Vrsta = ?
        WHERE ID = ?
    """, (novo_uporabnisko_ime, novo_geslo, nova_vrsta, id_uporabnika))
    if nova_vrsta == 1:
        cursor.execute("""
            UPDATE ucitelji
            SET Ime = ?, Priimek = ?, Eposta = ?, Cena = ?
            WHERE ID_uporabnika = ?
        """, (novo_ime, novi_priimek, nova_eposta, nova_cena, id_uporabnika))
    else:
        cursor.execute("""
            UPDATE ucenci
            SET Ime = ?, Priimek = ?, Eposta = ?
            WHERE ID_uporabnika = ?
        """, (novo_ime, novi_priimek, nova_eposta, id_uporabnika))
    povezava.commit()
    
if __name__ == "__main__":
    def ponastavi_bazo():
        """Ponastavi bazo podatkov: izbriše obstoječe tabele, ustvari nove in uvozi podatke."""
        try:
            with sqlite3.connect("baza.db") as povezava:
                baza.ustvari_bazo(povezava)
                povezava.commit()
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri ponastavitvi baze: {e}")

    # Ponastavi bazo ob zagonu
    ponastavi_bazo()