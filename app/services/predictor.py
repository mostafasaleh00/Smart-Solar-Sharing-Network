import numpy as np
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta

class EnergyPricePredictor:
    def __init__(self):
        self.model = RandomForestRegressor()
        self.features = [
            'time_of_day',
            'day_of_week',
            'month',
            'demand_level',
            'weather_score',
            'historical_avg_price'
        ]
        # Train the model with some initial data
        self._train_model()
    
    def _train_model(self):
        # Generate some synthetic training data
        X_train = []
        y_train = []
        
        # Generate data for different times of day, days of week, and months
        for month in range(1, 13):
            for day in range(7):
                for hour in range(24):
                    # Create features
                    features = {
                        'time_of_day': hour,
                        'day_of_week': day,
                        'month': month,
                        'demand_level': self._get_dummy_demand_level(hour),
                        'weather_score': np.random.uniform(0, 1),
                        'historical_avg_price': 0.15  # Base price
                    }
                    
                    # Calculate target price based on features
                    price = self._calculate_dummy_price(features)
                    
                    # Add to training data
                    X_train.append([features[feat] for feat in self.features])
                    y_train.append(price)
        
        # Convert to numpy arrays
        X_train = np.array(X_train)
        y_train = np.array(y_train)
        
        # Fit the model
        self.model.fit(X_train, y_train)
    
    def _get_dummy_demand_level(self, hour):
        if 9 <= hour <= 17:  # Peak hours
            return 0.8
        elif 6 <= hour <= 8 or 18 <= hour <= 20:  # Shoulder hours
            return 0.6
        else:  # Off-peak
            return 0.3
    
    def _calculate_dummy_price(self, features):
        # Base price
        price = 0.15
        
        # Adjust based on time of day
        if 9 <= features['time_of_day'] <= 17:  # Peak hours
            price *= 1.5
        elif 6 <= features['time_of_day'] <= 8 or 18 <= features['time_of_day'] <= 20:  # Shoulder hours
            price *= 1.2
        
        # Adjust based on demand
        price *= (1 + features['demand_level'])
        
        # Adjust based on weather
        price *= (1 + features['weather_score'])
        
        # Add some random variation
        price *= np.random.uniform(0.9, 1.1)
        
        return price
    
    def prepare_features(self, time, location, demand_level, weather_data):
        return {
            'time_of_day': time.hour,
            'day_of_week': time.weekday(),
            'month': time.month,
            'demand_level': demand_level,
            'weather_score': self._calculate_weather_score(weather_data),
            'historical_avg_price': self._get_historical_avg_price(time, location)
        }
    
    def predict_price(self, features):
        # Convert features to model input format
        X = self._format_features(features)
        # Return prediction
        return self.model.predict(X)[0]
    
    def _calculate_weather_score(self, weather_data):
        # Calculate weather score based on solar generation conditions
        # This is a simplified version
        score = 0
        score += weather_data.get('cloud_cover', 0) * -0.5
        score += weather_data.get('solar_radiation', 0) * 0.8
        return max(0, min(1, score))
    
    def _get_historical_avg_price(self, time, location):
        # This would connect to your database to get historical prices
        # For now, returning a dummy value
        return 0.15  # $0.15 per kWh as baseline
    
    def _format_features(self, features):
        # Convert features dictionary to numpy array for model input
        return np.array([[features[feat] for feat in self.features]]) 