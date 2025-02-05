import csv
import sqlite3

class Tabela:
    ime = None
    pot_podatkov = None
    
    def __init__(self, povezava):
        self.povezava = povezava
    
    def izbrisi(self):
        try:
            self.povezava.execute(f"DROP TABLE IF EXISTS {self.ime};")
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri brisanju tabele {self.ime}: {e}")
    
    def uvozi(self, encoding="UTF-8"):
        if self.pot_podatkov is None:
            return None
        try:
            with open(self.pot_podatkov, "r", encoding=encoding) as datoteka:
                podatki = csv.reader(datoteka)
                stolpci = next(podatki)
                query = "insert into {0}({1}) values ({2})"
                query = query.format(self.ime, ", ".join(stolpci), ", ".join("?" * len(stolpci)))
                cursor = self.povezava.cursor()
                for vrstica in podatki:
                    cursor.execute(query, vrstica)
                self.povezava.commit()
        except (FileNotFoundError, csv.Error) as e:
            print(f"Napaka pri uvozu podatkov v tabelo {self.ime}: {e}")
        
    def izprazni(self):
        try:
            self.povezava.execute(f"DELETE FROM {self.ime};")
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri praznjenju tabele {self.ime}: {e}")
    
    def dodajanje(self, stolpci=None):
        return f"""
                INSERT INTO {self.ime} ({", ".join(stolpci)})
                VALUES ({", ".join(["?" for _ in stolpci])});
                """
    
    def dodaj_vrstico(self, podatki):
        nov_slovar = dict()
        for kljuc, vrednost in podatki.items():
            if vrednost is not None:
                nov_slovar[kljuc] = vrednost
        poizvedba = self.dodajanje(nov_slovar.keys())
        try:
            cursor = self.povezava.execute(poizvedba, tuple(nov_slovar.values()))
            self.povezava.commit()
            return cursor.lastrowid
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri dodajanju vrstice v tabelo {self.ime}: {e}")
            return None

    def zapri_povezavo(self):
        if self.povezava:
            self.povezava.close()

class Ucitelji(Tabela):
    ime = "ucitelji"
    pot_podatkov = "data/ucitelji.csv"
    
    def ustvari(self):
        try:
            self.povezava.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.ime} (
                    ID                INTEGER        PRIMARY KEY AUTOINCREMENT,
                    Ime               VARCHAR (50)   NOT NULL,
                    Priimek           VARCHAR (50)   NOT NULL,
                    Eposta            VARCHAR (100)  NOT NULL,
                    Cena              DECIMAL (5, 2) NOT NULL,
                    ID_uporabnika     INTEGER        NOT NULL,
                    FOREIGN KEY (ID_uporabnika) REFERENCES uporabniki(ID)
                );
            """)
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri ustvarjanju tabele {self.ime}: {e}")
    
    def dodaj_vrstico(self, podatki):
        super().dodaj_vrstico(podatki)
    
    def uvozi(self, encoding="UTF-8"):
        super().uvozi(encoding)

class Ucenci(Tabela):
    ime = "ucenci"
    pot_podatkov = "data/ucenci.csv"
    
    def ustvari(self):
        try:
            self.povezava.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.ime} (
                    ID                INTEGER        PRIMARY KEY AUTOINCREMENT,
                    Ime               VARCHAR (50)   NOT NULL,
                    Priimek           VARCHAR (50)   NOT NULL,
                    Eposta            VARCHAR (100)  NOT NULL,
                    ID_uporabnika     INTEGER        NOT NULL,
                    FOREIGN KEY (ID_uporabnika) REFERENCES uporabniki(ID)
                );
            """)
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri ustvarjanju tabele {self.ime}: {e}")
    
    def dodaj_vrstico(self, podatki):
        super().dodaj_vrstico(podatki)
    
    def uvozi(self, encoding="UTF-8"):
        super().uvozi(encoding)

class Uporabniki(Tabela):
    ime = "uporabniki"
    pot_podatkov = "data/uporabniki.csv"
    
    def ustvari(self):
        try:
            self.povezava.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.ime} (
                    ID                INTEGER        PRIMARY KEY AUTOINCREMENT,
                    Uporabnisko_ime   VARCHAR (50)   NOT NULL UNIQUE,
                    Geslo             VARCHAR (100)  NOT NULL,
                    Vrsta             INTEGER        NOT NULL CHECK(Vrsta IN (0, 1, 2)) -- 0 za učence, 1 za učitelje, 2 za admin
                );
            """)
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri ustvarjanju tabele {self.ime}: {e}")
    
    def dodaj_vrstico(self, podatki):
        super().dodaj_vrstico(podatki)
    
    def uvozi(self, encoding="UTF-8"):
        super().uvozi(encoding)

class Predmeti(Tabela):
    ime = "predmeti"
    pot_podatkov = "data/predmeti.csv"
    
    def ustvari(self):
        try:
            self.povezava.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.ime} (
                    ID           INTEGER       PRIMARY KEY AUTOINCREMENT,
                    Ime_predmeta VARCHAR (100) NOT NULL
                );
            """)
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri ustvarjanju tabele {self.ime}: {e}")
    
    def dodaj_vrstico(self, podatki):
        super().dodaj_vrstico(podatki)
    
    def uvozi(self, encoding="UTF-8"):
        super().uvozi(encoding)

