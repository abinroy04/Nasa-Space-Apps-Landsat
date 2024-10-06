from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer
import rasterio
import numpy as np
from datetime import datetime, timedelta
from landsatxplore.errors import EarthExplorerError
import atexit

class LandsatAPI:
    def __init__(self, username, password):
        try:
            self.api = API(username, password)
            self.ee = EarthExplorer(username, password)
            atexit.register(self.cleanup)
        except EarthExplorerError as e:
            raise ValueError(f"Authentication failed: {str(e)}. Please check your username and password.")
    
    def search_scenes(self, lat, lon, start_date=None, end_date=None):
        try:
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
        
            print(f"Searching for scenes: lat={lat}, lon={lon}, start_date={start_date}, end_date={end_date}")
        
            scenes = self.api.search(
                dataset='landsat_ot_c2_l2',
                latitude=lat,
                longitude=lon,
                start_date=start_date,
                end_date=end_date,
                max_cloud_cover=50
            )
        
            print(f"API returned {len(scenes)} scenes")

            return [{'scene_id': scene['entity_id'],
                    'cloud_cover': scene['cloud_cover'],
                    'date': scene['acquisition_date']} for scene in scenes]
    
        except Exception as e:
            print(f"Error in search_scenes: {str(e)}")
            raise
    
    def cleanup(self):
        try:
            if hasattr(self, 'api'):
                self.api.logout()
            if hasattr(self, 'ee'):
                self.ee.logout()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

    def __del__(self):
        # This method is now empty as we're using atexit for cleanup
        pass
