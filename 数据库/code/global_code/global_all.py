#!/usr/bin/env python
# coding: utf-8

# In[7]:


import pandas as pd, numpy as np, re, os,datetime,calendar,matplotlib.pyplot as plt

import global_function as af #所有的function
############################################################################################################################################
global_path = 'K:\\Github\\GlobalPowerUpdate-Kow\\数据库\\data\\'
#################################################################US#########################################################################    
def us():
    file_path = os.path.join(global_path,'n_america','us')
    in_path = os.path.join(file_path,'raw')
    out_path_cleaned  = af.create_folder(file_path,'cleaned')
    out_path_simulated = af.create_folder(file_path,'simulated')
    in_path_file = os.path.join(in_path,'%s.csv' % '20211014_WenliZhao_df_US_format')
    in_path_file_2016 = os.path.join(in_path,'%s.csv' % 'US_daily_generation-2016-0.2_20201219')
    in_path_file_2017 = os.path.join(in_path,'%s.csv' % 'US_daily_generation-2017-0.2_20201219')
    in_path_file_2018 = os.path.join(in_path,'%s.csv' % 'US_daily_generation-2018-0.3_20210521')
#########################################raw-cleaned#################################################
    df = pd.read_csv(in_path_file).rename(columns = {'Natural gas':'gas','Petroleum':'oil'})
    df.columns = df.columns.map(lambda x:x.lower()) # 全小写
    df['datetime'] = pd.to_datetime(df[['year', 'month','day','hour']].assign(),errors='coerce')
    df = af.check_date(df,'datetime','h')#检查是否有missing date
    df['unit'] = 'Mwh'#单位
    af.time_info(df,'datetime')#日期
    #cleaned-simulated 准备工作
    for y in df['year'].drop_duplicates().tolist():
        df_cleaned = df[df['year'] == y].reset_index(drop = True)
        df_cleaned.to_csv(out_path_cleaned+'us-generation-'+str(y)+'-cleaned.csv', index = False, encoding = 'utf_8_sig')
    ###########################cleaned-simulated#################################
    #hourly
        out_path_simulated_yearly = af.create_folder(out_path_simulated,str(y))
        af.agg(df_cleaned,'datetime',out_path_simulated_yearly,'hourly',name = 'US_hourly_generation-'+str(y)+'.csv', folder = False, unit = False)

    #填补daily数据中缺失的年份
    df_daily = df.set_index('datetime').resample('d').sum().reset_index().drop(columns = ['day','hour'])
    af.time_info(df_daily,'datetime')
    af.total_proc(df_daily, unit = True)
    df_16 = pd.read_csv(in_path_file_2016)
    df_17 = pd.read_csv(in_path_file_2017)
    df_18 = pd.read_csv(in_path_file_2018)
    df_partall = pd.concat([df_16,df_17,df_18])
    df_partall = df_partall.rename(columns = {'date':'datetime'}).drop(columns = ['season'])
    af.time_info(df_partall,'datetime')
    df_daily = df_daily[df_daily['year'] != 2018].reset_index(drop = True)
    df_all = pd.concat([df_partall,df_daily]).reset_index(drop = True)
    for y in df_all['year'].drop_duplicates().tolist():
    #daily
        df_daily = df_all[df_all['year'] == y].reset_index(drop = True)
        df_monthly = df_daily.copy()
        out_path_simulated_yearly = af.create_folder(out_path_simulated,str(y))
        af.agg(df_daily,'datetime',out_path_simulated_yearly,'daily',name = 'US_daily_generation-'+str(y)+'.csv', folder = False, unit = False)
    #monthly
        af.time_info(df_monthly,'datetime')
        df_monthly = df_monthly.set_index('datetime').resample('m').sum().reset_index()
        out_path_simulated_yearly = af.create_folder(out_path_simulated,str(y))
        af.agg(df_monthly,'datetime',out_path_simulated_yearly,'monthly',name = 'US_monthly_generation-'+str(y)+'.csv', folder = False, unit = False)
