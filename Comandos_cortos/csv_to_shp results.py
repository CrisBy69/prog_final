import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import os

# Ruta base
base_folder = r'C:\Embarcaciones\AIS_canarias\datos_ais'

for i in range(1, 10):
    folder_name = f'result{i}.json'
    folder_path = os.path.join(base_folder, folder_name)

    for csv_name in ['result_filtrado.csv', 'results_filtrado.csv']:
        csv_path = os.path.join(folder_path, csv_name)
        if os.path.exists(csv_path):
            break
    else:
        print(f"No se encontró ningún CSV en {folder_path}")
        continue

    try:
        df = pd.read_csv(csv_path)

        if 'latitude' not in df.columns or 'longitude' not in df.columns:
            print(f"Faltan columnas de coordenadas en {csv_path}")
            continue

        # CORREGIDO: intercambiamos los valores, ya que están invertidos
        geometry = [Point(lat, lon) for lat, lon in zip(df['latitude'], df['longitude'])]

        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

        shapefile_path = os.path.splitext(csv_path)[0] + '.shp'
        gdf.to_file(shapefile_path)

        print(f"Shapefile creado correctamente: {shapefile_path}")

    except Exception as e:
        print(f"Error procesando {csv_path}: {e}")

