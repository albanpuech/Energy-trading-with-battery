############################# PARAMS AND SETS ##################


# hours in a day
set H ordered := {0..23};

# ----------- Battery specs -------------
# nominal energy capacity
param NEC >= 0 default 100000;
# initial energy capacity
param EC_init >= 0, <= NEC default 0;


# ----------- constants -------------
# eps 
param eps := 0.00000001;
# big M to compute is_charging and is_discharging
param M := NEC;



# ----------- Charge/ discharge curve discretization -------------

# incremental - number of intervals
param inc <= 100, >= 0, default 1;
# number of intervals
param Nint := 100/inc;
# interval indices 
set I ordered := {0..Nint};
# cut points
param S{i in I} := i*inc;
# max negative change in energy capacity (discharge)
param G_d{I} >= -NEC, <= 0 default -NEC/2;
# max positive change in energy capacity (charge)
param G_c{I} >=0, <= NEC default NEC/2;




# ----------- Price and costs -------------
# price of electricity per hour
param p{H};
# fixed grid cost per hour
param fgc{H} >= 0 default 0;
# variable grid cost per hour
param vgc{H} >= 0 default 0;


# ----------- Availability Constraints -------------
# minimum SOC required 
param min_SOC{H} >= 0, <= 1 default 0;
# max SOC required 
param max_SOC{H} >= 0, <= 1 default 1;

# ----------- UNUSED -------------
# current cycle count 
param CCC{H} >= 0 default 0;
param fc >=0 default 0;


############################# VARIABLES ##################


# ----------- Decision variables --------------
# energy "in" per hour
var x{H} >= -NEC, <= NEC;
# state of charge
var SOC{H} >= 0, <=1;
# absolute value of the energy "in" per hour 
var abs_x{H} >=0, <= NEC;


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
var interval_start_w{I,H} >=0, <= 1;
var interval_end_w{I,H} >= 0, <= 1;



############################# CONSTRAINTS ##################



#------------------- Auxiliary variables ----------------
# compute SOC[i]
subject to compute_soc {i in H}:
    SOC[i] = sum{t in 0..i} x[t] / NEC;
;

# get the absolute value of x[i]
subject to abs_x_creation {i in H}:
    abs_x[i] = is_charging[i] * x[i] - is_discharging[i] * x[i]
;


# ---------- charging/discharging or no action on the battery -------
subject to charging_down {i in H} : 
    x[i] <= eps + M*is_charging[i];

subject to charging_up {i in H} : 
    x[i] >= eps - M*(1-is_charging[i]);

subject to discharging_down {i in H} : 
    - x[i] <= eps + M*is_discharging[i];

subject to discharging_up {i in H} : 
    - x[i] >= eps - M*(1-is_discharging[i]);

subject to charge_or_discharge {i in H} : 
    is_charging_or_discharging[i] == is_charging[i] + is_discharging[i];



#------------------- Availability constraints ----------------
# keep SOC within bounds 
subject to availability_constraint {i in H}:
    min_SOC[i] <= SOC[i] <= max_SOC[i];



# ------------------- Find discretization parameters of SOC ------------
subject to find_weights_for_each_interval {i in H} : 
    sum{k in 1..Nint} (interval_start_w[k,i]*S[k-1]+ interval_end_w[k,i]*S[k]) == SOC[i];

subject to comvex_combination_constraint {k in I, i in H} : 
    interval_start_w[k,i] + interval_end_w[k,i] == in_interval[k,i];

subject to select_one_interval {i in H} : 
    sum{k in I} in_interval[k,i] == 1;



#-------------------Charge/ Discharge rate constraints ----------------
# energy increment should be below maximum increment 
subject to energy_increment {i in H}:
    sum{k in 1..Nint} (interval_start_w[k,i] * G_c[k-1] + interval_end_w[k,i] * G_c[k]) >= x[i];

# energy increment should be above minimum increment 
subject to energy_decrease {i in H}:
    sum{k in 1..Nint} (interval_start_w[k,i] * G_d[k-1] + interval_end_w[k,i] * G_d[k]) <= x[i];

############################# OBJECTIVE FUNCTION ##################

maximize profit :
    - sum{i in H} (x[i] * p[i] + fgc[i] * is_charging_or_discharging[i] + vgc[i] * abs_x[i]);



