import warnings
warnings.filterwarnings('ignore')
import sys
sys.dont_write_bytecode = True

try:
    sys.path.append('./code/africa/')
    print('Begin process South Africa...')
    import south_africa.south_africa_workflow as sa
    sa.main()
    print('Finish process South Africa...')
except Exception as e:
    print(e)

try:
    sys.path.append('./code/asian/')
    print('Begin process China...')
    import china.china_workflow as c
    c.main()
    print('Finish process China...')
except Exception as e:
    print(e)

try:
    sys.path.append('./code/asian/')
    print('Begin process India...')
    import india.india_workflow as i
    i.main()
    print('Finish process India...')
except Exception as e:
    print(e)

try:
    sys.path.append('./code/asian/')
    print('Begin process Japan...')
    import japan.japan_workflow as j
    j.main()
    print('Finish process Japan...')
except Exception as e:
    print(e)

try:
    sys.path.append('./code/europe/')
    print('Begin process EU...')
    import eu27_uk.eu_workflow as eu
    eu.main()
    print('Finish process EU...')
except Exception as e:
    print(e)

try:
    sys.path.append('./code/europe/')
    print('Begin process Russia...')
    import russia.russia_workflow as r
    r.main()
    print('Finish process Russia...')
except Exception as e:
    print(e)

try:
    sys.path.append('./code/n_america/')
    print('Begin process US...')
    import us.us_workflow as us
    us.main()
    print('Finish process US...')
except Exception as e:
    print(e)

try:
    sys.path.append('./code/s_america/')
    print('Begin process Brazil...')
    import brazil.brazil_workflow as b
    b.main()
    print('Finish process Brazil...')
except Exception as e:
    print(e)

try:
    print('Begin process iea...')
    import iea_workflow as iea
    iea.main()
    print('Finish process iea...')
except Exception as e:
    print(e)

try:
    print('Begin process bp...')
    import bp_workflow as bp
    bp.main()
    print('Finish process bp...')
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
print('Finish process draw_pic...')
