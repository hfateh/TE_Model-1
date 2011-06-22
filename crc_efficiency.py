# Chad Baker
# Created on 2011 Feb 10

# Distribution Modules
import scipy as sp
import matplotlib.pyplot as mpl
import os

os.chdir('/home/chad/Documents/UT Stuff/Research/Diesel TE/TE_Model')

# User Defined Modules
# In this directory
import tem
reload(tem)

Ntype = tem.Leg()
Ntype.material = 'ex1 n-type'
Ntype.area = (0.01)**2
Ntype.T_h_goal = 750.
Ntype.T_c = 400.

Ptype = tem.Leg()
Ptype.material = 'ex1 p-type'
Ptype.area = (0.01)**2 # area (m^2)
Ptype.T_h_goal = 750.
Ptype.T_c = 400.

Ntype.current_density = sp.arange(20., 51., 1.) * 100.**2
Ntype.currents = Ntype.current_density * Ntype.area
Ntype.etas = sp.zeros(sp.size(Ntype.currents))
for i in sp.arange(sp.size(Ntype.currents)):
    Ntype.I = Ntype.currents[i]
    Ntype.solve_leg()
    Ntype.etas[i] = Ntype.eta

Ptype.current_density = sp.arange(0., -2.55, -0.05) * 100.**2
Ptype.currents = Ptype.current_density * Ptype.area
Ptype.etas = sp.zeros(sp.size(Ptype.currents))
for i in sp.arange(sp.size(Ptype.currents)):
    Ptype.I = Ptype.currents[i]
    Ptype.solve_leg()
    Ptype.etas[i] = Ptype.eta

# Plot configuration
FONTSIZE = 18
mpl.rcParams['axes.labelsize'] = FONTSIZE
mpl.rcParams['axes.titlesize'] = FONTSIZE
mpl.rcParams['legend.fontsize'] = FONTSIZE
mpl.rcParams['xtick.labelsize'] = FONTSIZE
mpl.rcParams['ytick.labelsize'] = FONTSIZE
mpl.rcParams['lines.linewidth'] = 1.5

fig1 = mpl.figure()
ax1 = fig1.add_subplot(111)
ax1.plot(Ptype.current_density / 100.**2, Ptype.etas * 100.,
         label=Ptype.material, color='r')
ax1.set_xlabel(r'Current Density ($A/cm^2$)')
ax1.set_ylabel(r'$\eta$ (%)')
ax1.set_xlim(-2.5, 0.5)
ax2 = ax1.twiny()
ax3 = mpl.twinx()
ax3.plot(Ntype.current_density / 100.**2, Ntype.etas * 100.,
         label=Ntype.material, color='k')
ax3.set_xlim(20,50)
ax3.grid()
#ax2.set_title('Efficiency v. Current\n\n\n')  
fig1.subplots_adjust(bottom=0.12)
fig1.subplots_adjust(top=0.88)
fig1.savefig('Plots/eta v current ex1.pdf')
fig1.savefig('Plots/eta v current ex1.png')

# fig2 = mpl.figure()
# mpl.plot(Ntype.current_density / 100.**2, Ntype.etas * 100.,
#          label='P type')
# mpl.grid()
# mpl.xlabel(r'Current Density ($A/cm^2$)')
# mpl.ylabel(r'$\eta$ (%)')
# mpl.title('Efficiency v. Current\n' + Ntype.material)  
# mpl.legend(loc='best')
# fig2.subplots_adjust(bottom=0.12)
# fig2.subplots_adjust(top=0.88)
# fig2.savefig('Plots/eta v current ' + Ntype.material + '.pdf')
# fig2.savefig('Plots/eta v current ' + Ntype.material + '.png')

mpl.show()
