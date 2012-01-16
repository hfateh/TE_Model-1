"""functions to be used in both exhaust and coolant modules"""

import numpy as np
from scimath.units.api import *

@has_units(inputs="width:width:units=m")
def set_flow_geometry(self,width):
    """Given heat exchanger width, this function sets some
    geometry stuff."""
    self.perimeter = 2.*(self.height+width) # wetted perimeter (m) of
        # exhaust flow
    self.area = self.height * width # cross-section area (m^2) of
        # exhaust flow
    self.D = 4.*self.area / self.perimeter # coolant hydraulic diameter (m)

@has_units()
def set_Re_dependents(self):
    """Sets Nu and f based on Re."""
    self.set_Re()
    if np.size(self.Re_D) > 1:
        if (self.Re_D > 2300.).any(): # Do these correlations hold for any tube geometry?
            self.f = 0.078 * self.Re_D**(-1. / 4.) # friction factor for turbulent
            # flow from Bejan
            self.Nu_D = self.Nu_coeff * self.Re_D**(4. / 5.) * self.Pr**(1. / 3.) # Adrian
            # Bejan, Convection Heat Transfer, 3rd ed., Equation 8.30
        else:
            self.Nu_D = 7.54 # Bejan, Convection Heat Transfer, Table 3.2
                # parallel plates with constant T
            self.f = 24. / self.Re_D
    else:
        if (self.Re_D > 2300.): # Do these correlations hold for any tube geometry?
            self.f = 0.078 * self.Re_D**(-1. / 4.) # friction factor for turbulent
            # flow from Bejan
            self.Nu_D = self.Nu_coeff * self.Re_D**(4. / 5.)*self.Pr**(1. / 3.) # Adrian
            # Bejan, Convection Heat Transfer, 3rd ed., Equation 8.30
        else:
            self.Nu_D = 7.54 # Bejan, Convection Heat Transfer, Table 3.2
                # parallel plates with constant T
            self.f = 24. / self.Re_D

