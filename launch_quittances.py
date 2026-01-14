import os
import sys
import webbrowser
import django
from django.core.management import call_command
from io import StringIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Crée des flux fictifs pour stdout et stderr
out = StringIO()
err = StringIO()

# Exécute les migrations sans tenter d'écrire dans la console
call_command('migrate', interactive=False, stdout=out, stderr=err)

# Se placer dans le dossier du projet
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Ajouter le projet au sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Définir le module settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Rediriger stdout et stderr pour éviter crash avec --noconsole
sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

# Lancer automatiquement le navigateur
url = 'http://127.0.0.1:8000/admin'
webbrowser.open(url)

# Lancer le serveur Django sans autoreload
from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000', '--noreload'])

import os
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.conf import settings
settings.DATABASES['default']['NAME'] = os.path.join(BASE_DIR, 'db.sqlite3')