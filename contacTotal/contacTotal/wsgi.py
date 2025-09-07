"""
WSGI config for contacTotal project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from pathlib import Path
from django.core.wsgi import get_wsgi_application


try:
    from dotenv import load_dotenv
    BASE_DIR = Path(__file__).resolve().parent.parent
    load_dotenv(BASE_DIR / ".env")
except Exception:
    pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contacTotal.settings')

application = get_wsgi_application()