##############################################################India#########################################################################
def india():
    file_path = os.path.join(global_path,'asia','india')
    in_path = os.path.join(file_path,'raw')
    out_path_cleaned  = af.create_folder(file_path,'cleaned')
    out_path_simulated = af.create_folder(file_path,'simulated')
    in_path_file = os.path.join(in_path,'%s.csv' % 'India_POSOCO_Daily')
    in_path_file_2017 = os.path.join(in_path,'%s.csv' % 'C2017_india_daily_generation-v0.1_20201118')
    in_path_file_2018 = os.path.join(in_path,'%s.csv' % 'C2018_india_daily_generation-v0.1_20201118')
    ###################################################raw-cleaned########################################################
    df = pd.read_csv(in_path_file)
    #找出重复的日期值
    duplicated_date = df[df.duplicated(['X'])]['X'].tolist()
    #将重复日期修改
    for x in duplicated_date:
        my_yes_time = af.time_b_a(x,-1)
        if df[df['X'] == my_yes_time].empty == False: #如果前一天有值
            my_yes_time = af.time_b_a(x,+1)
            if df[df['X'] == my_yes_time].empty == True: #如果后一天没有值 则将这一天改为后一天
                index_back = df[df['X'] == x].index.tolist()
                df.loc[index_back[1],('X')] = my_yes_time
        else: #如果前一天没有值 则将这一天改为前一天
            index_front = df[df['X'] == x].index.tolist()
            df.loc[index_front[0],('X')] = my_yes_time

    #查找缺失日期并填充
    df = af.check_date(df,'X','d')
    df['date'] = pd.to_datetime(df['X'], format = '%Y-%m-%d')
    af.time_info(df,'X') #添加各种日期数据和单位
    df['unit'] = 'MU'
    df.columns = df.columns.map(lambda x:x.lower()) # 全小写
    df = df.rename(columns = {'gas..naptha...diesel':'gas_naptha_diesel','res..wind..solar..biomass...others.':'res'}).drop(columns = ['unnamed: 0','x']) #修改列名细节

    #输出没填充缺失值的
    year_list = df['year'].drop_duplicates().tolist()
    for x in year_list:
        df[df['year'] == x].to_csv(out_path_cleaned+'india-generation-'+str(x)+'-cleaned.csv', index = False, encoding = 'utf_8_sig')

    #处理缺失值并输出
    df_filled = df.copy()
    for x in df_filled.columns.tolist():
        if df_filled[x].dtype == float:
            df_filled[x] = df_filled[x].fillna(df_filled[x].interpolate())

    #################添加2017-2018的df_filled数据#####################
    df_17 = pd.read_csv(in_path_file_2017)
    df_18 = pd.read_csv(in_path_file_2018)

    df_filled = pd.concat([df_17,df_18,df_filled])
    df_filled['date'] = pd.to_datetime(df_filled['date'])
    af.time_info(df_filled,'date')
    df_filled = df_filled.reset_index(drop = True)
    #填充coal这一列
    index = df_filled.index.tolist()
    for t in index:
        if pd.isna(df_filled['coal'].iloc[t]) == True: #当coal没有值的时候
            df_filled.loc[t,('coal')] = df_filled.loc[t,('coal_lignite')]
    df_filled = df_filled[~df_filled.duplicated()].reset_index(drop = True)

    #处理重复值
    df_filled = df_filled.sort_values(by='date',na_position='first').reset_index(drop = True)
    index = df_filled.index.tolist()
    drop_list = []
    for t in index:
        if pd.isna(df_filled['coal'].iloc[t]) == False and pd.isna(df_filled['coal_lignite'].iloc[t]) == True:#当coal有值 coal_lignite没有值并且前面有相同日期的时候
            try:
                if df_filled['date'].iloc[t] == df_filled['date'].iloc[t-1] or df_filled['date'].iloc[t] == df_filled['date'].iloc[t+1]:
                    drop_list.append(t)
            except:
                pass
    df_filled = df_filled.drop(drop_list).reset_index(drop = True)
    ####################################################################
    #处理monthly数据做后续备用
    df_iea = af.iea_data('india')
    result = []
    for x in year_list:
        df_temp = df_filled[df_filled['year'] == x].reset_index(drop = True)
        df_temp.to_csv(out_path_cleaned+'india-generation-'+str(x)+'-cleaned-filled.csv', index = False, encoding = 'utf_8_sig')
    ##########################################cleaned-simulated###################################################
    for y in df_iea['year'].drop_duplicates().tolist():
        df_iea_temp = df_iea[df_iea['year'] == y].reset_index(drop = True)
        df_temp = df_filled[df_filled['year'] == y].reset_index(drop = True)
        month_range = df_iea_temp['month'].drop_duplicates().tolist()
        if month_range != 12:
            df_iea_temp = df_iea[df_iea['year'] == y-1].reset_index(drop = True)
            df_temp = df[df['year'] == y].reset_index(drop = True)
            month_range = df_iea_temp['month'].drop_duplicates().tolist()
        for i in month_range:
            df_temp_monthly = df_temp[df_temp['month'] == i].reset_index(drop = True)

            gas_value = df_iea_temp[df_iea_temp['month'] == i]['gas'].tolist()[0]
            oil_value = df_iea_temp[df_iea_temp['month'] == i]['oil'].tolist()[0]
            df_temp_monthly['gas'] = df_temp_monthly['gas_naptha_diesel']*(gas_value/(gas_value+oil_value))
            df_temp_monthly['oil'] = df_temp_monthly['gas_naptha_diesel']*(oil_value/(gas_value+oil_value))

            solar_value = df_iea_temp[df_iea_temp['month'] == i]['solar'].tolist()[0]
            wind_value = df_iea_temp[df_iea_temp['month'] == i]['wind'].tolist()[0]
            other_value = df_iea_temp[df_iea_temp['month'] == i]['other'].tolist()[0]
            df_temp_monthly['solar'] = df_temp_monthly['res']*(solar_value/(solar_value+wind_value+other_value))
            df_temp_monthly['wind'] = df_temp_monthly['res']*(wind_value/(solar_value+wind_value+other_value))
            df_temp_monthly['other'] = df_temp_monthly['res']*(other_value/(solar_value+wind_value+other_value))
            result.append(df_temp_monthly)

    df_all = pd.DataFrame(np.concatenate(result), columns = df_temp_monthly.columns)

    df_all['coal'] = (df_all['coal']+df_all['lignite'])
    for t in df_all.index.tolist():
        if pd.isna(df_all['coal'].iloc[t]) == True and pd.isna(df_all['lignite'].iloc[t]) == False:
            df_all.loc[t,('coal')] = df_all.loc[t,('lignite')]

    #生成缺失的日期
    start_range = str(min(df_iea['year']))+'-01-01' #从monthly里面最小年份开始
    end_range = min(df_all['date']) #从monthly里面最小年份开始一直到df_all里最小日期截至
    date_range = pd.date_range(start=start_range ,end=end_range ,freq = 'd')[:-1] #去掉最后一天

    for x in date_range:
        df_all = af.insert_date(df_all,'date',x)

    df_all = af.check_date(df_all,'date','d')#填补缺失的日期
    total_list = ['coal','gas','oil','nuclear','hydro','wind','solar','other']
    df_all[total_list] = df_all[total_list].astype(float)
    df_all[total_list] = df_all[total_list].interpolate()

    #填充缺失值
    df_all = af.fill_null(df_all,'india','date','daily')
    df_all[total_list] = df_all[total_list]*1000
    ##########################################################daily#############################################
    for y in df_all['year'].drop_duplicates().tolist():
        df_temp = df_all[df_all['year'] == y]
        df_daily = df_temp.copy()
        df_monthly= df_temp.copy()
        out_path_simulated_yearly = af.create_folder(out_path_simulated,str(y))
        #daily
        af.agg(df_daily,'date',out_path_simulated_yearly,'daily',name = 'India_daily_generation-'+str(y)+'.csv', folder = False, unit = False)
    #########################################################monthly##########################################
        #monthly
        df_monthly = df_monthly.set_index('date').resample('m').sum().reset_index()
        af.agg(df_monthly,'date',out_path_simulated_yearly,'monthly',name = 'India_monthly_generation-'+str(y)+'.csv', folder = False, unit = False)
