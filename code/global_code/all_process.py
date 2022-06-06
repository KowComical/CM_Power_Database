import warnings
warnings.filterwarnings('ignore')
import sys
sys.dont_write_bytecode = True

# south africa 单独运行
# try:
#     sys.path.append('./code/africa/south_africa/')
#     print('Begin process South Africa...')
#     import south_africa_workflow as sa
#     sa.main()
# except Exception as e:
#     print(e)

try:
    sys.path.append('./code/asian/')
    print('Begin process China...')
    import china.china_workflow as c
    c.main()
except Exception as e:
    print(e)

try:
    sys.path.append('./code/asian/')
    print('Begin process India...')
    import india.india_workflow as i
    i.main()
except Exception as e:
    print(e)

try:
    sys.path.append('./code/asian/')
    print('Begin process Japan...')
    import japan.japan_workflow as j
    j.main()
except Exception as e:
    print(e)

sys.path.append('./code/europe/')
print('Begin process EU...')
import eu27.eu_workflow as eu
eu.main()


# try:
#     sys.path.append('./code/europe/')
#     print('Begin process EU...')
#     import eu27_uk.eu_workflow as eu
#     eu.main()
# except Exception as e:
#     print(e)

try:
    sys.path.append('./code/europe/')
    print('Begin process Russia...')
    import russia.russia_workflow as r
    r.main()
except Exception as e:
    print(e)

try:
    sys.path.append('./code/n_america/')
    print('Begin process US...')
    import us.us_workflow as us
    us.main()
except Exception as e:
    print(e)

try:
    sys.path.append('./code/s_america/')
    print('Begin process Brazil...')
    import brazil.brazil_workflow as b
    b.main()
except Exception as e:
    print(e)

try:
    print('Begin process iea...')
    import iea_workflow as iea
    iea.main()
except Exception as e:
    print(e)

try:
    print('Begin process bp...')
    import bp_workflow as bp
    bp.main()
except Exception as e:
    print(e)

import cal_ef_emission as cal

cal.main()

# 输出图
print('Begin process draw_pic...')
import draw_pic as d

energy_list = ['coal', 'gas', 'oil', 'nuclear', 'hydro', 'solar', 'wind', 'other']
for e in energy_list:
    d.main(category=e)
d.main(category=False)
