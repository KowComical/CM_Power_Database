#!/usr/bin/env python
# coding: utf-8

# In[3]:


# ====================================================================================
#                           Interpreter: Python 3.6.1
#                            Test platform: Mac OS X
#
#                                Author: Zhu Deng
#                           Website: http://zhudeng.top
#                         Contact Email: zhudeng94@gmail.com
#                       Created: 2020 08 06 14:32
# ====================================================================================

#
# Brazil's electricity data are available from:
# http://www.ons.org.br/Paginas/resultados-da-operacao/historico-da-operacao
# The data could be only requested via tableau system
# This script is used to stimulate a request to tableau online system
# Keywords: Tableau; Brazil; Electricity


import pandas as pd
import requests
import json
import jsonpath
import datetime
import os
from requests_toolbelt import MultipartEncoder
import sys

sys.dont_write_bytecode = True
sys.path.append('./code/global_code/')
import global_function as af
import global_all as g

in_path = './data/s_america/brazil/raw/'
if not os.path.exists(in_path):
    os.mkdir(in_path)
    # Set time period
endDate = datetime.datetime.now().strftime('%d/%m/%Y')

types = ["Wind", "Hydro", "Nuclear", "Solar", "Thermal"]
thermal_types = ['Biomassa', 'Carvão', 'Carvão mineral', 'Gás', 'Gás natural',
                     'Gás Natural', 'Óleo Combustível', 'Óleo Diesel', 'Petróleo', 'Resíduos Industriais']


def main():
    for timeResolution in ['Hourly']:
        # Initial Session
        filename = os.path.join(in_path, 'Brazil_ONS_%s.csv' % timeResolution)
        sessionID = initialSession()

        startDate = '01/01/2016'
        setPeriod(sessionID, startDate, endDate)
        setTimeResolution(sessionID, timeResolution)

        # Resolve response data
        all = pd.DataFrame()
        for t in range(len(types)):
            df = resolveData(sessionID, t)
            df.columns = ['Date', types[t]]
            if t:
                all = pd.merge(all, df, how='outer')
            else:
                all = df

        # Resolve response data
        for t in range(len(thermal_types)):
            df = resolveThermalData(sessionID, t)
            df.columns = ['Date', 'Thermal:' + thermal_types[t]]
            all = pd.merge(all, df, how='outer')

        # Export data to file
        all['Date'] = pd.to_datetime(all['Date'], format="%d/%m/%Y %H:%M", errors='coerce')
        all.sort_values(by='Date', inplace=True)
        all.to_csv(filename, index=False)
        # 整理数据
        g.brazil()
        # 可视化数据
        af.draw_pic('brazil')


# initialize a new session to the tableau server
def initialSession():
    url = 'https://tableau.ons.org.br/t/ONS_Publico/views/GeraodeEnergia/HistricoGeraodeEnergia?:embed=y' \
          '&:showAppBanner=false&:showShareOptions=true&:display_count=no&:showVizHome=no'
    res = requests.get(url, verify=False)
    sessionID = res.headers['X-Session-Id']
    print('Successfully created a new session [%s]...' % sessionID)

    # Setting the session UI
    play_load = {
        'sheet_id:': 'Hist%C3%B3rico%20Gera%C3%A7%C3%A3o%20de%20Energia',
        'worksheetPortSize': '{"w":843,"h":771}',
        'dashboardPortSize': '{"w":843,"h":771}',
        'clientDimension': '{"w":843,"h":798}',
        'renderMapsClientSide': 'true',
        'isBrowserRendering': 'true',
        'browserRenderingThreshold': 100,
        'formatDataValueLocally': 'false',
        'navType': 'Nav',
        'navSrc': 'Top',
        'devicePixelRatio': 2,
        'clientRenderPixelLimit': 25000000,
        'allowAutogenWorksheetPhoneLayouts': 'true',
        'sheet_id': 'Hist%C3%B3rico%20Gera%C3%A7%C3%A3o%20de%20Energia',
        'showParams': '{"checkpoint":false,"refresh":false,"refreshUnmodified":false}',
        'stickySessionKey': '{"featureFlags":"{}","isAuthoring":false,"isOfflineMode":false,'
                            '"lastUpdatedAt":1596748654166,"viewId":309,"workbookId":273}',
        'filterTileSize': 200,
        'locale': 'en_US',
        'language': 'en',
        'verboseMode': 'false',
        ':session_feature_flags': '{}',
        'keychain_version': 1,
    }
    url = 'https://tableau.ons.org.br/vizql/t/ONS_Publico/w/GeraodeEnergia/v/HistricoGeraodeEnergia/bootstrapSession' \
          '/sessions/%s' % sessionID
    res = requests.post(url, data=play_load, verify=False)
    print('Initialize Session...')

    # Setting parameters
    url = 'https://tableau.ons.org.br/vizql/t/ONS_Publico/w/GeraodeEnergia/v/HistricoGeraodeEnergia/sessions/%s' \
          '/commands/tabdoc/set-parameter-value' % sessionID

    # Setting the unit to GWh
    fields = {
        'globalFieldName': '[Parameters].[Selecione GE Comp 3 (cópia)]',
        'valueString': 'Geração de Energia (GWh)',
        'useUsLocale': 'false',
    }
    command(url, fields)
    print('Set unit to GWh...')

    return sessionID


