import pandas as pd
import os
from datetime import datetime
import requests
import global_function as af  # 所有的function
import sys

sys.dont_write_bytecode = True

# ###########################################################################################################################################
global_path = './data/'


# ################################################################US#########################################################################
def us():
    import sys
    sys.dont_write_bytecode = True

    file_path = os.path.join(global_path, 'n_america', 'us')
    in_path = os.path.join(file_path, 'raw')
    out_path_cleaned = af.create_folder(file_path, 'cleaned')
    out_path_simulated = af.create_folder(file_path, 'simulated')
    in_path_file = os.path.join(in_path, '%s.csv' % 'raw')
    in_path_file_2016 = os.path.join(in_path, '%s.csv' % 'US_daily_generation-2016-0.2_20201219')
    in_path_file_2017 = os.path.join(in_path, '%s.csv' % 'US_daily_generation-2017-0.2_20201219')
    in_path_file_2018 = os.path.join(in_path, '%s.csv' % 'US_daily_generation-2018-0.3_20210521')
    # ########################################raw-cleaned#################################################
    df = pd.read_csv(in_path_file)
    df = af.check_date(df, 'datetime', 'h')  # 检查是否有missing date
    df['unit'] = 'Mwh'  # 单位
    af.time_info(df, 'datetime')  # 日期
    # cleaned-simulated 准备工作
    for y in df['year'].drop_duplicates().tolist():
        df_cleaned = df[df['year'] == y].reset_index(drop=True)
        df_cleaned.to_csv(os.path.join(out_path_cleaned, 'us-generation-%s-cleaned.csv' % y), index=False,
                          encoding='utf_8_sig')

        # ##########################cleaned-simulated#################################
        # hourly
        out_path_simulated_yearly = af.create_folder(out_path_simulated, str(y))
        af.agg(df_cleaned, 'datetime', out_path_simulated_yearly,
               'hourly', name='US_hourly_generation-' + str(y) + '.csv', folder=False, unit=False)

    # 填补daily数据中缺失的年份
    df_daily = df.set_index('datetime').resample('d').sum().reset_index().drop(columns=['hour'])
    af.time_info(df_daily, 'datetime')
    af.total_proc(df_daily, unit=True)
    df_16 = pd.read_csv(in_path_file_2016)
    df_17 = pd.read_csv(in_path_file_2017)
    df_18 = pd.read_csv(in_path_file_2018)
    df_part_all = pd.concat([df_16, df_17, df_18])
    df_part_all = df_part_all.rename(columns={'date': 'datetime'}).drop(columns=['season'])
    af.time_info(df_part_all, 'datetime')
    df_daily = df_daily[df_daily['year'] != 2018].reset_index(drop=True)
    df_all = pd.concat([df_part_all, df_daily]).reset_index(drop=True)
    for y in df_all['year'].drop_duplicates().tolist():
        # daily
        df_daily = df_all[df_all['year'] == y].reset_index(drop=True)
        df_monthly = df_daily.copy()
        out_path_simulated_yearly = af.create_folder(out_path_simulated, str(y))
        af.agg(df_daily, 'datetime', out_path_simulated_yearly,
               'daily', name='US_daily_generation-' + str(y) + '.csv', folder=False, unit=False)
        # monthly
        af.time_info(df_monthly, 'datetime')
        df_monthly = df_monthly.set_index('datetime').resample('m').sum().reset_index()
        out_path_simulated_yearly = af.create_folder(out_path_simulated, str(y))
        af.agg(df_monthly, 'datetime', out_path_simulated_yearly,
               'monthly', name='US_monthly_generation-' + str(y) + '.csv', folder=False, unit=False)


