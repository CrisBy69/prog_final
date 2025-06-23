import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

# Ruta de la carpeta
folder_path = r"C:\Final_Prog\Output"

# Combinar todos los archivos .xlsx que contengan '_cleaned'
all_data = []

for file in os.listdir(folder_path):
    if file.endswith('_cleaned.xlsx'):
        path = os.path.join(folder_path, file)
        df = pd.read_excel(path)

        # Asegurar tipos correctos si vienen mal
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['day'] = df['timestamp'].dt.day
        df['weekday'] = df['timestamp'].dt.weekday

        if df['longitude'].dtype == 'object':
            df['longitude'] = df['longitude'].astype(str).str.replace(',', '.').astype(float)
            df['latitude'] = df['latitude'].astype(str).str.replace(',', '.').astype(float)

        # Codificar IDs si no está hecho
        if 'station_id' not in df.columns:
            le = LabelEncoder()
            df['station_id'] = le.fit_transform(df['id'])

        all_data.append(df)

# Unir todos los DataFrames
full_df = pd.concat(all_data, ignore_index=True)

# Variables predictoras y objetivo
features = ['day', 'weekday', 'total_bases', 'longitude', 'latitude', 'station_id']
X = full_df[features]
y = full_df['in_use']

# Dividir en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entrenar modelos
models = {
    'Random Forest': RandomForestRegressor(random_state=42),
    'Neural Network': MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42),
    'XGBoost': XGBRegressor(random_state=42, verbosity=0)
}

results = {}

for name, model in models.items():
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    results[name] = {'MSE': mse, 'R2': r2}

# Mostrar resultados en consola
print("\nResultados comparativos:")
for model_name, metrics in results.items():
    print(f"{model_name}: MSE = {metrics['MSE']:.2f}, R2 = {metrics['R2']:.2f}")

# Graficar comparación
labels = list(results.keys())
mse_values = [results[m]['MSE'] for m in labels]
r2_values = [results[m]['R2'] for m in labels]

plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.bar(labels, mse_values, color='skyblue')
plt.title("MSE por modelo")
plt.ylabel("Mean Squared Error")

plt.subplot(1, 2, 2)
plt.bar(labels, r2_values, color='lightgreen')
plt.title("R2 por modelo")
plt.ylabel("R-squared")

plt.tight_layout()
plt.show()


