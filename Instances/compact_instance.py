# Chad Baker
# Created on 2011 Feb 10

# Distribution Modules
import matplotlib.pyplot as plt
import numpy as np


# User Defined Modules
# In this directory
import hx
reload(hx)

area = (0.002)**2
length = 2.e-3

hx = hx.HX()
hx.te_pair.method = 'analytical'
hx.thermoelectrics_on = True
hx.width = 9.e-2
hx.length = 0.195
hx.exh.bypass = 0.
hx.exh.height = 1.e-2
Vdot_cool = 4. # coolant flow rate (GPM) 
mdot_cool = 4. / 60. * 3.8 / 1000. * hx.cool.rho  
hx.cool.mdot = mdot_cool / 60. * 3.8
hx.cool.height = 0.5e-2
hx.te_pair.I = 4.5
hx.te_pair.length = length
hx.te_pair.Ntype.material = 'MgSi'
hx.te_pair.Ntype.area = area
hx.te_pair.Ptype.material = 'HMS'
hx.te_pair.Ptype.area = area * 2. 
hx.te_pair.area_void = 25. * area
hx.type = 'counter'
hx.exh.P = 100.

hx.cool.T_outlet = 300.
hx.exh.T_inlet = 700.
hx.set_mdot_charge()
hx.exh.mdot = hx.exh.mdot * 0.1
hx.solve_hx()

print "\nProgram finished."

# Plot configuration
FONTSIZE = 20
plt.rcParams['axes.labelsize'] = FONTSIZE
plt.rcParams['axes.titlesize'] = FONTSIZE
plt.rcParams['legend.fontsize'] = FONTSIZE
plt.rcParams['xtick.labelsize'] = FONTSIZE
plt.rcParams['ytick.labelsize'] = FONTSIZE
plt.rcParams['lines.linewidth'] = 1.5

plt.figure()
plt.plot(hx.x_dim * 100., hx.exh.T_nodes, '-r', label='Exhaust')
plt.plot(hx.x_dim * 100., hx.te_pair.T_h_nodes, '-g', label='TE_PAIR Hot Side')
plt.plot(hx.x_dim * 100., hx.te_pair.T_c_nodes, '-k', label='TE_PAIR Cold Side')
plt.plot(hx.x_dim * 100., hx.cool.T_nodes, '-b', label='Coolant')

plt.xlabel('Distance Along HX (cm)')
plt.ylabel('Temperature (K)')
#plt.title('Temperature v. Distance, '+hx.type)
plt.grid()
plt.legend(loc='best')
plt.subplots_adjust(bottom=0.15)
plt.savefig('Plots/temp '+hx.type+'.png')
plt.savefig('Plots/temp '+hx.type+'.pdf')

plt.show()
