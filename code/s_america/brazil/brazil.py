import sys

module_path_string = "K:\\Github\\GlobalPowerUpdate-Kow\\code\\global_code"
sys.path.append(module_path_string)

import global_all as g
import global_function as af
import brazil_craw as bc

# 爬虫
bc.main()
# 处理数据
g.brazil()
# 作图
af.draw_pic('brazil')