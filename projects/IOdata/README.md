# IOdata project
Goes through some standard steps of setting up balanced IO data for a CGE model:
1. Reading IO data from "standard" excel sheets 
	* ```IO2018_full.ipynb``` defines a 146 sector IO from Danish data.
	* ```IO1990_2020.ipynb``` reads in data on Danish IO from 1990-2020 and defines a single database IO69.
2. Aggregating sector and durable definitions.
	* ```AggIO.ipynb``` shows how to aggregate the definition of durables from 7 to 2 and aggregate production sectors.
3. Set up stylized model data for a CGE model, including splitting up values into quantities and prices etc.. Naturally, the required model data changes from implementation to implementation, but this sets out a simple standard for a small open economy implementation.
	* ```modelDataFromIO.ipynb``` shows this. 