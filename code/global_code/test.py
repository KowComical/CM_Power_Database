import warnings
warnings.filterwarnings('ignore')
import sys
sys.dont_write_bytecode = True
sys.path.append('./code/asian/china/')
import china_workflow
sys.path.append('./code/asian/india/')
import india_workflow as i
i.main()
sys.path.append('./code/asian/japan/')
import japan_workflow as j
j.main()
sys.path.append('./code/europe/eu27_uk/')
import eu_workflow as e
e.main()
sys.path.append('./code/europe/russia/')
import russia_workflow
sys.path.append('./code/n_america/us/')
import us_workflow
sys.path.append('./code/s_america/brazil/')
import brazil_workflow as b
b.main()

