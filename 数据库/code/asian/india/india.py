import sys
module_path_string = "K:\\Github\\GlobalPowerUpdate-Kow\\数据库\\code\\global_code"
sys.path.append(module_path_string)

import global_all as g
import india_craw as c
import global_function as af

# 爬虫
c.main()
# 处理数据
g.india()
# 画图
af.draw_pic('india')

