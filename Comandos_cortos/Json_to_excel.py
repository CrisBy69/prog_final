import json
import csv

input_file = "C:/Final_Prog/Input/202203.json"
output_file = "C:/Final_Prog/Output/estaciones_planas.csv"

rows = []

with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():  # evita líneas vacías
            record = json.loads(line)
            timestamp = record["_id"]
            for idx, station in enumerate(record["stations"]):
                flat_row = {
                    "timestamp": timestamp,
                    "entry_id": idx,
                    **station  # descompone el diccionario en columnas
                }
                rows.append(flat_row)

# Obtener todos los nombres de columnas (ordenados)
fieldnames = ["timestamp", "entry_id"] + list(rows[0].keys() - {"timestamp", "entry_id"})

with open(output_file, "w", encoding="utf-8", newline="") as f_out:
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ Archivo CSV exportado: {output_file}")

