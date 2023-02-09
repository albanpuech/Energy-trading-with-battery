# ----------------- PARAMS AND SETS ------------------


# hours in a day
set H ordered := {0..23};

# ----------- Battery specs -------------
# nominal energy capacity
param NEC >= 0 default 100000;
# initial energy capacity
param EC_init >= 0 default 0;


# ----------- constants -------------
# eps 
param eps = 0.00000001;
# big M to compute is_charging and is_discharging
param M = NEC;



# ----------- Charge/ discharge curve discretization -------------

# incremental - number of intervals
param inc <= 100, >= 0, default 1;
# number of intervals
param Nint = 100/inc;
# interval indices 
set I ordered := {0..Nint};
# cut points
param S{i in I} = i*inc;
# max negative change in energy capacity (discharge)
param G_d{I};
# max positive change in energy capacity (charge)
param G_c{I};




# ----------- Price and costs -------------
# price of electricity per hour
param p{H};
# fixed grid cost per hour
param fgc{H};
# variable grid cost per hour
param vgc{H};


# ----------- Availability Constraints -------------
# minimum SOC required 
param min_soc{H} >= 0 default 0;
# max SOC required 
param max_soc{H} >= 0 default 100;

# ----------- UNUSED -------------
# current cycle count 
param CCC{H} >= 0 default 0;
param fc >=0 default 0;


# ----------------- VARIABLES ------------------


# ----------- Decision variables --------------
# energy "in" per hour
var x{H};
# state of charge
var soc{H} >= 0;
# absolute value of the energy "in" per hour 
var abs_x{H} >=0;


# ----------- operation booleans -------------
# boolean indicating if we are buying = charging (1), or holding (0)
var is_charging{H} binary;
# boolean indicating if we are selling = discharging (1), or holding (0)
var is_discharging{H} binary;
# boolean indicating if we are charging or discharging (1), or holding (0)
var is_charging_or_discharging{H} binary; 



# ----------- Charge/ discharge curve discretization -------------
# interval indicator
var in_interval{I,H} binary;
# convex combination weights
var interval_start_w{I,H} >=0;
var interval_end_w{I,H} >= 0;









