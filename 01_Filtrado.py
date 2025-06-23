import json
import pandas as pd
from datetime import datetime

def json_to_excel():
    input_file = "C:/Final_Prog/Input/202205.json"
    output_excel = "C:/Final_Prog/Output/202205_filtrada.xlsx"
    output_csv_temp = "C:/Final_Prog/Output/estaciones_planas.csv"
    rows = []

    with open(input_file, "r", encoding="latin-1") as f:
        for line in f:
            if line.strip():
                record = json.loads(line)
                timestamp = record["_id"]
                for idx, station in enumerate(record["stations"]):
                    flat_row = {
                        "timestamp": timestamp,
                        "entry_id": idx,
                        **station
                    }
                    rows.append(flat_row)

    df = pd.DataFrame(rows)

    # Convertir timestamp a datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')

    # Mapear días de la semana en español
    dias_semana = {
        0: "Lunes",
        1: "Martes",
        2: "Miércoles",
        3: "Jueves",
        4: "Viernes",
        5: "Sábado",
        6: "Domingo"
    }
    df["weekday"] = df["timestamp"].dt.dayofweek.map(dias_semana)

    df.to_excel(output_excel, index=False)
    df.to_csv(output_csv_temp, index=False, encoding="utf-8")
    print(f"✅ Archivos exportados:\n- Excel: {output_excel}\n- CSV temporal: {output_csv_temp}")

def filtrar_todas_entradas_a_las_14(input_excel, output_excel):
    df = pd.read_excel(input_excel)
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df_filtrado = df[df['timestamp'].dt.hour == 14]
    df_filtrado.to_excel(output_excel, index=False)
    print(f"✅ Archivo filtrado guardado con todas las entradas de las 14h: {output_excel}")

def exportar_columnas_reducidas(input_excel, output_excel):
    columnas_deseadas = [
        "timestamp", "weekday", "id", "name", "total_bases", "free_bases",
        "number", "longitude", "latitude", "address", "dock_bikes"
    ]

    df = pd.read_excel(input_excel)

    # Asegurarse de que las columnas necesarias existen para calcular in_use
    if "total_bases" in df.columns and "free_bases" in df.columns:
        df["in_use"] = df["total_bases"] - df["free_bases"]
    else:
        print("❌ No se encontraron las columnas necesarias para calcular 'in_use'.")
        df["in_use"] = None

    # Insertar 'in_use' justo después de 'free_bases'
    columnas_finales = []
    for col in columnas_deseadas:
        columnas_finales.append(col)
        if col == "free_bases":
            columnas_finales.append("in_use")

    columnas_presentes = [col for col in columnas_finales if col in df.columns]
    df_reducido = df[columnas_presentes]

    df_reducido.to_excel(output_excel, index=False)
    print(f"✅ Archivo Excel con columnas reducidas exportado: {output_excel}")

def separar_por_comas_excel(input_file, output_file):
    df = pd.read_excel(input_file)
    new_df = pd.DataFrame()

    for col in df.columns:
        if df[col].dtype == object and df[col].astype(str).str.contains(",", na=False).any():
            split_cols = df[col].astype(str).str.split(",", expand=True)
            split_cols.columns = [f"{col}_{i+1}" for i in range(split_cols.shape[1])]
            new_df = pd.concat([new_df, split_cols], axis=1)
        else:
            new_df[col] = df[col]

    new_df.to_excel(output_file, index=False)
    print(f"✅ Archivo Excel con columnas separadas exportado: {output_file}")

if __name__ == "__main__":
    json_to_excel()
    input_excel = "C:/Final_Prog/Output/202205_filtrada.xlsx"
    filtered_excel = "C:/Final_Prog/Output/estaciones_filtradas_14h.xlsx"
    filtrar_todas_entradas_a_las_14(input_excel, filtered_excel)
    reduced_excel = "C:/Final_Prog/Output/estaciones_reducidas.xlsx"
    exportar_columnas_reducidas(filtered_excel, reduced_excel)
    output_excel_final = "C:/Final_Prog/Output/202205_filtrada.xlsx"
    separar_por_comas_excel(reduced_excel, output_excel_final)






