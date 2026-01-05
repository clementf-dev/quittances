from db.database import get_connection
from models.locataire import Locataire

def ajouter_locataire(locataire: Locataire):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO locataires(prenom, nom, loyer) VALUES (?, ?, ?)",
        (locataire.prenom, locataire.nom, locataire.loyer)
    )

    conn.commit()
    conn.close()

def lister_locataire():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT prenom, nom, loyer FROM locataires")
    rows = cursor.fetchall()

    conn.close()
    
    locataires = []
    for row in rows:
        locataires.append(Locataire(*row))
    return locataires