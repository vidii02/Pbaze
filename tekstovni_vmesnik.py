from pomozne import *
from model import *

def vnesi_izbiro(moznosti):
    """
    Uporabniku da na izbiro podane možnosti.
    """
    moznosti = list(moznosti)
    for i, moznost in enumerate(moznosti, 1):
        print(f'{i}) {moznost}')
    izbira = None
    while True:
        try:
            izbira = int(input('> ')) - 1
            return moznosti[izbira]
        except (ValueError, IndexError):
            print("Napačna izbira!")

def Izhod():
    """Pozdravi pred izhodom."""
    print('Adijo!')

@prekinitev
def vsi_ucitelji():
    """Izpiše vse učitelje."""
    result = Ucitelji.vsi_ucitelji()
    # print("Test")
    for el in result:
        print(el)

class GlavniMeni(Meni):
    """Glavni meni"""
    Ucitelji = ("Vsi učitelji", vsi_ucitelji)
    IZHOD = ("Izhod", Izhod)

@prekinitev
def glavni_meni():
    """Prikazuje glavni meni, dokler uporabnika ne izbere izhoda."""
    print("Glavni meni!")
    while True:
        print("Katero izbiro želiš?")
        izbira = vnesi_izbiro(GlavniMeni)
        izbira.funkcija()
        if izbira == GlavniMeni.IZHOD:
            return

glavni_meni()