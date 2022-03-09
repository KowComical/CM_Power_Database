#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd, numpy as np, re, os,datetime
    
################################备注########################################
#df_cleaned 时间列 = ['datetime','date','year','month','month_date','weekday','hour']
#df_simulated_hourly 时间列 = ['datetime','date','year','month','month_date','weekday','hour'] unit = ['Mwh']
#df_simulated_daily 时间列 = ['date','year','month','month_date','weekday'] unit = ['Gwh']
#df_simulated_monthly 时间列 = ['year','month'] unit = ['Gwh']
############################function#########################################
def create_folder(file_path,Type): #建立需要的文件夹
    out_path = file_path+Type+'\\'
    if not os.path.exists(out_path): #如果有了文件夹的话就直接pass掉
        os.mkdir(out_path)
    return out_path

def check_col(df,Type): #检查数据的现存列名是否一致 如果不一致就删掉多余的
    df_col = df.columns.tolist()
    if Type == 'hourly': #如果是simulated_hourly
        r_col = ['datetime', 'date','year','month','month_date','weekday','hour','coal','oil','gas','nuclear','hydro','wind','solar','other','fossil','low.carbon','total.prod','coal.perc','oil.perc','gas.perc','nuclear.perc','hydro.perc','wind.perc','solar.perc','other.perc','fossil.perc','low.carbon.perc','unit']
        df['unit'] = 'Mwh'
    if Type == 'daily':
        r_col = ['date','year','month','month_date','weekday','coal','oil','gas','nuclear','hydro','wind','solar','other','fossil','low.carbon','total.prod','coal.perc','oil.perc','gas.perc','nuclear.perc','hydro.perc','wind.perc','solar.perc','other.perc','fossil.perc','low.carbon.perc','unit']
        df['unit'] = 'Gwh'
    if Type == 'monthly':
        r_col = ['year','month','coal','oil','gas','nuclear','hydro','wind','solar','other','fossil','low.carbon','total.prod','coal.perc','oil.perc','gas.perc','nuclear.perc','hydro.perc','wind.perc','solar.perc','other.perc','fossil.perc','low.carbon.perc','unit']
        df['unit'] = 'Gwh'
    if r_col !=df_col:
        drop_list = list(set(df_col)-set(r_col))
        for d in drop_list:
            df = df.drop(columns = d)
    return df

def time_b_a(x,which): #根据which 选择得到所选日期的前which天或者后which天
    myday = datetime.datetime.strptime(x,'%Y-%m-%d')
    delta = datetime.timedelta(days=which)
    my_yestoday = myday + delta
    my_yes_time = my_yestoday.strftime('%Y-%m-%d')
    return my_yes_time
        
def time_info(df,date_name): #添加各种时间列
    df[date_name] = pd.to_datetime(df[date_name])
    df['year'] = df[date_name].dt.year
    df['month'] = df[date_name].dt.month
    df['month_date']  = df[date_name].dt.strftime('%m-%d')
    df['weekday'] = df[date_name].dt.day_name()
    
def check_date(df,date_name,f): #检查现存时间是否有缺失
    df[date_name] = pd.to_datetime(df[date_name])
    real_date = pd.date_range(start=min(df[date_name]),end = max(df[date_name]),freq = f).tolist()
    df_date = df[date_name].drop_duplicates().tolist()
    missing_date = list(set(real_date)-set(df_date))
    return missing_date

def insert_date(df,date_name,x): #根据缺失的时间进行填补并重新排序
    df = df.append([{date_name:x}], ignore_index=True)
    df = df.sort_values(by = date_name).reset_index(drop = True)
    return df

def total_proc(df,unit): #处理数据
    unit = unit
    fossil_list = ['coal','gas','oil']
    carbon_list = ['nuclear','hydro','wind','solar','other']
    perc_list = ['fossil','low.carbon']
    df['fossil'] = df[fossil_list].astype(float).sum(axis = 1)
    df['low.carbon'] = df[carbon_list].astype(float).sum(axis = 1)
    df['total.prod'] = df[perc_list].astype(float).sum(axis = 1)
    if unit == True:
        if 'hour' not in df.columns:#如果没有hour这一列 那就代表是daily或者monthly数据
            for z in df.columns.tolist():
                if df[z].dtype == float:
                    df[z] = df[z]/1000
    for y in df.columns.tolist():
        if df[y].dtype == float:
            if y != 'total.prod' and 'perc' not in y:
                df[y+'.perc'] = df[y]/df['total.prod']          
    df['unit'] = 'Gwh' #补充单位
    
def agg(df,date_name,path,Type,name): #输出
    time_info(df,date_name)
    total_proc(df, unit = True)
    df = check_col(df,Type)
    out_path = create_folder(path,Type)
    out_file = out_path+name
    df.to_csv(out_file, index = False, encoding = 'utf_8_sig')

