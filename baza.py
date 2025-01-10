import csv
import sqlite3

PARAM_FMT = ":{}" # za PostgreSQL/MySQL

class Tabela:
    ime = None
    pot_podatkov = None
    
    def __init__(self, povezava):
        self.povezava = povezava
    
    def izbrisi(self):
        """
        Izbriši tabelo.

        Opis:
            Metoda odstrani tabelo in vse njene podatke iz baze.
        """
        try:
            self.povezava.execute(f"DROP TABLE IF EXISTS {self.ime};")
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri brisanju tabele {self.ime}: {e}")
    
    def uvozi(self, encoding="UTF-8"):
        """
        Uvoz podatkov v tabelo.

        Argumenti:
            encoding - Način kodiranja.

        Opis:
            Uvozi podatke v tabelo.
        """
        if self.pot_podatkov is None:
            return None
        try:
            with open(self.pot_podatkov, encoding=encoding) as beri:
                podatki = csv.reader(beri)
                stolpci = next(podatki)
                for vrstica in podatki:
                    nov_slovar = dict()
                    for k, v in zip(stolpci, vrstica):
                        if v == "":
                            nov_slovar[k] = None
                        else:
                            nov_slovar[k] = v
                    self.dodaj_vrstico(nov_slovar)
        except (FileNotFoundError, csv.Error) as e:
            print(f"Napaka pri uvozu podatkov v tabelo {self.ime}: {e}")
        
    def izprazni(self):
        """
        Izprazni tabelo.

        Opis:
            Metoda odstrani vse vrstice iz tabele, vendar struktura tabele ostane.
        """
        try:
            self.povezava.execute(f"DELETE FROM {self.ime};")
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri praznjenju tabele {self.ime}: {e}")
    
    def dodajanje(self, stolpci=None):
        """
        Gradnja poizvedbe.

        Argumenti:
            stolpci - Seznam stolpcev.

        Opis:
            Pripravi poizvedbo.
        """
        return f"""
                INSERT INTO {self.ime} ({", ".join(stolpci)})
                VALUES ({", ".join(['?' for _ in stolpci])});
                """
    
    def dodaj_vrstico(self, podatki):
        """
        Dodaj vrstico v bazo.

        Argumenti:
            podatki - Slovar podatkov.

        Opis:
            Metoda doda vrstico v tabelo.
        """
        nov_slovar = dict()
        for kljuc, vrednost in podatki.items():
            if vrednost is not None:
                nov_slovar[kljuc] = vrednost
        poizvedba = self.dodajanje(nov_slovar.keys())
        try:
            self.povezava.execute(poizvedba, tuple(nov_slovar.values()))
            self.povezava.commit()  # Potrdi spremembe v bazi
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri dodajanju vrstice v tabelo {self.ime}: {e}")
        return self.povezava.lastrowid

    def zapri_povezavo(self):
        """
        Zapre povezavo z bazo.
        """
        if self.povezava:
            self.povezava.close()

    def __del__(self):
        self.zapri_povezavo()

class Ucitelji(Tabela):
    """Razred za učitelje"""
    ime = "ucitelji"
    pot_podatkov = "data/ucitelji.csv"
    
    def ustvari(self):
        """Ustvari tabelo."""
        try:
            self.povezava.execute(f"""
                CREATE TABLE {self.ime} (
                    id INTEGER PRIMARY KEY,
                    ime TEXT NOT NULL,
                    priimek TEXT NOT NULL,
                    eposta TEXT NOT NULL,
                    cena REAL NOT NULL
                );
            """)
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri ustvarjanju tabele {self.ime}: {e}")
    
    def dodaj_vrstico(self, podatki):
        """
        Dodaj vrstico v bazo.

        Argumenti:
            podatki - Slovar podatkov.

        Opis:
            Metoda doda vrstico v tabelo.
        """
        super().dodaj_vrstico(podatki)
    
    def uvozi(self, encoding="UTF-8"):
        """
        Uvoz podatkov v tabelo.

        Argumenti:
            encoding - Način kodiranja.

        Opis:
            Uvozi podatke v tabelo.
        """
        super().uvozi(encoding)

class Ucenci(Tabela):
    """Razred za učence"""
    ime = "ucenci"
    pot_podatkov = "data/ucenci.csv"
    
    def ustvari(self):
        """Ustvari tabelo."""
        try:
            self.povezava.execute(f"""
                CREATE TABLE {self.ime} (
                    id INTEGER PRIMARY KEY,
                    ime TEXT NOT NULL,
                    priimek TEXT NOT NULL,
                    eposta TEXT NOT NULL
                );
            """)
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri ustvarjanju tabele {self.ime}: {e}")
    
    def dodaj_vrstico(self, podatki):
        """
        Dodaj vrstico v bazo.

        Argumenti:
            podatki - Slovar podatkov.

        Opis:
            Metoda doda vrstico v tabelo.
        """
        super().dodaj_vrstico(podatki)
    
    def uvozi(self, encoding="UTF-8"):
        """
        Uvoz podatkov v tabelo.

        Argumenti:
            encoding - Način kodiranja.

        Opis:
            Uvozi podatke v tabelo.
        """
        super().uvozi(encoding)

