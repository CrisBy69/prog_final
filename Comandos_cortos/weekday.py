import pandas as pd
from datetime import datetime

# Diccionario para los días en español
dias_semana = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo"
}

def agregar_columna_weekday(file_path):
    try:
        df = pd.read_excel(file_path)
        if "timestamp" not in df.columns:
            print(f"⚠️ El archivo no contiene columna 'timestamp': {file_path}")
            return
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
        df["weekday"] = df["timestamp"].dt.dayofweek.map(dias_semana)
        df.to_excel(file_path, index=False)
        print(f"✅ Procesado con weekday: {file_path}")
    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")

def procesar_archivos_excel():
    base_path = "C:/Final_Prog/Output/"
    for mes in range(1, 13):
        mes_str = str(mes).zfill(2)
        file_name = f"2022{mes_str}_filtrada.xlsx"
        file_path = base_path + file_name
        agregar_columna_weekday(file_path)

if __name__ == "__main__":
    procesar_archivos_excel()
