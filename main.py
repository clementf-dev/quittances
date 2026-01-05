from models.locataire import Locataire
from db.locataire_repositery import ajouter_locataire, lister_locataire

locataire1 = Locataire ("Jean","Paul",2)
locataire2 = Locataire("Hervé","Dupont",600)
locataire3 = Locataire("Catherine","Dessort",300)

ajouter_locataire(Locataire("Jean","Paul",2))
ajouter_locataire(Locataire("Hervé","Dupont",600))
ajouter_locataire(Locataire("Catherine","Dessort",300))

locataires = lister_locataire()
for loc in locataires:
    print(loc.prenom, loc.nom, loc.loyer)