# #############################################################India#########################################################################
def india():
    import sys
    sys.dont_write_bytecode = True

    file_path = os.path.join(global_path, 'asia', 'india')
    in_path = os.path.join(file_path, 'raw')
    out_path_cleaned = af.create_folder(file_path, 'cleaned')
    out_path_simulated = af.create_folder(file_path, 'simulated')
    in_path_file = os.path.join(in_path, '%s.csv' % 'India_POSOCO_Daily')
    in_path_file_thermal = os.path.join(in_path, '%s.csv' % 'India_POSOCO_Daily_Thermal')
    # ##################################################raw-cleaned########################################################
    # 将两个表格合并
    df = pd.read_csv(in_path_file)
    df['coal'] = df['Coal'] + df['Lignite']
    df = df.drop(columns=['Coal', 'Lignite'])
    df_thermal = pd.read_csv(in_path_file_thermal).rename(columns={'Thermal (Coal & Lignite)': 'coal'})
    df_all = pd.concat([df_thermal, df])
    df_all['date'] = pd.to_datetime(df_all['date']).astype(str)
    df_all = df_all.sort_values(by='date').reset_index(drop=True)
    # 删除重复行
    df_all = df_all.drop_duplicates()

    df_all['date'] = pd.to_datetime(df_all['date']).astype(str)
    # 有些coal没有值
    df_all['coal'] = df_all['Total'] - df_all[
        ['Hydro', 'Nuclear', 'Gas, Naptha & Diesel', 'RES (Wind, Solar, Biomass & Others)']].sum(axis=1)

    # 找出重复的日期值
    duplicated_date = df_all[df_all.duplicated(['date'])]['date'].tolist()
    # 将重复日期修改
    for x in duplicated_date:
        my_yes_time = af.time_b_a(x, -1)
        if not df_all[df_all['date'] == my_yes_time].empty:  # 如果前一天有值
            my_yes_time = af.time_b_a(x, +1)
            if df_all[df_all['date'] == my_yes_time].empty:  # 如果后一天没有值 则将这一天改为后一天
                index_back = df_all[df_all['date'] == x].index.tolist()
                df_all.loc[index_back[1], 'date'] = my_yes_time
        else:  # 如果前一天没有值 则将这一天改为前一天
            index_front = df_all[df_all['date'] == x].index.tolist()
            df_all.loc[index_front[0], 'date'] = my_yes_time

    # 2017-05-26这一天单独有个值 剩余就是一直到2017年10月左右
    df_all['date'] = pd.to_datetime(df_all['date'])
    df_all = df_all[df_all['date'] != '2017-05-26'].reset_index(drop=True)

    # 查找缺失日期并填充
    df_all = af.check_date(df_all, 'date', 'd')
    df_all['date'] = pd.to_datetime(df_all['date'], format='%Y-%m-%d')
    af.time_info(df_all, 'date')  # 添加各种日期数据和单位
    df_all['unit'] = 'MU'
    df_all.columns = df_all.columns.map(lambda k: k.lower())  # 全小写
    df_all = df_all.rename(
        columns={'gas, naptha & diesel': 'gas_naptha_diesel', 'res (wind, solar, biomass & others)': 'res'}).drop(
        columns=['hour'])  # 修改列名细节
    # 输出没填充缺失值的
    year_list = df_all['year'].drop_duplicates().tolist()
    for x in year_list:
        df_all[df_all['year'] == x].to_csv(os.path.join(out_path_cleaned, 'india-generation-%s-cleaned.csv' % x),
                                           index=False, encoding='utf_8_sig')

    # 处理缺失值并输出
    for x in df_all.columns.tolist():
        if df_all[x].dtype == float:
            df_all[x] = df_all[x].fillna(df_all[x].interpolate())
    for x in year_list:
        df_temp = df_all[df_all['year'] == x].reset_index(drop=True)
        df_temp.to_csv(os.path.join(out_path_cleaned, 'india-generation-%s-cleaned-filled.csv' % x), index=False,
                       encoding='utf_8_sig')

    ####################################################################
    # 处理monthly数据做后续备用
    df_iea = af.iea_data('india')
    df_new_result = pd.DataFrame()
    # #########################################cleaned-simulated###################################################
    for y in df_all['year'].drop_duplicates().tolist():
        df_iea_temp = df_iea[df_iea['year'] == y].reset_index(drop=True)
        df_temp = df_all[df_all['year'] == y].reset_index(drop=True)
        month_range = df_iea_temp['month'].drop_duplicates().tolist()
        if month_range != 12:
            df_iea_temp = df_iea[df_iea['year'] == y - 1].reset_index(drop=True)
            df_temp = df_all[df_all['year'] == y].reset_index(drop=True)
            month_range = df_iea_temp['month'].drop_duplicates().tolist()
        for i in month_range:
            df_temp_monthly = df_temp[df_temp['month'] == i].reset_index(drop=True)

            gas_value = df_iea_temp[df_iea_temp['month'] == i]['gas'].tolist()[0]
            oil_value = df_iea_temp[df_iea_temp['month'] == i]['oil'].tolist()[0]
            df_temp_monthly['gas'] = df_temp_monthly['gas_naptha_diesel'] * (gas_value / (gas_value + oil_value))
            df_temp_monthly['oil'] = df_temp_monthly['gas_naptha_diesel'] * (oil_value / (gas_value + oil_value))

            solar_value = df_iea_temp[df_iea_temp['month'] == i]['solar'].tolist()[0]
            wind_value = df_iea_temp[df_iea_temp['month'] == i]['wind'].tolist()[0]
            other_value = df_iea_temp[df_iea_temp['month'] == i]['other'].tolist()[0]
            df_temp_monthly['solar'] = df_temp_monthly['res'] * (solar_value / (solar_value + wind_value + other_value))
            df_temp_monthly['wind'] = df_temp_monthly['res'] * (wind_value / (solar_value + wind_value + other_value))
            df_temp_monthly['other'] = df_temp_monthly['res'] * (other_value / (solar_value + wind_value + other_value))
            df_new_result = pd.concat([df_new_result, df_temp_monthly]).reset_index(drop=True)
    df_all = df_new_result.copy()

    for t in df_all.index.tolist():
        if pd.isna(df_all['coal'].iloc[t]) is True and pd.isna(df_all['lignite'].iloc[t]) is False:
            df_all.loc[t, 'coal'] = df_all.loc[t, 'lignite']

    # 生成缺失的日期
    start_range = str(min(df_iea['year'])) + '-01-01'  # 从monthly里面最小年份开始
    end_range = min(df_all['date'])  # 从monthly里面最小年份开始一直到df_all里最小日期截至
    date_range = pd.date_range(start=start_range, end=end_range, freq='d')[:-1]  # 去掉最后一天

    for x in date_range:
        df_all = af.insert_date(df_all, 'date', x)

    df_all = af.check_date(df_all, 'date', 'd')  # 填补缺失的日期
    total_list = ['coal', 'gas', 'oil', 'nuclear', 'hydro', 'wind', 'solar', 'other']
    df_all[total_list] = df_all[total_list].astype(float)
    df_all[total_list] = df_all[total_list].interpolate()

    # 填充缺失值
    df_all = af.fill_null(df_all, 'india', 'date', 'daily')
    df_all[total_list] = df_all[total_list] * 1000

    for y in df_all['year'].drop_duplicates().tolist():
        df_temp = df_all[df_all['year'] == y]
        df_daily = df_temp.copy()
        df_monthly = df_temp.copy()
        out_path_simulated_yearly = af.create_folder(out_path_simulated, str(y))
        # daily
        af.agg(df_daily, 'date', out_path_simulated_yearly, 'daily', name='India_daily_generation-' + str(y) + '.csv',
               folder=False, unit=False)
        # monthly
        df_monthly = df_monthly.set_index('date').resample('m').sum().reset_index()
        af.agg(df_monthly, 'date', out_path_simulated_yearly, 'monthly',
               name='India_monthly_generation-' + str(y) + '.csv', folder=False, unit=False)


