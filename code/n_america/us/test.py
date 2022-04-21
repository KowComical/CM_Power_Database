# ====================================================================================
#                           Interpreter: Python 3.6.1
#                            Test platform: Mac OS X
#
#                                Author: Zhu Deng
#                           Website: http://zhudeng.top
#                         Contact Email: zhudeng94@gmail.com
#                       Created: 2020 08 04 15:56
# ====================================================================================

import pandas as pd
import os
import sys
sys.path.append('./code/global_code/')
import global_function as af

in_path = './data/n_america/us/craw/'
out_path = './data/n_america/us/raw/'

# data_process
file_name = af.search_file(os.path.join(in_path, 'time_line'))
df = pd.concat(pd.read_csv(f) for f in file_name).sort_values(by='datetime')
df = df.groupby(['datetime']).sum().reset_index()
col_list = ['datetime', 'coal', 'wind', 'hydro', 'solar', 'other', 'oil', 'nuclear', 'gas']
df.columns = col_list
df.to_csv(os.path.join(out_path, 'raw.csv'), index=False)
