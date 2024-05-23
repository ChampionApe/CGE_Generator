import pyDatabases, pandas as pd
import warnings
from pyDatabases import OrdSet, noneInit, adj, adjMultiIndex

_stdOrder = OrdSet(['t','s','ss','n','nn','taxTypes','gc'])

def stdSort(symbol, order = None):
	if isinstance(pyDatabases.getIndex(symbol), pd.MultiIndex):
		return symbol.reorder_levels([x for x in noneInit(order, _stdOrder+OrdSet(pyDatabases.getDomains(symbol))) if x in pyDatabases.getDomains(symbol)])
	else:
		return symbol

def extrapolateUpper(symbol, globalMax, rule = 'nearestNeighbor', level = 't'):
	if isinstance(symbol.index, pd.MultiIndex):
		df = symbol.unstack([k for k in symbol.index.names if k != level])
		maxLevel = df.index.max()
		if maxLevel<globalMax:
			with warnings.catch_warnings():
				warnings.filterwarnings("ignore", category = FutureWarning)
				df = pd.concat([df, pd.DataFrame(None, index = pd.Index(range(maxLevel+1, globalMax+1), name = level), columns = df.columns)], axis = 0).ffill()
				return df.stack([k for k in symbol.index.names if k != level]).reorder_levels(symbol.index.names)
		else:
			return symbol
	else:
		maxLevel = symbol.index.max()
		if maxLevel<globalMax:
			return pd.concat([symbol, pd.Series(symbol.xs(maxLevel), index = pd.Index(range(maxLevel+1,globalMax+1), name = level), name = symbol.name)], axis = 0)
		else:
			return symbol


# def extrapolateLower(symbol, globalMin, rule = 'nearestNeighbor', t = 't'):
# 	""" Extrapolate symbol to years from minimum in symbol to globalMin """
# 	_min = symbol.index.get_level_values(t).min()
# 	if _min == globalMin:
# 		return symbol
# 	else:
# 		if rule == 'nearestNeighbor':
# 			applyToRange = pd.Index(range(globalMin, _min), name = t)
# 			extrapolatedVals = adjMultiIndex.bc(symbol.xs(_min, level=t), applyToRange).reorder_levels(symbol.index.names) if isinstance(symbol.index, pd.MultiIndex) else pd.Series(symbol.xs(_min), index = applyToRange)
# 			return pd.concat([extrapolatedVals, symbol], axis = 0)
# 		else:
# 			raise TypeError(f"Extrapolation rule '{rule}' is invalid. Choose 'nearestNeighbor' for now. ")

# def extrapolateUpper(symbol, globalMax, rule = 'nearestNeighbor', t='t'):
# 	""" Extrapolate symbol to years from max in symbol to globalMax """
# 	_max = symbol.index.get_level_values(t).max()
# 	if _max == globalMax:
# 		return symbol
# 	else:
# 		if rule == 'nearestNeighbor':
# 			applyToRange = pd.Index(range(_max+1, globalMax+1), name = t)
# 			extrapolatedVals = adjMultiIndex.bc(symbol.xs(_max, level=t), applyToRange).reorder_levels(symbol.index.names) if isinstance(symbol.index, pd.MultiIndex) else pd.Series(symbol.xs(_max), index = applyToRange)
# 			return pd.concat([symbol, extrapolatedVals], axis = 0)
# 		else:
# 			raise TypeError(f"Extrapolation rule '{rule}' is invalid. Choose 'nearestNeighbor' for now. ")

# def interpolateBetweenTwoYears(symbol, t0, t1, rule = 'linear', t = 't', **kwargs):
# 	fullDomain = symbol.xs(t0,level=t).index.union(symbol.xs(t1,level=t).index)
# 	return adjMultiIndex.addGrid(adjMultiIndex.bc(symbol.xs(t0, level=t), fullDomain),
# 								 adjMultiIndex.bc(symbol.xs(t1, level=t), fullDomain),
# 								 pd.Index(range(t0, t1+1), name = t), symbol.name, gridtype = rule, **kwargs).reorder_levels(symbol.index.names)

# def interpolateYears(symbol, rule = 'linear', t='t', **kwargs):
# 	""" Interpolate data in symbol between yearly increments """
# 	tind = sorted(symbol.index.get_level_values(t).unique())
# 	return _dropDuplicated(pd.concat([interpolateBetweenTwoYears(symbol, tind[i-1], tind[i], rule = rule, t=t, **kwargs) for i in range(1,len(tind))], axis = 0))

# def _dropDuplicated(symbol):
# 	return symbol[~symbol.index.duplicated(keep='first')]
