# Chad Baker
# Created on 2011 Feb 10

# Distribution Modules
import numpy as np
import matplotlib.pyplot as plt
import os


# User Defined Modules
# In this directory
import hx
reload(hx)

# parameters for TE legs
area = (0.002)**2
length = 1.e-3
current = 5. # this is really close to max for these params
area_ratio = 0.69
fill_fraction = 1. / 75. # this is still about right so fill_fraction
                         # may be independent of current.  

hx_ducts = hx.HX()
hx_ducts.width = 30.e-2
# hx_ducts.exh.bypass = 0.
hx_ducts.exh.height = 3.5e-2
hx_ducts.length = 1.
hx_ducts.tem.I = current
hx_ducts.tem.length = length

hx_ducts.tem.Ntype.material = 'MgSi'
hx_ducts.tem.Ptype.material = 'HMS'

hx_ducts.tem.Ptype.area = area                           
hx_ducts.tem.Ntype.area = hx_ducts.tem.Ptype.area * area_ratio
hx_ducts.tem.area_void = ( (1. - fill_fraction) / fill_fraction *
                           (hx_ducts.tem.Ptype.area +
                            hx_ducts.tem.Ntype.area) )  

hx_ducts.tem.method = 'analytical'
hx_ducts.type = 'parallel'
hx_ducts.exh.enhancement = "straight fins"
hx_ducts.exh.fin.thickness = 5.e-3
hx_ducts.exh.fins = 22 # 22 fins seems to be best.  

hx_ducts.exh.T_inlet = 800.
hx_ducts.exh.P = 100.
hx_ducts.cool.T_inlet = 300.

ducts = np.arange(2, 18, 1)

hx_ducts.exh.height_array = 3.5e-2 / ducts
hx_ducts.cool.height_array = 2.e-2 / (ducts + 1.)

hx_ducts.set_mdot_charge()
hx_ducts.exh.mdot0 = hx_ducts.exh.mdot 

hx_ducts.exh.mdot_array = hx_ducts.exh.mdot0 / ducts
hx_ducts.cool.mdot_array = hx_ducts.cool.mdot * 2. / (ducts + 1.) 

hx_ducts.height_array = ( ducts * hx_ducts.exh.height_array +  (ducts
                            + 1) * hx_ducts.cool.height_array ) 

# Initializing arrays for storing loop results.  
hx_ducts.Qdot_array = np.zeros(np.size(ducts))
hx_ducts.tem.power_array = np.zeros(np.size(ducts)) 
hx_ducts.power_net_array = np.zeros(np.size(ducts))
hx_ducts.Wdot_pumping_array = np.zeros(np.size(ducts)) 


for i in np.arange(np.size(ducts)):
    hx_ducts.exh.height = hx_ducts.exh.height_array[i]
    hx_ducts.cool.height = hx_ducts.cool.height_array[i]

    hx_ducts.exh.mdot = hx_ducts.exh.mdot_array[i]
    hx_ducts.cool.mdot = hx_ducts.cool.mdot_array[i]

    hx_ducts.solve_hx()
    print "Finished solving for", ducts[i], "ducts\n"
    
    hx_ducts.Qdot_array[i] = hx_ducts.Qdot * ducts[i]
    hx_ducts.tem.power_array[i] = hx_ducts.tem.power_total * ducts[i]
    hx_ducts.power_net_array[i] = hx_ducts.power_net * ducts[i]
    hx_ducts.Wdot_pumping_array[i] = hx_ducts.Wdot_pumping * ducts[i]
    
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

FIGDIM1 = ([0.12, 0.12, 0.75, 0.75])

XTICKS = hx_ducts.exh.height_array[0::3].copy() * 100.
XTICKS = list(XTICKS)

for i in range(len(XTICKS)):
    XTICKS[i] = ('{:01.1f}'.format(XTICKS[i])) 

XTICKS[0] = ''
fig = plt.figure()
ax1 = fig.add_axes(FIGDIM1)
ax1.plot(ducts, hx_ducts.Qdot_array / 10., 'db', label=r'$\dot{Q}/10$') 
ax1.plot(ducts, hx_ducts.tem.power_array, 'og', label='TEM')
ax1.plot(ducts, hx_ducts.power_net_array, 'sr', label='$P_{net}$')  
ax1.plot(ducts, hx_ducts.Wdot_pumping_array, '*k', label='Pumping')
ax1.legend(loc='best')
ax1.grid()
ax1.set_xlabel('Ducts')
ax1.set_ylabel('Power (kW)')
ax1.set_ylim(0,7)
ax1.set_ylim(ymin=0)
ax2 = plt.twiny(ax1)
plt.xticks(np.arange(len(XTICKS)), XTICKS)
ax2.set_xlabel('Exhaust Duct Height (cm)')

fig.savefig('Plots/power v stacked ducts.pdf')
fig.savefig('Plots/power v stacked ducts.pdf')

# plt.show()

print "\nCurrent =", current
print "Length =", length
print "Fill Fraction", fill_fraction
print "power =", hx_ducts.power_net_array.max()
