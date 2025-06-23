import json
import logging
from pathlib import Path
from datetime import datetime

import click
import pandas as pd

# Configuración de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def json_to_excel(input_file: Path, output_excel: Path, output_csv_temp: Path) -> None:
    """
    Convierte un archivo JSON con registros anidados en un archivo Excel plano.

    Parameters
    ----------
    input_file : Path
        Ruta al archivo .json de entrada con estaciones y timestamps.
    output_excel : Path
        Ruta donde se guardará el Excel plano generado.
    output_csv_temp : Path
        Ruta donde se guardará un CSV temporal como respaldo.

    """
    rows = []

    logging.info(f"Leyendo archivo JSON: {input_file}")
    with input_file.open("r", encoding="utf-8") as f:
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
    df.to_excel(output_excel, index=False)
    df.to_csv(output_csv_temp, index=False, encoding="utf-8")

    logging.info(f"Exportado a Excel: {output_excel}")
    logging.info(f"Exportado a CSV temporal: {output_csv_temp}")


def filtrar_entradas_14h(input_excel: Path, output_excel: Path) -> None:
    """
    Filtra las filas de un archivo Excel donde la hora del timestamp sea 14h.

    Parameters
    ----------
    input_excel : Path
        Ruta al archivo Excel con datos planos.
    output_excel : Path
        Ruta donde se guardará el Excel filtrado por hora.

    """
    logging.info(f"Filtrando entradas con hora 14h en: {input_excel}")
    df = pd.read_excel(input_excel)
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df_filtrado = df[df['timestamp'].dt.hour == 14]
    df_filtrado.to_excel(output_excel, index=False)
    logging.info(f"Archivo filtrado guardado en: {output_excel}")


def exportar_columnas_reducidas(input_excel: Path, output_excel: Path) -> None:
    """
    Extrae columnas clave del Excel, calcula 'in_use' y exporta el resultado.

    Parameters
    ----------
    input_excel : Path
        Ruta al archivo Excel filtrado.
    output_excel : Path
        Ruta donde se guardará el archivo con columnas reducidas.

    """
    columnas_deseadas = [
        "timestamp", "id", "name", "total_bases", "free_bases",
        "number", "longitude", "latitude", "address", "dock_bikes"
    ]

    logging.info(f"Exportando columnas reducidas desde: {input_excel}")
    df = pd.read_excel(input_excel)

    if "total_bases" in df.columns and "free_bases" in df.columns:
        df["in_use"] = df["total_bases"] - df["free_bases"]
    else:
        logging.warning("No se encontraron las columnas necesarias para calcular 'in_use'.")
        df["in_use"] = None

    columnas_finales = []
    for col in columnas_deseadas:
        columnas_finales.append(col)
        if col == "free_bases":
            columnas_finales.append("in_use")

    columnas_presentes = [col for col in columnas_finales if col in df.columns]
    df_reducido = df[columnas_presentes]
    df_reducido.to_excel(output_excel, index=False)

    logging.info(f"Archivo reducido exportado a: {output_excel}")


def separar_por_comas(input_excel: Path, output_excel: Path) -> None:
    """
    Separa en nuevas columnas los valores que contienen comas en texto.

    Parameters
    ----------
    input_excel : Path
        Ruta al archivo Excel de entrada con posibles columnas de texto con comas.
    output_excel : Path
        Ruta donde se guardará el Excel con columnas separadas.

    """
    logging.info(f"Separando columnas por comas en: {input_excel}")
    df = pd.read_excel(input_excel)
    new_df = pd.DataFrame()

    for col in df.columns:
        if df[col].dtype == object and df[col].str.contains(",", na=False).any():
            split_cols = df[col].str.split(",", expand=True)
            split_cols.columns = [f"{col}_{i+1}" for i in range(split_cols.shape[1])]
            new_df = pd.concat([new_df, split_cols], axis=1)
        else:
            new_df[col] = df[col]

    new_df.to_excel(output_excel, index=False)
    logging.info(f"Archivo final con comas separadas exportado a: {output_excel}")


@click.command()
@click.option("--input_json", type=click.Path(exists=True, path_type=Path), required=True, help="Archivo JSON de entrada")
@click.option("--output_dir", type=click.Path(file_okay=False, path_type=Path), required=True, help="Directorio de salida")
def main(input_json: Path, output_dir: Path) -> None:
    """
    Pipeline principal para transformar datos de estaciones desde JSON hasta Excel limpio y separado.

    Parameters
    ----------
    input_json : Path
        Ruta del archivo .json con los datos originales.
    output_dir : Path
        Carpeta donde se guardarán todos los archivos intermedios y finales.

    """
    output_dir.mkdir(parents=True, exist_ok=True)

    excel_path = output_dir / "estaciones_planas.xlsx"
    csv_temp_path = output_dir / "estaciones_planas.csv"
    json_to_excel(input_json, excel_path, csv_temp_path)

    filtered_path = output_dir / "estaciones_filtradas_14h.xlsx"
    filtrar_entradas_14h(excel_path, filtered_path)

    reduced_path = output_dir / "estaciones_reducidas.xlsx"
    exportar_columnas_reducidas(filtered_path, reduced_path)

    final_output = output_dir / "estaciones_final_comas_separadas.xlsx"
    separar_por_comas(reduced_path, final_output)

    logging.info("Proceso completo finalizado.")


if __name__ == "__main__":
    main()

