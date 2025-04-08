from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import EnergyListing, Transaction, energy_listings, transactions, users

bp = Blueprint('dashboard', __name__)

@bp.route('/')
@bp.route('/dashboard')
@login_required
def index():
    # Get user's listings and transactions
    user_listings = [listing for listing in energy_listings.values() 
                    if listing.producer_id == current_user.id]
    user_transactions = [transaction for transaction in transactions.values() 
                        if (current_user.role == 'producer' and transaction.producer_id == current_user.id) or
                           (current_user.role == 'consumer' and transaction.consumer_id == current_user.id)]
    
    # Calculate statistics
    stats = {
        'total_listings': len(user_listings),
        'total_energy': sum(listing.amount for listing in user_listings),
        'total_earnings': sum(transaction.amount * transaction.price 
                            for transaction in user_transactions 
                            if transaction.producer_id == current_user.id),
        'total_purchases': len([t for t in user_transactions if t.consumer_id == current_user.id]),
        'total_spent': sum(transaction.amount * transaction.price 
                          for transaction in user_transactions 
                          if transaction.consumer_id == current_user.id)
    }
    
    # Add user information to transactions
    for transaction in user_transactions:
        transaction.producer = users[transaction.producer_id]
        transaction.consumer = users[transaction.consumer_id]
    
    return render_template('dashboard/index.html',
                         listings=user_listings,
                         transactions=user_transactions,
                         stats=stats) 