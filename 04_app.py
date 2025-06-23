import streamlit as st
import pandas as pd
import os
import joblib
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder

st.set_page_config(page_title="Predicción de Bicis", layout="centered")

# Rutas
folder_path = r"C:\Final_Prog\Output"
modelo_path = os.path.join(folder_path, "modelo_xgboost_entrenado.joblib")

@st.cache_resource
def cargar_modelo_y_datos():
    if not os.path.exists(modelo_path):
        all_data = []
        for file in os.listdir(folder_path):
            if file.endswith('_cleaned.xlsx'):
                df = pd.read_excel(os.path.join(folder_path, file))
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['day'] = df['timestamp'].dt.day
                df['weekday'] = df['timestamp'].dt.weekday

                if df['longitude'].dtype == 'object':
                    df['longitude'] = df['longitude'].astype(str).str.replace(',', '.').astype(float)
                    df['latitude'] = df['latitude'].astype(str).str.replace(',', '.').astype(float)

                if 'station_id' not in df.columns:
                    le = LabelEncoder()
                    df['station_id'] = le.fit_transform(df['id'])

                all_data.append(df)

        df = pd.concat(all_data, ignore_index=True)
        X = df[['day', 'weekday', 'total_bases', 'longitude', 'latitude', 'station_id']]
        y = df['in_use']

        model = XGBRegressor(random_state=42, verbosity=0)
        model.fit(X, y)
        joblib.dump(model, modelo_path)
    else:
        model = joblib.load(modelo_path)
        all_data = []
        for file in os.listdir(folder_path):
            if file.endswith('_cleaned.xlsx'):
                df = pd.read_excel(os.path.join(folder_path, file))
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['day'] = df['timestamp'].dt.day
                df['weekday'] = df['timestamp'].dt.weekday
                all_data.append(df)
        df = pd.concat(all_data, ignore_index=True)

    return model, df

model, data = cargar_modelo_y_datos()

station_info = data.groupby('name').agg({
    'station_id': 'first',
    'total_bases': 'first',
}).reset_index()

mean_usage = data.groupby('name')['in_use'].mean().to_dict()

# Interfaz principal
st.title("🚲 Predicción de Bicis en Uso a las 14:00")
st.markdown("Selecciona una estación y la fecha para predecir la cantidad de bicicletas en uso:")

col1, col2 = st.columns(2)
with col1:
    day = st.selectbox("📆 Día del mes", list(range(1, 32)), index=14)
    weekday = st.selectbox("📅 Día de la semana",
                           options=[0, 1, 2, 3, 4, 5, 6],
                           format_func=lambda x: ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][x])
with col2:
    station_name = st.selectbox("🏙️ Estación", sorted(station_info['name'].unique()))

# Asignación automática del tipo de día
if weekday <= 4:
    tipo_dia = "Laborable"
else:
    tipo_dia = "Fin de semana"

station_data = station_info[station_info['name'] == station_name].iloc[0]
station_id = station_data['station_id']
total_bases = station_data['total_bases']

st.info(f"📍 ID estación: `{station_id}` | 🔧 Total de bases: `{total_bases}`")

# 🌦️ Expansión de condiciones externas (opcionales)
with st.expander("🧪 Ajustes avanzados (factores externos)"):
    st.markdown(f"🗓️ Tipo de día detectado automáticamente: **{tipo_dia}**")
    temperatura = st.selectbox("Temperatura", ["", "Normal (10-30°C)", "Menor a 10°C", "Mayor a 30°C"], index=0)
    lluvia = st.selectbox("Precipitaciones", ["", "Sin lluvia", "Lluvia leve", "Lluvia intensa"], index=0)
    estacion = st.selectbox("Estación del año", ["", "Primavera o verano", "Otoño o invierno"], index=0)

# Botón de predicción
if st.button("🔮 Predecir bicicletas en uso"):
    input_df = pd.DataFrame([{
        'day': day,
        'weekday': weekday,
        'total_bases': total_bases,
        'longitude': 0,
        'latitude': 0,
        'station_id': station_id
    }])

    pred = model.predict(input_df)[0]
    pred_base = int(round(pred))

    # Calcular ajustes solo si se ha seleccionado una opción
    factor = 1.0

    if tipo_dia == "Fin de semana":
        factor *= 0.90
    elif tipo_dia == "Laborable":
        factor *= 0.95

    if temperatura == "Menor a 10°C":
        factor *= 0.80
    elif temperatura == "Mayor a 30°C":
        factor *= 0.85

    if lluvia == "Lluvia leve":
        factor *= 0.75
    elif lluvia == "Lluvia intensa":
        factor *= 0.60

    if estacion == "Primavera o verano":
        factor *= 0.85
    elif estacion == "Otoño o invierno":
        factor *= 0.95

    pred_ajustada = int(round(pred_base * factor))
    disponibles = total_bases - pred_ajustada

    # Mostrar resultados
    media = mean_usage.get(station_name, 0)
    if pred_ajustada > total_bases:
        st.error("🚫 La estimación supera la capacidad de la estación.")
    else:
        estado = "✅ Uso habitual"
        if pred_ajustada < media * 0.5:
            estado = "⬇️ Menor uso de lo habitual"
        elif pred_ajustada > media * 1.2:
            estado = "🔥 Alta demanda"

        st.markdown("### 📊 Resultados")
        st.success(f"**Predicción base**: {pred_base} bicis en uso\n\n"
                   f"**Predicción ajustada**: {pred_ajustada} bicis en uso\n\n"
                   f"🅿️ Bicis disponibles: {disponibles}")
        st.markdown(f"**{estado}** *(Media histórica: {media:.1f} bicis en uso)*")

#abrir la aplicación: streamlit run 04_app.py