# Command to the tableau UI
def command(url, fields):
    play_load = MultipartEncoder(
        fields=fields
    )
    res = requests.post(url, data=play_load, headers={'Content-Type': play_load.content_type})
    return res


# Set time period
def setPeriod(sessionID, startDate, endDate):
    url = 'https://tableau.ons.org.br/vizql/t/ONS_Publico/w/GeraodeEnergia/v/HistricoGeraodeEnergia/sessions/%s' \
          '/commands/tabdoc/set-parameter-value' % sessionID

    # Set start date as startDate
    fields = {
        'globalFieldName': '[Parameters].[Início Primeiro Período GE Comp 3 (cópia)]',
        'valueString': startDate,
        'useUsLocale': 'false',
    }
    command(url, fields)
    print('Start date: %s...' % startDate)

    # Set end date as endDate...
    fields = {
        'globalFieldName': '[Parameters].[Fim Primeiro Período GE Comp 3 (cópia)]',
        'valueString': endDate,
        'useUsLocale': 'false',
    }
    command(url, fields)
    print('End date: %s...' % endDate)


# Set time period
def setTimeResolution(sessionID, timeResolution):
    url = 'https://tableau.ons.org.br/vizql/t/ONS_Publico/w/GeraodeEnergia/v/HistricoGeraodeEnergia/sessions/%s' \
          '/commands/tabdoc/set-parameter-value' % sessionID
    ts = 'Dia'
    if timeResolution == 'Hourly': ts = 'Hora'
    fields = {
        'globalFieldName': '[Parameters].[Escala de Tempo GE Comp 3 (cópia)]',
        'valueString': ts,
        'useUsLocale': 'false',
    }
    command(url, fields)
    print('Time Resolution %s...' % timeResolution)


# Set production ty
def setProductionType(sessionID, t):
    # Setting production types
    url = 'https://tableau.ons.org.br/vizql/t/ONS_Publico/w/GeraodeEnergia/v/HistricoGeraodeEnergia/sessions/%s' \
          '/commands/tabdoc/categorical-filter-by-index' % sessionID
    fields = {
        'visualIdPresModel': '{"worksheet":"Simples Geração de Energia Barra Semana","dashboard":"Painel Simples '
                             'Geração de Energia","storyboard":"Histórico Geração de Energia","storyPointId":5}',
        'globalFieldName': '[federated.14ob1hf1l48s251gwbqcg15ujjvd].[none:nom_tipousinasite, nom_tipousinasite, '
                           'nom_tipousinasite and 1 more:nk]',
        'filterIndices': '[%d]' % t,
        'filterUpdateType': 'filter-replace',
    }
    res = command(url, fields)
    print('Downloading %s production data...' % types[t])

    return res


def setThermalType(sessionID, t):
    # Setting production types
    url = 'https://tableau.ons.org.br/vizql/t/ONS_Publico/w/GeraodeEnergia/v/HistricoGeraodeEnergia/sessions/%s' \
          '/commands/tabdoc/categorical-filter-by-index' % sessionID
    fields = {
        'visualIdPresModel': '{"worksheet":"Simples Geração de Energia Barra Semana","dashboard":"Painel Simples '
                             'Geração de Energia","storyboard":"Histórico Geração de Energia","storyPointId":5}',
        'globalFieldName': '[federated.14ob1hf1l48s251gwbqcg15ujjvd].[none:nom_tipocombustivel (tb_referenciacegusina '
                           '(Conjunto)), nom_tipocombustivel (tb_referenciacegusina1 (PrevCarga)), '
                           'nom_tipocombustivel (tb_referenciacegusina (Pequena)) e 1 mais:nk]',
        'membershipTarget': 'filter',
        'filterUpdateType': 'filter-delta',
        'filterAddIndices': '[%d]' % t,
        'filterRemoveIndices': '[%d]' % (t - 1),
    }
    if t == 0:
        fields['filterRemoveIndices'] = str(list(range(1, 10)))
    res = command(url, fields)
    print('Downloading %s production data...' % thermal_types[t])

    return res


def resolveData(sessionID, t):
    res = setProductionType(sessionID, t)
    data = json.loads(res.content.decode())
    viewID = jsonpath.jsonpath(data, '$..Simples Geração de Energia Dia')[0]
    url = 'https://tableau.ons.org.br/vizql/t/ONS_Publico/w/GeraodeEnergia/v/HistricoGeraodeEnergia/vudcsv/sessions' \
          '/%s/views/%s?summary=true' % (
              sessionID, viewID)
    df = pd.read_csv(url).dropna()
    result = df[['Data Dica', 'Selecione Tipo de GE Simp 4']]
    return result


def resolveThermalData(sessionID, t):
    res = setThermalType(sessionID, t)
    data = json.loads(res.content.decode())
    viewID = jsonpath.jsonpath(data, '$..Simples Geração de Energia Dia')[0]
    url = 'https://tableau.ons.org.br/vizql/t/ONS_Publico/w/GeraodeEnergia/v/HistricoGeraodeEnergia/vudcsv/sessions' \
          '/%s/views/%s?summary=true' % (
              sessionID, viewID)
    # print(url)
    df = pd.read_csv(url).dropna()
    result = df[['Data Dica', 'Selecione Tipo de GE Simp 4']]
    return result


if __name__ == '__main__':
    main()
