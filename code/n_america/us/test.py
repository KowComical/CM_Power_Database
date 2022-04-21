import sys
sys.path.append('./code/global_code/')
import global_function as af
import os
# import pandas as pd
in_path = './data/n_america/us/craw/'
out_path = './data/n_america/us/raw/'

file_name = af.search_file(os.path.join(in_path, 'time_line'))
print(file_name)
# df = pd.concat(pd.read_csv(f) for f in file_name).sort_values(by='datetime')
# df = df.groupby(['datetime']).sum().reset_index()
# col_list = ['datetime', 'coal', 'wind', 'hydro', 'solar', 'other', 'oil', 'nuclear', 'gas']
# df.columns = col_list
# df.to_csv(os.path.join(out_path, 'raw.csv'), index=False)