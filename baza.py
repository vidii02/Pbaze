import csv

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
            Metoda odstrani tabelo in vse njenje podatke iz baze.
        """
        self.povezava.execute(f"DROP TABLE IF EXISTS {self.ime};")
    
    def uvozi(self, encoding = "UTF-8"):
        """
        Uvoz podatkov v tabelo.

        Argumenti:
            encoding - Način kodiranja.

        Opis:
            Uvozi podatke v tabelo.
        """
        if self.pot_podatkov is None:
            return None
        with open(self.pot_podatkov, encoding = encoding) as beri:
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
        
    def izprazni(self):
        """
        Izprazni tabelo.

        Opis:
            Metoda odstrani vse vrstice iz tabele, vendar struktura tabele ostane.
        """
        self.povezava.execute(f"DELETE FROM {self.ime};")
    
    def dodajanje(self, stolpci = None):
        """
        Gradnja poizvedbe.

        Argumenti:
            stolpci - Seznam stolpcev.

        Opis:
            Pripravi poizvedbo.
        """
        return f"""
                INSERT INTO {self.ime} ({", ".join(stolpci)})
                VALUES ({", ".join(PARAM_FMT.format(s) for s in stolpci)});
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
        podatki = nov_slovar
        poizvedba = self.dodajanje(podatki.keys())
        cur = self.povezava.execute(poizvedba, podatki)
        return cur.lastrowid



class Ucitelji(Tabela):
    """"""
    ime = "ucitelji"
    pot_podatkov = "data/ucitelji.csv"
    
    def ustvari(self):
        """
        Ustvari tabelo.

        Opis:
            Metoda ustvari tabelo ucitelj.
        """
        
        self.povezava.execute("""
                CREATE TABLE ucitelji (
                ID      INTEGER        PRIMARY KEY AUTOINCREMENT,
                Ime     VARCHAR (50)   NOT NULL,
                Priimek VARCHAR (50)   NOT NULL,
                Eposta  VARCHAR (100)  NOT NULL,
                Cena    DECIMAL (5, 2) NOT NULL
            );
        """)
        
    def dodaj_vrstico(self, podatki):
        """
        Dodaj vrstico v bazo.

        Argumenti:
            podatki - Slovar podatkov.

        Opis:
            Metoda doda vrstico v tabelo.
        """
        assert "ID" in podatki
        cur = self.povezava.execute("""
            SELECT id FROM ucitelji
            WHERE id = :ID;
        """, podatki)
        result = cur.fetchone()
        if result is None:
            return super().dodaj_vrstico(podatki)
        return result[0]
    
    def uvozi(self, encoding = "UTF-8"):
        super().uvozi(encoding)

# TODO preostale razrede za tabele



def ustvari_tabele(tabele):
    """
    Ustvari podane tabele.
    """
    for tab in tabele:
        tab.ustvari()

def izbrisi_tabele(tabele):
    """
    Izbriši podane tabele.
    """
    for tab in tabele:
        tab.izbrisi()

def uvozi_podatke(tabele):
    """
    Uvozi podatke v podane tabele.
    """
    for tab in tabele:
        tab.uvozi()

def izprazni_tabele(tabele):
    """
    Izprazni podane tabele.
    """
    for tab in tabele:
        tab.izprazni()

def ustvari_bazo(povezava):
    """Ustvari bazo"""
    tabele = pripravi_tabele(povezava)
    izbrisi_tabele(tabele)
    ustvari_tabele(tabele)
    uvozi_podatke(tabele)

def pripravi_tabele(povezava):
    """Pripravi objekte za tabele"""
    ucitelji = Ucitelji(povezava)
    return [ucitelji,]

def ustvari_bazo_ce_ne_obstaja(conn):
    """
    Ustvari bazo, če ta še ne obstaja.
    """
    with conn:
        cur = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
        if cur.fetchone()[0] == 0:
            ustvari_bazo(conn)
