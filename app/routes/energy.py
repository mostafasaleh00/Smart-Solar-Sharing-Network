from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import EnergyListing, Transaction, energy_listings, transactions, users
import uuid

bp = Blueprint('energy', __name__, url_prefix='/energy')

@bp.route('/list', methods=['GET', 'POST'])
@login_required
def list_energy():
    if current_user.role != 'producer':
        flash('Only producers can list energy')
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        price = float(request.form.get('price'))
        
        listing_id = str(uuid.uuid4())
        listing = EnergyListing(
            id=listing_id,
            producer_id=current_user.id,
            amount=amount,
            price=price
        )
        energy_listings[listing_id] = listing
        
        flash('Energy listing created successfully!')
        return redirect(url_for('energy.list_energy'))
        
    return render_template('energy/list.html')

@bp.route('/marketplace')
@login_required
def marketplace():
    # Get filter parameters
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_amount = request.args.get('min_amount', type=float)
    max_amount = request.args.get('max_amount', type=float)
    location = request.args.get('location')
    sort_by = request.args.get('sort_by', 'timestamp')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Get available listings
    available_listings = [listing for listing in energy_listings.values() 
                         if listing.status == 'available']
    
    # Add producer information to each listing
    for listing in available_listings:
        listing.producer = users[listing.producer_id]
    
    # Get unique locations from available listings
    locations = sorted(set(listing.producer.location for listing in available_listings))
    
    # Apply filters
    if min_price is not None:
        available_listings = [l for l in available_listings if l.price >= min_price]
    if max_price is not None:
        available_listings = [l for l in available_listings if l.price <= max_price]
    if min_amount is not None:
        available_listings = [l for l in available_listings if l.amount >= min_amount]
    if max_amount is not None:
        available_listings = [l for l in available_listings if l.amount <= max_amount]
    if location:
        available_listings = [l for l in available_listings if l.producer.location == location]
    
    # Sort listings
    if sort_by == 'price':
        available_listings.sort(key=lambda x: x.price, reverse=(sort_order == 'desc'))
    elif sort_by == 'amount':
        available_listings.sort(key=lambda x: x.amount, reverse=(sort_order == 'desc'))
    else:  # timestamp
        available_listings.sort(key=lambda x: x.timestamp, reverse=(sort_order == 'desc'))
    
    return render_template('energy/marketplace.html', 
                         listings=available_listings,
                         locations=locations)

@bp.route('/checkout/<listing_id>')
@login_required
def checkout(listing_id):
    if current_user.role != 'consumer':
        flash('Only consumers can purchase energy')
        return redirect(url_for('dashboard.index'))
    
    listing = energy_listings.get(listing_id)
    if not listing:
        flash('Energy listing not found')
        return redirect(url_for('energy.marketplace'))
    
    if listing.status != 'available':
        flash('This energy listing is no longer available')
        return redirect(url_for('energy.marketplace'))
    
    # Add producer information to the listing
    listing.producer = users[listing.producer_id]
    
    return render_template('energy/checkout.html', listing=listing)

@bp.route('/purchase/<listing_id>', methods=['POST'])
@login_required
def purchase(listing_id):
    if current_user.role != 'consumer':
        flash('Only consumers can purchase energy')
        return redirect(url_for('dashboard.index'))
    
    listing = energy_listings.get(listing_id)
    if not listing:
        flash('Energy listing not found')
        return redirect(url_for('energy.marketplace'))
    
    if listing.status != 'available':
        flash('This energy listing is no longer available')
        return redirect(url_for('energy.marketplace'))
    
    # Create transaction
    transaction_id = str(uuid.uuid4())
    transaction = Transaction(
        id=transaction_id,
        producer_id=listing.producer_id,
        consumer_id=current_user.id,
        energy_listing_id=listing_id,
        amount=listing.amount,
        price=listing.price
    )
    transactions[transaction_id] = transaction
    
    # Update listing status
    listing.status = 'sold'
    
    flash('Energy purchased successfully!')
    return redirect(url_for('dashboard.index')) 