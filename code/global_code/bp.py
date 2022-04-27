import pandas as pd

file_path = '../../../data/#global_rf/bp/'

file = file_path + 'bp-stats-review-2021-all-data.xlsx'
xl = pd.ExcelFile(file).sheet_names
sheet_list = [xl[i] for i, x in enumerate(xl) if x.find('TWh') != -1]
sheet_fossil = [xl[i] for i, x in enumerate(xl) if x.find('Gen from') != -1]
xl = sheet_list + sheet_fossil

df_all = pd.DataFrame()
for x in xl:
    df = pd.read_excel(file, sheet_name=x, header=2).rename(columns={'Terawatt-hours': 'country'})
    df = df.dropna(axis=0, how='all', thresh=2).reset_index(drop=True)  # 非空值小于2时删除行
    df = df.dropna(axis=1, how='all').iloc[:, :-3]  # 最后三列不要

    # 不要total asia pacific之后的行
    ignore_index = df[df['country'] == 'Total Asia Pacific'].index.tolist()[0]
    df = df[:ignore_index]

    #  去掉汇总的行
    df = df[~df['country'].str.contains('Total')].reset_index(drop=True)
    df = df[~df['country'].str.contains('Other')].reset_index(drop=True)

    df = df.set_index(['country']).stack().reset_index().rename(columns={'level_1': 'date', 0: 'value'})
    df['type'] = x
    df_all = pd.concat([df, df_all]).reset_index(drop=True)
df_all = pd.pivot_table(df_all, index=['country', 'date'], values='value', columns='type').reset_index()
df_all['other'] = df_all[['Elec Gen from Other', 'Geo Biomass Other - TWh']].sum(axis=1)

df_all = df_all.rename(columns={'Elec Gen from Coal': 'coal', 'Elec Gen from Gas': 'gas', 'Elec Gen from Oil': 'oil',
                                'Hydro Generation - TWh': 'hydro', 'Nuclear Generation - TWh': 'nuclear',
                                'Solar Generation - TWh': 'solar', 'Wind Generation - TWh': 'wind'})

df_all = df_all[['country', 'date', 'coal', 'gas', 'oil', 'nuclear', 'hydro', 'wind', 'solar', 'other']]
df_all.to_csv(file_path + 'bp_cleaned.csv', index=False, encoding='utf_8_sig')
