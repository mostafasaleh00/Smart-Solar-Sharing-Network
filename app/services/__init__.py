import os
from dotenv import load_dotenv
from .predictor import EnergyPricePredictor
from .features import FeatureExtractor

load_dotenv()

predictor = EnergyPricePredictor()
feature_extractor = FeatureExtractor(weather_api_key=os.getenv('WEATHER_API_KEY')) 