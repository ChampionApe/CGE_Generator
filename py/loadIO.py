import pyDatabases, os, pandas as pd, IOfunctions_withoutDurables
from pyDatabases import GpyDB, OrdSet, gpyDB, adjMultiIndex, noneInit
from pyDatabases.gpyDB_wheels import adj, read


def repeatIndex(s, i1 = 'n', i2 = 's'):
    return s.reset_index().assign(**{i2: s.index}).set_index([i2,i1]).iloc[:,0]

##################################################################
############# ------------	1. DURABLES ------------ #############
##################################################################

def addDurablesToDb(db, dur, t):
	""" Add data on durables to IO database"""
	[db.__setitem__(k, dur[k].xs(str(t),level='t')) for k in dur]

def getDurables(file, sheet, namesToInv, namesInvVariables, ilocs = None, **kwargs):
	""" High-level function going through the relevant durable methods"""
	df = durablesReadData(file, sheet) # read in data
	df = durablesAddIndices(df, namesToInv, namesInvVariables) # add relevant indices 
	return durablesCreateData(df, **kwargs) # return as dict of variables

def dfIlocs(x, ilocs):
	return x.iloc[ilocs[0]:ilocs[1],ilocs[2]:ilocs[3]]

def durablesReadData(file, sheet, ilocs = None):
	if ilocs is None:
		ilocs = [None, None, 1, None]
	return dfIlocs(pd.DataFrame(read.simpleLoad(file)[sheet].values), ilocs)

def durablesAddIndices(df, namesToInv, namesInvVariables):
	""" This takes the data from DST table and returns a dataframe with full indices.
		It includes a couple of hardcoded steps, e.g. that DST uses '..' syntax for missing values. """
	# 1. Add "dense" variable names to the first index
	variableRows = df[1].dropna()
	for i in range(len(variableRows)):
		if i < len(variableRows)-1:
			df.iloc[variableRows.index[i]:variableRows.index[i+1], 0] = namesInvVariables[variableRows.iloc[i]]
		else:
			df.iloc[variableRows.index[i]:, 0] = namesInvVariables[variableRows.iloc[i]]
	# 2. Add "dense" investment good type to the second index
	catRows = df[2].dropna()
	for i in range(len(catRows)):
		if i < len(catRows)-1:
			df.iloc[catRows.index[i]:catRows.index[i+1],1] = namesToInv[catRows.iloc[i]]
		else:
			df.iloc[catRows.index[i]:, 1] = namesToInv[catRows.iloc[i]]
	# 3. Add sector index
	branchIndex = df[3].dropna().str.split(' ').str[0]
	df.iloc[branchIndex.index[0]:branchIndex.index[-1]+1,2] = branchIndex
	df_ = df.dropna().set_index([1,2,3])
	df_.columns = pd.Index(df.iloc[2, df_.columns[0]-1:df_.columns[-1]], name = 't')
	df_k = df_.rename_axis(['var','n','s'],axis=0)
	return df_k.replace("..", 0)

def durablesCreateData(df, deprName = 'Depr1', durName = 'K', invName = 'I'):
	""" Adjust durables data for missing values issue: For the years 1990-1992
		investments are not identified on sufficiently detailed level. Instead,
		we use 'Depr1' to identify δK and back out the investment level from 
		the law of motion. """
	s = df.stack()
	vD_dur = s.xs(durName).rename('vD_dur')
	vD_depr= s.xs(deprName).rename('vD_depr')
	I_imputed = s.xs('Kp1')-vD_dur+vD_depr
	vD_inv = adj.rc_pd(I_imputed, pd.Index(['1990','1991','1992'], name = 't')).combine_first(s.xs(invName))
	return {'vD_dur': vD_dur, 'vD_depr': vD_depr, 'vD_inv': vD_inv}


###################################################################
############# ------------	2. Emissions ------------ #############
###################################################################

def addLevelToMultiIndex(symbol, level, values):
	return symbol.set_axis(symbol.reset_index().assign(**{level:values}).set_index([level]+symbol.index.names).index)

def addEmissionsToDb(db, emissions, t):
	""" Add data on emissions to main IO database """
	db['qCO2'] = emissions['qCO2'].xs(str(t),level='t')
	if str(t) in emissions['τ'].index.levels[1]:
		gpyDB.add_or_merge_vals(db, addLevelToMultiIndex(emissions['τ'].xs(str(t),level='t'), 'taxTypes','Emissions').rename('vTax'))

def emissionsReadData(file,scaleTaxes = 1000):
	""" Measure CO2 emissions in mio. tonnes, taxes in 1000 DKK"""
	rawData = read.simpleLoad(file)
	DRIVHUS = pd.DataFrame(rawData['DRIVHUS'].values)
	MRS1 = pd.DataFrame(rawData['MRS1'].values)
	MRO2 = pd.DataFrame(rawData['MRO2'].values)
	return {'qCO2': pd.DataFrame(DRIVHUS.iloc[1:,2:].values, columns = pd.Index(DRIVHUS.iloc[0,2:], name = 't'),
															index = pd.Index(DRIVHUS.iloc[1:,1], name = 's').str.split(' ').str[0]).dropna().stack()/1000,
			'τ': pd.DataFrame(MRS1.iloc[1:,2:].values,	columns = pd.Index(MRS1.iloc[0,2:], name = 't'),
															index 	= pd.Index(MRS1.iloc[1:,1], name = 's').str.split(' ').str[0]).dropna().stack()*scaleTaxes,
			'totalEmissions': pd.Series(MRO2.iloc[2,2:].values/1000, index = pd.Index(MRO2.iloc[0,2:], name = 't'))}

###########################################################################
############# ------------	3. Create model data ------------ #############
###########################################################################

def model_vS(db):
	vS = repeatIndex(adj.rc_pd(db.get('vD'), ('or', [db.get('n_p'), db.get('inv_p')])).groupby('n').sum())
	vS.loc[('HH','L')] = db.get('vD').xs('L',level='n').sum() # value of labor supply from households
	gpyDB.add_or_merge_vals(db, vS, name = 'vS') # add to database

def model_p(db):
	pDefault = pd.Series(1, index = db.get('vS').index.levels[-1].union(db.get('n_F')))
	gpyDB.add_or_merge_vals(db, pDefault, name = 'p')

def model_durables(db, glbl):
	gpyDB.add_or_merge_vals(db, adj.rc_pd(db.get('vD'), db.get('dur_p')), name = 'qD')
	staticUserCost = adjMultiIndex.applyMult(db.get('p').rename_axis(index = {'n':'nn'}), db.get('dur2inv')).dropna().droplevel('nn') * (glbl.db['R_LR'].vals/(1+glbl.db['infl_LR'].vals)+db.get('rDepr')-1)
	gpyDB.add_or_merge_vals(db, staticUserCost, name = 'pD_dur')

def model_quantNonDurables(db):
	gpyDB.add_or_merge_vals(db, adj.rc_pd(db.get('vD'), ('not', db.get('dur_p')))/db.get('p'), name = 'qD')
	gpyDB.add_or_merge_vals(db, db.get('vS') / db.get('p'), name = 'qS')