# ##############################################################Brazil###########################################################################
def brazil():
    import sys
    sys.dont_write_bytecode = True
    # ##############################################################路径#######################################################
    file_path = os.path.join(global_path, 's_america', 'brazil')
    in_path = os.path.join(file_path, 'raw')
    out_path_cleaned = af.create_folder(file_path, 'cleaned')
    out_path_simulated = af.create_folder(file_path, 'simulated')
    in_path_file = os.path.join(in_path, 'Brazil_ONS_Hourly.csv')
    # #############################################################Raw-Cleaned########################################################
    df = pd.read_csv(in_path_file).rename(columns={'Date': 'datetime'})
    df = af.check_date(df, 'datetime', 'h')  # 判断是否有缺失日期
    af.time_info(df, 'datetime')  # 填充时间列

    # cleaned 输出
    for y in df['year'].drop_duplicates().tolist():
        df_cleaned = df[df['year'] == y]
        df_cleaned.to_csv(os.path.join(out_path_cleaned, 'brazil-generation-%s-cleaned.csv' % y), index=False)

        # #######################################################cleaned-simulated######################################
        df_hourly = df[df['year'] == y].reset_index(drop=True).fillna(0)
        df_hourly['Thermal.Gás.natural'] = df_hourly['Thermal:Gás natural'].astype(float) + df_hourly[
            'Thermal:Gás Natural'].astype(float)
        df_hourly = df_hourly.drop(columns=['Thermal:Gás Natural'])
        df_hourly.columns = df_hourly.columns.map(lambda x: x.lower())  # 全小写
        df_col = df_hourly.columns.tolist()
        coal_list = [df_col[i] for i, x in enumerate(df_col) if x.find('carv') != -1]
        gas_list = [df_col[i] for i, x in enumerate(df_col) if x.find('gás') != -1]
        oil_list = [df_col[i] for i, x in enumerate(df_col) if x.find('leo') != -1]
        other_list = ['thermal:biomassa', 'thermal:resíduos industriais']
        df_hourly['coal'] = df_hourly[coal_list].astype(float).sum(axis=1)
        df_hourly['gas'] = df_hourly[gas_list].astype(float).sum(axis=1)
        df_hourly['oil'] = df_hourly[oil_list].astype(float).sum(axis=1)
        type_list = ['nuclear', 'hydro', 'wind', 'solar']
        df_hourly[type_list] = df_hourly[type_list].astype(float)
        df_hourly['other'] = df_hourly[other_list].astype(float).sum(axis=1)
        df_col = df_hourly.columns.tolist()
        all_list = [df_col[i] for i, x in enumerate(df_col) if not x.find('thermal') != -1]
        df_hourly = df_hourly[all_list].groupby(all_list).sum().reset_index()
        df_daily = df_hourly.copy()
        df_monthly = df_hourly.copy()
        out_path_simulated_yearly = af.create_folder(out_path_simulated, str(y))
        # hourly
        af.agg(df_hourly, 'datetime', out_path_simulated_yearly, 'hourly',
               name='Brazil_hourly_generation-' + str(y) + '.csv', folder=False, unit=False)
        # #############################################################daily#########################################
        # daily
        df_daily = df_daily.set_index('datetime').resample('d').sum().reset_index()
        af.agg(df_daily, 'datetime', out_path_simulated_yearly, 'daily',
               name='Brazil_daily_generation-' + str(y) + '.csv', folder=False, unit=False)
        # #############################################monthly###############################################
        # monthly
        df_monthly = df_monthly.set_index('datetime').resample('m').sum().reset_index()
        af.agg(df_monthly, 'datetime', out_path_simulated_yearly, 'monthly',
               name='Brazil_monthly_generation-' + str(y) + '.csv', folder=False, unit=False)


