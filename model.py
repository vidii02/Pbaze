from datetime import *
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
    def ucenci_ucitelja(id_ucitelja, limit=None, offset=None):
        """Vrne vse učence, ki jih poučuje določen učitelj, z možnostjo straničenja"""
        sql = """
            SELECT ucenci.id, ucenci.ime, ucenci.priimek, ucenci.eposta
            FROM ucenci
            JOIN instrukcije ON ucenci.id = instrukcije.id_ucenca
            WHERE instrukcije.id_ucitelja = ?
            GROUP BY ucenci.id, ucenci.ime, ucenci.priimek, ucenci.eposta
            """
        params = [id_ucitelja]
        if limit is not None and offset is not None:
            sql += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        results = []
        for id, ime, priimek, eposta in povezava.execute(sql, params):
            results.append(Ucenec(id, ime, priimek, eposta, None))
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
    
    @staticmethod
    def pridobi_statistiko(id_ucitelja):
        """Vrne statistiko za določenega učitelja"""
        sql = """
            SELECT 
                COUNT(*) AS stevilo_instrukcij,
                SUM(CASE WHEN status = 'Opravljeno' THEN 1 ELSE 0 END) AS stevilo_opravljenih,
                SUM(CASE WHEN status = 'Rezervirano' THEN 1 ELSE 0 END) AS stevilo_rezerviranih,
                SUM(CASE WHEN status = 'Preklicano' THEN 1 ELSE 0 END) AS stevilo_preklicanih,
                SUM(CASE WHEN status = 'Opravljeno' THEN trajanje / 60.0 * ucitelji.cena ELSE 0 END) AS zasluzek,
                SUM(CASE WHEN status = 'Opravljeno' AND ocena BETWEEN 1 AND 5 THEN ocena ELSE 0 END) / NULLIF(COUNT(CASE WHEN status = 'Opravljeno' AND ocena BETWEEN 1 AND 5 THEN 1 END), 0) AS povprecna_ocena,
                (SELECT COUNT(DISTINCT id_ucenca) FROM instrukcije WHERE id_ucitelja = ?) AS stevilo_ucencev,
                (SELECT COUNT(DISTINCT id_predmeta) FROM instrukcije WHERE id_ucitelja = ?) AS stevilo_predmetov,
                SUM(trajanje) / 60.0 AS skupno_stevilo_ur,
                SUM(CASE WHEN status = 'Opravljeno' THEN trajanje ELSE 0 END) / NULLIF(COUNT(CASE WHEN status = 'Opravljeno' THEN 1 ELSE NULL END), 0) AS povprecno_trajanje,
                SUM(CASE WHEN status = 'Opravljeno' THEN trajanje / 60.0 * ucitelji.cena ELSE 0 END) / NULLIF(COUNT(CASE WHEN status = 'Opravljeno' THEN 1 ELSE NULL END), 0) AS povprecen_zasluzek_na_instrukcijo,
                (SELECT ime_predmeta FROM predmeti WHERE id = (SELECT id_predmeta FROM instrukcije WHERE id_ucitelja = ? GROUP BY id_predmeta ORDER BY COUNT(*) DESC LIMIT 1)) AS najpogostejsi_predmet,
                (SELECT ime || ' ' || priimek FROM ucenci WHERE id = (SELECT id_ucenca FROM instrukcije WHERE id_ucitelja = ? GROUP BY id_ucenca ORDER BY SUM(trajanje) DESC LIMIT 1)) AS najpogostejsi_ucenec
            FROM instrukcije
            JOIN ucitelji ON instrukcije.id_ucitelja = ucitelji.id
            WHERE instrukcije.id_ucitelja = ?
            """
        result = povezava.execute(sql, [id_ucitelja, id_ucitelja, id_ucitelja, id_ucitelja, id_ucitelja]).fetchone()
        stevilo_opravljenih = result[1] or 0
        stevilo_rezerviranih = result[2] or 0
        statistika = {
            "stevilo_instrukcij": result[0] or 0,
            "stevilo_opravljenih": stevilo_opravljenih,
            "stevilo_rezerviranih": stevilo_rezerviranih,
            "stevilo_preklicanih": result[3] or 0,
            "zasluzek": result[4] or 0.0,
            "povprecna_ocena": result[5] or 0.0,
            "stevilo_ucencev": result[6] or 0,
            "stevilo_predmetov": result[7] or 0,
            "skupno_stevilo_ur": result[8] or 0.0,
            "povprecno_trajanje": result[9] or 0.0,
            "povprecen_zasluzek_na_instrukcijo": result[10] or 0.0,
            "najpogostejsi_predmet": result[11] or "Ni podatkov",
            "najpogostejsi_ucenec": result[12] or "Ni podatkov",
            "stopnja_uspesnosti_rezervacij": (stevilo_opravljenih / result[0] * 100) if result[0] > 0 else 0.0
        }
        return statistika

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
    def pridobi_ucence_za_delno_ime(ime_ucenca):
        """Vrne učence na podlagi delnega imena"""
        sql = """
            SELECT id, ime || ' ' || priimek AS name FROM ucenci
            WHERE ime LIKE ? OR priimek LIKE ?
            ORDER BY name
        """
        params = [f"{ime_ucenca}%", f"{ime_ucenca}%"]
        results = []
        for id, name in povezava.execute(sql, params):
            results.append({"id": id, "name": name})
        return results
    
    @staticmethod
    def ime_ucenca(id_ucenca):
        """Vrne ime in priimek učenca na podlagi njegovega ID-ja"""
        sql = """
            SELECT ime, priimek FROM ucenci WHERE id = ?
            """
        ime_priimek = povezava.execute(sql, [id_ucenca]).fetchone()
        if ime_priimek:
            return f"{ime_priimek[0]} {ime_priimek[1]}"
        return None
    
    @staticmethod
    def vsi_ucenci(limit=None, offset=None):
        """Vrne vse učence z možnostjo straničenja"""
        sql = """
            SELECT id, ime, priimek, eposta, id_uporabnika FROM ucenci
            """
        params = []
        if limit is not None and offset is not None:
            sql += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        results = []
        for id, ime, priimek, eposta, id_uporabnika in povezava.execute(sql, params):
            results.append(Ucenec(id, ime, priimek, eposta, id_uporabnika))
        return results
    
    @staticmethod
    def pridobi_statistiko(id_ucenca):
        """Vrne statistiko za določenega učenca"""
        sql = """
            SELECT 
                COUNT(*) AS stevilo_instrukcij,
                SUM(CASE WHEN status = 'Opravljeno' THEN 1 ELSE 0 END) AS stevilo_opravljenih,
                SUM(CASE WHEN status = 'Rezervirano' THEN 1 ELSE 0 END) AS stevilo_rezerviranih,
                SUM(CASE WHEN status = 'Preklicano' THEN 1 ELSE 0 END) AS stevilo_preklicanih,
                SUM(trajanje) / 60.0 AS skupno_stevilo_ur,
                (SELECT COUNT(DISTINCT id_ucitelja) FROM instrukcije WHERE id_ucenca = ?) AS stevilo_uciteljev,
                (SELECT COUNT(DISTINCT id_predmeta) FROM instrukcije WHERE id_ucenca = ?) AS stevilo_predmetov,
                SUM(trajanje) / NULLIF(COUNT(*), 0) AS povprecna_dolzina_instrukcije,
                (SELECT ime_predmeta FROM predmeti WHERE id = (SELECT id_predmeta FROM instrukcije WHERE id_ucenca = ? GROUP BY id_predmeta ORDER BY COUNT(*) DESC LIMIT 1)) AS najpogostejsi_predmet,
                (SELECT ime || ' ' || priimek FROM ucitelji WHERE id = (SELECT id_ucitelja FROM instrukcije WHERE id_ucenca = ? GROUP BY id_ucitelja ORDER BY SUM(trajanje) DESC LIMIT 1)) AS najpogostejsi_ucitelj,
                AVG(ocena) AS povprecna_ocena
            FROM instrukcije
            WHERE id_ucenca = ?
        """
        result = povezava.execute(sql, [id_ucenca, id_ucenca, id_ucenca, id_ucenca, id_ucenca]).fetchone()
        statistika = {
            "stevilo_instrukcij": result[0] or 0,
            "stevilo_opravljenih": result[1] or 0,
            "stevilo_rezerviranih": result[2] or 0,
            "stevilo_preklicanih": result[3] or 0,
            "skupno_stevilo_ur": result[4] or 0.0,
            "stevilo_uciteljev": result[5] or 0,
            "stevilo_predmetov": result[6] or 0,
            "povprecna_dolzina_instrukcije": result[7] or 0.0,
            "najpogostejsi_predmet": result[8] or "Ni podatkov",
            "najpogostejsi_ucitelj": result[9] or "Ni podatkov",
            "povprecna_ocena": result[10] or 0.0
        }
        return statistika
    
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

    @staticmethod
    def pridobi_uporabnike(uporabnisko_ime, ime, priimek, eposta, vrsta, cena_operator, cena, page=1, limit=100):
        offset = (page - 1) * limit
        sql = """
            SELECT 
                u.ID AS id_uporabnika,
                u.Uporabnisko_ime,
                COALESCE(uc.Ime, ut.Ime) AS Ime,
                COALESCE(uc.Priimek, ut.Priimek) AS Priimek,
                COALESCE(uc.Eposta, ut.Eposta) AS Eposta,
                u.Vrsta,
                COALESCE(ut.Cena, '') AS Cena
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
        
        sql += " ORDER BY id_uporabnika LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        results = []
        for row in povezava.execute(sql, params):
            id_uporabnika, uporabnisko_ime, ime, priimek, eposta, vrsta, cena = row
            results.append({
                "id_uporabnika": id_uporabnika,
                "uporabnisko_ime": uporabnisko_ime,
                "ime": ime,
                "priimek": priimek,
                "eposta": eposta,
                "vrsta": vrsta,
                "cena": cena,
            })
        return results

    @staticmethod
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

    @staticmethod
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
    def vsi_uporabniki(uporabnisko_ime, ime, priimek, eposta, vrsta, cena, cena_operator, page=1, limit=100):
        offset = (page - 1) * limit
        sql = """
            SELECT 
                u.ID AS id_uporabnika,
                u.Uporabnisko_ime,
                COALESCE(uc.Ime, ut.Ime) AS Ime,
                COALESCE(uc.Priimek, ut.Priimek) AS Priimek,
                COALESCE(uc.Eposta, ut.Eposta) AS Eposta,
                u.Vrsta,
                COALESCE(ut.Cena, '') AS Cena
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
        
        sql += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        results = []
        for id_uporabnika, uporabnisko_ime, ime, priimek, eposta, vrsta, cena in povezava.execute(sql, params):
            results.append({
                "id_uporabnika": id_uporabnika,
                "uporabnisko_ime": uporabnisko_ime,
                "ime": ime,
                "priimek": priimek,
                "eposta": eposta,
                "vrsta": vrsta,
                "cena": cena,
            })
        return results
    
    @staticmethod
    @staticmethod
    def preveri_uporabnika(uporabnisko_ime, geslo):
        cursor = povezava.cursor()
        cursor.execute("SELECT Uporabnisko_ime, Geslo, Vrsta FROM uporabniki WHERE Uporabnisko_ime = ? AND Geslo = ?", (uporabnisko_ime, geslo))
        uporabnik = cursor.fetchone()
        if uporabnik:
            vrsta = "učitelj" if uporabnik[2] == 1 else "učenec" if uporabnik[2] == 0 else "admin"
            return {"uporabnisko_ime": uporabnik[0], "geslo": uporabnik[1], "vrsta": vrsta}
        return None

    @staticmethod
    def preveri_uporabnisko_ime(uporabnisko_ime):
        cursor = povezava.cursor()
        cursor.execute("SELECT Uporabnisko_ime FROM uporabniki WHERE Uporabnisko_ime = ?", (uporabnisko_ime,))
        return cursor.fetchone() is not None

    @staticmethod
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

    @staticmethod
    def pridobi_id_uporabnika(uporabnisko_ime):
        cursor = povezava.cursor()
        cursor.execute("SELECT ID FROM uporabniki WHERE Uporabnisko_ime = ?", (uporabnisko_ime,))
        uporabnik = cursor.fetchone()
        if uporabnik:
            return uporabnik[0]
        return None

    @staticmethod
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

    @staticmethod
    def pridobi_uporabnike(uporabnisko_ime, ime, priimek, eposta, vrsta, cena_operator, cena):
        sql = """
            SELECT 
                u.ID AS id_uporabnika,
                u.Uporabnisko_ime,
                COALESCE(uc.Ime, ut.Ime) AS Ime,
                COALESCE(uc.Priimek, ut.Priimek) AS Priimek,
                COALESCE(uc.Eposta, ut.Eposta) AS Eposta,
                u.Vrsta,
                COALESCE(ut.Cena, '') AS Cena
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
        
        sql += " ORDER BY u.Uporabnisko_ime"
        
        results = []
        for row in povezava.execute(sql, params):
            id_uporabnika, uporabnisko_ime, ime, priimek, eposta, vrsta, cena = row
            results.append({
                "id_uporabnika": id_uporabnika,
                "uporabnisko_ime": uporabnisko_ime,
                "ime": ime,
                "priimek": priimek,
                "eposta": eposta,
                "vrsta": vrsta,
                "cena": cena,
            })
        return results

    @staticmethod
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
    
    @staticmethod
    def pridobi_predmete_za_delno_ime(ime_predmeta):
        """Vrne predmete na podlagi delnega imena"""
        sql = """
            SELECT id, ime_predmeta FROM predmeti
            WHERE ime_predmeta LIKE ?
            ORDER BY ime_predmeta
        """
        params = [f"{ime_predmeta}%"]
        results = []
        for id, ime_predmeta in povezava.execute(sql, params):
            results.append({"id": id, "ime_predmeta": ime_predmeta})
        return results

class Instrukcije:
    """Razred za inštrukcije"""
    def __init__(self, id, datum, trajanje, status, id_ucitelja, id_ucenca, ocena=None, mnenje=None, ime_predmeta=None):
        self.id = id
        self.datum = datum
        self.trajanje = trajanje
        self.status = status
        self.id_ucitelja = id_ucitelja
        self.id_ucenca = id_ucenca
        self.ocena = ocena
        self.mnenje = mnenje
        self.ime_predmeta = ime_predmeta
    
    def __str__(self):
        return f"Inštrukcije ID: {self.id}, Datum: {self.datum}, Trajanje: {self.trajanje} minut, Status: {self.status}, Učitelj ID: {self.id_ucitelja}, Učenec ID: {self.id_ucenca}, Ocena: {self.ocena}, Mnenje: {self.mnenje}, Ime predmeta: {self.ime_predmeta}"
    
    @staticmethod
    def vse_instrukcije_ucitelja(id_ucitelja, limit=None, offset=None):
        """Vrne vse inštrukcije za določenega učitelja z možnostjo straničenja"""
        sql = """
            SELECT i.id, i.datum, i.trajanje, i.status, i.id_ucitelja, i.id_ucenca, u.ime, u.priimek, u.eposta,
                   i.ocena, i.mnenje, p.ime_predmeta
            FROM instrukcije i
            JOIN ucenci u ON i.id_ucenca = u.id
            JOIN predmeti p ON i.id_predmeta = p.id
            WHERE i.id_ucitelja = ?
            ORDER BY i.datum ASC
            """
        params = [id_ucitelja]
        if limit is not None and offset is not None:
            sql += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        results = []
        for row in povezava.execute(sql, params):
            id, datum, trajanje, status, id_ucitelja, id_ucenca, ime_ucenca, priimek_ucenca, eposta_ucenca, ocena, mnenje, ime_predmeta = row
            instrukcija = Instrukcije(id, datum, trajanje, status, id_ucitelja, id_ucenca, ocena, mnenje, ime_predmeta)
            instrukcija.ime_ucenca = ime_ucenca
            instrukcija.priimek_ucenca = priimek_ucenca
            instrukcija.eposta_ucenca = eposta_ucenca
            results.append(instrukcija)
        return results

    @staticmethod
    def vse_instrukcije_ucenca(id_ucenca):
        """Vrne vse inštrukcije za določenega učenca"""
        sql = """
            SELECT * FROM instrukcije WHERE id_ucenca = ?
            """
        results = []
        for id, datum, trajanje, status, id_ucitelja, id_ucenca in povezava.execute(sql, [id_ucenca]):
            results.append(Instrukcije(id, datum, trajanje, status, id_ucitelja, id_ucenca))
        return results
    
    @staticmethod
    def filtrirane_instrukcije_ucenec(id_ucenca: int, instrukcija_status: list, week_start: datetime, week_end: datetime, ucitelj: str):
        sql = """
            SELECT i.id, i.datum, i.trajanje, i.status, i.id_ucitelja, i.id_ucenca, 
                    u.eposta, ut.eposta, i.ocena, i.mnenje, p.ime_predmeta, 
                    u.ime || ' ' || u.priimek AS ucenec, 
                    ut.ime || ' ' || ut.priimek AS ucitelj
            FROM instrukcije i
            JOIN ucenci u ON i.id_ucenca = u.id
            JOIN predmeti p ON i.id_predmeta = p.id
            JOIN ucitelji ut ON i.id_ucitelja = ut.id
            WHERE i.id_ucenca = ?
              AND DATE(i.datum) BETWEEN DATE(?) AND DATE(?)
        """
        params = [id_ucenca, week_start, week_end]

        if instrukcija_status:
            sql += " AND (" + " OR ".join(["i.status = ?"] * len(instrukcija_status)) + ")"
            params.extend(instrukcija_status)
        else:
            sql += " AND i.status = '/'"

        if ucitelj:
            sql += " AND i.id_ucitelja IN (SELECT id FROM ucitelji WHERE ime LIKE ? OR priimek LIKE ?)"
            params.append(f"{ucitelj}%")
            params.append(f"{ucitelj}%")

        sql += " ORDER BY i.datum ASC"

        results = []
        for row in povezava.execute(sql, params):
            id, datum, trajanje, status, id_ucitelja, id_ucenca, eposta_ucenca, eposta_ucitelja, ocena, mnenje, ime_predmeta, ucenec, ucitelj = row
            instrukcija = Instrukcije(id, datum, trajanje, status, id_ucitelja, id_ucenca, ocena, mnenje, ime_predmeta)
            instrukcija.ucenec = ucenec
            instrukcija.eposta_ucenca = eposta_ucenca
            instrukcija.ucitelj = ucitelj
            instrukcija.eposta_ucitelja = eposta_ucitelja
            results.append(instrukcija)
        return results
    
    @staticmethod
    def filtrirane_instrukcije_ucitelj(id_ucitelja: int, vrsta_instrukcije: list, week_start: datetime, week_end: datetime, ucenec: str):
        sql = """
            SELECT i.id, i.datum, i.trajanje, i.status, i.id_ucitelja, i.id_ucenca, 
                    u.eposta, ut.eposta, i.ocena, i.mnenje, p.ime_predmeta, 
                    u.ime || ' ' || u.priimek AS ucenec, 
                    ut.ime || ' ' || ut.priimek AS ucitelj
            FROM instrukcije i
            JOIN ucenci u ON i.id_ucenca = u.id
            JOIN predmeti p ON i.id_predmeta = p.id
            JOIN ucitelji ut ON i.id_ucitelja = ut.id
            WHERE i.id_ucitelja = ?
              AND DATE(i.datum) BETWEEN DATE(?) AND DATE(?)
        """
        params = [id_ucitelja, week_start, week_end]

        if vrsta_instrukcije:
            sql += " AND (" + " OR ".join(["i.status = ?"] * len(vrsta_instrukcije)) + ")"
            params.extend(vrsta_instrukcije)
        else:
            sql += " AND i.status = '/'"

        if ucenec:
            sql += " AND i.id_ucenca IN (SELECT id FROM ucenci WHERE ime LIKE ? OR priimek LIKE ?)"
            params.append(f"{ucenec}%")
            params.append(f"{ucenec}%")

        sql += " ORDER BY i.datum ASC"

        results = []
        for row in povezava.execute(sql, params):
            id, datum, trajanje, status, id_ucitelja, id_ucenca, eposta_ucenca, eposta_ucitelja, ocena, mnenje, ime_predmeta, ucenec, ucitelj = row
            instrukcija = Instrukcije(id, datum, trajanje, status, id_ucitelja, id_ucenca, ocena, mnenje, ime_predmeta)
            instrukcija.ucenec = ucenec
            instrukcija.eposta_ucenca = eposta_ucenca
            instrukcija.ucitelj = ucitelj
            instrukcija.eposta_ucitelja = eposta_ucitelja
            results.append(instrukcija)
        return results
    
    @staticmethod
    def pridobi_instrukcijo(id_instrukcije):
        sql = """
            SELECT i.id, i.datum, i.trajanje, i.status, i.id_ucitelja, i.id_ucenca, 
                   i.ocena, i.mnenje, p.ime_predmeta, 
                   u.ime || ' ' || u.priimek AS ucenec, 
                   ut.ime || ' ' || ut.priimek AS ucitelj
            FROM instrukcije i
            JOIN ucenci u ON i.id_ucenca = u.id
            JOIN predmeti p ON i.id_predmeta = p.id
            JOIN ucitelji ut ON i.id_ucitelja = ut.id
            WHERE i.id = ?
        """
        row = povezava.execute(sql, [id_instrukcije]).fetchone()
        if row:
            id, datum, trajanje, status, id_ucitelja, id_ucenca, ocena, mnenje, ime_predmeta, ucenec, ucitelj = row
            instrukcija = Instrukcije(id, datum, trajanje, status, id_ucitelja, id_ucenca, ocena, mnenje, ime_predmeta)
            instrukcija.ucenec = ucenec
            instrukcija.ucitelj = ucitelj
            return instrukcija
        return None

    @staticmethod
    def posodobi_oceno_in_komentar(id_instrukcije, ocena, komentar):
        sql = """
            UPDATE instrukcije
            SET ocena = ?, mnenje = ?
            WHERE id = ?
        """
        povezava.execute(sql, [ocena, komentar, id_instrukcije])
        povezava.commit()
    
    @staticmethod
    def dodaj_instrukcijo(datum, trajanje, status, id_ucitelja, id_ucenca, id_predmeta, ocena=None, mnenje=None):
        sql = """
            INSERT INTO instrukcije (datum, trajanje, status, id_ucitelja, id_ucenca, id_predmeta, ocena, mnenje)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        povezava.execute(sql, [datum, trajanje, status, id_ucitelja, id_ucenca, id_predmeta, ocena, mnenje])
        povezava.commit()
    
    @staticmethod
    def posodobi_instrukcijo(id_instrukcije, datum, trajanje, status, id_ucenca, id_predmeta, ocena=None, mnenje=None):
        sql = """
            UPDATE instrukcije
            SET datum = ?, trajanje = ?, status = ?, id_ucenca = ?, id_predmeta = ?, ocena = ?, mnenje = ?
            WHERE id = ?
        """
        povezava.execute(sql, [datum, trajanje, status, id_ucenca, id_predmeta, ocena, mnenje, id_instrukcije])
        povezava.commit()

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