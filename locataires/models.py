from django.db import models
from django.utils import timezone

class Locataire(models.Model):
    prenom = models.CharField(max_length=30)
    nom = models.CharField(max_length=30)
    adresse = models.CharField(max_length=200)
    date_entree = models.DateField(verbose_name="Date d'entrée dans les lieux")
    loyer = models.DecimalField(max_digits=10, decimal_places=2)
    charges = models.DecimalField(max_digits=5,decimal_places=2)
    
    class Meta:
        verbose_name_plural = "Locataires"
    
    def __str__(self):
        return f"{self.nom} {self.prenom}"
    
    def loyer_annuel(self):
        return (self.loyer + self.charges) * 12


class Quittance(models.Model):
    locataire = models.ForeignKey(Locataire, on_delete=models.CASCADE)

    MOIS_CHOICES = [
        (1, "Janvier"), (2, "Février"), (3, "Mars"), (4, "Avril"),
        (5, "Mai"), (6, "Juin"), (7, "Juillet"), (8, "Août"),
        (9, "Septembre"), (10, "Octobre"), (11, "Novembre"), (12, "Décembre")
    ]
    mois = models.PositiveSmallIntegerField(choices=MOIS_CHOICES)
    annee = models.PositiveSmallIntegerField()

    date_debut_periode = models.DateField(verbose_name="Début de période", null=True, blank=True)
    date_fin_periode = models.DateField(verbose_name="Fin de période", null=True, blank=True)

    date_paiement = models.DateField(verbose_name="Date du paiement", default=timezone.now)
    loyer = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Loyer mensuel (€)")
    charges = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Charges mensuelles (€)") # type: ignore
    total = models.DecimalField(max_digits=8, decimal_places=2)
    montant_paye = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Montant payé (€)") # type: ignore
    date_generation = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Quittances"
        unique_together = ('locataire', 'mois', 'annee')
        ordering = ['locataire__nom', 'annee', 'mois']

    def __str__(self):
        return f"Quittance {self.get_mois_display()} {self.annee} - {self.locataire}" # type: ignore

    def save(self, *args, **kwargs):
        import calendar
        from datetime import date
        if not self.date_debut_periode or not self.date_fin_periode:
            self.date_debut_periode = date(self.annee, self.mois, 1)
            self.date_fin_periode = date(
                self.annee,
                self.mois,
                calendar.monthrange(self.annee, self.mois)[1]
            )
        super().save(*args, **kwargs)
        
    @property
    def reste_du(self):
        return self.total - (self.montant_paye or 0)

    @property
    def statut_paiement(self):
        """
        Retourne :
        - 'payé' si tout est payé
        - 'partiel' si paiement partiel
        - 'impayé' si rien n'est payé
        """
        if self.montant_paye >= self.total:
            return "payé"
        elif self.montant_paye > 0:
            return "partiel"
        else:
            return "impayé"


class Document(models.Model):
    locataire = models.ForeignKey(Locataire, on_delete=models.CASCADE, related_name='documents')
    fichier = models.FileField(upload_to='documents_locataires/')
    description = models.CharField(max_length=200, blank=True)
    date_upload = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Documents"

    def __str__(self):
        return f"{self.fichier.name} ({self.locataire})"