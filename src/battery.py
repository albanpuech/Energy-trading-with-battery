import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt


class Battery():
    '''
    
    Battery class. 

    Parameters :

    - SOC: practical state of charge in [0,1] 
    - NEC: practical nominal energy capacity (Wh)
    - CR: Charging rate (W/Wh)
    - DR: Discharging rate (W/Wh)
    - Nint: Number of intervals used for the linear approximation of max_SOC_change_charge and min_SOC_change_discharge
    - init_eff: Initial discharge efficiency
    - init_NEC: Initial NEC
    - min_eff: Min discharge efficiency (reached at end of life, i.e. after max_cycles)
    - min_eff: Min NEC (reached at end of life, i.e. after max_cycles)
    - max_cycles: Number of cycles before min_NEC and min_eff are attained


    Functions : 

    - SOC_to_CR_function: Returns CR for given SOC
    - SOC_to_DR_function: Returns DR for given SOC
    - max_SOC_change_charge: Returns the max positive SOC change in one hour of charge started at given SOC
    - min_SOC_change_discharge: Returns the min negative SOC change in one hour of discharge started at given SOC

    '''

    def __init__(self,SOC_to_CR_function, SOC_to_DR_function,Nint=5, init_NEC = 1000000, init_eff = 0.99, max_cycles=4000):
        
        self.SOC_to_CR_function = SOC_to_CR_function
        self.SOC_to_DR_function = SOC_to_DR_function 
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
        '''
        Computes current eff given n_cycles
        '''
        return max(self.min_eff, self.init_eff - self.n_cycles * self.eff_decrease_rate)

    @property
    def NEC(self) :
        '''
        Computes current NEC given n_cycles
        '''
        return max(self.min_NEC, self.init_NEC - self.n_cycles * self.NEC_decrease_rate)
    
    def reset(self) :
        self.n_cycles =  0
    

    
    def get_max_SOC_change(self,Nint) :
        '''
        Computes max_SOC_change_charge(x) and min_SOC_change_discharge(x) by integral approximation for Nint+1 points uniformly distributed in [0,1]
        '''
        S = np.linspace(0,1,Nint+1)
        max_SOC_change_charge = np.zeros(len(S))
        min_SOC_change_discharge = np.zeros(len(S))

        for i,SOC_init in enumerate(S) :
            SOC = SOC_init
            for t in range(3600) :
                SOC = min(1,SOC + 1/3600  * self.SOC_to_CR_function(SOC))
            max_SOC_change_charge[i] = (SOC-SOC_init) 

            
        for i,SOC_init in enumerate(S) :
            SOC = SOC_init
            for t in range(3600) :
                SOC = max(0,SOC- 1/3600 * self.SOC_to_DR_function(SOC))
            min_SOC_change_discharge[i] =  (SOC-SOC_init) 

            
        return max_SOC_change_charge, min_SOC_change_discharge

    


    
        

        
        

    
    
        