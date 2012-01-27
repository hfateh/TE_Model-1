# Chad Baker
# Created on 2011 Feb 10

# Distribution Modules
import numpy as np
import matplotlib.pyplot as plt
import os,sys
from scipy.optimize import fsolve, fmin_tnc, fmin

# User Defined Modules
cmd_folder = os.path.dirname(os.path.abspath('../Modules/hx.py'))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

import harmonica
reload(harmonica)

hohner = harmonica.Harmonica()
hohner.hx1.te_pair.method = 'analytical'
hohner.hx2.te_pair.method = 'analytical'

hohner.solve_harmonica()