# ################################################################EU###########################################################################
def eu():
    import sys
    sys.dont_write_bytecode = True
    file_path = os.path.join(global_path, 'europe', 'eu27_uk')
    in_path_entsoe = os.path.join(file_path, 'raw', 'entsoe')
    out_path_cleaned = af.create_folder(file_path, 'cleaned')
    out_path_simulated = af.create_folder(file_path, 'simulated')
    in_path_bmrs_file = os.path.join(file_path, 'raw', 'uk-BMRS', 'UK_BMRS_Hourly.csv')

    end_year = str(datetime.now().year)  # 数据截至年
    end_month = str(datetime.now().month).zfill(2)  # 数据截至年
    end_day = str(datetime.now().day).zfill(2)  # 数据截至年
    now = end_year + '-' + end_month + '-' + end_day
    # ###############################################################################################################################
    coal_list = ['Fossil Brown coal/Lignite  - Actual Aggregated [MW]',
                 'Fossil Coal-derived gas  - Actual Aggregated [MW]',
                 'Fossil Hard coal  - Actual Aggregated [MW]',
                 'Fossil Peat  - Actual Aggregated [MW]']
    gas_list = ['Fossil Gas  - Actual Aggregated [MW]']
    oil_list = ['Fossil Oil  - Actual Aggregated [MW]',
                'Fossil Oil shale  - Actual Aggregated [MW]']
    other_list = ['Biomass  - Actual Aggregated [MW]',
                  'Geothermal  - Actual Aggregated [MW]',
                  'Other  - Actual Aggregated [MW]',
                  'Other renewable  - Actual Aggregated [MW]',
                  'Waste  - Actual Aggregated [MW]']
    hydro_list = ['Hydro Pumped Storage  - Actual Aggregated [MW]',
                  'Hydro Pumped Storage  - Actual Consumption [MW]',
                  'Hydro Run-of-river and poundage  - Actual Aggregated [MW]',
                  'Hydro Water Reservoir  - Actual Aggregated [MW]']
    wind_list = ['Wind Offshore  - Actual Aggregated [MW]',
                 'Wind Onshore  - Actual Aggregated [MW]']
    # ################################################################################################################
    file = os.listdir(in_path_entsoe)
    file_name = []
    for dbtype in file:
        if os.path.isfile(os.path.join(in_path_entsoe, dbtype)):
            file_name.append(dbtype)
    # ################################################raw-cleaned-simulated_bmrs##########################################
    # bmrs
    df_bmrs = pd.read_csv(in_path_bmrs_file)
    af.time_info(df_bmrs, 'startTimeOfHalfHrPeriod')
    df_bmrs = df_bmrs[df_bmrs['date'] < now].reset_index(drop=True)
    for y in df_bmrs['year'].drop_duplicates().tolist():
        df_bmrs_cleaned_yearly = df_bmrs[df_bmrs['year'] == y].reset_index(drop=True)
        out_path_cleaned_yearly = af.create_folder(out_path_cleaned, str(y))
        df_bmrs_cleaned_yearly.to_csv(os.path.join(out_path_cleaned_yearly, 'United_Kingdom_BMRS.csv'), index=False,
                                      encoding='utf_8_sig')

    df_bmrs['gas'] = df_bmrs['ccgt'] + df_bmrs['ocgt']
    df_bmrs['hydro'] = df_bmrs['ps'] + df_bmrs['npshyd']
    df_bmrs['other'] = df_bmrs['biomass'] + df_bmrs['other']
    df_bmrs['solar'] = 0  # 存疑

    df_bmrs['datetime'] = pd.to_datetime(df_bmrs['startTimeOfHalfHrPeriod']) + pd.to_timedelta(
        (df_bmrs['settlementPeriod'] / 2 - 0.5), unit='h')

    df_bmrs = df_bmrs.set_index('datetime').resample('H').mean().reset_index()
    af.time_info(df_bmrs, 'datetime')
    for y in df_bmrs['year'].drop_duplicates().tolist():
        # simulated准备工作
        df_bmrs_hourly = df_bmrs[df_bmrs['year'] == y].reset_index(drop=True)
        df_bmrs_daily = df_bmrs_hourly.copy()
        df_bmrs_monthly = df_bmrs_hourly.copy()
        out_path_simulated_yearly = af.create_folder(out_path_simulated, str(y))
        out_path_simulated_yearly_per = af.create_folder(out_path_simulated_yearly, 'per_country')
        # hourly
        af.agg(df_bmrs_hourly, 'datetime', out_path_simulated_yearly_per, 'hourly', name='United_Kingdom_BMRS.csv',
               folder=True, unit=False)
        # daily
        df_bmrs_daily = df_bmrs_daily.set_index('datetime').resample('d').sum().reset_index()
        af.agg(df_bmrs_daily, 'datetime', out_path_simulated_yearly_per, 'daily', 'United_Kingdom_BMRS.csv',
               folder=True, unit=True)
        # monthly
        df_bmrs_monthly = df_bmrs_monthly.set_index('datetime').resample('m').sum().reset_index()
        af.agg(df_bmrs_monthly, 'datetime', out_path_simulated_yearly_per, 'monthly', 'United_Kingdom_BMRS.csv',
               folder=True, unit=True)
    # ########################################entose-raw-cleaned-simulated#############################################
    for x in file_name:
        df_cleaned = pd.read_csv(os.path.join(in_path_entsoe, x)).rename(columns={'MTU': 'datetime'})
        af.time_info(df_cleaned, 'datetime')
        df_cleaned = df_cleaned[df_cleaned['date'] < now].reset_index(drop=True)
        for y in df_cleaned['year'].drop_duplicates().tolist():
            df_cleaned_yearly = df_cleaned[df_cleaned['year'] == y].reset_index(drop=True)
            df_hourly = df_cleaned_yearly.copy()
            out_path_cleaned_yearly = af.create_folder(out_path_cleaned, str(y))
            df_cleaned_yearly.to_csv(os.path.join(out_path_cleaned_yearly, x), index=False, encoding='utf_8_sig')

            # ######simulated 准备工作
            df_hourly['coal'] = df_hourly[coal_list].astype(float).sum(axis=1)
            df_hourly['oil'] = df_hourly[oil_list].astype(float).sum(axis=1)
            df_hourly['gas'] = df_hourly[gas_list].astype(float).sum(axis=1)
            df_hourly['nuclear'] = df_hourly['Nuclear  - Actual Aggregated [MW]']
            df_hourly['hydro'] = df_hourly[hydro_list].astype(float).sum(axis=1)
            df_hourly['wind'] = df_hourly[wind_list].astype(float).sum(axis=1)
            df_hourly['solar'] = df_hourly['Solar  - Actual Aggregated [MW]']
            df_hourly['other'] = df_hourly[other_list].astype(float).sum(axis=1)

            df_col = df_hourly.columns.tolist()
            all_list = [df_col[i] for i, x in enumerate(df_col) if not x.find('MW') != -1]
            df_hourly = df_hourly[all_list]

            df_daily = df_hourly.copy()
            df_monthly = df_hourly.copy()
            out_path_simulated_yearly = af.create_folder(out_path_simulated, str(y))
            out_path_simulated_yearly_per = af.create_folder(out_path_simulated_yearly, 'per_country')
            # hourly
            af.agg(df_hourly, 'datetime', out_path_simulated_yearly_per, 'hourly', x, folder=True, unit=False)
            # daily
            df_daily = df_daily.set_index('datetime').resample('d').sum().reset_index()
            af.agg(df_daily, 'datetime', out_path_simulated_yearly_per, 'daily', x, folder=True, unit=True)
            # monthly
            df_monthly = df_monthly.set_index('datetime').resample('m').sum().reset_index()
            af.agg(df_monthly, 'datetime', out_path_simulated_yearly_per, 'monthly', x, folder=True, unit=True)


