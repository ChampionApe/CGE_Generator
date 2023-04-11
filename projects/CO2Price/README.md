# CO2 price 
The project requires running the following:
* ```IOdata.ipynb```: Load and arranges IO data from 1990 - current year (currently 2019 is the latest year). The data is arranged in a specific way before moving on:
	* The raw data includes 7 durables - we aggregate them into 2 types (buildings and machines).
	* A simple RAS-like adjustment is performed to achieve a more sparse IO dataset. 
	* Standard variables are defined on this basis: quantities demand+supply, prices demand+supply, average taxes, trade mappings etc.
* ```ModelData_t.ipynb```: Takes the IO data for a given year and sets up relevant nesting structure used in the economic model.
* Individual modules are then run separately to etablish a baseline solution to the model:
	* ```mProduction.ipynb```: Dynamic model with optimal investments in two durables and installation costs. *Currently, this does not include emissions.* 
	* ```mConsumer.ipynb```: Ramsey household with endogenous labor supply. *NB: Requires more though on emissions + other taxes e.g. labor income.*
	* ```mInvestments.ipynb```: Akin to ```mProduction``` but without durables. 
	* ```mGovernment.ipynb```: Simple balanced budget model. *NB: Requires revision with emissions*. 
	* ```mIventorty.ipynb```: Ad-hoc inventory module.
	* ```mTrade.ipynb```: Armington-like trade model.
* ```mGeneralEquilibrium.ipynb```: Establishes general equilibrium starting from the individual modules.
* ```shockGeneralEquilibrium.ipynb```: Tests out a few shocks to the system.


Main to do:
* Include emissions + regulation thereof.
* Include data on main historical regulation.
* Run for each $t$. 
* Implement carbon budget and estimate shadow price of CO2. 