class Instrukcije(Tabela):
    ime = "instrukcije"
    pot_podatkov = "data/instrukcije.csv"
    
    def ustvari(self):
        try:
            self.povezava.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.ime} (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Datum DATE NOT NULL,
                    Cas TIME NOT NULL,
                    Trajanje INTEGER NOT NULL, -- trajanje v minutah
                    Status TEXT NOT NULL CHECK(Status IN ('Rezervirano', 'Opravljeno', 'Preklicano')),
                    ID_ucitelja INTEGER NOT NULL,
                    ID_ucenca INTEGER NOT NULL,
                    FOREIGN KEY (ID_ucitelja) REFERENCES ucitelji(ID),
                    FOREIGN KEY (ID_ucenca) REFERENCES ucenci(ID)
                );
            """)
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri ustvarjanju tabele {self.ime}: {e}")
    
    def dodaj_vrstico(self, podatki):
        super().dodaj_vrstico(podatki)
    
    def uvozi(self, encoding="UTF-8"):
        super().uvozi(encoding)

class UciteljiPredmeti(Tabela):
    ime = "uciteljiPredmeti"
    pot_podatkov = "data/uciteljiPredmeti.csv"
    
    def ustvari(self):
        try:
            self.povezava.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.ime} (
                    ID_ucitelja INTEGER NOT NULL,
                    ID_predmeta INTEGER NOT NULL,
                    PRIMARY KEY (ID_ucitelja, ID_predmeta),
                    FOREIGN KEY (ID_ucitelja) REFERENCES ucitelji(ID),
                    FOREIGN KEY (ID_predmeta) REFERENCES predmeti(ID)
                );
            """)
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri ustvarjanju tabele {self.ime}: {e}")
    
    def dodaj_vrstico(self, podatki):
        super().dodaj_vrstico(podatki)
    
    def uvozi(self, encoding="UTF-8"):
        super().uvozi(encoding)

def ustvari_tabele(tabele):
    for tab in tabele:
        try:
            print(f"Ustvarjam tabelo {tab.ime}")
            tab.ustvari()
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri ustvarjanju tabele {tab.ime}: {e}")

def izbrisi_tabele(tabele):
    for tab in tabele:
        try:
            print(f"Praznem tabelo {tab.ime}")
            tab.izprazni()
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri praznjenju tabele {tab.ime}: {e}")
    
    for tab in tabele:
        try:
            print(f"Brišem tabelo {tab.ime}")
            tab.izbrisi()
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri brisanju tabele {tab.ime}: {e}")

def uvozi_podatke(tabele):
    for tab in tabele:
        try:
            print(f"Uvažam podatke v tabelo {tab.ime}")
            tab.uvozi()
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri uvozu podatkov v tabelo {tab.ime}: {e}")

def izprazni_tabele(tabele):
    for tab in tabele:
        try:
            tab.izprazni()
        except sqlite3.DatabaseError as e:
            print(f"Napaka pri praznjenju tabele {tab.ime}: {e}")

def pripravi_tabele(povezava):
    ucitelji = Ucitelji(povezava)
    ucenci = Ucenci(povezava)
    uporabniki = Uporabniki(povezava)
    predmeti = Predmeti(povezava)
    instrukcije = Instrukcije(povezava)
    uciteljiPredmeti = UciteljiPredmeti(povezava)
    return [uporabniki, ucitelji, ucenci, predmeti, instrukcije, uciteljiPredmeti]

def ustvari_bazo(povezava):
    tabele = pripravi_tabele(povezava)
    tabele_brisanje = [tabele[i] for i in [5, 4, 1, 2, 3, 0]]
    izbrisi_tabele(tabele_brisanje)
    ustvari_tabele(tabele)
    uvozi_podatke(tabele)

def pripravi_bazo(povezava):
    try:
        with povezava:
            cur = povezava.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
            if cur.fetchone()[0] == 0:
                ustvari_bazo(povezava)
    except sqlite3.DatabaseError as e:
        print(f"Napaka pri preverjanju obstoja baze: {e}")