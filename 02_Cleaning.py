import pandas as pd
import os
from sklearn.preprocessing import LabelEncoder

# Ruta de la carpeta
folder_path = r"C:\Final_Prog\Output"

# Verifica si la carpeta existe
if not os.path.exists(folder_path):
    print(f"La carpeta no existe: {folder_path}")
else:
    print(f"Buscando archivos en: {folder_path}")

    archivos_excel = [f for f in os.listdir(folder_path) if f.endswith(".xlsx")]

    if not archivos_excel:
        print("No se encontraron archivos .xlsx en la carpeta.")
    else:
        print(f"Archivos encontrados: {archivos_excel}\n")

        for filename in archivos_excel:
            file_path = os.path.join(folder_path, filename)
            print(f"Procesando: {file_path}")

            try:
                # Leer archivo Excel
                df = pd.read_excel(file_path)

                # Convertir 'timestamp' a datetime
                df['timestamp'] = pd.to_datetime(df['timestamp'])

                # Separar características temporales
                df['day'] = df['timestamp'].dt.day
                df['weekday'] = df['timestamp'].dt.weekday  # 0=Lunes, 6=Domingo

                # Reemplazar comas en coordenadas si es necesario
                if df['longitude'].dtype == 'object':
                    df['longitude'] = df['longitude'].astype(str).str.replace(',', '.').astype(float)
                    df['latitude'] = df['latitude'].astype(str).str.replace(',', '.').astype(float)

                # Codificar ID de estación
                le = LabelEncoder()
                df['station_id'] = le.fit_transform(df['id'])

                # Guardar archivo con nuevo nombre
                name_part = os.path.splitext(filename)[0]
                cleaned_name = f"{name_part}_cleaned.xlsx"
                cleaned_path = os.path.join(folder_path, cleaned_name)

                df.to_excel(cleaned_path, index=False)
                print(f"Guardado: {cleaned_path}\n")

            except Exception as e:
                print(f"Error procesando {filename}: {e}")


