import pandas as pd

def load_data(path = "data/european_wholesale_electricity_price_data_hourly.csv", country = "Germany", start = "2022-01-01 00:00:00", end = "2023-01-01 00:00:00") :

    df = pd.read_csv(path)
    df.rename(columns={"Datetime (UTC)":"timestamp","Price (EUR/MWhe)":"price_euros_wh"},inplace=True, errors='raise')
    
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%dT%H:%M:%S.%f%Z")

    df = df[df["Country"] == country]
    df = df[(df.timestamp<end) & (df.timestamp>=start)]

    df["vgc"] = 5 / 10 ** 6 # vgc of 5 EUR/ MWh
    df["fgc"] = 0 # fgc of 0 EUR/ hour of grid use
    df.price_euros_wh /= 10 ** 6

    return df
