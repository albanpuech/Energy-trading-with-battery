## Current implementation :

### Current settings :
- Battery capacity of 100 kWH
- Constant charge/ discharge rate of 0.5C 
- No limit on number of daily cycles 

### Questions/ next steps : 
- What other constraints should I add ?
- Are grid + trading cost for charge and discharge ?
- Should the max number of cycles be a parameter ?
- What battery efficiency ? 
- Should there be a "rest" period between the charge/ discharge cycles ?


## Day-ahead market considerations :

### Constraints :
- So far, the schedule was based on the true day-ahead hourly prices
- In reality, market participant is price taker, and does not know the clearing price in advance
- We need to submit a pair (quantity, price) for each potential price within the price range 
- Accepted bids become binding agreements
- Need to make adjustments on the intra-day market if a buying order preceding an accepted selling order has not been accepted 
- As price are not known in advance, need for a price prediction
- Inputs usually used: gas prices, wind production forecast, load forecast, date, ...


### Questions :
- Can we assume that our bid will always be accepted ? 
- What did we originally want the schedule to be "recomputed" during the day ?
- If not, we need access to the intra-day market - How do we integrate this into the algorithm ?

## Other considerations :
Model performance depends :
- Forecast accuracy (effect of forecasting accuracy is even more important for battery that charge fast (charging slowly averages the buying price))
- Tuning of a risk parameter 





