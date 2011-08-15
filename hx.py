# Chad Baker
# Created on 2011 Feb 10

# Distribution Modules
import scipy as sp
import matplotlib.pyplot as mpl

# User Defined Modules
# In this directory
import engine
import tem
import exhaust
import coolant


class _PlateWall():
    """class for modeling metal walls of heat exchanger"""
    k = 0.2 # thermal conductivity (kW/m-K) of Aluminum HX plate
    t = 0.005 # thickness (m) of HX plate
    def set_h(self):
        self.h = self.k/self.t


class HX():
    """class for handling HX system"""

    def __init__(self):
        """Geometry and constants"""
        self.width = 10.e-2 # width (cm*10**-2) of HX duct. This model treats
            # duct as parallel plates for simpler modeling.
        self.length = 20.e-2 # length (m) of HX duct
        self.nodes = 25 # number of nodes for numerical heat transfer model

        # initialization of sub classes
        self.cool = coolant.Coolant()
        self.exh = exhaust.Exhaust()
        self.tem = tem.TEModule()
        self.plate = _PlateWall()
        self.cummins = engine.Engine()

        self.fix_geometry()

    def fix_geometry(self):
        """Makes sure that common geometry like width and length is
        the same between exh, cool, and the overal heat exchanger."""
        self.cool.width = self.width
        self.cool.length = self.length
        self.exh.width = self.width
        self.exh.length = self.length

    def set_mdot_charge(self):
        """Sets exhaust mass flow rate. Eventually, this should be a
        function of speed, load, and EGR fraction.  Also, it should
        come from experimental data.  Also, it should probably go
        within the exhaust module."""
        self.cummins.set_mdot_charge() # mass flow rate (kg/s) of exhaust
        self.exh.mdot = self.cummins.mdot_charge * (1. - self.exh.bypass) 

    def solve_node(self):
        """solves for performance of streamwise slice of HX"""
        self.exh.T_out = self.exh.T_in - 5
        # Guess at exhaust node out temperature (K)

        # Exhaust stuff
        self.exh.set_flow()
        # self.exh.h = self.exh.h * 10.
        if self.exh.enhancement == 'straight fins':
            self.exh.fin.h = self.exh.h
        # Coolant stuff
        self.cool.set_flow()
        # Wall stuff
        self.plate.set_h()
        # TE stuff
        self.tem.solve_tem()

        self.exh.R_thermal = 1 / self.exh.h
        self.plate.R_thermal = 1 / self.plate.h
        self.tem.R_thermal = 1 / self.tem.h
        self.cool.R_thermal = 1 / self.cool.h

        self.leg_pairs = int(self.area / self.tem.area) # Number of TEM leg pairs per node
        # Heat exchanger stuff
        if self.exh.C < self.cool.C:
            self.C_min = self.exh.C
            self.C_max = self.cool.C
        else:
            self.C_min = self.cool.C
            self.C_max = self.exh.C
        self.R_C = self.C_min / self.C_max 
        self.U = ( (self.exh.R_thermal + self.plate.R_thermal + self.tem.R_thermal +
        self.plate.R_thermal + self.cool.R_thermal )**-1 ) # overall heat transfer
            # coefficient (kW/m^2-K)
        self.NTU = self.U * self.area / self.C_min # number
            # of transfer units
#################### dependent on HX configuration  
        if self.type == 'parallel':                                        
            self.effectiveness = ( (1 - sp.exp(-self.NTU * (1 + self.R_C))) / (1
             + self.R_C) )  # NTU method for parallel flow from Mills Heat
                # Transfer Table 8.3a  
            self.Qdot = ( self.effectiveness * self.C_min * (self.exh.T_in -
             self.cool.T_in)  ) # NTU heat transfer (kW)
            self.cool.T_out = ( self.cool.T_in + self.Qdot / self.cool.C )
            # temperature (K) at coolant outlet

        elif self.type == 'counter':
            self.effectiveness = ( (1 - sp.exp(-self.NTU * (1 - self.R_C))) /
           (1 - self.R_C * sp.exp(-self.NTU * (1 - self.R_C))) )
            self.Qdot = ( (self.effectiveness * self.C_min * (self.exh.T_in -
             self.cool.T_out)) / (1 - self.effectiveness * self.C_min / self.cool.C) ) # NTU heat transfer (kW) 
            self.cool.T_in = ( self.cool.T_out - self.Qdot / self.cool.C )

