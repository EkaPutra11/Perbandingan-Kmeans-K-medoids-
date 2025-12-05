from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.models import db


def create_app():
    app = Flask(__name__)

    # Set secret key for sessions
    app.secret_key = 'your-secret-key-change-this-in-production'

    # SQLAlchemy configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/db_penjualan_arwana'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # Import models so they are registered with SQLAlchemy
    from app.models import (
        Penjualan, 
        KMeansResult, 
        KMedoidsResult,
        KMeansClusterDetail,
        KMedoidsClusterDetail
    )

    # Create database tables if needed
    with app.app_context():
        pass  # Tables already exist in database

    # import blueprint dari routes
    from app.routes import main
    app.register_blueprint(main)

    return app
