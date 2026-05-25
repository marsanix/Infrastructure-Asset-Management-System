"""Blueprint API v1 — semua modul diimport di sini."""
from flask import Blueprint

api_v1 = Blueprint('api_v1', __name__)

# Import urutan penting: base_crud harus sebelum modul yang menggunakannya
from . import auth
from . import assets
from . import accounts
from . import departments
from . import locations
from . import categories
from . import brands
from . import models
from . import employees
from . import network
from . import credentials
from . import incidents
from . import changes
from . import problems
from . import requests_bp
from . import reports
from . import audit
