# Chad Baker
# Created on 2011 Feb 10

# Distribution Modules
import numpy as np
import matplotlib.pyplot as plt
import os,sys
import time

# User Defined Modules
cmd_folder = os.path.dirname(os.path.abspath('../Modules/hx.py'))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)
import hx
reload(hx)

time0 = time.clock()

hx_osf_opt = hx.HX()

hx_osf_opt.width = 20. * 2.54e-2
hx_osf_opt.exh.height = 2.5 * 2.54e-2
hx_osf_opt.cool.height = 1. * 2.54e-2
hx_osf_opt.length = 20. * 2.54e-2

hx_osf_opt.te_pair.Ntype.material = 'MgSi'
hx_osf_opt.te_pair.Ptype.material = 'HMS'

hx_osf_opt.te_pair.set_leg_areas()

hx_osf_opt.te_pair.method = 'numerical'
hx_osf_opt.type = 'counter'

hx_osf_opt.exh.set_enhancement('OffsetStripFin')
# hx_osf_opt.exh.enh.thickness = 0.25 * 2.54e-2
# 0.25 inches is too thick to manufacture
hx_osf_opt.exh.enh.l = 10.e-3

hx_osf_opt.cool.enh = hx_osf_opt.cool.set_enhancement('IdealFin')

OPT_PAR_DIR = "../output/osf_opt/"

hx_osf_opt.exh.enh.spacing = (
    np.load(OPT_PAR_DIR + 'exh.enh.spacing.npy')     
    )
hx_osf_opt.te_pair.fill_fraction = (
    np.load(OPT_PAR_DIR + 'te_pair.fill_fraction.npy')
    )
hx_osf_opt.te_pair.I = (
    np.load(OPT_PAR_DIR + 'te_pair.I.npy')            
    )
hx_osf_opt.te_pair.leg_area_ratio = (
    np.load(OPT_PAR_DIR + 'te_pair.leg_area_ratio.npy')
    )
hx_osf_opt.te_pair.length = (
    np.load(OPT_PAR_DIR + 'te_pair.length.npy')       
    )

hx_osf_opt.exh.T_inlet = 800.
hx_osf_opt.cool.T_inlet_set = 300.
hx_osf_opt.cool.T_outlet = 310.

hx_osf_opt.set_mdot_charge()

hx_osf_opt.apar_list.append(['hx_osf_opt', 'exh', 'enh', 'spacing'])
# hx_osf_opt.apar_list.append(['hx_osf_opt', 'exh', 'enh', 'l'])
# l cannot be allowed to vary or it will get really large.  

hx_osf_opt.optimize()
hx_osf_opt.save_opt_par(OPT_PAR_DIR)

print "\nProgram finished."

elapsed = time.clock() - time0

print "elapsed time:", elapsed

print "\nPlotting..."

# Plot configuration
FONTSIZE = 20
plt.rcParams['axes.labelsize'] = FONTSIZE
plt.rcParams['axes.titlesize'] = FONTSIZE
plt.rcParams['legend.fontsize'] = FONTSIZE
plt.rcParams['xtick.labelsize'] = FONTSIZE
plt.rcParams['ytick.labelsize'] = FONTSIZE
plt.rcParams['lines.linewidth'] = 1.5

plt.close()

plt.figure()
plt.plot(hx_osf_opt.x * 100., hx_osf_opt.exh.T_nodes, '-r', label='Exhaust')
plt.plot(hx_osf_opt.x * 100., hx_osf_opt.te_pair.T_h_nodes, '-g', label='TE_PAIR Hot Side')
plt.plot(hx_osf_opt.x * 100., hx_osf_opt.te_pair.T_c_nodes, '-k', label='TE_PAIR Cold Side')
plt.plot(hx_osf_opt.x * 100., hx_osf_opt.cool.T_nodes, '-b', label='Coolant')

plt.xlabel('Distance Along HX (cm)')
plt.ylabel('Temperature (K)')
#plt.title('Temperature v. Distance, '+hx_osf_opt.type)
plt.grid()
plt.legend(loc='center left')
plt.subplots_adjust(bottom=0.15)

# plt.show()

print "length of osf", hx_osf_opt.exh.enh.l * 1000., 'mm'
print "spacing", hx_osf_opt.exh.enh.spacing * 1000., 'mm'
print "power net:", hx_osf_opt.power_net * 1000., 'W'
print "power raw:", hx_osf_opt.te_pair.power_total * 1000., 'W'
print "pumping power:", hx_osf_opt.Wdot_pumping * 1000., 'W'
hx_osf_opt.exh.volume = hx_osf_opt.exh.height * hx_osf_opt.exh.width * hx_osf_opt.length
print "exhaust volume:", hx_osf_opt.exh.volume * 1000., 'L'
print "exhaust power density:", hx_osf_opt.power_net / hx_osf_opt.exh.volume, 'kW/m^3'


