from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
import numpy as np
from datetime import datetime, timedelta
import joblib
import os
import tensorflow as tf

bp = Blueprint('predictions', __name__)

def generate_mock_weather_data():
    """Generate mock weather data for testing"""
    # Generate 24 hours of mock data
    hours = 24
    current_time = datetime.now()
    
    # Generate temperature data (simulating daily cycle)
    base_temp = 25  # Base temperature in Celsius
    temp_variation = 5  # Temperature variation
    temperatures = [
        base_temp + temp_variation * np.sin(2 * np.pi * (i % 24) / 24)
        for i in range(hours)
    ]
    
    # Generate irradiance data (simulating daily cycle with some randomness)
    base_irradiance = 800  # Base irradiance in W/m²
    irradiance_variation = 200  # Irradiance variation
    irradiances = [
        max(0, base_irradiance + irradiance_variation * np.sin(2 * np.pi * (i % 24) / 24) + np.random.normal(0, 50))
        for i in range(hours)
    ]
    
    # Generate timestamps
    timestamps = [
        (current_time + timedelta(hours=i)).strftime('%Y-%m-%d %H:%M')
        for i in range(hours)
    ]
    
    return list(zip(timestamps, temperatures, irradiances))

@bp.route('/solar-predictions')
@login_required
def solar_predictions():
    """Display solar energy predictions page"""
    if current_user.role != 'producer':
        return render_template('error.html', message="Only producers can access solar predictions")
    
    # Generate mock weather data
    weather_data = generate_mock_weather_data()
    
    # Load the model and scalers
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
    try:
        # Load scalers
        scaler_x = joblib.load(os.path.join(models_dir, 'scaler_X.pkl'))
        scaler_y = joblib.load(os.path.join(models_dir, 'scaler_y.pkl'))
        
        # Load the model
        model = tf.keras.models.load_model(os.path.join(models_dir, 'meta_model.h5'))
        
        # Make predictions
        predictions = []
        for timestamp, temp, irrad in weather_data:
            # Prepare input data
            input_data = np.array([[temp, irrad]])
            
            # Scale input data
            scaled_input = scaler_x.transform(input_data)
            
            # Make prediction
            scaled_output = model.predict(scaled_input, verbose=0)
            
            # Inverse transform the prediction
            predicted_output = scaler_y.inverse_transform(scaled_output)[0][0]
            
            predictions.append({
                'timestamp': timestamp,
                'temperature': round(temp, 1),
                'irradiance': round(irrad, 1),
                'predicted_output': round(max(0, predicted_output), 2)
            })
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        # Fallback to simple model if loading fails
        predictions = []
        for timestamp, temp, irrad in weather_data:
            # Simple physical model for fallback
            panel_efficiency = 0.15  # 15% efficiency
            panel_area = 1.6  # 1.6 m²
            predicted_output = panel_efficiency * panel_area * irrad * (1 - 0.004 * (temp - 25))
            
            predictions.append({
                'timestamp': timestamp,
                'temperature': round(temp, 1),
                'irradiance': round(irrad, 1),
                'predicted_output': round(max(0, predicted_output), 2)
            })
    
    return render_template('predictions/solar.html', predictions=predictions)

@bp.route('/api/solar-predictions')
@login_required
def api_solar_predictions():
    """API endpoint for solar predictions"""
    if current_user.role != 'producer':
        return jsonify({'error': 'Only producers can access solar predictions'}), 403
    
    weather_data = generate_mock_weather_data()
    
    # Load the model and scalers
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
    try:
        # Load scalers
        scaler_x = joblib.load(os.path.join(models_dir, 'scaler_X.pkl'))
        scaler_y = joblib.load(os.path.join(models_dir, 'scaler_y.pkl'))
        
        # Load the model
        model = tf.keras.models.load_model(os.path.join(models_dir, 'meta_model.h5'))
        
        predictions = []
        for timestamp, temp, irrad in weather_data:
            # Prepare and scale input data
            input_data = np.array([[temp, irrad]])
            scaled_input = scaler_x.transform(input_data)
            
            # Make prediction
            scaled_output = model.predict(scaled_input, verbose=0)
            predicted_output = scaler_y.inverse_transform(scaled_output)[0][0]
            
            predictions.append({
                'timestamp': timestamp,
                'temperature': round(temp, 1),
                'irradiance': round(irrad, 1),
                'predicted_output': round(max(0, predicted_output), 2)
            })
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        # Fallback to simple model
        predictions = []
        for timestamp, temp, irrad in weather_data:
            panel_efficiency = 0.15
            panel_area = 1.6
            predicted_output = panel_efficiency * panel_area * irrad * (1 - 0.004 * (temp - 25))
            predictions.append({
                'timestamp': timestamp,
                'temperature': round(temp, 1),
                'irradiance': round(irrad, 1),
                'predicted_output': round(max(0, predicted_output), 2)
            })
    
    return jsonify(predictions) 