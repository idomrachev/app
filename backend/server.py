"""
Django ASGI/WSGI entry point for uvicorn
"""
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'damage_project.settings')

from django.core.wsgi import get_wsgi_application

# For uvicorn compatibility
app = get_wsgi_application()
