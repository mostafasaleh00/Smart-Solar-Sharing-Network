from flask import Flask
from config import Config
from app.extensions import login_manager
from app.mock_data import create_mock_data

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register blueprints
    from app.routes import auth, energy, predictions, dashboard
    app.register_blueprint(auth.bp)
    app.register_blueprint(energy.bp)
    app.register_blueprint(predictions.bp)
    app.register_blueprint(dashboard.bp)

    # Create mock data
    with app.app_context():
        create_mock_data()

    return app 