# #################################################################Japan#############################################################################
def japan():
    import sys
    sys.dont_write_bytecode = True
    # ###############################################################
    file_path = os.path.join(global_path, 'asia', 'japan')
    in_path = os.path.join(file_path, 'raw')
    month_path = os.path.join(in_path, 'month')
    out_path_cleaned = af.create_folder(file_path, 'cleaned')
    out_path_simulated = af.create_folder(file_path, 'simulated')
    in_path_file = os.path.join(in_path, 'occto.csv')
    in_path_file_2016 = os.path.join(in_path, 'Japan_daily_generation-2016-v0.1_20201221.csv')
    in_path_file_2017 = os.path.join(in_path, 'Japan_daily_generation-2017-v0.1_20201221.csv')
    in_path_file_2018 = os.path.join(in_path, 'Japan_daily_generation-demand-2018-0.1_20201221.csv')
    # #########################################################
    df = pd.read_csv(in_path_file)
    month_name = af.search_file(month_path)
    df_new = pd.concat(pd.read_csv(f, encoding='shift-jis', header=3) for f in month_name).reset_index(drop=True)
    df = pd.concat([df, df_new]).reset_index(drop=True)
    # 添加各种日期和单位
    df['hour'] = df['時刻'].str.replace('時', '').astype(int)  # 将hour列整理出来
    df['date'] = pd.to_datetime(df['月日'])
    df['datetime'] = pd.to_datetime(df['date']) + pd.to_timedelta((df['hour']), unit='h')  # 生成datetime

    df['year'] = df['datetime'].dt.year
    df['month'] = df['datetime'].dt.month
    df['month_date'] = df['datetime'].dt.strftime('%m-%d')

    df['unit'] = 'Mwh'
    df = df.drop(columns=['月日', '時刻'])

    # 改列名为英文
    col_list = ['demand', 'nuclear', 'geothermal', 'hydroelectric', 'fossil_fuel_fired', 'biomass', 'wind',
                'wind_regulated', 'photovoltaic',
                'photovoltaic_regulated', 'pumped_storage_hydroelectricity',
                'hour', 'date', 'datetime', 'year', 'month', 'month_date', 'unit']
    df.columns = col_list

    # 输出
    year_list = df['year'].drop_duplicates().tolist()
    for x in year_list:
        df[df['year'] == x].to_csv(os.path.join(out_path_cleaned, 'japan-generation-%s-cleaned.csv' % x), index=False,
                                   encoding='utf_8_sig')

    # ##################################cleaned-simulated######################################################
    # iea数据
    df_iea = af.iea_data('japan')
    df_new_result = pd.DataFrame()
    for y in df['year'].drop_duplicates().tolist():
        df_iea_temp = df_iea[df_iea['year'] == y].reset_index(drop=True)
        df_temp = df[df['year'] == y].reset_index(drop=True)
        month_range = df_iea_temp['month'].drop_duplicates().tolist()
        if month_range != 12:
            df_iea_temp = df_iea[df_iea['year'] == y - 1].reset_index(drop=True)
            df_temp = df[df['year'] == y].reset_index(drop=True)
            month_range = df_iea_temp['month'].drop_duplicates().tolist()
        for i in month_range:
            df_temp_monthly = df_temp[df_temp['month'] == i].reset_index(drop=True)

            coal_value = df_iea_temp[df_iea_temp['month'] == i]['coal'].tolist()[0]
            gas_value = df_iea_temp[df_iea_temp['month'] == i]['gas'].tolist()[0]
            oil_value = df_iea_temp[df_iea_temp['month'] == i]['oil'].tolist()[0]

            df_temp_monthly['coal'] = df_temp_monthly['fossil_fuel_fired'] * (
                    coal_value / (coal_value + gas_value + oil_value))
            df_temp_monthly['gas'] = df_temp_monthly['fossil_fuel_fired'] * (
                    gas_value / (coal_value + gas_value + oil_value))
            df_temp_monthly['oil'] = df_temp_monthly['fossil_fuel_fired'] * (
                    oil_value / (coal_value + gas_value + oil_value))

            df_temp_monthly['hydro'] = df_temp_monthly['hydroelectric'] + df_temp_monthly[
                'pumped_storage_hydroelectricity']
            df_temp_monthly['solar'] = df_temp_monthly['photovoltaic'] + df_temp_monthly['photovoltaic_regulated']
            df_temp_monthly['wind'] = df_temp_monthly['wind'] + df_temp_monthly['wind_regulated']
            df_temp_monthly['other'] = df_temp_monthly['biomass'] + df_temp_monthly['geothermal']
            df_new_result = pd.concat([df_new_result, df_temp_monthly]).reset_index(drop=True)
    df_all = df_new_result.copy()

    for x in df_all.columns:
        # noinspection PyBroadException
        try:
            df_all[x] = df_all[x].astype(float)
        except:
            pass
    af.time_info(df_all, 'datetime')

    for y in df_all['year'].drop_duplicates().tolist():
        df_hourly = df_all[df_all['year'] == y].reset_index(drop=True)
        df_daily = df_hourly.copy()
        df_monthly = df_hourly.copy()
        out_path_simulated_yearly = af.create_folder(out_path_simulated, str(y))
        # hourly
        af.agg(df_hourly, 'datetime', out_path_simulated_yearly, 'hourly',
               name='Japan_hourly_generation-' + str(y) + '.csv', folder=False, unit=True)
        # daily
        df_daily = df_daily.set_index('datetime').resample('d').sum().reset_index()
        af.agg(df_daily, 'datetime', out_path_simulated_yearly, 'daily',
               name='Japan_daily_generation-' + str(y) + '.csv', folder=False, unit=True)
        # monthly
        df_monthly = df_monthly.set_index('datetime').resample('m').sum().reset_index()
        af.agg(df_monthly, 'datetime', out_path_simulated_yearly, 'monthly',
               name='Japan_monthly_generation-' + str(y) + '.csv', folder=False, unit=True)

    # daily-simulated 16-18年数据
    df_16 = pd.read_csv(in_path_file_2016)
    df_17 = pd.read_csv(in_path_file_2017)
    df_18 = pd.read_csv(in_path_file_2018).drop(columns=['total.demand'])
    df_p = pd.concat([df_16, df_17, df_18]).reset_index(drop=True)
    df_p = af.check_date(df_p, 'date', 'd')  # 填充缺失日期
    df_p = af.fill_null(df_p, 'japan', 'date', 'daily')
    for x in df_p.columns.tolist():
        if df_p[x].dtype == float:
            df_p[x] = df_p[x] * 1000

    for y in df_p['year'].drop_duplicates().tolist():
        df_daily = df_p[df_p['year'] == y].reset_index(drop=True)
        df_monthly = df_daily.copy()
        out_path_simulated_yearly = af.create_folder(out_path_simulated, str(y))
        # daily
        af.agg(df_daily, 'date', out_path_simulated_yearly, 'daily', name='Japan_daily_generation-' + str(y) + '.csv',
               folder=False, unit=False)
        # monthly
        df_monthly = df_monthly.set_index('date').resample('m').sum().reset_index()
        af.agg(df_monthly, 'date', out_path_simulated_yearly, 'monthly',
               name='Japan_monthly_generation-' + str(y) + '.csv', folder=False, unit=False)

    # 预测一个月的数据
    # 读取old 数据
    file_name = af.search_file(file_path)
    old_name = [file_name[i] for i, x in enumerate(file_name) if x.find('hourly') != -1]
    df_old = pd.concat([pd.read_csv(f) for f in old_name]).reset_index(drop=True)
    df_new = pd.read_csv(os.path.join(in_path, 'craw_data.csv'))
    df_new['date'] = pd.to_datetime(df_new['date'])

    # 用去年同月的百分比估算今年下一个月的值 # 2022年3月的值用2021年3月的百分比
    # 添加一个新的月
    next_month_first = pd.date_range(start=df_old['date'].max(), periods=2, freq='d')[1]
    next_month_end = pd.date_range(start=df_old['date'].max(), periods=2, freq='M')[1]
    # 生成下一个月的日期范围
    month_range = pd.date_range(start=next_month_first, end=next_month_end, freq='h')
    # 填补缺失的一天 我也不知道为啥会缺失
    month_range = list(month_range) + list((pd.date_range(start=month_range.max(), periods=24, freq='h')[1:]))
    # 只有当下个月有完整月份数据时 才会处理下方代码
    if len(month_range) == len(df_new[df_new['date'].isin(month_range)]):
        df_insert = df_new[df_new['date'].isin(month_range)].reset_index(drop=True)
        df_insert['date'] = pd.to_datetime(df_insert['date'])
        df_insert['year'] = df_insert['date'].dt.year - 1  # 去年
        df_insert['month'] = df_insert['date'].dt.month
        df_insert['day'] = df_insert['date'].dt.day
        df_insert['hour'] = df_insert['date'].dt.hour
        month_list = pd.to_datetime(df_insert[['year', 'month', 'day', 'hour']].assign(), errors='coerce')
        df_insert['datetime'] = month_list
        df_old['datetime'] = pd.to_datetime(df_old['datetime'])
        df_insert = df_insert[['datetime', 'gwh']]

        df_insert = pd.merge(df_insert, df_old)

        perc_list = df_insert.loc[:, df_insert.columns.str.contains('perc', case=False)].columns

        for p in perc_list:
            df_insert[p[:-5]] = df_insert['gwh'] * df_insert[p]

        df_insert['datetime'] = month_range

        # 整理新的数据
        af.time_info(df_insert, 'datetime')
        af.total_proc(df_insert, unit=False)
        df_insert = af.check_col(df_insert, 'hourly')

        df_result = pd.concat([df_old, df_insert]).reset_index(drop=True)
        af.time_info(df_result, 'datetime')
        af.total_proc(df_result, unit=False)
        df_result = af.check_col(df_result, 'hourly')

        for y in df_result['year'].drop_duplicates().tolist():
            df_hourly = df_result[df_result['year'] == y].reset_index(drop=True)
            df_daily = df_hourly.copy()
            df_monthly = df_hourly.copy()
            out_path_simulated_yearly = af.create_folder(out_path_simulated, str(y))
            # hourly
            af.agg(df_hourly, 'datetime', out_path_simulated_yearly, 'hourly',
                   name='Japan_hourly_generation-' + str(y) + '.csv', folder=False, unit=False)
            # daily
            df_daily = df_daily.set_index('datetime').resample('d').sum().reset_index()
            af.agg(df_daily, 'datetime', out_path_simulated_yearly, 'daily',
                   name='Japan_daily_generation-' + str(y) + '.csv', folder=False, unit=False)
            # monthly
            df_monthly = df_monthly.set_index('datetime').resample('m').sum().reset_index()
            af.agg(df_monthly, 'datetime', out_path_simulated_yearly, 'monthly',
                   name='Japan_monthly_generation-' + str(y) + '.csv', folder=False, unit=False)


