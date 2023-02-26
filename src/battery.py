import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt


class Battery():
    '''
    Battery class. 

    Nomenclature :
    - SOC: state of charge in [0,1]
    - CPL: charging power level (W/Wh)
    - DPL: discharging power level (W/Wh)
    '''

    def __init__(self,SOC_to_CPL_function, SOC_to_DPL_function,Nint=5, init_NEC = 1000000, init_eff = 0.99, max_cycles=4000):
        
        self.SOC_to_CPL_function = SOC_to_CPL_function
        self.SOC_to_DPL_function = SOC_to_DPL_function 
        self.max_SOC_change_charge, self.min_SOC_change_discharge = self.get_max_SOC_change(Nint)
        self.Nint = Nint
        self.max_cycles = max_cycles


        self.init_eff = init_eff
        self.min_eff = self.init_eff * 0.8
        self.eff_decrease_rate = (self.init_eff - self.min_eff)/self.max_cycles
        

        self.init_NEC = init_NEC
        self.min_NEC = self.init_NEC * 0.8
        self.NEC_decrease_rate = (self.init_NEC - self.min_NEC)/self.max_cycles

        self.reset()

    @property
    def eff(self) :
        return max(self.min_eff, self.init_eff - self.n_cycles * self.eff_decrease_rate)

    @property
    def NEC(self) :
        return max(self.min_NEC, self.init_NEC - self.n_cycles * self.NEC_decrease_rate)
    
    def reset(self) :
        self.n_cycles =  0
    

    
    def get_max_SOC_change(self,Nint) :
        S = np.linspace(0,1,Nint+1)
        max_SOC_change_charge = np.zeros(len(S))
        min_SOC_change_discharge = np.zeros(len(S))

        for i,SOC_init in enumerate(S) :
            SOC = SOC_init
            for t in range(3600) :
                SOC = min(1,SOC + 1/3600  * self.SOC_to_CPL_function(SOC))
            max_SOC_change_charge[i] = (SOC-SOC_init) 

            
        for i,SOC_init in enumerate(S) :
            SOC = SOC_init
            for t in range(3600) :
                SOC = max(0,SOC- 1/3600 * self.SOC_to_DPL_function(SOC))
            min_SOC_change_discharge[i] =  (SOC-SOC_init) 

            
        return max_SOC_change_charge, min_SOC_change_discharge

    


    
        

        
        

    
    
        