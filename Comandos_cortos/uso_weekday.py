import pandas as pd
import matplotlib.pyplot as plt

# Ruta base donde están los archivos
base_path = "C:/Final_Prog/Output/"

# Días de la semana ordenados correctamente
dias_ordenados = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# Lista para acumular todos los datos
todos_los_datos = []

# Leer y combinar los 12 archivos
for mes in range(1, 13):
    mes_str = str(mes).zfill(2)
    file_path = f"{base_path}2022{mes_str}_filtrada.xlsx"
    try:
        df = pd.read_excel(file_path)
        if "in_use" in df.columns and "weekday" in df.columns:
            todos_los_datos.append(df[["weekday", "in_use"]])
        else:
            print(f"⚠️ Saltando {file_path}: falta 'weekday' o 'in_use'")
    except Exception as e:
        print(f"❌ Error leyendo {file_path}: {e}")

# Unir todos los datos en uno solo
df_total = pd.concat(todos_los_datos, ignore_index=True)

# Agrupar por día de la semana y sumar in_use
uso_total = df_total.groupby("weekday")["in_use"].sum()

# Reordenar según los días de la semana
uso_total = uso_total.reindex(dias_ordenados)

# Graficar
plt.figure(figsize=(10, 6))
plt.bar(uso_total.index, uso_total.values, color='coral')
plt.title("Uso total de bicicletas por día de la semana (2022)")
plt.xlabel("Día de la semana")
plt.ylabel("Bicicletas en uso (suma total)")
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
