import pandas as pd
import numpy as np
from amplpy import AMPL, modules


def get_schedule(bat, df, forecasted=True, frame_size=14, update_period=1, start=None):
    """
    Computed optimal schedule for each day of the  
    """

    if start == None and forecasted:
        start = frame_size

    if start == None:
        start = 0

    bat.reset()
    n_hours = len(df)
    G_c, G_d = bat.max_SOC_change_charge, bat.min_SOC_change_discharge

    n_cycles_list = np.zeros(n_hours)
    eff_list = np.zeros(n_hours)
    NEC_list = np.zeros(n_hours)
    price_forecast_list = np.zeros(n_hours)
    schedule = np.zeros(n_hours)

    modules.load()  # load all AMPL modules
    ampl = AMPL()  # instantiate AMPL object
    ampl.read("ampl/ampl.mod")

    if n_hours % 24 != 0:
        raise Exception(
            "The dataframe should contain only full days (24 hours)")

    # optimization done for each day :
    for i, day in enumerate(range(start, n_hours//24)):

        day_indices = slice(day*24, (day+1)*24)

        if forecasted and (i % update_period == 0):
            price_forecast = df.iloc[(day-frame_size)*24:day*24, :].groupby(
                df.timestamp.dt.hour).price_euros_wh.mean().to_numpy()

        if not forecasted:
            price_forecast = df.iloc[day_indices].price_euros_wh.to_numpy()

        n_cycles_list[day_indices] = bat.n_cycles
        eff_list[day_indices] = bat.eff
        NEC_list[day_indices] = bat.NEC
        price_forecast_list[day_indices] = price_forecast

        ampl = AMPL()  # instantiate AMPL object
        ampl.read("ampl/ampl.mod")

        vgc = df.vgc.iloc[day*24:(day+1)*24].to_numpy()
        ampl.get_parameter("vgc").set_values(vgc)

        ampl.get_parameter("p").set_values(price_forecast)

        ampl.get_parameter("eff").set_values([bat.eff])
        ampl.get_parameter("Nint").set_values([bat.Nint])
        ampl.get_parameter("max_SOC").set_values([1]*23 + [0])
        ampl.get_parameter("G_c").set_values(np.array(G_c)*bat.NEC)
        ampl.get_parameter("G_d").set_values(np.array(G_d)*bat.NEC)
        ampl.get_parameter("NEC").set_values([bat.NEC])

        ampl.option["solver"] = "gurobi"
        ampl.solve()
        daily_schedule = ampl.get_variable('x').get_values().to_pandas()[
            "x.val"].to_numpy()
        ampl.reset()

        bat.n_cycles += abs(daily_schedule).sum()/(2*bat.init_NEC)

        schedule[day_indices] = daily_schedule

    df = df.assign(n_cycles=n_cycles_list,
                   eff=eff_list,
                   NEC=NEC_list,
                   price_forecast=price_forecast_list,
                   schedule=schedule,
                   capacity=np.hstack(
                       (np.array([0]), np.cumsum(schedule)[:-1])),
                   SOC=lambda x: 100 * x.capacity/x.NEC,
                   charge_energy=lambda x: x.schedule.mask(x.schedule < 0, 0),
                   discharge_energy=lambda x: -
                   x.schedule.mask(x.schedule > 0, 0) * x.eff,
                   electricity_revenue=lambda x: x.price_euros_wh *
                   (x.discharge_energy - x.charge_energy),
                   grid_cost=lambda x: x.vgc *
                   (x.discharge_energy - x.charge_energy),
                   hourly_profit=lambda x: x.electricity_revenue - x.grid_cost
                   )

    return df.iloc[start*24:]
