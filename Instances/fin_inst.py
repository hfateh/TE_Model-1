# Chad Baker
# Created on 2011 Feb 10

# Distribution Modules
import scipy as sp
import matplotlib.pyplot as plt
import os


# User Defined Modules
# In this directory
import hx
reload(hx)

area = (0.002)**2
length = 1.e-3
current = 5.5 # this is really close to max for these params
area_ratio = 0.69
fill_fraction = 1. / 20.

hx_fins0 = hx.HX()
hx_fins0.width = 30.e-2
hx_fins0.exh.bypass = 0.
hx_fins0.exh.height = 3.5e-2
hx_fins0.length = 1.
hx_fins0.tem.I = current
hx_fins0.tem.length = length

hx_fins0.tem.Ntype.material = 'MgSi'
hx_fins0.tem.Ptype.material = 'HMS'

hx_fins0.tem.Ptype.area = area                           
hx_fins0.tem.Ntype.area = hx_fins0.tem.Ptype.area * area_ratio
hx_fins0.tem.area_void = ( (1. - fill_fraction) / fill_fraction *
                           (hx_fins0.tem.Ptype.area +
                            hx_fins0.tem.Ntype.area) )  

hx_fins0.tem.method = 'analytical'
hx_fins0.type = 'parallel'
hx_fins0.exh.enhancement = "straight fins"
hx_fins0.exh.fin.thickness = 5.e-3
hx_fins0.exh.fins = 30

hx_fins0.exh.T_inlet = 800.
hx_fins0.cool.T_inlet = 300.

hx_fins0.set_mdot_charge()
hx_fins0.solve_hx()


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

plt.figure()
plt.plot(hx_fins0.x_dim * 100., hx_fins0.exh.T_nodes, '-r', label='Exhaust')
plt.plot(hx_fins0.x_dim * 100., hx_fins0.tem.T_h_nodes, '-g', label='TEM Hot Side')
plt.plot(hx_fins0.x_dim * 100., hx_fins0.tem.T_c_nodes, '-k', label='TEM Cold Side')
plt.plot(hx_fins0.x_dim * 100., hx_fins0.cool.T_nodes, '-b', label='Coolant')

plt.xlabel('Distance Along HX (cm)')
plt.ylabel('Temperature (K)')
#plt.title('Temperature v. Distance, '+hx_fins0.type)
plt.grid()
plt.legend(loc='center left')
plt.subplots_adjust(bottom=0.15)
plt.savefig('Plots/temp '+hx_fins0.type+str(hx_fins0.exh.fins)+'.png')
plt.savefig('Plots/temp '+hx_fins0.type+str(hx_fins0.exh.fins)+'.pdf')

# plt.show()

print hx_fins0.power_net