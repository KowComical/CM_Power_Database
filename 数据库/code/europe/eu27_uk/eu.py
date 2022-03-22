import sys
import eu_craw as c
import eu_craw_raw as cr
import uk_bmrs as u


module_path_string = "K:\\Github\\GlobalPowerUpdate-Kow\\数据库\\code\\global_code"
sys.path.append(module_path_string)

import global_all as g
import global_function as af

# 爬取entose数据
c.main()
# 爬取bmrs数据
u.main()
# 处理entose数据
cr.main()
# 处理数据
g.eu()
# 作图
af.draw_pic('eu27_uk')
