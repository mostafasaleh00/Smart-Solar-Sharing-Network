from datetime import datetime, timedelta
import random
from app.models import User, EnergyListing, Transaction, users, energy_listings, transactions

def create_mock_data():
    # Create mock users if they don't exist
    if not users:
        # Create producers
        producers = [
            {
                "id": "producer1",
                "name": "John Producer",
                "email": "producer@example.com",
                "role": "producer",
                "location": "New York"
            },
            {
                "id": "producer2",
                "name": "Sarah Solar",
                "email": "sarah@example.com",
                "role": "producer",
                "location": "Los Angeles"
            },
            {
                "id": "producer3",
                "name": "Mike Green",
                "email": "mike@example.com",
                "role": "producer",
                "location": "Chicago"
            }
        ]
        
        for producer_data in producers:
            producer = User(**producer_data)
            producer.set_password("password123")
            users[producer_data["id"]] = producer

        # Create consumers
        consumers = [
            {
                "id": "consumer1",
                "name": "Alice Consumer",
                "email": "consumer@example.com",
                "role": "consumer",
                "location": "Boston"
            },
            {
                "id": "consumer2",
                "name": "Bob Buyer",
                "email": "bob@example.com",
                "role": "consumer",
                "location": "Seattle"
            }
        ]
        
        for consumer_data in consumers:
            consumer = User(**consumer_data)
            consumer.set_password("password123")
            users[consumer_data["id"]] = consumer

    # Create mock energy listings if they don't exist
    if not energy_listings:
        # Generate 20 mock listings
        for i in range(20):
            listing_id = f"listing{i+1}"
            # Randomly assign to a producer
            producer_id = random.choice(["producer1", "producer2", "producer3"])
            
            # Generate more realistic energy amounts and prices
            amount = random.uniform(5, 200)  # Random amount between 5 and 200 kWh
            base_price = random.uniform(0.05, 0.3)  # Base price between $0.05 and $0.3 per kWh
            
            # Add some variation based on time of day (simulating peak/off-peak pricing)
            hour = datetime.utcnow().hour
            if 8 <= hour <= 20:  # Peak hours
                price = base_price * 1.2  # 20% higher during peak hours
            else:
                price = base_price * 0.8  # 20% lower during off-peak hours
            
            listing = EnergyListing(
                id=listing_id,
                producer_id=producer_id,
                amount=amount,
                price=price
            )
            
            # Set random timestamp within last 48 hours
            listing.timestamp = datetime.utcnow() - timedelta(
                hours=random.uniform(0, 48),
                minutes=random.uniform(0, 60)
            )
            
            # Randomly mark some as sold (40% chance)
            if random.random() < 0.4:
                listing.status = 'sold'
            
            energy_listings[listing_id] = listing

    # Create mock transactions if they don't exist
    if not transactions:
        # Create transactions for sold listings
        sold_listings = [l for l in energy_listings.values() if l.status == 'sold']
        for i, listing in enumerate(sold_listings):
            transaction_id = f"transaction{i+1}"
            # Randomly assign to a consumer
            consumer_id = random.choice(["consumer1", "consumer2"])
            
            transaction = Transaction(
                id=transaction_id,
                producer_id=listing.producer_id,
                consumer_id=consumer_id,
                energy_listing_id=listing.id,
                amount=listing.amount,
                price=listing.price
            )
            
            # Set transaction timestamp slightly after listing timestamp
            transaction.timestamp = listing.timestamp + timedelta(minutes=random.uniform(1, 60))
            transactions[transaction_id] = transaction 