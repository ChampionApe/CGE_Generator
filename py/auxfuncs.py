import pyDatabases, pandas as pd
from pyDatabases import OrdSet, noneInit, adj, adjMultiIndex

_stdOrder = OrdSet(['t','s','ss','n','nn','taxTypes','gc'])

def stdSort(symbol, order = None):
	if isinstance(pyDatabases.getIndex(symbol), pd.MultiIndex):
		return symbol.reorder_levels([x for x in noneInit(order, _stdOrder+OrdSet(pyDatabases.getDomains(symbol))) if x in pyDatabases.getDomains(symbol)])
	else:
		return symbol
