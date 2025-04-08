from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import login_manager

# In-memory storage
users = {}
energy_listings = {}
transactions = {}

class User(UserMixin):
    def __init__(self, id, name, email, role, location, profile_picture=None):
        self.id = id
        self.name = name
        self.email = email
        self.role = role  # 'producer' or 'consumer'
        self.location = location
        self.profile_picture = profile_picture
        self._password = None

    def set_password(self, password):
        self._password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password, password)

class EnergyListing:
    def __init__(self, id, producer_id, amount, price):
        self.id = id
        self.producer_id = producer_id
        self.amount = amount
        self.price = price
        self.status = 'available'  # 'available' or 'sold'
        self.timestamp = datetime.utcnow()

class Transaction:
    def __init__(self, id, producer_id, consumer_id, energy_listing_id, amount, price):
        self.id = id
        self.producer_id = producer_id
        self.consumer_id = consumer_id
        self.energy_listing_id = energy_listing_id
        self.amount = amount
        self.price = price
        self.timestamp = datetime.utcnow()

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id) 