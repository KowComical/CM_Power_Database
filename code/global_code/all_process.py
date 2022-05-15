import warnings
warnings.filterwarnings('ignore')
import sys
sys.dont_write_bytecode = True

# noinspection PyBroadException
try:
    sys.path.append('./code/asian/china/')
    print('Begin process China...')
    import china_workflow
except:
    print('error in China')

# noinspection PyBroadException
try:
    sys.path.append('./code/asian/india/')
    print('Begin process India...')
    import india_workflow as i
    i.main()
except:
    print('error in India')

# noinspection PyBroadException
try:
    sys.path.append('./code/asian/japan/')
    print('Begin process Japan...')
    import japan_workflow as j
    j.main()
except:
    print('error in Japan')

# noinspection PyBroadException
try:
    sys.path.append('./code/europe/eu27_uk/')
    print('Begin process EU...')
    import eu_workflow as e
    e.main()
except:
    print('error in EU')

# noinspection PyBroadException
try:
    sys.path.append('./code/europe/russia/')
    print('Begin process Russia...')
    import russia_workflow
except:
    print('error in Russia')

# noinspection PyBroadException
try:
    sys.path.append('./code/n_america/us/')
    print('Begin process US...')
    import us_workflow
except:
    print('error in US')

# noinspection PyBroadException
try:
    sys.path.append('./code/s_america/brazil/')
    print('Begin process Brazil...')
    import brazil_workflow as b
    b.main()
except:
    print('error in Brazil')

import cal_ef_emission
import draw_pic