class Predmeti(Tabela):
    """Razred za predmete"""
    ime = "predmeti"
    pot_podatkov = "data/predmeti.csv"
    
    def ustvari(self):
        """Ustvari tabelo."""
        try:
            self.povezava.execute(f"""
                CREATE TABLE {self.ime} (
                    id INTEGER PRIMARY KEY,
                    ime_predmeta TEXT NOT NULL
                );
            """)
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri ustvarjanju tabele {self.ime}: {e}")
    
    def dodaj_vrstico(self, podatki):
        """
        Dodaj vrstico v bazo.

        Argumenti:
            podatki - Slovar podatkov.

        Opis:
            Metoda doda vrstico v tabelo.
        """
        super().dodaj_vrstico(podatki)
    
    def uvozi(self, encoding="UTF-8"):
        """
        Uvoz podatkov v tabelo.

        Argumenti:
            encoding - Način kodiranja.

        Opis:
            Uvozi podatke v tabelo.
        """
        super().uvozi(encoding)

class Instrukcije(Tabela):
    """Razred za inštrukcije"""
    ime = "instrukcije"
    pot_podatkov = "data/instrukcije.csv"
    
    def ustvari(self):
        """Ustvari tabelo."""
        try:
            self.povezava.execute(f"""
                CREATE TABLE {self.ime} (
                    id INTEGER PRIMARY KEY,
                    datum TEXT NOT NULL,
                    cas TEXT NOT NULL,
                    trajanje INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    id_ucitelja INTEGER NOT NULL,
                    id_ucenca INTEGER NOT NULL,
                    FOREIGN KEY (id_ucitelja) REFERENCES ucitelji(id),
                    FOREIGN KEY (id_ucenca) REFERENCES ucenci(id)
                );
            """)
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri ustvarjanju tabele {self.ime}: {e}")
    
    def dodaj_vrstico(self, podatki):
        """
        Dodaj vrstico v bazo.

        Argumenti:
            podatki - Slovar podatkov.

        Opis:
            Metoda doda vrstico v tabelo.
        """
        super().dodaj_vrstico(podatki)
    
    def uvozi(self, encoding="UTF-8"):
        """
        Uvoz podatkov v tabelo.

        Argumenti:
            encoding - Način kodiranja.

        Opis:
            Uvozi podatke v tabelo.
        """
        super().uvozi(encoding)

class UciteljiPredmeti(Tabela):
    """Razred za povezovanje učiteljev in predmetov"""
    ime = "uciteljiPredmeti"
    pot_podatkov = "data/uciteljiPredmeti.csv"
    
    def ustvari(self):
        """Ustvari tabelo."""
        try:
            self.povezava.execute(f"""
                CREATE TABLE {self.ime} (
                    id INTEGER PRIMARY KEY,
                    id_ucitelja INTEGER NOT NULL,
                    id_predmeta INTEGER NOT NULL,
                    FOREIGN KEY (id_ucitelja) REFERENCES ucitelji(id),
                    FOREIGN KEY (id_predmeta) REFERENCES predmeti(id)
                );
            """)
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri ustvarjanju tabele {self.ime}: {e}")
    
    def dodaj_vrstico(self, podatki):
        """
        Dodaj vrstico v bazo.

        Argumenti:
            podatki - Slovar podatkov.

        Opis:
            Metoda doda vrstico v tabelo.
        """
        super().dodaj_vrstico(podatki)
    
    def uvozi(self, encoding="UTF-8"):
        """
        Uvoz podatkov v tabelo.

        Argumenti:
            encoding - Način kodiranja.

        Opis:
            Uvozi podatke v tabelo.
        """
        super().uvozi(encoding)

def ustvari_tabele(tabele):
    """Ustvari podane tabele."""
    for tab in tabele:
        try:
            tab.ustvari()
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri ustvarjanju tabele {tab.ime}: {e}")

def izbrisi_tabele(tabele):
    """Izbriši podane tabele."""
    for tab in tabele:
        try:
            tab.izbrisi()
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri brisanju tabele {tab.ime}: {e}")

def uvozi_podatke(tabele):
    """Uvozi podatke v podane tabele."""
    for tab in tabele:
        try:
            tab.uvozi()
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri uvozu podatkov v tabelo {tab.ime}: {e}")

def izprazni_tabele(tabele):
    """Izprazni podane tabele."""
    for tab in tabele:
        try:
            tab.izprazni()
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri praznjenju tabele {tab.ime}: {e}")

def ustvari_bazo(povezava):
    """Ustvari bazo"""
    tabele = pripravi_tabele(povezava)
    izbrisi_tabele(tabele)
    ustvari_tabele(tabele)
    uvozi_podatke(tabele)

def pripravi_tabele(povezava):
    """Pripravi objekte za tabele"""
    ucitelji = Ucitelji(povezava)
    ucenci = Ucenci(povezava)
    predmeti = Predmeti(povezava)
    instrukcije = Instrukcije(povezava)
    uciteljiPredmeti = UciteljiPredmeti(povezava)
    return [ucitelji, ucenci, predmeti, instrukcije, uciteljiPredmeti]

def ustvari_bazo_ce_ne_obstaja(povezava):
    """Ustvari bazo, če ta še ne obstaja."""
    try:
        with povezava:
            cur = povezava.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
            if cur.fetchone()[0] == 0:
                ustvari_bazo(povezava)
    except sqlite3.DatabaseError as e:
        print(f"Napaka pri preverjanju obstoja baze: {e}")