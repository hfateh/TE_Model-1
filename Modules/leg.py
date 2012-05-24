# Distribution modules

import types
import numpy as np
import matplotlib.pyplot as mpl
import time
from scipy.optimize import fsolve
from scipy.integrate import odeint

# User defined modules
import te_prop
reload(te_prop)

class Leg(object):
    """class for individual p-type or n-type TE leg"""

    def __init__(self):
        """Sets the following: 
        self.I : current (A) in TE leg pair
        self.nodes : number of nodes for finite difference model
        self.length : leg length (m)
        self.area = : leg area (m^2)
        self.T_h_goal : hot side temperature (K) that matches HX BC
        self.T_c : cold side temperature (K)
        self.T : initial array for temperature (K) for finite
        difference model
        self.q : initial array for heat flux (W/m^2)
        self.V_nodes : initial array for Seebeck voltage (V)
        self.P_flux_nodes : initial array for power flux in node (W/m^2)

        Binds the following methods:
        te_prop.set_prop_fit
        te_prop.set_TEproperties"""
    
        self.I = 0.5 
        self.nodes = 10 
        self.length = 1.e-3
        self.area = (3.e-3)**2. 
        self.T_h_goal = 550. 
        self.T_c = 350. 

        self.alpha_nodes = np.zeros(self.nodes)
        self.rho_nodes = np.zeros(self.nodes)
        self.k_nodes = np.zeros(self.nodes)
        self.V_nodes = np.zeros(self.nodes) 
        self.P_flux_nodes = np.zeros(self.nodes) 

        self.set_constants()

        self.set_prop_fit = types.MethodType(te_prop.set_prop_fit,
        self) 
        self.set_TEproperties = (
        types.MethodType(te_prop.set_TEproperties, self) )
    
    def set_constants(self):
        """sets a few parameters"""
        self.node_length = self.length / self.nodes
        # length of each node (m)
        self.x = np.linspace(0., self.length, self.nodes) 

        self.J = self.I / self.area # (Amps/m^2)

    def set_q_c_guess(self):
        """Sets guess for q_c to be used by iterative solutions.""" 
        self.T_h = self.T_h_goal
        self.T_props = 0.5 * (self.T_h + self.T_c)
        self.set_TEproperties(T_props=self.T_props)
        delta_T = self.T_h - self.T_c
        self.q_c = ( self.alpha * self.T_c * self.J - delta_T /
                     self.length * self.k - self.J**2 * self.length * self.rho )

        self.q_c_guess = self.q_c

    def get_Yprime(self, y, x):
        """Function for evaluating the derivatives of
        temperature and heat flux w.r.t. x."""
        
        T = y[0]
        q = y[1]
        V = y[2]
        R_int = y[3]
        
        self.T_props = T
        self.set_TEproperties(self.T_props)

        dT_dx = ( 1. / self.k * (self.J * T * self.alpha - q) )   

        dq_dx = ( (self.rho * self.J**2. * (1. + self.alpha**2. * T /
        (self.rho * self.k)) - self.J * self.alpha * q / self.k) )      

        dV_dx = ( self.alpha * dT_dx + self.J * self.rho ) 
        
        dR_dx = ( self.rho / self.area )  

        return dT_dx, dq_dx, dV_dx, dR_dx
            
    def solve_leg_once(self, q_c):
        """Solution procedure comes from Ch. 12 of Thermoelectrics
        Handbook, CRC/Taylor & Francis 2006. The model guesses a cold
        side heat flux and changes that heat flux until it results in
        the desired hot side temperature.  Hot side and cold side
        temperature as well as hot side heat flux must be
        specified.""" 

        self.q_c = q_c
        self.y0 = np.array([self.T_c, self.q_c, 0, 0])

        self.y = odeint(self.get_Yprime, y0=self.y0, t=self.x) 

        self.T_nodes = self.y[:,0]
        self.q_nodes = self.y[:,1]
        self.V_nodes = self.y[:,2]
        self.R_int_nodes = self.y[:,3]

        self.T_h = self.T_nodes[-1]
        self.q_h = self.q_nodes[-1]

        self.V = self.V_nodes[-1] 
        self.R_internal = self.R_int_nodes[-1]

        self.P_flux = self.J * self.V
        self.P = self.P_flux * self.area
        # Power for the entire leg (W)

        self.eta = self.P / (self.q_h * self.area)
        # Efficiency of leg
        self.R_load = - self.V / self.I

        self.T_h_error = self.T_h - self.T_h_goal
        
        return self.T_h_error
            
    def solve_leg(self):
        """Solves leg until specified hot side temperature is met.""" 

        self.set_q_c_guess()
        fsolve(self.solve_leg_once, x0=self.q_c_guess) 

    def solve_leg_anal(self):
        """Analytically solves the leg based on lumped properties.  No
        iteration is needed."""

        self.T_h = self.T_h_goal
        self.T_props = 0.5 * (self.T_h + self.T_c)
        self.set_TEproperties(T_props=self.T_props)
        delta_T = self.T_h - self.T_c
        self.q_h = ( self.alpha * self.T_h * self.J - delta_T /
                     self.length * self.k + self.J**2. * self.length * self.rho
                     / 2. ) 
        self.q_c = ( self.alpha * self.T_c * self.J - delta_T /
                     self.length * self.k - self.J**2 * self.length * self.rho )

        self.P_flux = ( (self.alpha * delta_T * self.J + self.rho *
                         self.J**2 * self.length) ) 
        self.P = self.P_flux  * self.area
        self.eta = self.P / (self.q_h * self.area)
        self.eta_check = ( (self.J * self.alpha * delta_T + self.rho *
                            self.J**2. * self.length) / (self.alpha *
                            self.T_h * self.J - delta_T / self.length
                            * self.k + self.J**2 * self.length *
                            self.rho / 2.) ) 
        self.V = -self.P / np.abs(self.I)
        self.R_internal = self.rho * self.length / self.area
        self.R_load = - self.V / self.I

    def set_ZT(self):
        """Sets ZT based on formula
        self.ZT = self.sigma * self.alpha**2. / self.k""" 
        self.ZT = self.alpha**2. * self.T_props / (self.k * self.rho)

    def set_power_factor(self):
        """Sets power factor and maximum theoretical power for leg."""
        self.power_factor = self.alpha**2 * self.sigma
        self.power_max = ( self.power_factor * self.T_props**2 /
        self.length * self.area ) 

