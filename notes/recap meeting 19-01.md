## Meeting recap 19/01/2023 :

### Battery efficiency :
- Use two different capacities : Charge and discharge capacity.
- Charge capacity = (discharge capacity) / efficiency
- pros: reflects the additional cost due to the inefficiency of the battery as "we pay for the energy that we can't get back when discharging the battery"

### Battery degradation :
- Update discharge capacity of the battery using a capacity fade curve after each cycle as shown in [1]
- As battery gets older, discharge capacity decreases but internal resistance increases 
    - We assume the charge capacity to be constant (time to charge stays constant as the battery gets older)

### Grid cost :
- We don't consider fixed-cost yearly subscription (will be taken into account during the profitability study in view of the expected yearly profit)
- Time varying grid tariffs per kwh
    - Use schedule as input 
- Fixed grid tariffs (per transaction) if necessary 

### Market considerations :
- Selling prices equal to day ahead market prices 
- Known at 2pm the day before, don't change during the day
- No need for any prediction, no uncertainty regarding the prices




[1] https://www.researchgate.net/publication/334753282_Algorithm_to_Determine_the_Knee_Point_on_Capacity_Fade_Curves_of_Lithium-Ion_Cells/figures?lo=1