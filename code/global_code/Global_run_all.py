import time
import sys

start = time.perf_counter()

module_path_string = 'K:\\Github\\GlobalPowerUpdate-Kow\\code\\n_america\\us'
sys.path.append(module_path_string)
module_path_string = 'K:\\Github\\GlobalPowerUpdate-Kow\\code\\s_america\\brazil'
sys.path.append(module_path_string)
module_path_string = 'K:\\Github\\GlobalPowerUpdate-Kow\\code\\europe\\eu27_uk'
sys.path.append(module_path_string)
module_path_string = 'K:\\Github\\GlobalPowerUpdate-Kow\\code\\europe\\russia'
sys.path.append(module_path_string)
module_path_string = 'K:\\Github\\GlobalPowerUpdate-Kow\\code\\asian\\india'
sys.path.append(module_path_string)
module_path_string = 'K:\\Github\\GlobalPowerUpdate-Kow\\code\\asian\\japan'
sys.path.append(module_path_string)

import brazil
import us
import russia
import eu
import india
import japan

end = time.perf_counter()
print("运行耗时", round(end))