# #################################################################Russia#############################################################################
def russia():
    import sys
    sys.dont_write_bytecode = True
    file_path = os.path.join(global_path, 'europe', 'russia')
    in_path = os.path.join(file_path, 'raw')
    out_path_simulated = af.create_folder(file_path, 'simulated')
    bp_path_file = os.path.join(global_path, '#global_rf', 'bp', 'bp_cleaned.csv')
    in_path_file = os.path.join(in_path, 'Russia_Hourly_Generation.csv')

    # 读取raw数据并处理
    df_russia = pd.read_csv(in_path_file)
    df_russia = df_russia.rename(
        columns={'M_DATE': 'datetime', 'P_AES': 'nuclear', 'P_GES': 'hydro', 'P_TES': 'fossil', 'P_REN': 'renewables'})

    df_russia['renewables'] = df_russia['renewables'] + df_russia['P_BS']  # 合并renwables
    df_russia['total.prod'] = df_russia[['nuclear', 'hydro', 'fossil', 'renewables']].sum(axis=1)  # 计算总发电
    # 转换日期格式
    df_russia['datetime'] = pd.to_datetime(df_russia['datetime'], format='%d.%m.%Y %H:%M:%S') + pd.to_timedelta(
        (df_russia['INTERVAL']), unit='h')
    df_russia['year'] = df_russia['datetime'].dt.year

    df_russia['nuclear.perc'] = df_russia['nuclear'] / df_russia['total.prod']
    df_russia['hydro.perc'] = df_russia['hydro'] / df_russia['total.prod']
    df_russia['fossil.perc'] = df_russia['fossil'] / df_russia['total.prod']

    df_bp = pd.read_csv(bp_path_file)
    df_bp = df_bp[df_bp['country'].str.contains('Russia')].reset_index(drop=True)
    df_bp['total.prod'] = df_bp[['coal', 'gas', 'oil', 'nuclear', 'hydro', 'wind', 'solar', 'other']].sum(axis=1)

    # fossil 各自占比
    ratio_list = []
    fossil_list = ['coal', 'gas', 'oil']
    for f in fossil_list:
        name = '%s_ratio' % f
        df_bp[name] = df_bp[f] / df_bp[['coal', 'gas', 'oil']].sum(axis=1)
        ratio_list.append(name)

    # renewables 各自占比
    renew_list = ['solar', 'wind', 'other']
    for r in renew_list:
        name = '%s_ratio' % r
        df_bp[name] = df_bp[r] / df_bp[['solar', 'wind', 'other']].sum(axis=1)
        ratio_list.append(name)

    df_bp = df_bp.fillna(method='bfill')

    df_bp = df_bp[['date'] + ratio_list]

    max_year = df_bp['date'].max()  # bp数据的截至年份
    current_year = int(datetime.now().strftime('%Y'))  # 当前年

    # 添加缺失的年份
    for i in range(max_year + 1, current_year + 1):
        df_bp = df_bp.append([{'date': i}], ignore_index=True)
    df_bp = df_bp.fillna(method='ffill').rename(columns={'date': 'year'})

    df_russia = pd.merge(df_russia, df_bp)

    df_russia['coal'] = df_russia['coal_ratio'] * df_russia['fossil']
    df_russia['gas'] = df_russia['gas_ratio'] * df_russia['fossil']
    df_russia['oil'] = df_russia['oil_ratio'] * df_russia['fossil']

    df_russia['solar'] = df_russia['solar_ratio'] * df_russia['renewables']
    df_russia['wind'] = df_russia['wind_ratio'] * df_russia['renewables']
    df_russia['other'] = df_russia['other_ratio'] * df_russia['renewables']

    # 去除Russia最后几天的Null值
    df_russia = df_russia.dropna(axis=0, how='all', thresh=12).reset_index(drop=True)
    # 输出
    for y in df_russia['year'].drop_duplicates().tolist():
        out_path_simulated_yearly = af.create_folder(out_path_simulated, str(y))
        # hourly
        df_hourly = df_russia[df_russia['year'] == y].reset_index(drop=True)
        af.agg(df_hourly, 'datetime', out_path_simulated_yearly, 'hourly',
               name='Russia_hourly_generation-' + str(y) + '.csv', folder=False, unit=False)
        df_daily = df_hourly.copy()
        df_monthly = df_hourly.copy()
        # daily
        df_daily = df_daily.set_index('datetime').resample('d').sum().reset_index()
        af.agg(df_daily, 'datetime', out_path_simulated_yearly, 'daily',
               name='Russia_daily_generation-' + str(y) + '.csv', folder=False, unit=True)
        # monthly
        df_monthly = df_monthly.set_index('datetime').resample('m').sum().reset_index()
        af.agg(df_monthly, 'datetime', out_path_simulated_yearly, 'monthly',
               name='Russia_monthly_generation-' + str(y) + '.csv', folder=False, unit=True)


