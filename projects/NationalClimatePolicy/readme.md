# Status

Currently, we have four implementations running. The "up-to-date" version is the "H2M0" version. The other ones are not updated in all steps (data, calibration, shocks).

* ```ModelData.ipynb, Calibration.ipynb, Shocks.ipynb```: Baseline version with one type of household (Ramsey) and a "small" economy with only four sectors. I believe code is up to date except ```Shocks.ipynb```.
* ```x_H2M.ipynb```:  Extends the setup with two household types (H2M). The H2M household has a proportional share of the wealth and is in the baseline modelled as a Ramsey consumer. In the shocks, they are switched to be H2M with an exogenous path of assets --> marginal propensity to consume = 1. Code should be up to date except ```Shocks_H2M.ipynb``` file.
* ```xGR_H2M0.ipynb```: Akin to ```x_H2M.ipynb```, but with full GreenREFORM sector detail *and* the hand-to-mouth consumer has no initial wealth. Progress is the same as above.
* ```x_H2M0.ipynb```: Most up to date.