import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///landsat.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LANDSAT_USERNAME = os.getenv('LANDSAT_USERNAME') 
    LANDSAT_PASSWORD = os.getenv('LANDSAT_PASSWORD')