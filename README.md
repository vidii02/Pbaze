# Sistem za inštrukcije

Za seminarsko nalogo bova naredila sistem za inštrukcije. Glavne entitete bodo učitelji, učenci, inštrukcije in predmeti.

## Entitete

### Učitelji
- **ID**: Enolični identifikator učitelja
- **Ime**: Ime učitelja
- **Priimek**: Priimek učitelja
- **E-pošta**: Elektronski naslov učitelja
- **Cena na uro**: Cena, ki jo učitelj zaračuna za uro inštrukcij

### Učenci
- **ID**: Enolični identifikator učenca
- **Ime**: Ime učenca
- **Priimek**: Priimek učenca
- **E-pošta**: Elektronski naslov učenca

### Predmeti
- **ID**: Enolični identifikator predmeta
- **Ime predmeta**: Ime predmeta

### Inštrukcije
- **ID**: Enolični identifikator inštrukcije
- **Datum**: Datum inštrukcije
- **Čas**: Čas začetka inštrukcije
- **Trajanje**: Trajanje inštrukcije
- **Status**: Status inštrukcije (rezervirano, opravljeno, preklicano)
- **ID učitelja**: Enolični identifikator učitelja, ki izvaja inštrukcijo
- **ID učenca**: Enolični identifikator učenca, ki se udeležuje inštrukcije

## Relacije

- **Učitelji - Inštrukcije**: 1:n (en učitelj ima lahko več inštrukcij, vsaki inštrukciji pa pripada en učitelj)
- **Učenci - Inštrukcije**: 1:n (en učenec ima lahko več inštrukcij, vsaki inštrukciji pa pripada en učenec)
- **Učitelji - Predmeti**: m:n (več učiteljev lahko poučuje isti predmet, en učitelj pa lahko poučuje več predmetov)

## Opis sistema

Sistem omogoča upravljanje inštrukcij med učitelji in učenci. Učitelji lahko določijo ceno na uro za svoje inštrukcije, učenci pa lahko rezervirajo inštrukcije pri različnih učiteljih. Sistem omogoča tudi spremljanje statusa inštrukcij (rezervirano, opravljeno, preklicano) ter upravljanje predmetov, ki jih učitelji poučujejo.

## Tehnologije

- **Python**: Programski jezik za razvoj aplikacije
- **SQLite**: Relacijska baza podatkov za shranjevanje podatkov
- **Bottle**: Mikro spletni okvir za razvoj spletnih aplikacij
- **HTML/CSS**: Za oblikovanje uporabniškega vmesnika

## Namestitev in zagon

1. Klonirajte repozitorij:
    ```bash
    git clone <URL_repozitorija>
    ```
2. Zaženite aplikacijo:
    ```bash
    python spletni_vmesnik.py
    ```

## Avtorja

- **Alen Nemanič**
- **Vid Julijan Ahačevčič**