# Chad Baker
# Created on 2011 Feb 10

# Distribution Modules
import matplotlib.pyplot as plt
import os, sys
from scipy.optimize import fsolve
import numpy as np

# User Defined Modules

cmd_folder = os.path.dirname(os.path.abspath('../Modules/hx.py'))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

import hx
reload(hx)
import enhancement
reload(enhancement)
    
# parameters from xmin2
# 7.049488398024472691e-01
# 2.074354421989454272e-02
# 1.033370547666811676e-03
# 4.634972529966798760e+00

leg_area = (0.002)**2
leg_length = 1.03e-3
current = 4.63
area_ratio = 0.705
fill_fraction = 2.07e-2

hx_jets = hx.HX()
hx_jets.exh.enhancement = enhancement.JetArray()

hx_jets.te_pair.method = 'analytical'
hx_jets.width = 30.e-2
hx_jets.exh.height = 3.5e-2
hx_jets.cool.mdot = 1.
hx_jets.length = 1.
hx_jets.te_pair.I = current
hx_jets.te_pair.length = leg_length

hx_jets.te_pair.Ptype.material = 'HMS'
hx_jets.te_pair.Ntype.material = 'MgSi'

hx_jets.te_pair.Ptype.area = leg_area                           
hx_jets.te_pair.Ntype.area = hx_jets.te_pair.Ptype.area * area_ratio
hx_jets.te_pair.area_void = ( (1. - fill_fraction) / fill_fraction *
                           (hx_jets.te_pair.Ptype.area +
                            hx_jets.te_pair.Ntype.area) )  

hx_jets.type = 'counter'

hx_jets.exh.T_inlet = 800.
hx_jets.cool.T_inlet_set = 300.
hx_jets.cool.T_outlet = 310.

H = np.linspace(0.5, 4., 25) * 1e-2
# range of annular height to be used for getting results
D = np.linspace(1, 4., 26) * 0.001
# range of jet diameter
X = np.linspace(5., 20., 26) * 0.001
# range of jet spacing

power_net_HD = np.zeros([H.size,D.size])
power_net_DX = np.zeros(D.size)
power_net_XH = np.zeros(X.size)

hx_jets.set_mdot_charge()

def set_values():
    hx_jets.exh.enhancement.spacing = 0.5e-2
    hx_jets.exh.enhancement.D = 1.0e-3
    hx_jets.exh.enhancement.H = 1.0e-2

set_values()

for i in range(H.size):
    hx_jets.exh.enhancement.H = H[i]
    # hx_jets.cool.T_outlet = fsolve(hx_jets.get_T_inlet_error, x0=hx_jets.cool.T_outlet)
    hx_jets.solve_hx()
    power_net_HD[i] = hx_jets.power_net
    if i%5 == 0:
        print "loop 1 of 3, iteration", i, "of", H.size

set_values()
    
for i in range(D.size):
    hx_jets.exh.enhancement.D = D[i]
    # hx_jets.cool.T_outlet = fsolve(hx_jets.get_T_inlet_error, x0=hx_jets.cool.T_outlet)
    hx_jets.solve_hx()
    power_net_DX[i] = hx_jets.power_net
    if i%5 == 0:
        print "loop 2 of 3, iteration", i, "of", D.size

set_values()
    
for i in range(X.size):
    hx_jets.exh.enhancement.spacing = X[i]
    # hx_jets.cool.T_outlet = fsolve(hx_jets.get_T_inlet_error, x0=hx_jets.cool.T_outlet)
    hx_jets.solve_hx()
    power_net_XH[i] = hx_jets.power_net
    if i%5 == 0:
        print "loop 3 of 3, iteration", i, "of", X.size

print "\nProgram finished."
print "\nPlotting..."

# Plot configuration
FONTSIZE = 20
plt.rcParams['axes.labelsize'] = FONTSIZE
plt.rcParams['axes.titlesize'] = FONTSIZE
plt.rcParams['legend.fontsize'] = FONTSIZE
plt.rcParams['xtick.labelsize'] = FONTSIZE
plt.rcParams['ytick.labelsize'] = FONTSIZE
plt.rcParams['lines.linewidth'] = 1.5
plt.rcParams['figure.subplot.left'] = 0.15
plt.rcParams['figure.subplot.right'] = 0.85
plt.rcParams['figure.subplot.bottom'] = 0.15
plt.rcParams['figure.subplot.top'] = 0.9

plt.close('all')

plt.figure()
plt.plot(H * 100., power_net_HD)
plt.xlabel('Annular Duct Height (cm)')
plt.ylabel('Net Power')
plt.grid()

plt.figure()
plt.plot(D * 1000., power_net_DX)
plt.xlabel('Jet Orifice Diameter (mm)')
plt.ylabel('Net Power')
plt.grid()

plt.figure()
plt.plot(X * 100., power_net_XH)
plt.xlabel('Jet Spacing (cm)')
plt.ylabel('Net Power')
plt.grid()

# plt.show()

