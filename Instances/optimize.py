# Chad Baker
# Nick Malaya
# Created on 2011 August 30th
# using
# http://docs.scipy.org/doc/scipy/reference/optimize.html

# Distribution Modules
import time
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import os, sys
from scipy.optimize import fmin
from scipy.optimize import fmin_powell
from scipy.optimize import anneal
from scipy.optimize import fmin_l_bfgs_b

# User Defined Modules
cmd_folder = os.path.dirname(os.path.abspath('../Modules/hx.py'))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)
import hx
reload(hx)
    
t0 = time.clock()

area = (0.002)**2
length = 1.e-3
current = 4.
area_ratio = 0.69
fill_fraction = 1. / 40.

hx = hx.HX()
hx.te_pair.method = 'analytical'
hx.width = 30.e-2
hx.exh.bypass = 0.
hx.exh.height = 3.5e-2
hx.cool.mdot = 1.
hx.length = 1.
hx.te_pair.I = current
hx.te_pair.length = length

hx.te_pair.Ptype.material = 'HMS'
hx.te_pair.Ntype.material = 'MgSi'

hx.te_pair.Ptype.area = area                           
hx.te_pair.Ntype.area = hx.te_pair.Ptype.area * area_ratio
hx.te_pair.area_void = ( (1. - fill_fraction) / fill_fraction *
                           (hx.te_pair.Ptype.area +
                            hx.te_pair.Ntype.area) )  

hx.type = 'parallel'

hx.exh.T_inlet = 800.
hx.exh.P = 100.
hx.cool.T_inlet = 300.

hx.set_mdot_charge()

# this is our optimization method 
# (what we desire to optimize)
def optim(apar):
    # unpack guess vector
    apar=np.asarray(apar)
    hx.te_pair.leg_ratio     = apar[0]
    hx.te_pair.fill_fraction = apar[1]
    hx.te_pair.length        = apar[2]
    hx.te_pair.I             = apar[3]

    # reset surrogate variables
    hx.te_pair.Ntype.area = hx.te_pair.leg_ratio*hx.te_pair.Ptype.area
    hx.te_pair.area_void = ( (1. - hx.te_pair.fill_fraction) / hx.te_pair.fill_fraction *
                           (hx.te_pair.Ptype.area + hx.te_pair.Ntype.area) )
    hx.set_constants()
    hx.solve_hx()

    # 1/power_net -- fmin is a minimization routine
    return 1./(hx.power_net)

# dummy function
def fprime():
    return 1

#
# parameter optimization:
#
#   I) te_pair.leg_ratio
#  II) te_pair.fill_fraction
# III) hx.te_pair.length
#  IV) hx.te_pair.I
#
# initial guess {I-IV}:
x0 = 0.71, 0.02, .001, 4.5

# bounds for the parameters {I-IV}:
xb = [(0.2,1.5),(0.001,0.05),(0.0005,0.01),(1,10.0)]

# optimization loop
print "Beginning optimization..."

# find min
#xmin1 = fmin(optim,x0)

# find min using L-BFGS-B algorithm
# xmin1 = fmin_l_bfgs_b(optim,x0,fprime,approx_grad=True,bounds=xb)

# Find min using Powell's method
# xmin_powell = fmin_powell(optim,x0)

# Find min using downhill simplex algorithm
xmin1 = fmin(optim,x0)
t1 = time.clock() - t0
print """xmin1 found. Switching to numerical model.
Elapsed time solving xmin1 =""", t1 

# Find min again using the numerical model.  The analytical model
# should run first to provide a better initial guess.
hx.te_pair.method = 'numerical'
xmin2 = fmin(optim, xmin1)
t2 = time.clock() - t1

print """xmin2 found.
Elapsed time solving xmin2 =""", t2

t = time.clock() - t0

print """Total elapsed time =""", t 

print "Finalizing optimization..."

# output optimal parameters

print """\nProgram finished.
Writing to output/optimize/xmin1 and output/optimize/xmin2"""

np.savetxt('output/optimize/xmin1', xmin1)
np.savetxt('output/optimize/xmin2', xmin2)

print xmin1
print xmin2

# notes:
#
# define a variable, te_pair.leg_ratio = te_pair.Ntype.area / te_pair.Ptype.area .  
# Keep te_pair.Ptype.area = 10.e-6 and vary te_pair.Ntype.area by varying leg_ratio.  
# leg_ratio can be anywhere from 0.2 up to 5.
#
# The next parameter is the leg area to the void area. 
# define te_pair.fill_fraction = te_pair.Ptype.area / te_pair.area_void.   
# vary this between 1 and 100 by changing area_void.  
#
# The next one is leg length or height, hx.te_pair.length.  
# Vary this between 0.0005 and 0.01.  
#
# The last one is current, hx.te_pair.I.  Vary this between 0.1 and 10. 
#
