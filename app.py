from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta
import os
from utils.landsat_api import LandsatAPI
from utils.data_processing import process_landsat_data, create_csv
from database import init_app, db, User, Search, save_search, save_pixel_data
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
init_app(app)

try:
    landsat_api = LandsatAPI(
        username=app.config['LANDSAT_USERNAME'],
        password=app.config['LANDSAT_PASSWORD']
    )
except ValueError as e:
    print(f"Error initializing LandsatAPI: {str(e)}")
    landsat_api = None
    
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/landsat/data', methods=['POST'])
def get_landsat_data():
    if landsat_api is None:
        return jsonify({'error': 'LandsatAPI is not initialized. Check your credentials.'}), 500

    data = request.json
    lat = data.get('latitude')
    lon = data.get('longitude')
    scene_id = data.get('scene_id')
    
    try:
        pixel_data = landsat_api.get_pixel_data(scene_id, lat, lon)
        processed_data = process_landsat_data(pixel_data)
        
        # Save to database - assuming user_id 1 for now
        search = save_search(user_id=1, lat=lat, lon=lon, 
                            scene_id=scene_id, 
                            cloud_cover=processed_data.get('metadata', {}).get('cloud_cover'))
        
        # Save pixel data
        for i, pixel in enumerate(processed_data['grid']):
            save_pixel_data(search.id, pixel, is_center=(i==4), position=i)
        
        return jsonify(processed_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/landsat/search', methods=['POST'])
def search_landsat_scenes():
    if landsat_api is None:
        print("Error: LandsatAPI is not initialized")
        return jsonify({'error': 'LandsatAPI is not initialized. Check your credentials.'}), 500

    data = request.json
    lat = data.get('latitude')
    lon = data.get('longitude')
    
    print(f"Searching for scenes at lat: {lat}, lon: {lon}")
    
    try:
        scenes = landsat_api.search_scenes(lat, lon)
        print(f"Found {len(scenes)} scenes")
        return jsonify(scenes)
    except Exception as e:
        print(f"Error searching for Landsat scenes: {str(e)}")
        return jsonify({'error': f'Error searching for Landsat scenes: {str(e)}'}), 500
    

if __name__ == '__main__':
    app.run(debug=True)