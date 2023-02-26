import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt





def get_SOC_CT_functions(SOC_to_CPL_function, NEC):
    '''
    Approximates SOC -> CT and CT -> SOC functions from the SOC -> CPL function
    '''
    # start with empty battery and charging time = 0
    CT = [0]
    EC = 0
    SOC = [0]

    while EC < NEC : # until battery is full
        EC = EC + 1/3600 * NEC * SOC_to_CPL_function(SOC[-1]) # charge the battery for one sec using appropriate CPL
        CT.append(CT[-1]+1) # update time 
        SOC.append(EC/NEC) # update SOC 
    
    # interpolate data to get functions
    SOC_to_CT_function = interp1d(SOC, CT) 
    CT_to_SOC_function = interp1d(CT+[np.inf], SOC+[1.])

    return SOC_to_CT_function, CT_to_SOC_function


def get_SOC_DT_functions(SOC_to_DPL_function, NEC):
    '''
    Approximates SOC -> DT and DT -> SOC functions from the SOC -> CPL function
    '''
    # start with fully charged battery
    DT = [0]
    EC = NEC
    SOC = [1.]
    # iteratively discharge the battery
    while EC >0 :
        EC = EC - 1/3600 * NEC * SOC_to_DPL_function(SOC[-1])
        DT.append(DT[-1]+1)
        SOC.append(EC/NEC)
    
    SOC_to_DT_function = interp1d(SOC, DT)
    DT_to_SOC_function = interp1d(DT+[np.inf], SOC+[0.])

    return SOC_to_DT_function, DT_to_SOC_function


    

def get_max_energy_change(bat,S,) :
    capacity_change_charge = np.zeros(len(S))
    capacity_change_discharge = np.zeros(len(S))

    for i,SOC_init in enumerate(S) :
        SOC = SOC_init
        for t in range(3600) :
            SOC = min(1,SOC + 1/3600  * bat.SOC_to_CPL_function(SOC))
        capacity_change_charge[i] = (SOC-SOC_init) 

        
    for i,SOC_init in enumerate(S) :
        SOC = SOC_init
        for t in range(3600) :
            SOC = max(0,SOC- 1/3600 * bat.SOC_to_DPL_function(SOC))
        capacity_change_discharge[i] =  (SOC-SOC_init) 

        
    return capacity_change_charge, capacity_change_discharge


class Battery():
    '''
    Battery class. 

    Nomenclature :
    - SOC: state of charge in [0,1]
    - CT: charging time (s)
    - DT: discharging time (s)
    - NEC: nominal energy capacity (Wh)
    - EC: energy capacity (Wh)
    - CPL: charging power level (W)
    - DPL: discharging power level (W)
    '''

    def __init__(self,SOC_to_CPL_function, SOC_to_DPL_function, NEC = 75000):
        self.NEC = NEC 
        self.EC = NEC ## initialize fully-charged battery 
        self.SOC_to_CPL_function = SOC_to_CPL_function ## SOC [0,1] to Charging Power Level in Watts
        self.SOC_to_DPL_function = SOC_to_DPL_function ## SOC [0,1] to Discharging Power Level in Watts
        self.SOC_to_CT_function, self.CT_to_SOC_function = get_SOC_CT_functions(SOC_to_CPL_function, NEC) 
        self.SOC_to_DT_function, self.DT_to_SOC_function = get_SOC_DT_functions(SOC_to_DPL_function, NEC)

    @ property
    def SOC(self) :
        return self.EC/self.NEC
        

    def charge(self,max_charging_time):
        '''
        Charges the battery for a maximum duration of max_charging_time. 
        Returns the updated SOC and the charging time (strictly less than max_charging_time if 
        less time than max_charging_time was needed to fully charge the battery)
        '''
        initial_CT = self.SOC_to_CT_function(self.SOC) # For how long the battery has already been charging 
        final_SOC = self.CT_to_SOC_function(initial_CT+max_charging_time) # SOC after charging 
        time_to_charge = self.SOC_to_CT_function(final_SOC)-initial_CT # Time it took to reach updated SOC 
        self.EC = final_SOC * self.NEC 
        return final_SOC, time_to_charge

    def discharge(self,max_discharging_time):
        '''
        Discharges the battery for a maximum duration of max_discharging_time. 
        Returns the updated SOC and the discharging time (strictly less than max_discharging_time if 
        less time than max_discharging_time was needed to fully discharge the battery)
        '''
        initial_DT = self.SOC_to_DT_function(self.SOC)
        final_SOC = self.DT_to_SOC_function(initial_DT+max_discharging_time)
        time_to_discharge = self.SOC_to_DT_function(final_SOC)-initial_DT
        self.EC = final_SOC * self.NEC
        return final_SOC, time_to_discharge


        
        

    
    
        