##########################################################################################################################################            
def brazil():
###############################################################路径#######################################################
    file_path = os.path.join(global_path, 's_america', 'brazil')
    in_path = os.path.join(file_path, 'raw')
    out_path_cleaned = af.create_folder(file_path, 'cleaned')
    out_path_simulated = af.create_folder(file_path, 'simulated')
    in_path_file = os.path.join(in_path, 'Brazil_ONS_Hourly.csv')
##############################################################Raw-Cleaned########################################################
    df = pd.read_csv(in_path_file).drop(columns=['Unnamed: 0']) #存疑
    df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y %H:%M",errors='coerce')
    df = df[~df[['Date']].isnull().T.any()].rename(columns={'Date':'datetime'}).reset_index(drop=True) #去除错误行
    df = df.drop_duplicates().reset_index(drop=True) #去除重复行

    df = af.check_date(df, 'datetime', 'h')#判断是否有缺失日期
    af.time_info(df,'datetime')#填充时间列

    #cleaned 输出
    for y in df['year'].drop_duplicates().tolist():
        df_cleaned = df[df['year'] == y]
        df_cleaned.to_csv(out_path_cleaned+'brazil-generation-'+str(y)+'-cleaned.csv', index=False)
########################################################cleaned-simulated######################################
        df_hourly = df[df['year'] == y].reset_index(drop = True).fillna(0)
        df_hourly['Thermal.Gás.natural'] = df_hourly['Thermal.Gás.natural'].astype(float)+df_hourly['Thermal.Gás.Natural'].astype(float)
        df_hourly = df_hourly.drop(columns = ['Thermal.Gás.Natural'])
        df_hourly.columns = df_hourly.columns.map(lambda x:x.lower()) # 全小写
        df_col = df_hourly.columns.tolist()
        coal_list = [df_col[i] for i,x in enumerate(df_col) if x.find('carv')!=-1]
        gas_list = [df_col[i] for i,x in enumerate(df_col) if x.find('gás')!=-1]
        oil_list = [df_col[i] for i,x in enumerate(df_col) if x.find('leo')!=-1]
        other_list = ['thermal.biomassa','thermal.resíduos.industriais']
        df_hourly['coal'] = df_hourly[coal_list].astype(float).sum(axis = 1)
        df_hourly['gas'] = df_hourly[gas_list].astype(float).sum(axis = 1)
        df_hourly['oil'] = df_hourly[oil_list].astype(float).sum(axis = 1)
        type_list = ['nuclear','hydro','wind','solar']
        df_hourly[type_list] = df_hourly[type_list].astype(float)
        df_hourly['other'] = df_hourly[other_list].astype(float).sum(axis = 1)
        df_col = df_hourly.columns.tolist()
        all_list = [df_col[i] for i,x in enumerate(df_col) if not x.find('thermal')!=-1]
        df_hourly = df_hourly[all_list].groupby(all_list).sum().reset_index()
        df_daily = df_hourly.copy()
        df_monthly = df_hourly.copy()
        out_path_simulated_yearly = af.create_folder(out_path_simulated,str(y))
        #hourly
        af.agg(df_hourly,'datetime',out_path_simulated_yearly,'hourly',name = 'Brazil_hourly_generation-'+str(y)+'.csv', folder = False, unit = False)
        ##############################################################daily#########################################
        #daily
        df_daily = df_daily.set_index('datetime').resample('d').sum().reset_index()
        af.agg(df_daily,'datetime',out_path_simulated_yearly,'daily',name = 'Brazil_daily_generation-'+str(y)+'.csv',folder = False, unit = False)
       ##############################################monthly###############################################
        #monthly
        df_monthly = df_monthly.set_index('datetime').resample('m').sum().reset_index()
        af.agg(df_monthly,'datetime',out_path_simulated_yearly,'monthly',name = 'Brazil_monthly_generation-'+str(y)+'.csv',folder = False, unit = False)
