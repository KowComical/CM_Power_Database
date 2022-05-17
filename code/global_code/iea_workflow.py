import requests
import pandas as pd
import re
import os
from datetime import datetime
import sys

sys.dont_write_bytecode = True

file_path = './data/#global_rf/iea/'

url = 'https://www.iea.org/data-and-statistics/data-product/monthly-electricity-statistics'
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14) '
                         'AppleWebKit/605.1.15 (KHTML, like Gecko) '
                         'Version/12.0 Safari/605.1.15',
           'cookie': '_ga=GA1.2.517429514.1645169191; remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d'
                     '=eyJpdiI6IlF3UjByNTh6dTBZdHk4YWU0QjdyclE9PSIsInZhbHVlIjoiSDVxNE9HbkxRblwvWjMzV2JETjIrZW'
                     'Y4SGVVWVM1aDZ6S2pDNWZHajFtdXk0Snd1UWtpdUszQ1M2d0laREZoR1JJXC8zRkdCMEFkYUdjN25QMGFwY0'
                     'JiZWN4K2RZdklyZlBZWHpzWFZaUm1mWUprcU5nVE12QTFROFExbHJlMngzNlpDeDN6YnZaYkNJQmtjSkpNUGdpT'
                     'WlYY1NvWGtMZ0UxRHRNaTdOU3pHZmdQXC9VcmtEWmhKRXo1aDVvMXBhdWNoIiwibWFjIjoiMDNjZWYwMTkxNjF'
                     'kZTc0MmNkN2Y0NWIyYjI3Y2EyZjlmYzFhMDY3NDZlNTAwYTg4NzA1NzhjODlhZjNmMjA4MyJ9; _gid=GA1.2.173745561'
                     '3.1649130369; _gat_UA-30291846-5=1; '
                     'XSRF-TOKEN=eyJpdiI6IlNNZmthZ0VKbTJsQkhLZDFwenBsdkE9PSIsInZhbHVl'
                     'IjoiK1dDNXhLMkwwYXk1VEdQSmFYMEUwQ0trRTRUa08yU3BNXC9SNkFHY3pZR21ieERCREtjMDVUVEpVbXFsWkR0Mlci'
                     'LCJtYWMiOiIxMzExNGQ1ZDQ5YzI5NzA4NmY3NThjMTU1ZTVhNmUyODRjZTU1ZmFlNmU0NTBkNWNhZDgwNzQ1MDM3ZTgx'
                     'MGRmIn0=; '
                     'iea_session=eyJpdiI6ImVSMk80R252R1JQMVBSbUdTK0cyclE9PSIsInZhbHVlIjoidEdPcHpLOWJnUlpKdEJlT2ZTUF'
                     'hDekFUZXNKZ2ZmdzdyZWFQZ0VwVXBmc2FGZHdEcEwyWFBPeHk2OFlCKzhjNiIsIm1hYyI6IjdmMWE2OWZmNmM1MjBmMGU'
                     '1YmQ4YzJhOGIyNzcyYWU2MzM5M2IzZGEzZTBiNzE4ODYwY2I3NWI5YmZhMjI4ZTIifQ== '}
r = requests.get(url, headers=headers).text
path = re.compile(r'<a class="a-link a-link--accent a-link--plain " href="(?P<in_path>.*?)"', re.S)
path_name = 'https://www.iea.org' + path.findall(r)[0]

r = requests.get(path_name, headers=headers)
with open(os.path.join(file_path, 'iea_raw.csv'), 'wb') as f:
    f.write(r.content)

df_iea = pd.read_csv(os.path.join(file_path, 'iea_raw.csv'), encoding='shift-jis',
                     header=8)
df_iea = df_iea[df_iea['Balance'] == 'Net Electricity Production'].reset_index(drop=True)

date = []
for t in df_iea['Time'].tolist():
    d = datetime.strptime(t, '%b-%y')
    date.append(d.strftime('%Y-%m-%d'))

df_iea['date'] = date
df_iea['date'] = pd.to_datetime(df_iea['date'])

df_iea = pd.pivot_table(df_iea, index=['Country', 'date', 'Balance'], values='Value', columns='Product').reset_index()
df_iea = df_iea.rename(columns={'Coal, Peat and Manufactured Gases': 'coal',
                                'Natural Gas': 'gas',
                                'Oil and Petroleum Products': 'oil',
                                'Nuclear': 'nuclear',
                                'Hydro': 'hydro',
                                'Solar': 'solar',
                                'Wind': 'wind',
                                'Country': 'country'})
df_iea['year'] = df_iea['date'].dt.year
df_iea['month'] = df_iea['date'].dt.month

# 一般国家
df_normal = df_iea.copy()
df_normal['other'] = df_normal[['Combustible Renewables', 'Geothermal', 'Other Renewables']].sum(axis=1)

df_normal = df_normal[
    ['country', 'year', 'month', 'coal', 'gas', 'oil', 'nuclear', 'hydro', 'solar', 'wind', 'other']].reset_index(drop=True)
df_normal.fillna(0).sort_values(['country', 'year', 'month']).to_csv(os.path.join(file_path, 'iea_cleaned.csv'),
                                                                     index=False,
                                                                     encoding='utf_8_sig')

# China
df_china = df_iea.copy()
df_china['other'] = df_china['Total Combustible Fuels'] - df_china['coal'] - df_china['oil'] - df_china['gas']

df_china = df_china[
    ['country', 'year', 'month', 'coal', 'gas', 'oil', 'nuclear', 'hydro', 'solar', 'wind',
     'other']].reset_index(
    drop=True)
df_china.fillna(0).sort_values(['country', 'year', 'month']).to_csv(os.path.join(file_path, 'iea_china.csv'),
                                                                    index=False,
                                                                    encoding='utf_8_sig')
