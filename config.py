import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    # Add more configuration variables as needed 