# Projet Quittances

Application Django pour gérer les locataires, générer des quittances rétroactives et stocker des documents.

---

## Fonctionnalités

- Créer des quittances rétroactives en choisissant **mois et année**.
- Modifier la **date de paiement** directement depuis l'admin.
- Upload de **documents** pour chaque locataire.
- Boutons dans l'admin pour :
  - 📄 Générer une quittance
  - ➕ Ajouter un document
  - 📂 Voir les documents
- Génération de **PDF de quittances** avec ReportLab.

---

## Installation

### 1. Cloner le projet

```bash
git clone <URL_DE_TON_REPO>
cd quittances
```

### 2. Créer un environnement virtuel et l'activer

```bash
# Linux / macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Appliquer les migrations

```bash
python manage.py migrate
```

### 5. Créer un super utilisateur

```bash
python manage.py createsuperuser
```

### 6. Lancer le serveur

```bash
python manage.py runserver
```