def china():
    import sys
    sys.dont_write_bytecode = True
    file_path = os.path.join(global_path, 'asia', 'china')
    in_path = os.path.join(file_path, 'raw')
    out_path_simulated = af.create_folder(file_path, 'simulated')

    # 获取daily数据
    url = 'http://emres.cn/api/carbonmonitor/getChinaCoalConsumption.php'
    df_daily = pd.DataFrame(requests.get(url).json()['data']).reset_index(drop=True)
    df_daily['Date'] = pd.to_datetime(df_daily['Date'])
    df_daily['year'] = df_daily['Date'].dt.year
    df_daily['month'] = df_daily['Date'].dt.month
    df_daily['Total'] = df_daily['Total'].astype(float)
    df_t = df_daily.groupby(['year', 'month']).sum().reset_index().rename(columns={'Total': 'thermal'})

    # 获取raw数据
    file_name = af.search_file(in_path)
    df = pd.concat([pd.read_csv(f) for f in file_name])

    df['fossil_other'] = df[['fossil', 'other']].sum(axis=1)
    df['renewable'] = df[['nuclear', 'hydro', 'wind', 'solar']].sum(axis=1)

    # merge
    df_new = pd.merge(df_daily, df, how='inner', on=['year', 'month'])
    df_new = pd.merge(df_new, df_t, how='inner', on=['year', 'month'])

    df_new['new_thermal'] = df_new['Total'] * df_new['fossil_other'] / df_new['thermal']
    df_new['coal'] = df_new['new_thermal'] * df_new['coal'] / df_new['fossil_other']
    df_new['gas'] = df_new['new_thermal'] * df_new['gas'] / df_new['fossil_other']
    df_new['oil'] = df_new['new_thermal'] * df_new['oil'] / df_new['fossil_other']
    df_new['other'] = df_new['new_thermal'] * df_new['other'] / df_new['fossil_other']

    df_new['total.prod'] = df_new['new_thermal'] * df_new['total.prod'] / df_new['fossil_other']
    df_new['lc'] = df_new['total.prod'] - df_new['new_thermal']

    df_new['nuclear'] = df_new['lc'] * df_new['nuclear'] / df_new['renewable']
    df_new['hydro'] = df_new['lc'] * df_new['hydro'] / df_new['renewable']
    df_new['solar'] = df_new['lc'] * df_new['solar'] / df_new['renewable']
    df_new['wind'] = df_new['lc'] * df_new['wind'] / df_new['renewable']

    df_new = df_new.sort_values(by='Date').reset_index(drop=True).rename(columns={'Date': 'date'})

    for y in df_new['year'].drop_duplicates().tolist():
        df_temp = df_new[df_new['year'] == y]
        df_monthly = df_temp.copy()
        out_path_simulated_yearly = af.create_folder(out_path_simulated, str(y))
        # daily
        af.agg(df_temp, 'date', out_path_simulated_yearly, 'daily', name='China_daily_generation-' + str(y) + '.csv',
               folder=False, unit=False)
        # monthly
        df_monthly = df_monthly.set_index('date').resample('m').sum().reset_index()
        af.agg(df_monthly, 'date', out_path_simulated_yearly, 'monthly',
               name='China_monthly_generation-' + str(y) + '.csv', folder=False, unit=False)
