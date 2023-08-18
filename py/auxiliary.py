import pandas as pd
from pyDatabases import adjMultiIndex

def extrapolateLower(symbol, globalMin, rule = 'nearestNeighbor', t = 't'):
	""" Extrapolate symbol to years from minimum in symbol to globalMin """
	_min = symbol.index.get_level_values(t).min()
	if _min == globalMin:
		return symbol
	else:
		if rule == 'nearestNeighbor':
			applyToRange = pd.Index(range(globalMin, _min), name = t)
			extrapolatedVals = adjMultiIndex.bc(symbol.xs(_min, level=t), applyToRange).reorder_levels(symbol.index.names) if isinstance(symbol.index, pd.MultiIndex) else pd.Series(symbol.xs(_min), index = applyToRange)
			return pd.concat([extrapolatedVals, symbol], axis = 0)
		else:
			raise TypeError(f"Extrapolation rule '{rule}' is invalid. Choose 'nearestNeighbor' for now. ")

def extrapolateUpper(symbol, globalMax, rule = 'nearestNeighbor', t='t'):
	""" Extrapolate symbol to years from max in symbol to globalMax """
	_max = symbol.index.get_level_values(t).max()
	if _max == globalMax:
		return symbol
	else:
		if rule == 'nearestNeighbor':
			applyToRange = pd.Index(range(_max+1, globalMax+1), name = t)
			extrapolatedVals = adjMultiIndex.bc(symbol.xs(_max, level=t), applyToRange).reorder_levels(symbol.index.names) if isinstance(symbol.index, pd.MultiIndex) else pd.Series(symbol.xs(_max), index = applyToRange)
			return pd.concat([symbol, extrapolatedVals], axis = 0)
		else:
			raise TypeError(f"Extrapolation rule '{rule}' is invalid. Choose 'nearestNeighbor' for now. ")

def interpolateBetweenTwoYears(symbol, t0, t1, rule = 'linear', t = 't', **kwargs):
	fullDomain = symbol.xs(t0,level=t).index.union(symbol.xs(t1,level=t).index)
	return adjMultiIndex.addGrid(adjMultiIndex.bc(symbol.xs(t0, level=t), fullDomain),
								 adjMultiIndex.bc(symbol.xs(t1, level=t), fullDomain),
								 pd.Index(range(t0, t1+1), name = t), symbol.name, gridtype = rule, **kwargs).reorder_levels(symbol.index.names)

def interpolateYears(symbol, rule = 'linear', t='t', **kwargs):
	""" Interpolate data in symbol between yearly increments """
	tind = sorted(symbol.index.get_level_values(t).unique())
	return _dropDuplicated(pd.concat([interpolateBetweenTwoYears(symbol, tind[i-1], tind[i], rule = rule, t=t, **kwargs) for i in range(1,len(tind))], axis = 0))

def _dropDuplicated(symbol):
	return symbol[~symbol.index.duplicated(keep='first')]


# Algorithm for elimination of overshoot -- linear reduction:
def func_M̃LR(MLR, t0, T̃, T):
	return pd.Series(MLR, index = pd.Index(range(t0+T̃+1, t0+T+2), name = 't'))
def func_α(T̃, T, t0, OS, M, MLR):
	if OS == 0:
		return 0
	elif T == T̃:
		return 1/T
	else:
		return 1/T̃-sum(M.loc[t0+T̃+1:t0+T+1]-MLR)/(OS * T̃)
def func_M̃(T̃, T, t0, OS, M, MLR):
	return (M.loc[t0+1:t0+T̃]-func_α(T̃, T, t0, OS, M, MLR) * OS).combine_first(func_M̃LR(MLR, t0, T̃,T))

def eliminateOvershoot(t0, T, M, OS, maxIter = 30):
	""" Find path of overshoot"""
	if sum(M.loc[t0+1:t0+T]-M.loc[t0+T+1])<OS:
		x = M.loc[t0+1:].rename('x').reset_index()
		y = x.assign(T = x['t']-t0, xcumsum = x['x'].cumsum())
		z = y['xcumsum'] - y['x'] * y['T'] - OS
		Tnew = y['T'].iloc[z[z>0].index.min()]-1
		print(f"""**** Warning: Elimination of overshoot not feasible with T = {T} years of linear reduction; increases to minimum feasible number {Tnew}""")
		T = Tnew
	MLR = M.loc[t0+T+1]
	n = 0 
	T̃ = T-n
	M̃ = func_M̃(T̃, T, t0, OS, M, MLR)
	while M̃.loc[t0+T̃]<MLR:
		n = n+1
		T̃ = T-n
		M̃ = func_M̃(T̃,T,t0,OS,M,MLR)
		if n>maxIter:
			break
	if M̃.loc[t0+T̃]<MLR:
		raise ValueError('Algorithm did not converge; raise maxIter or check if solution is feasible.')
	else:
		return M̃