############################################################################################################################################        
def eu():
    file_path = os.path.join(global_path,'europe','eu27_uk')
    in_path_entsoe = os.path.join(file_path,'raw','entsoe')
    in_path_bmrs = os.path.join(file_path,'raw','uk-BMRS')
    out_path_cleaned  = af.create_folder(file_path,'cleaned')
    out_path_simulated = af.create_folder(file_path,'simulated')
    in_path_bmrs_file = os.path.join(file_path,'raw','uk-BMRS','UK_BMRS_Hourly.csv')
    ################################################################################################################################
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
    #################################################################################################################
    file = os.listdir(in_path_entsoe)
    file_name = []
    for dbtype in file:
        if os.path.isfile(os.path.join(in_path_entsoe,dbtype)):
            file_name.append(dbtype)
    #################################################raw-cleaned-simulated_bmrs##########################################
    #bmrs
    df_bmrs = pd.read_csv(in_path_bmrs_file)
    af.time_info(df_bmrs,'startTimeOfHalfHrPeriod')
    for y in df_bmrs['year'].drop_duplicates().tolist():
        df_bmrs_cleaned_yearly = df_bmrs[df_bmrs['year'] == y].reset_index(drop = True)
        df_hourly = df_bmrs_cleaned_yearly.copy()
        out_path_cleaned_yearly = af.create_folder(out_path_cleaned,str(y))
        df_bmrs_cleaned_yearly.to_csv(out_path_cleaned_yearly+'United_Kingdom_BMRS.csv', index = False, encoding = 'utf_8_sig')

    df_bmrs['gas'] = df_bmrs['ccgt']+df_bmrs['ocgt']
    df_bmrs['hydro'] = df_bmrs['ps']+df_bmrs['npshyd']
    df_bmrs['other'] = df_bmrs['biomass']+df_bmrs['other']
    df_bmrs['solar'] = 0 #存疑

    df_bmrs['datetime'] = pd.to_datetime(df_bmrs['startTimeOfHalfHrPeriod']) + pd.to_timedelta((df_bmrs['settlementPeriod']/2-0.5), unit='h')

    df_bmrs = df_bmrs.set_index('datetime').resample('H').mean().reset_index()
    af.time_info(df_bmrs,'datetime')
    for y in df_bmrs['year'].drop_duplicates().tolist():
        #simulated准备工作
        df_bmrs_hourly = df_bmrs[df_bmrs['year'] == y].reset_index(drop = True)
        df_bmrs_daily = df_bmrs_hourly.copy()
        df_bmrs_monthly = df_bmrs_hourly.copy()
        out_path_simulated_yearly = af.create_folder(out_path_simulated,str(y))
        out_path_simulated_yearly_per = af.create_folder(out_path_simulated_yearly,'per_country')
    #hourly
        af.af.agg(df_bmrs_hourly,'datetime',out_path_simulated_yearly_per,'hourly',name = 'United_Kingdom_BMRS.csv', folder = True, unit = False)
    #daily
        df_bmrs_daily = df_bmrs_daily.set_index('datetime').resample('d').sum().reset_index()
        af.af.agg(df_bmrs_daily,'datetime',out_path_simulated_yearly_per,'daily','United_Kingdom_BMRS.csv', folder = True, unit = True)
    #monthly
        df_bmrs_monthly = df_bmrs_monthly.set_index('datetime').resample('m').sum().reset_index()
        af.af.agg(df_bmrs_monthly,'datetime',out_path_simulated_yearly_per,'monthly','United_Kingdom_BMRS.csv', folder = True, unit = True)
    #########################################entose-raw-cleaned-simulated#############################################
    for x in file_name:
        df_cleaned = pd.read_csv(in_path_entsoe+'\\'+x).rename(columns = {'MTU':'datetime'})
        af.time_info(df_cleaned,'datetime')
        for y in df_cleaned['year'].drop_duplicates().tolist():
            df_cleaned_yearly = df_cleaned[df_cleaned['year'] == y].reset_index(drop = True)
            df_hourly = df_cleaned_yearly.copy()
            out_path_cleaned_yearly = af.create_folder(out_path_cleaned,str(y))
            df_cleaned_yearly.to_csv(out_path_cleaned_yearly+x, index = False, encoding = 'utf_8_sig')
    #######simulated 准备工作
            df_hourly['coal'] = df_hourly[coal_list].astype(float).sum(axis = 1)
            df_hourly['oil'] = df_hourly[oil_list].astype(float).sum(axis = 1)
            df_hourly['gas'] = df_hourly[gas_list].astype(float).sum(axis = 1)
            df_hourly['nuclear'] = df_hourly['Nuclear  - Actual Aggregated [MW]']
            df_hourly['hydro'] = df_hourly[hydro_list].astype(float).sum(axis = 1)
            df_hourly['wind'] = df_hourly[wind_list].astype(float).sum(axis = 1)
            df_hourly['solar'] = df_hourly['Solar  - Actual Aggregated [MW]']
            df_hourly['other'] = df_hourly[other_list].astype(float).sum(axis = 1)

            df_col = df_hourly.columns.tolist()
            all_list =  [df_col[i] for i,x in enumerate(df_col) if not x.find('MW')!=-1]
            df_hourly = df_hourly[all_list]
            df_daily = df_hourly.copy()
            df_monthly = df_hourly.copy()
            out_path_simulated_yearly = af.create_folder(out_path_simulated,str(y))
            out_path_simulated_yearly_per = af.create_folder(out_path_simulated_yearly,'per_country')
    #####hourly
            af.af.agg(df_hourly,'datetime',out_path_simulated_yearly_per,'hourly',x, folder = True, unit = False)
    #####daily
            df_daily = df_daily.set_index('datetime').resample('d').sum().reset_index()
            af.af.agg(df_daily,'datetime',out_path_simulated_yearly_per,'daily',x, folder = True, unit = True)
    #####monthly
            df_monthly = df_monthly.set_index('datetime').resample('m').sum().reset_index()
            af.af.agg(df_monthly,'datetime',out_path_simulated_yearly_per,'monthly',x, folder = True, unit = True)
