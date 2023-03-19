import pandas as pd
import numpy as np
from amplpy import AMPL, modules
import datetime 

import datetime 
import pandas as pd
import numpy as np
from amplpy import AMPL, modules
import datetime 

def run_simulation(bat, df, start, end, forecasted=True, frame_size=14, update_period=1):
    """
    Run a simulation starting from the start-th day of the dataframe.
    For every day of the simulation, a schedule is generated (either based on true prices or prediction) and different 
    metrics are recorded.
    We return a dataframe containing the results of the simulation
    """
    
    try :
        end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S') - datetime.timedelta(hours=1)
        start_index = df.index.get_loc(df.index[df.timestamp==start][0]) 
        end_index = df.index.get_loc(df.index[df.timestamp==end][0])
    except : raise ValueError("The dataframe does not contain all the data between the start and end dates")
    start_df = start_index - 24 * frame_size if forecasted else start_index
    if  start_df < 0 : raise ValueError("The dataframe does not contain enough data for the price prediction relying on the {} last days to be computed".format(frame_size))
    
    df = df.iloc[start_df: end_index+1, :]
    n_hours = (end_index-start_df) + 1
    
    if  n_hours% 24 != 0:
        raise Exception(
            "The dataframe should contain only full days (24 hours)")


    bat.reset()  # start with a new battery, and get the max SOC change when charging and discharging
    G_c, G_d = bat.max_SOC_change_charge, bat.min_SOC_change_discharge

    n_cycles_list = np.zeros(n_hours)
    eff_list = np.zeros(n_hours)
    NEC_list = np.zeros(n_hours)
    price_forecast_list = np.zeros(n_hours)
    schedule = np.zeros(n_hours)





    # optimization done for each day :
    for i, day in enumerate(range((frame_size if forecasted else 0), n_hours//24)):

        day_indices = slice(day*24, (day+1)*24)

        # if using forecasted prices, get new forecast evert update_period iterations :
        if forecasted and (i % update_period == 0):
            prices = df.iloc[(day-frame_size)*24:day*24, :].groupby(
                df.timestamp.dt.hour).price_euros_wh.mean().to_numpy()

        # Otherwise, use the true prices for the current day
        if not forecasted:
            prices = df.iloc[day_indices].price_euros_wh.to_numpy()

        # get the variable grid cost
        vgc = df.vgc.iloc[day*24:(day+1)*24].to_numpy()

        # get the fixed grid cost
        fgc = df.fgc.iloc[day*24:(day+1)*24].to_numpy()

        # store battery state
        n_cycles_list[day_indices] = bat.n_cycles
        eff_list[day_indices] = bat.eff
        NEC_list[day_indices] = bat.NEC
        price_forecast_list[day_indices] = prices

        # get optimized schedule
        schedule[day_indices] = get_daily_schedule(
            prices, vgc, fgc, bat, G_c, G_d)

    ## store simulation results 
    df = df.assign(n_cycles=n_cycles_list,
                   eff=eff_list, 
                   NEC=NEC_list,
                   price_forecast=price_forecast_list,
                   schedule=schedule,
                   capacity=np.hstack(
                       (np.array([0]), np.cumsum(schedule)[:-1])),
                   SOC=lambda x: 100 * x.capacity/x.NEC,
                   charge_energy=lambda x: x.schedule.mask(x.schedule < 0, 0), ## energy delivered to the battery
                   discharge_energy=lambda x: -
                   x.schedule.mask(x.schedule > 0, 0) * x.eff, ## energy obtained from the battery (taking into account the discharge efficiency)
                   electricity_revenue=lambda x: x.price_euros_wh * ## net revenue from electricity trading (before grid costs)
                   (x.discharge_energy - x.charge_energy),
                   grid_cost=lambda x: x.vgc * ## grid costs
                   (x.discharge_energy - x.charge_energy) +
                   x.fgc * (abs(x.schedule) > 10**-5),
                   hourly_profit=lambda x: x.electricity_revenue - x.grid_cost ## profits
                   )

    return df.iloc[(frame_size if forecasted else 0) * 24:]


def get_daily_schedule(prices, vgc, fgc, bat, G_c, G_d):
    """
    Obtain schedule given the battery model, prices, vgc and fgc.
    """

    ## the arrays have to contain the data for the 24 hours of the day
    if not (len(prices == 24) and len(vgc == 24) and len(fgc == 24)) :
        raise Exception(
            "The arrays should contain the data for a full day (24 hours)")

    ## instantiate AMPL object and load the model
    modules.load()  # load all AMPL modules
    ampl = AMPL()  
    ampl.read("ampl/ampl.mod")  

    ## set parameters 
    ampl.get_parameter("vgc").set_values(vgc)
    ampl.get_parameter("fgc").set_values(fgc)
    ampl.get_parameter("p").set_values(prices)
    ampl.get_parameter("eff").set_values([bat.eff])
    ampl.get_parameter("Nint").set_values([bat.Nint])
    ampl.get_parameter("max_SOC").set_values([1]*23 + [0])
    ampl.get_parameter("G_c").set_values(np.array(G_c)*bat.NEC)
    ampl.get_parameter("G_d").set_values(np.array(G_d)*bat.NEC)
    ampl.get_parameter("NEC").set_values([bat.NEC])

    ## solve and get optimization solution
    ampl.option["solver"] = "gurobi"
    ampl.solve()
    daily_schedule = ampl.get_variable('x').get_values().to_pandas()[
        "x.val"].to_numpy()
    ampl.reset()

    ## update battery state
    bat.n_cycles += abs(daily_schedule).sum()/(2*bat.init_NEC)

    return daily_schedule
