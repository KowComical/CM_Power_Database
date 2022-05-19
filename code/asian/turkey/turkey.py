import pandas as pd

from global_code.global_function import time_info, total_proc, check_col

file_path = 'K:\\Github\\PowerMonitor\\Data\\Asia\\Turkey\\'

df = pd.read_csv(file_path + 'Turkey_TEIAS_Hourly_2014.csv').rename(columns={'Date': 'date', 'Hour': 'hour'}).fillna(0)  # 将异常值改为0
# 能源改名与汇总
# Coal
coal_list = ['Asphaltite Coal', 'Imported Coal', 'Lignite', 'Hard Coal']
df['coal'] = df[coal_list].astype(float).sum(axis=1)
# Gas
gas_list = ['Natural Gas', 'LNG', 'LPG']
df['gas'] = df[gas_list].astype(float).sum(axis=1)
# Oil
oil_list = ['Fuel Oil', 'Naphtha', 'Dıesel Oil']
df['oil'] = df[oil_list].astype(float).sum(axis=1)
# Other
other_list = ['Waste', 'Biomass', 'Geothermal']
df['other'] = df[other_list].astype(float).sum(axis=1)
# Solar
solar_list = ['Solar']
df['solar'] = df[solar_list].astype(float).sum(axis=1)
# Wind
wind_list = ['Wind']
df['wind'] = df[wind_list].astype(float).sum(axis=1)
# Nuclear
nuclear_list = ['nukleer']
df['nuclear'] = df[nuclear_list].astype(float).sum(axis=1)
# Hydro
hydro_list = ['Hydro Storage', 'Run Of River']
df['hydro'] = df[hydro_list].astype(float).sum(axis=1)

df['date'] = pd.to_datetime(df['date'])
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['day'] = df['date'].dt.day
df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']].assign(), errors='coerce')
time_info(df, 'datetime')
total_proc(df, unit=False)
df = check_col(df, 'hourly')
print(df)
