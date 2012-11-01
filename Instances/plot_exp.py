"""Plots results from heat exchanger experiments."""

from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from mpl_toolkits.mplot3d import Axes3D
# pychecker will flag this statement, but it is necessary
import numpy as np
import matplotlib.pyplot as plt

f = open('../output/model_validation/file',"r")
FILE = f.read()
f.close()

# FILE = 'copper'

npzfile = np.load(
    '../output/model_validation/' + FILE + '.npz'
    ) 
deltaP = npzfile['deltaP']
mdot = npzfile['mdot']
Qdot_arr = npzfile['Qdot_arr']
T_in = npzfile['T_in']
Qdot = npzfile['Qdot']
Qdot_surf = npzfile['Qdot_surf']
deltaP_arr = npzfile['deltaP_arr']
mdot2d = npzfile['mdot2d']
T_in2d = npzfile['T_in2d']
velocity = npzfile['velocity']
rho = npzfile['rho']
Re_D = npzfile['Re_D']

# Plot configuration
FONTSIZE = 24
plt.rcParams['axes.labelsize'] = FONTSIZE
plt.rcParams['axes.titlesize'] = FONTSIZE
plt.rcParams['legend.fontsize'] = FONTSIZE
plt.rcParams['xtick.labelsize'] = FONTSIZE
plt.rcParams['ytick.labelsize'] = FONTSIZE
plt.rcParams['lines.linewidth'] = 1.5
plt.rcParams['lines.markersize'] = 10

plt.show()
plt.close()
    
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# ax.scatter(
#     mdot, T_in, Qdot
#     )
# ax.scatter(
#     mdot, T_in, Qdot_arr, color='r',
#     )
# ax.set_xlabel(r'$\dot{m}$ (kg/s)')
# ax.set_ylabel(r'$T_{exh,in}$ (K)')
# ax.set_zlabel(r'$\dot{Q}$')
# plt.savefig('../Plots/plot_exp/' + FILE + '/Qdot.pdf')

# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# ax.scatter(
#     mdot, T_in, deltaP
#     )
# ax.scatter(
#     mdot, T_in, deltaP_arr,
#     color='r'
#     )

# ax.set_xlabel(r'$\dot{m}$ (kg/s)')
# ax.set_ylabel(r'$T_{exh,in}$ (K)')
# ax.set_zlabel(r'$\Delta P$')
# plt.savefig('../Plots/plot_exp/' + FILE + '/deltaP.pdf')

# fig = plt.figure()
# ax = fig.gca(projection='3d')
# ax.scatter(
#     mdot, T_in, Qdot
#     )
# surf = ax.plot_surface(
#     mdot2d, T_in2d, Qdot_surf, alpha=0.4, rstride=1,
#     cstride=1, cmap=cm.jet, linewidth=0, antialiased=False
#     )
# fig.colorbar(surf, shrink=0.5, aspect=5)
# ax.set_xlabel(r'$\dot{m}$ (kg/s)')
# ax.set_ylabel(r'$T_{exh,in}$ (K)')
# ax.set_zlabel(r'$\dot{Q}$')
# plt.savefig('../Plots/plot_exp/' + FILE + '/Qdot_fit.pdf')

f2 = open("../output/model_validation/fit", "r")
fit_status = f2.read()
f2.close()

fig = plt.figure()
dimless_P_mod = deltaP_arr / (0.5 * rho * velocity ** 2.)
dimless_P_exp = deltaP / (0.5 * rho * velocity ** 2.)
plt.plot(
    Re_D, dimless_P_mod * 1e3, linestyle='', marker='s', color='b',
    label='model'
    )
plt.plot(
    Re_D, dimless_P_exp * 1e3, linestyle='', marker='o', color='r',
    label='experiment'
    )
plt.xlabel(r'Re$_D$')
plt.ylabel(r'$\frac{\Delta P}{1/2 \rho U^2}$x10$^3$')
plt.xticks(rotation=45)
plt.subplots_adjust(left=0.15, bottom=0.21)
plt.grid()
plt.legend(loc='best')
plt.savefig(
    '../Plots/plot_exp/' + FILE + '_dimless_P.pdf'
    )

fig = plt.figure()
plt.plot(
    mdot, Qdot_arr, linestyle='', marker='s', color='b', label='model'
    )
plt.plot(
    mdot, Qdot, linestyle='', marker='o', color='r', label='experiment'
    )
plt.xlabel("Exhaust Mass Flow Rate (kg/s)")
plt.ylabel("Heat Transfer Rate (kW)")
plt.grid()
plt.legend(loc='best')
plt.xticks(rotation=45)
plt.subplots_adjust(bottom=0.21)
plt.savefig(
    '../Plots/plot_exp/' + FILE + '_Qdot_v_mdot.pdf'
    )

fig = plt.figure()
plt.plot(
    T_in, Qdot_arr, linestyle='', marker='s', color='b', label='model'
    )
plt.plot(
    T_in, Qdot, linestyle='', marker='o', color='r', label='experiment'
    )
plt.xlabel("HX Inlet Temperature (K)")
plt.ylabel("Heat Transfer Rate (kW)")
plt.grid()
plt.legend(loc='best')
plt.xticks(rotation=45)
plt.subplots_adjust(bottom=0.21)
plt.savefig(
'../Plots/plot_exp/' + FILE + '_Qdot_v_T_in.pdf'
)

# plt.show()
