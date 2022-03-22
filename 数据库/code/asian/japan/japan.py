import sys

module_path_string = "K:\Github\GlobalPowerUpdate-Kow\数据库\code\global_code"
sys.path.append(module_path_string)

import global_all as g
import global_function as af

# 处理数据
g.japan()
# 作图
af.draw_pic('japan')