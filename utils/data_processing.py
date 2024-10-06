import numpy as np
import pandas as pd

def process_landsat_data(grid_data):
    processed_data = {
        'grid': [],
        'center_pixel': {},
        'metadata': {
            'band_names': ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2'],
            'wavelengths': [0.48, 0.56, 0.65, 0.86, 1.61, 2.2]
        }
    }
    
    # Process each pixel in the 3x3 grid
    for i in range(3):
        for j in range(3):
            pixel_data = {f'B{b}': grid_data[f'B{b}'][i, j] for b in range(2, 8)}
            processed_data['grid'].append(pixel_data)
            
            # Store center pixel data separately
            if i == 1 and j == 1:
                processed_data['center_pixel'] = pixel_data
    
    return processed_data

def create_csv(data):
    df = pd.DataFrame(data['grid'])
    center_df = pd.DataFrame([data['center_pixel']])
    
    return {
        'grid_csv': df.to_csv(index=False),
        'center_csv': center_df.to_csv(index=False)
    }