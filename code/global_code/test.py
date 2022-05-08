# from n_america.us import us_workflow
# from s_america.brazil import brazil_workflow
# from europe.eu27_uk import eu_workflow
# from europe.russia import russia_workflow
# from asian.china import china_workflow
# from asian.india import india_workflow
# from asian.japan import japan_workflow
import sys
sys.dont_write_bytecode = True
sys.path.append('./code/asian/china/')
import china_workflow.py
sys.path.append('./code/asian/india/')
import india_workflow.py
sys.path.append('./code/asian/japan/')
import japan_workflow.py
sys.path.append('./code/europe/eu27_uk/')
import eu_workflow.py
sys.path.append('./code/europe/russia/')
import russia_workflow.py
sys.path.append('./code/n_america/us/')
import us_workflow.py
sys.path.append('./code/s_amercia/brazil/')
import brazil_workflow.py

