import pandas as pd
from datetime import datetime

df_iea = pd.read_csv(r'K:\Github\GlobalPowerUpdate-Kow\data\#global_rf\iea\MES_122021.csv', encoding='shift-jis',
                     header=8)
df_iea = df_iea[df_iea['Balance'] == 'Net Electricity Production'].reset_index(drop=True)
df_iea = pd.pivot_table(df_iea, index=['Country', 'Time', 'Balance'], values='Value', columns='Product').reset_index()
df_iea['other'] = df_iea['Total Renewables (Geo, Solar, Wind, Other)'] - df_iea[['Solar', 'Hydro', 'Wind']].sum(axis=1)

df_iea = df_iea.rename(columns={'Coal, Peat and Manufactured Gases': 'coal',
                                'Natural Gas': 'gas',
                                'Oil and Petroleum Products': 'oil',
                                'Nuclear': 'nuclear',
                                'Hydro': 'hydro',
                                'Solar': 'solar',
                                'Wind': 'wind',
                                'Country': 'country'})

date = []
for t in df_iea['Time'].tolist():
    d = datetime.strptime(t, '%B %Y')
    date.append(d.strftime('%Y-%m-%d'))

df_iea['date'] = date
df_iea['date'] = pd.to_datetime(df_iea['date'])

df_iea['year'] = df_iea['date'].dt.year
df_iea['month'] = df_iea['date'].dt.month
df_iea = df_iea[
    ['country', 'year', 'month', 'coal', 'gas', 'oil', 'nuclear', 'hydro', 'solar', 'wind', 'other']].reset_index(
    drop=True)
df_iea.sort_values(['country', 'year', 'month']).to_csv(
    r'K:\Github\GlobalPowerUpdate-Kow\data\#global_rf\iea\iea_all.csv', index=False, encoding='utf_8_sig')

