import sys
import us_craw as uc

module_path_string = 'K:\\Github\\GlobalPowerUpdate-Kow\\code\\global_code'
sys.path.append(module_path_string)

import global_all as g
import global_function as af

# 爬虫
uc.main()

# 处理数据
g.us()
# 作图
af.draw_pic('us')
