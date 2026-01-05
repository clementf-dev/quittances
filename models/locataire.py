class Locataire:
    def __init__(self, prenom, nom, loyer):
        self.prenom = prenom
        self.nom = nom
        self.loyer = loyer

    def afficher(self):
        print(f"{self.prenom} {self.nom} - {self.loyer} euros")

    def loyer_annuel(self):
        return self.loyer * 12