#################### independent of HX configuration  
        self.exh.T_out = ( self.exh.T_in - self.Qdot / self.exh.C )
            # temperature (K) at exhaust outlet
        self.exh.T = (self.exh.T_in + self.exh.T_out) / 2. 

    def solve_hx(self): # solve parallel flow heat exchanger
        """solves for performance of entire HX"""
        self.node_length = self.length / self.nodes
        # length (m) of each node
        self.x_dim = sp.arange(self.node_length/2, self.length +
        self.node_length/2, self.node_length)   
        # x coordinate (m)
        self.fix_geometry()
        self.set_mdot_charge()
        self.exh.set_flow_geometry(self.exh.width) 
        self.cool.set_flow_geometry(self.cool.width)
        
        self.area = self.node_length*self.width*self.cool.ducts # area (m^2)
                                        # through which heat flux
                                        # occurs in each node
        self.exh.T_in = self.exh.T_inlet
        # T_in and T_out correspond to the temperatures going into and
        # out of the node.  The suffix "let" means the temperature is
        # referring to the HX inlet or outlet.    
        if self.type == 'parallel':
            self.cool.T_in = self.cool.T_inlet
        elif self.type == 'counter':
            self.cool.T_out = self.cool.T_outlet  

        self.tem.Ptype.set_prop_fit()
        self.tem.Ntype.set_prop_fit()

        # initializing arrays for tracking variables at nodes
        ZEROS = sp.zeros(self.nodes)
        self.Qdot_nodes = ZEROS.copy() # initialize array for storing
                                    # heat transfer (kW) in each node 
        self.effectiveness_nodes = ZEROS.copy() # initialize array for storing
                                    # heat transfer (kW) in each node 
        self.exh.T_nodes = ZEROS.copy() # initializing array for storing
                                     # temperature (K) in each node 
        self.exh.h_nodes = ZEROS.copy()
        self.cool.T_nodes = ZEROS.copy() # initializing array for storing
                                     # temperature (K) in each node 
        self.cool.h_nodes = ZEROS.copy() 
        self.U_nodes = ZEROS.copy() 
        self.tem.T_c_nodes = ZEROS.copy() # initializing array for storing
                                     # temperature (K) in each node 
        self.tem.T_h_nodes = ZEROS.copy() # initializing array for storing
                                     # temperature (K) in each node
        self.tem.h_nodes = ZEROS.copy()                                     
        self.tem.power_nodes = ZEROS.copy()
        self.tem.eta_nodes = ZEROS.copy()
        
        # for loop iterates of nodes of HX in streamwise direction
        for i in sp.arange(self.nodes):
            print "\nSolving node", i
            if self.type == 'parallel':
                self.tem.T_c = self.cool.T_in
                # guess at cold side tem temperature (K)
            elif self.type == 'counter':
                self.tem.T_c = self.cool.T_out
                # guess at cold side tem temperature (K)
            self.tem.T_h_goal = self.exh.T_in
            # guess at hot side TEM temperature (K)

            self.tem.h_iter = sp.empty(10)
            # array of empty entries for while loop to check for
            # convergence 

            # This loop iterates until the thermal resistance of the
            # TE device matches up with the thermal resistance assumed
            # by the heat exchanger model.   
            for j in range(2): 
                self.solve_node()
                self.tem.h_iter[j] = self.tem.h
                self.tem.T_h_goal = ( self.exh.T - self.Qdot / ((self.exh.h**-1 +
                self.plate.h**-1)**-1 * self.area) )
                # redefining TEM hot side temperature (K) based on known heat flux 
                self.tem.T_c = ( self.Qdot * (1 / (self.plate.h * self.area) + 1 /
                (self.cool.h * self.area)) + self.cool.T)
                # redefining TEM cold side temperature (K) based on
                # known heat flux

            j = 1
            while ( sp.absolute(self.tem.h_iter[j] -
            self.tem.h_iter[j-1]) / self.tem.h_iter[j-1] > 0.01 ):
                j = j + 1
                self.solve_node()
                self.tem.h_iter[j] = self.tem.h
                self.tem.T_h_goal = ( self.exh.T - self.Qdot / ((self.exh.h**-1 +
                self.plate.h**-1)**-1 * self.area) )
                # redefining TEM hot side temperature (K) based on known heat flux 
                self.tem.T_c = ( self.Qdot * (1 / (self.plate.h * self.area) + 1 /
                (self.cool.h * self.area)) + self.cool.T)
                # redefining TEM cold side temperature (K) based on
                # known heat flux
                self.iterations = j

            self.Qdot_nodes[i] = self.Qdot # storing node heat transfer in array
            self.effectiveness_nodes[i] = self.effectiveness # storing node heat transfer in array

            self.exh.T_nodes[i] = self.exh.T
            self.exh.h_nodes[i] = self.exh.h
            self.cool.h_nodes[i] = self.cool.h
            self.tem.T_h_nodes[i] = self.tem.T_h # hot side
                                        # temperature (K) of TEM at
                                        # each node
            self.cool.T_nodes[i] = (self.cool.T_in + self.cool.T_out)/2.
            self.tem.T_c_nodes[i] = self.tem.T_c
            # cold side temperature (K) of TEM at each node.  
            self.U_nodes[i] = self.U
            self.tem.power_nodes[i] = self.tem.P * self.leg_pairs
            self.tem.eta_nodes[i] = self.tem.eta
            self.tem.h_nodes[i] = self.tem.h

            # redefining outlet temperature (K) for next node
            self.exh.T_in = self.exh.T_out
            if self.type == 'parallel':
                self.cool.T_in = self.cool.T_out
            elif self.type == 'counter':
                self.cool.T_out = self.cool.T_in
                
        # redefining HX outlet/inlet temperatures (K)
        self.exh.T_outlet = self.exh.T_out
        if self.type == 'parallel':
            self.cool.T_outlet = self.cool.T_out
        elif self.type == 'counter':
            self.cool.T_inlet = self.cool.T_in

        self.Qdot = sp.sum(self.Qdot_nodes)
        self.available = self.exh.C * (self.exh.T_inlet - self.exh.T_ref)
        self.effectiveness = self.Qdot / self.available # global HX effectiveness                                        
        self.tem.power = sp.sum(self.tem.power_nodes)
        # total TE power output (kW)
        self.Wdot_pumping = self.exh.Wdot_pumping + self.cool.Wdot_pumping
        # total pumping power requirement (kW) 
        self.power_net = self.tem.power - self.Wdot_pumping 
        self.eta_1st = self.power_net / self.Qdot
        self.eta_1st_modified = self.power_net / self.available

