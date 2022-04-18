import time
from n_america.us import us
from s_america.brazil import brazil
from europe.eu27_uk import eu
from europe.russia import russia
from asian.india import india
from asian.japan import japan
from asian.china import china

start = time.perf_counter()

us.main()
brazil.main()
eu.main()
russia.main()
india.main()
japan.main()
china.main()

end = time.perf_counter()
print("运行耗时", round(end))