###############################################################################################################################################                
def japan():
    ################################################################
    file_path = os.path.join(global_path,'asia','japan')
    in_path = os.path.join(file_path,'raw')
    out_path_cleaned  = af.create_folder(file_path,'cleaned')
    out_path_simulated = af.create_folder(file_path,'simulated')
    in_path_file = os.path.join(in_path,'occto.csv')
    in_path_file_2016 = os.path.join(in_path,'Japan_daily_generation-2016-v0.1_20201221.csv')
    in_path_file_2017 = os.path.join(in_path,'Japan_daily_generation-2017-v0.1_20201221.csv')
    in_path_file_2018 = os.path.join(in_path,'Japan_daily_generation-demand-2018-0.1_20201221.csv')
##########################################################        
    df = pd.read_csv(in_path_file)
    #添加各种日期和单位
    df['hour'] = df['時刻'].str.replace('時','').astype(int) #将hour列整理出来
    df['date'] = pd.to_datetime(df['月日'])
    df['datetime'] = pd.to_datetime(df['date']) + pd.to_timedelta((df['hour']), unit='h') #生成datetime

    df['year'] = df['datetime'].dt.year
    df['month'] = df['datetime'].dt.month
    df['month_date']  = df['datetime'].dt.strftime('%m-%d')

    df['unit'] = 'Mwh'
    df = df.drop(columns = ['月日','時刻'])

    #改列名为英文
    col_list = ['demand','nuclear','geothermal','hydroelectric','fossil_fuel_fired','biomass','wind','wind_regulated','photovoltaic',
                'photovoltaic_regulated','pumped_storage_hydroelectricity',
                'hour','date','datetime','year', 'month','month_date','unit']
    df.columns = col_list

    #输出
    year_list = df['year'].drop_duplicates().tolist()
    for x in year_list:
        df[df['year'] == x].to_csv(out_path_cleaned+'japan-generation-'+str(x)+'-cleaned.csv', index = False, encoding = 'utf_8_sig')
    ###################################cleaned-simulated######################################################
    #iea数据
    df_iea = af.iea_data('japan')
    result = []
    for y in df_iea['year'].drop_duplicates().tolist():
        df_iea_temp = df_iea[df_iea['year'] == y].reset_index(drop = True)
        df_temp = df[df['year'] == y].reset_index(drop = True)
        month_range = df_iea_temp['month'].drop_duplicates().tolist()
        if month_range != 12:
            df_iea_temp = df_iea[df_iea['year'] == y-1].reset_index(drop = True)
            df_temp = df[df['year'] == y].reset_index(drop = True)
            month_range = df_iea_temp['month'].drop_duplicates().tolist()
        for i in month_range:
            df_temp_monthly = df_temp[df_temp['month'] == i].reset_index(drop = True)

            coal_value = df_iea_temp[df_iea_temp['month'] == i]['coal'].tolist()[0]
            gas_value = df_iea_temp[df_iea_temp['month'] == i]['gas'].tolist()[0]
            oil_value = df_iea_temp[df_iea_temp['month'] == i]['oil'].tolist()[0]

            df_temp_monthly['coal'] = df_temp_monthly['fossil_fuel_fired']*(coal_value/(coal_value+gas_value+oil_value))
            df_temp_monthly['gas'] = df_temp_monthly['fossil_fuel_fired']*(gas_value/(coal_value+gas_value+oil_value))
            df_temp_monthly['oil'] = df_temp_monthly['fossil_fuel_fired']*(oil_value/(coal_value+gas_value+oil_value))

            df_temp_monthly['hydro'] = df_temp_monthly['hydroelectric']+df_temp_monthly['pumped_storage_hydroelectricity']
            df_temp_monthly['solar'] = df_temp_monthly['photovoltaic']+df_temp_monthly['photovoltaic_regulated']
            df_temp_monthly['wind'] = df_temp_monthly['wind']+df_temp_monthly['wind_regulated']
            df_temp_monthly['other'] = df_temp_monthly['biomass']+df_temp_monthly['geothermal']
            result.append(df_temp_monthly)
    df_all = pd.DataFrame(np.concatenate(result), columns = df_temp_monthly.columns)

    for x in df_all.columns.tolist():
        try:
            df_all[x] = df_all[x].astype(float)
        except:
            pass
    af.time_info(df_all,'datetime')
    for y in df_all['year'].drop_duplicates().tolist():
        df_hourly = df_all[df_all['year'] == y].reset_index(drop = True)
        df_daily = df_hourly.copy()
        df_monthly = df_hourly.copy()
        out_path_simulated_yearly = af.create_folder(out_path_simulated,str(y))
        #hourly
        af.agg(df_hourly,'datetime',out_path_simulated_yearly,'hourly',name = 'Japan_hourly_generation-'+str(y)+'.csv', folder = False, unit = True)
        #daily
        df_daily = df_daily.set_index('datetime').resample('d').sum().reset_index()
        af.agg(df_daily,'datetime',out_path_simulated_yearly,'daily',name = 'Japan_daily_generation-'+str(y)+'.csv',folder = False, unit = True)
        #monthly
        df_monthly = df_monthly.set_index('datetime').resample('m').sum().reset_index()
        af.agg(df_monthly,'datetime',out_path_simulated_yearly,'monthly',name = 'Japan_monthly_generation-'+str(y)+'.csv',folder = False, unit = True)

    #daily-simulated 16-18年数据
    df_16 = pd.read_csv(in_path_file_2016)
    df_17 = pd.read_csv(in_path_file_2017)
    df_18 = pd.read_csv(in_path_file_2018).drop(columns = ['total.demand'])
    df_p = pd.concat([df_16,df_17,df_18]).reset_index(drop = True)
    df_p = af.check_date(df_p,'date','d') #填充缺失日期
    df_p = af.fill_null(df_p,'japan','date','daily')
    for x in df_p.columns.tolist():
        if df_p[x].dtype == float:
            df_p[x] = df_p[x]*1000

    for y in df_p['year'].drop_duplicates().tolist():
        df_daily = df_p[df_p['year'] == y].reset_index(drop = True)
        df_monthly = df_daily.copy()
        out_path_simulated_yearly = af.create_folder(out_path_simulated,str(y))
        #daily
        af.agg(df_daily,'date',out_path_simulated_yearly,'daily',name = 'Japan_daily_generation-'+str(y)+'.csv',folder = False, unit = False)
        #monthly
        df_monthly = df_monthly.set_index('date').resample('m').sum().reset_index()
        af.agg(df_monthly,'date',out_path_simulated_yearly,'monthly',name = 'Japan_monthly_generation-'+str(y)+'.csv',folder = False, unit = False)

