import warnings
warnings.filterwarnings('ignore')
import sys
sys.dont_write_bytecode = True

sys.path.append('./code/asian/china/')
print('Begin process China...')
import china_workflow

sys.path.append('./code/asian/india/')
print('Begin process India...')
import india_workflow as i
i.main()

sys.path.append('./code/asian/japan/')
print('Begin process japan...')
import japan_workflow as j
j.main()

sys.path.append('./code/europe/eu27_uk/')
print('Begin process EU...')
import eu_workflow as e
e.main()

sys.path.append('./code/europe/russia/')
print('Begin process Russia...')
import russia_workflow

sys.path.append('./code/n_america/us/')
print('Begin process US...')
import us_workflow

sys.path.append('./code/s_america/brazil/')
print('Begin process Brazil...')
import brazil_workflow as b
b.main()

