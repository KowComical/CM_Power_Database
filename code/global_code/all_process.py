import warnings
warnings.filterwarnings('ignore')
import sys
sys.dont_write_bytecode = True

try:
    sys.path.append('./code/asian/china/')
    print('Begin process China...')
    import china_workflow
except Exception as e:
    print(e)

try:
    sys.path.append('./code/asian/india/')
    print('Begin process India...')
    import india_workflow as i
    i.main()
except Exception as e:
    print(e)

try:
    sys.path.append('./code/asian/japan/')
    print('Begin process Japan...')
    import japan_workflow as j
    j.main()
except Exception as e:
    print(e)

try:
    sys.path.append('./code/europe/eu27_uk/')
    print('Begin process EU...')
    import eu_workflow as e
    e.main()
except Exception as e:
    print(e)

try:
    sys.path.append('./code/europe/russia/')
    print('Begin process Russia...')
    import russia_workflow
except Exception as e:
    print(e)

try:
    sys.path.append('./code/n_america/us/')
    print('Begin process US...')
    import us_workflow
except Exception as e:
    print(e)

try:
    sys.path.append('./code/s_america/brazil/')
    print('Begin process Brazil...')
    import brazil_workflow as b
    b.main()
except Exception as e:
    print(e)
try:
    import iea_workflow
except Exception as e:
    print(e)
import cal_ef_emission
import draw_pic
