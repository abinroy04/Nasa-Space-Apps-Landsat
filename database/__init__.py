"""
Database models and initialization for the Landsat Data Explorer application.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """User model for storing user information."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    searches = db.relationship('Search', backref='user', lazy=True)

class Search(db.Model):
    """Search model for storing search history."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    scene_id = db.Column(db.String(120))
    cloud_cover = db.Column(db.Float)

class PixelData(db.Model):
    """Model for storing processed Landsat pixel data."""
    id = db.Column(db.Integer, primary_key=True)
    search_id = db.Column(db.Integer, db.ForeignKey('search.id'), nullable=False)
    band_2 = db.Column(db.Float)  # Blue
    band_3 = db.Column(db.Float)  # Green
    band_4 = db.Column(db.Float)  # Red
    band_5 = db.Column(db.Float)  # NIR
    band_6 = db.Column(db.Float)  # SWIR1
    band_7 = db.Column(db.Float)  # SWIR2
    is_center = db.Column(db.Boolean, default=False)
    grid_position = db.Column(db.Integer)  # 0-8 for the 3x3 grid

def init_app(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()

# Database utility functions
def save_search(user_id, lat, lon, scene_id, cloud_cover):
    """Save a search to the database."""
    search = Search(
        user_id=user_id,
        latitude=lat,
        longitude=lon,
        scene_id=scene_id,
        cloud_cover=cloud_cover
    )
    db.session.add(search)
    db.session.commit()
    return search

def save_pixel_data(search_id, pixel_data, is_center=False, position=None):
    """Save pixel data to the database."""
    pixel = PixelData(
        search_id=search_id,
        band_2=pixel_data['B2'],
        band_3=pixel_data['B3'],
        band_4=pixel_data['B4'],
        band_5=pixel_data['B5'],
        band_6=pixel_data['B6'],
        band_7=pixel_data['B7'],
        is_center=is_center,
        grid_position=position
    )
    db.session.add(pixel)
    db.session.commit()
    return pixel

def get_user_searches(user_id, limit=10):
    """Get recent searches for a user."""
    return Search.query.filter_by(user_id=user_id).order_by(Search.timestamp.desc()).limit(limit).all()

def get_pixel_data(search_id):
    """Get all pixel data for a search."""
    return PixelData.query.filter_by(search_id=search_id).all()
