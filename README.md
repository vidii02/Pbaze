#Sistem za inštrukcije
Za seminarsko nalogo bova naredila sistem za inštrukcije. Glavne entitete bodo učitelji, učenci, inštrukcije in predmeti.
Učitelji bodo imeli atribute ID, ime in priimek, e-pošta ter ceno na uro. Učenci bodo imeli ID, ime in priimek ter e-pošto.
Predmeti bodo imeli ID ter ime predmeta. Entiteta inštrukcije pa bo imela ID, datum, čas, trajanje, status(rezervirano,
opravljeno ali preklicano) ter ID učitelja in ID učenca. Relacija med učitelji in inštrukcijami je 1:n (en učitelj ima lahko več
inštrukcij, vsaki inštrukciji pa pripada en učitelj). Tudi med učenci in inštrukcijami je 1:n. Relacija med učitelji in predmeti
pa je m:n saj lahko več učiteljev poučuje isti predmet. 
