from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.colors import black

from .models import Quittance
from django.utils import timezone
import os
import sys
from django.conf import settings
from num2words import num2words

def generer_pdf_quittance(request, quittance_id):
    quittance = Quittance.objects.get(id=quittance_id)
    locataire = quittance.locataire

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="quittance_{locataire.nom}_{quittance.mois}_{quittance.annee}.pdf"'
    )

    p = canvas.Canvas(response, pagesize=A4)
    largeur, hauteur = A4

    # ───────── CADRE ─────────
    p.rect(1.5*cm, 1.5*cm, largeur-3*cm, hauteur-3*cm)

    # ───────── TITRE ─────────
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(
        largeur / 2,
        hauteur - 3*cm,
        f"Quittance de loyer du mois de {quittance.get_mois_display()} {quittance.annee}"
    )

    # ───────── PROPRIÉTAIRE (GAUCHE) ─────────
    p.setFont("Helvetica", 11)
    y_gauche = hauteur - 5*cm

    p.drawString(2.5*cm, y_gauche, "Jean-Marie Favresse")
    p.drawString(2.5*cm, y_gauche - 0.6*cm, "6 Les Grands Augerons")
    p.drawString(2.5*cm, y_gauche - 1.2*cm, "18300 Menetou-Râtel")

    # ───────── LOCATAIRE (DROITE) ─────────
    y_droite = hauteur - 6*cm
    p.setFont("Helvetica-Oblique", 11)

    p.drawString(11*cm, y_droite, f"{locataire.prenom} {locataire.nom}")
    p.drawString(11*cm, y_droite - 0.6*cm, locataire.adresse)
    p.drawString(
        11*cm,
        y_droite - 1.8*cm,
        f"Fait à Paris, le {quittance.date_generation.strftime('%d/%m/%Y')}"
    )

    # ───────── ADRESSE LOCATION ─────────
    y = hauteur - 9*cm
    p.setFont("Helvetica-Bold", 11)
    p.drawString(2.5*cm, y, "Adresse de la location :")
    p.setFont("Helvetica", 11)
    p.drawString(2.5*cm, y - 0.6*cm, locataire.adresse)

    # ───────── TEXTE JURIDIQUE ─────────
    debut = quittance.date_debut_periode.strftime('%d/%m/%Y')
    fin = quittance.date_fin_periode.strftime('%d/%m/%Y')
    total_lettres = num2words(quittance.total, lang='fr')
    texte = (
        f"Je soussigné Jean-Marie Favresse, propriétaire du logement désigné ci-dessus, "
        f"déclare avoir reçu de Monsieur / Madame {locataire.prenom} {locataire.nom}, "
        f"la somme de {total_lettres} euros, au titre du paiement du loyer et des charges "
        f"pour la période de location du {debut} "
        f"au {fin} et lui en donne quittance, "
        f"sous réserve de tous mes droits."
    )

    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontName = "Helvetica"
    style.fontSize = 11
    style.alignment = TA_JUSTIFY

    paragraph = Paragraph(texte, style)
    paragraph.wrapOn(p, largeur - 5*cm, 6*cm)
    paragraph.drawOn(p, 2.5*cm, hauteur - 14*cm)

    # ───────── DÉTAIL DU RÈGLEMENT ─────────
    y = hauteur - 19*cm
    p.setFont("Helvetica-Bold", 11)
    p.drawString(2.5*cm, y, "Détail du règlement :")
    ligne_y = y - 1.2*cm
    p.setFont("Helvetica", 11)
    p.drawString(2.5*cm, ligne_y, f"Loyer : {quittance.loyer:.2f} €")
    ligne_y -= 0.7*cm
    p.drawString(2.5*cm, ligne_y, f"Charges : {quittance.charges:.2f} €")
    ligne_y -= 0.7*cm
    p.setFont("Helvetica-Bold", 11)
    p.drawString(2.5*cm, ligne_y, f"Total : {quittance.total:.2f} €")

    # ───────── SIGNATURE ─────────
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(12*cm, 4*cm, "Signature du propriétaire")

    # ───────── Chemin dynamique pour la signature ─────────
    if getattr(sys, 'frozen', False):
        # Mode .exe : PyInstaller extrait les fichiers dans _MEIPASS
        base_dir = sys._MEIPASS  # ← CHANGE ICI
    else:
        # Mode développement
        base_dir = settings.BASE_DIR

    # Le chemin doit correspondre à ton .spec : 'locataires/static'
    signature_path = os.path.join(base_dir, 'locataires', 'static', 'signature.png')  # ← ET ICI

    if os.path.exists(signature_path):
        p.drawImage(
            signature_path,
            11.5*cm,
            1.8*cm,
            width=5*cm,
            height=2*cm,
            preserveAspectRatio=True
        )
    else:
        # Message de debug pour voir quel chemin est utilisé
        p.setFont("Helvetica", 8)
        p.drawString(11.5*cm, 2*cm, "[Signature manquante]")
        p.drawString(11.5*cm, 1.5*cm, f"Chemin: {signature_path}")

    p.showPage()
    p.save()

    return response