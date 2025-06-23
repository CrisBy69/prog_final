import pandas as pd
from datetime import datetime

# Ruta a tu archivo
ruta_archivo = r"C:\Final_Prog\Output\202209_filtrada_cleaned.xlsx"

# Cargar el archivo Excel
df = pd.read_excel(ruta_archivo)

# Convertir la primera columna (columna 0) a tipo datetime
df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], dayfirst=True, errors='coerce')

# Función para cambiar el mes a enero
def cambiar_mes_a_enero(fecha):
    if pd.isnull(fecha):
        return fecha
    return fecha.replace(month=9)

# Aplicar la función
df.iloc[:, 0] = df.iloc[:, 0].apply(cambiar_mes_a_enero)

# Guardar el archivo modificado
ruta_salida = r"C:\Final_Prog\Output\202209_filtrada_modificada.xlsx"
df.to_excel(ruta_salida, index=False)

print("Archivo guardado como:", ruta_salida)
