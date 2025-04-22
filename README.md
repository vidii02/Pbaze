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

## Dodatna entiteta: Uporabniki

Sistem vključuje tudi tabelo **Uporabniki**, ki centralizira prijavne podatke.

### Uporabniki
- **ID**: Enolični identifikator
- **Uporabniško ime**: Unikatno ime za prijavo
- **Geslo**: Šifrirano geslo
- **Vrsta uporabnika**: Vrsta (učitelj, učenec, admin)

### Relacije
- **Uporabniki - Učitelji**: 1:1 (en uporabnik je povezan z enim učiteljem)
- **Uporabniki - Učenci**: 1:1 (en uporabnik je povezan z enim učencem)

### Razlog za razdelitev
Osebni podatki, kot so ime, priimek, e-pošta in drugi atributi, specifični za učitelje ali učence, so shranjeni v tabelah **Učitelji** in **Učenci**. Ti podatki so specifični za posamezno vlogo in niso potrebni za prijavo v sistem.

Tabela **Uporabniki** je namenjena centraliziranemu upravljanju prijavnih podatkov, kot so uporabniško ime, geslo in vrsta uporabnika (učitelj, učenec, admin). Ta razdelitev omogoča boljšo modularnost in varnost, saj so občutljivi podatki za prijavo ločeni od osebnih podatkov, specifičnih za posamezne vloge.

## Testni uporabniki

Za hitro testiranje sistema lahko uporabite naslednje uporabniške podatke, ki so zapisani v datoteki `ucitelj_ucenec_najvec_instrukcij.txt`:

- **Učitelj z največ inštrukcijami**:
  - Uporabniško ime: `sabelovz`
  - Geslo: `vpfaXR2791jq`
- **Učenec z največ inštrukcijami**:
  - Uporabniško ime: `vpandya3w`
  - Geslo: `jekwRC34w`

## Opis sistema

Sistem omogoča upravljanje inštrukcij med učitelji in učenci. Učitelji lahko določijo ceno na uro za svoje inštrukcije, učenci pa lahko rezervirajo inštrukcije pri različnih učiteljih. Sistem omogoča tudi spremljanje statusa inštrukcij (rezervirano, opravljeno, preklicano) ter upravljanje predmetov, ki jih učitelji poučujejo.

## Namestitev in zagon

1. Klonirajte repozitorij:
    ```bash
    git clone <URL_repozitorija>
    ```
2. Zagon spletnega vmesnika:
    ```bash
    python spletni_vmesnik.py
    ```
    Zagon tekstovnega vmesnika:
    ```bash
    python tekstovni_vmesnik.py
    ```

## Avtorja

- **Alen Nemanič**
- **Vid Julijan Ahačevčič**