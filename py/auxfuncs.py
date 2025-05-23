import pyDatabases, pandas as pd, numpy as np
import warnings
from pyDatabases import OrdSet, noneInit, adj, adjMultiIndex
from functools import reduce

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

def extrapolateLower(symbol, globalMin, rule = 'nearestNeighbor', level = 't'):
	if isinstance(symbol.index, pd.MultiIndex):
		df = symbol.unstack([k for k in symbol.index.names if k != level])
		minLevel = df.index.min()
		if minLevel>globalMin:
			with warnings.catch_warnings():
				warnings.filterwarnings("ignore", category = FutureWarning)
				df = pd.concat([pd.DataFrame(None, index = pd.Index(range(globalMin, minLevel), name = level), columns = df.columns), df], axis = 0).bfill()
				return df.stack([k for k in symbol.index.names if k != level]).reorder_levels(symbol.index.names)
		else:
			return symbol
	else:
		minLevel = symbol.index.min()
		if minLevel>globalMin:
			return pd.concat([pd.Series(symbol.xs(minLevel), index = pd.Index(range(globalMin,minLevel), name = level), name = symbol.name), symbol], axis = 0)
		else:
			return symbol

def interpolateYears(s, t = 't', method = 'linear', limit_area = 'inside', **kwargs):
	if isinstance(s.index, pd.MultiIndex):
		domsxt = [n for n in s.index.names if n != t]
		x = s.unstack(domsxt).astype(float)
		xf = x.combine_first(pd.DataFrame(None, index = pd.Index(range(x.index.min(), x.index.max()), name = t), columns = x.columns))
		return xf.interpolate(method = method, limit_area=limit_area, **kwargs).stack(level = domsxt, future_stack = True)
	elif isinstance(s.index, pd.Index):
		return s.astype(float).combine_first(pd.Series(None, index = pd.Index(range(s.index.min(), s.index.max()), name = t))).interpolate(method = method, limit_area=limit_area, **kwargs)

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