def russia():
    file_path = os.path.join(global_path,'europe','russia')
    in_path = os.path.join(file_path,'raw')
    out_path_cleaned  = af.create_folder(file_path,'cleaned')
    out_path_simulated = af.create_folder(file_path,'simulated')
    in_path_file = os.path.join(in_path,'Russia_SOUPS_Hourly (Corrected).csv')

    df = pd.read_csv(in_path_file)
    total_list = ['nuclear','hydro','fossil','P_BS','renewables']
    df.columns = ['date','nuclear','hydro','fossil','P_BS','renewables']
    df['total.prod'] = df[total_list].sum(axis = 1)
    df['low.carbon'] = df['total.prod'] - df['fossil']
    for z in df.columns.tolist():
        if df[z].dtype == float:
            df[z] = df[z]/1000
    for y in df.columns.tolist():
        if df[y].dtype == float:
            if y != 'total.prod' and 'perc' not in y:
                df[y+'.perc'] = df[y]/df['total.prod']
    df['unit'] = 'Gwh'

    #daily
    af.time_info(df,'date')
    df = df.drop(columns = ['hour'])
    for x in df['year'].drop_duplicates().tolist():
        out_path_simulated_yearly = af.create_folder(out_path_simulated,str(x))
        df[df['year'] == x].to_csv(out_path_simulated_yearly+'Russia_daily_generation-'+str(x)+'.csv', index = False, encoding = 'utf_8_sig')

    #monthly
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').resample('m').sum().reset_index()
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    for y in df.columns.tolist():
        if df[y].dtype == float:
            if y != 'total.prod' and 'perc' not in y:
                df[y+'.perc'] = df[y]/df['total.prod']
    df['unit'] = 'Gwh'
    df = df.drop(columns = ['date'])
    for x in df['year'].drop_duplicates().tolist():
        out_path_simulated_yearly = af.create_folder(out_path_simulated,str(x))
        df[df['year'] == x].to_csv(out_path_simulated_yearly+'Russia_monthly_generation-'+str(x)+'.csv', index = False, encoding = 'utf_8_sig')

