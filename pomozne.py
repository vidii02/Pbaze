from enum import Enum
from functools import wraps

class Meni(Enum):
    """Razerd za izbiro možnosti v menijih."""
    def __init__(self, ime, funkcija):
        self.ime = ime
        self.funkcija = funkcija
    
    def __str__(self):
        return self.ime
    
def prekinitev(funkcija):
    """Dekorator za obravnavo prekinitve s CTRL + C."""
    @wraps(funkcija)
    def wrapper(*largs, **kwargs):
        try:
            funkcija(*largs, **kwargs)
        except KeyboardInterrupt:
            print("\Končano!")
    return wrapper