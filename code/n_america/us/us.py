import us_craw as uc

from global_code import global_all as g
from global_code import global_function as af

# 爬虫
uc.main()

# 处理数据
g.us()
# 作图
af.draw_pic('us')


