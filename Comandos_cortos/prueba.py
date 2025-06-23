import pandas as pd

# Abre el archivo Excel
df = pd.read_excel("C:/Final_Prog/Output/estaciones_limpias.xlsx")

# Muestra las primeras filas
print(df.head())

# Opcional: ver las columnas
print(df.columns)

# Ver tipos de datos
print(df.dtypes)
