from datetime import datetime
import requests

class FeatureExtractor:
    def __init__(self, weather_api_key):
        self.weather_api_key = weather_api_key
    
    def get_weather_data(self, location):
        # Call weather API to get current conditions
        # This is a placeholder - you'll need to implement actual API calls
        api_url = f"https://api.weatherapi.com/v1/current.json?key={self.weather_api_key}&q={location}"
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                return {
                    'cloud_cover': data['current']['cloud'],
                    'solar_radiation': data['current']['uv'],
                    'temperature': data['current']['temp_c']
                }
        except Exception as e:
            print(f"Error fetching weather data: {e}")
        return {
            'cloud_cover': 0,
            'solar_radiation': 0,
            'temperature': 0
        }
    
    def get_demand_level(self, location, time):
        # This would normally query your system's current demand
        # Returning dummy data for now
        hour = time.hour
        if 9 <= hour <= 17:  # Peak hours
            return 0.8
        elif 6 <= hour <= 8 or 18 <= hour <= 20:  # Shoulder hours
            return 0.6
        else:  # Off-peak
            return 0.3 