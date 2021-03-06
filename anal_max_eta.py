import numpy as np
import scipy.optimize as spopt
import matplotlib.pyplot as plt
import matplotlib as mpl

import tem

Ptype = tem.Leg()
Ntype = tem.Leg()

Ntype.material = 'MgSi'
Ptype.material = 'HMS'
Ptype.set_prop_fit()
Ntype.set_prop_fit()

T_h = 500.
T_c = 300.

Ptype.T_props = 0.5 * (T_h + T_c)
Ptype.set_TEproperties()
Ntype.T_props = 0.5 * (T_h + T_c)
Ntype.set_TEproperties()

delta_T = T_h - T_c

alpha_p = Ptype.alpha
alpha_n = Ntype.alpha
alpha_pn = alpha_p - alpha_n
k_p = Ptype.k
k_n = Ntype.k 
sigma_p = Ptype.sigma
sigma_n = Ntype.sigma
rho_p = 1. / sigma_p
rho_n = 1. / sigma_n

def get_eta(x):
    """Return thermoelectric device efficiency assuming average
    material properties."""
    A = x[0]
    J = x[1]
    L = x[2]

    R = ( alpha_pn * delta_T / J - (rho_p / A + rho_n) * L ) 
    
    eta = ( J**2 * R / (alpha_pn * T_h * J + delta_T / L * (A * k_p +
    k_n) - J**2 * L * 0.5 * (rho_p / A + rho_n)) )  

    return eta, R

def get_eta_max(L):
    A_opt = (rho_p * k_n / (rho_n * k_p))**0.5

    R_opt = ( (1. + Z * T_bar)**0.5 * (rho_p / A_opt + rho_n) * L)

    J_opt = alpha_pn * delta_T / (R_opt + (rho_p / A_opt + rho_n) * L)  

    x = [A_opt, J_opt, L]
    eta_max_check = get_eta(x)[0] 
    eta_max = ( delta_T / T_h * ((1. + T_bar * Z)**0.5 - 1.) / ((1. +
    T_bar * Z)**0.5 + T_c / T_h) )
    return A_opt, R_opt, J_opt, eta_max_check, eta_max

area = (0.002)**2

A = np.linspace(0.1,3,50)
I = np.linspace(0.1,10,51)
J = I / area
L = np.linspace(0.1,5,52) * 0.001

A0 = 1.44
I0 = 5.07
J0 = I0 / area
L0 = 1. * 0.001

A2d_I, I2d_A = np.meshgrid(A,I)
A2d_L, L2d_A = np.meshgrid(A,L * 1000.)
I2d_L, L2d_I = np.meshgrid(I,L * 1000.)

eta_ij = np.empty([np.size(A), np.size(J)])
eta_jk = np.empty([np.size(J), np.size(L)])
eta_ik = np.empty([np.size(A), np.size(L)])

for i in range(np.size(A)):
    for j in range(np.size(J)):
        x = np.array([A[i], J[j], L0])
        eta_ij[i,j] = get_eta(x)[0]

for j in range(np.size(J)):
    for k in range(np.size(L)):
        x = np.array([A0, J[j], L[k]])
        eta_jk[j,k] = get_eta(x)[0]

for i in range(np.size(A)):
    for k in range(np.size(L)):
        x = np.array([A[i], J0, L[k]])
        eta_ik[i,k] = get_eta(x)[0]

Z = ( (alpha_pn / ((rho_p * k_p)**0.5 + (rho_n * k_n)**0.5))**2. ) 
T_bar = 0.5 * (T_h + T_c)

eta_max = get_eta_max(L0)[-1]
A_opt = 1. / get_eta_max(L0)[0]

xi = ( (-alpha_pn * (eta_max * T_h - delta_T) + np.sqrt((alpha_pn *
    (eta_max * T_h - delta_T))**2. - 4. * (rho_p / A_opt + rho_n) * (1. -
    eta_max / 2.) * (-eta_max * delta_T * (k_p * A_opt + k_n)))) /
    (2. * (rho_p / A_opt + rho_n) * (1. - eta_max / 2.)) )

xi = ( (-(eta_max * alpha_pn * T_h - alpha_pn * delta_T) +
       np.sqrt((eta_max * alpha_pn * T_h - alpha_pn * delta_T)**2. -
       4. * ((rho_p + rho_n / A_opt) - eta_max * (rho_p + rho_n /
       A_opt) / 2. ) * eta_max * delta_T * (k_p + k_n * A_opt))) /
       (2. * ((rho_p + rho_n / A_opt) - eta_max * (rho_p + rho_n /
       A_opt) / 2.)) ) 

L_opt = xi / I * area * 1000.

plt.close('all')

# Plot configuration
FONTSIZE = 15
plt.rcParams['axes.labelsize'] = FONTSIZE
plt.rcParams['axes.titlesize'] = FONTSIZE
plt.rcParams['legend.fontsize'] = FONTSIZE
plt.rcParams['xtick.labelsize'] = FONTSIZE
plt.rcParams['ytick.labelsize'] = FONTSIZE
plt.rcParams['lines.linewidth'] = 1.5
plt.rcParams['lines.markersize'] = 10
plt.rcParams['axes.formatter.limits'] = -3,3

LEVELS = np.linspace(0,eta_max * 100,15)

fig1 = plt.figure()
FCS = plt.contourf(A2d_I, I2d_A, eta_ij.T * 100., levels=LEVELS) 
CB = plt.colorbar(FCS, orientation='vertical', format="%.2f")
CB.set_label('TE Thermal Efficiency (%)')
plt.grid()
plt.xlabel("P:N Area Ratio")
plt.ylabel("Current (A)")
fig1.savefig('Plots/Analytical/nparea_current.pdf')
fig1.savefig('Plots/Analytical/nparea_current.png')

fig2 = plt.figure()
FCS = plt.contourf(I2d_L, L2d_I, eta_jk.T * 100., levels=LEVELS) 
CB = plt.colorbar(FCS, orientation='vertical', format="%.2f")
CB.set_label('TE Thermal Efficiency (%)')
plt.plot(I, L_opt, '-b')
plt.ylim(ymax=L.max()*1000.)
plt.grid()
plt.xlabel("Current (A)")
plt.ylabel("Leg Length (mm)")
fig2.savefig('Plots/Analytical/current_length.pdf')
fig2.savefig('Plots/Analytical/current_length.png')

fig3 = plt.figure()
FCS = plt.contourf(A2d_L, L2d_A, eta_ik.T * 100., levels=LEVELS)
CB = plt.colorbar(FCS, orientation='vertical', format="%.2f")
CB.set_label('TE Thermal Efficiency (%)')
plt.grid()
plt.xlabel("P:N Area Ratio")
plt.ylabel("Leg Length (mm)")
fig3.savefig('Plots/Analytical/nparea_length.pdf')
fig3.savefig('Plots/Analytical/nparea_length.png')

# plt.show()
