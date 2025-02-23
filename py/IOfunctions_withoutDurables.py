from auxfuncs import *
import numpy as np
from pyDatabases.gpyDB import GpyDB, DbFromExcel

_stdOffset = {'row0': 1, 'rowE': -1, 'col0': 0, 'colE': -1}

def getLoc(x, loc):
	return x[x==loc].index[0]
def getOffset(r,c):
	return _stdOffset | r['offset'] | c['offset']
def getLocs(r = None, rr = None, c = None, cc = None, rowCategories = None, colCategories = None):
	o = getOffset(r, c)
	return [(getLoc(rowCategories, r['ref'])+o['row0'], getLoc(rowCategories, rr['ref'])+o['rowE']+1), 
			(getLoc(colCategories, c['ref'])+o['col0'], getLoc(colCategories, cc['ref'])+o['colE']+1)]
def extractBlock(df, locs):
	return df.iloc[locs[0][0]:locs[0][1], locs[1][0]:locs[1][1]]
def extractRow(df, rMarker, cMarkers, r = 0, c = 1, rIndex = 3):
    return pd.Series(df.iloc[getLoc(df.iloc[:,r], rMarker),getLoc(df.iloc[1,:], cMarkers[0]):getLoc(df.iloc[c,:], cMarkers[1])].values, index = pd.Index(df.iloc[rIndex,getLoc(df.iloc[1,:], cMarkers[0]):getLoc(df.iloc[c,:], cMarkers[1])], name = 's', dtype=str))
def mergeNone(x,y):
	return x if y is None else x | y

def standardCleanSettings(db, threshold):
	""" The standard settings for the RAS adjustments """
	return {'AI': createDataBlock(db('vD'), ('and', [db('n_p'),  ('or', [db('s_p'), db('s_i')])]), threshold),
			'BJ': createDataBlock(db('vD'), ('and', [db('n_F'), ('or', [db('s_p'), db('s_i')])]), threshold, leaveCols = db('n_F'))}

def createDataBlock(v0, conditions, threshold, leaveRows = None, leaveCols = None):
	d = {'v0': adj.rc_pd(v0, conditions), 'kwargs': {'leaveRows': leaveRows, 'leaveCols': leaveCols}}
	d['vBar'] = sparseNonNegative(d, threshold)
	return d

def sparseNonNegative(d, threshold):
	""" Leave out anything below a threshold value"""
	lmo = leaveOutMax(d['v0'])
	return lmo[lmo<threshold] * 0

def leaveOutMax(v0):
	max_i = pd.MultiIndex.from_tuples(v0.astype(float).groupby(v0.index.names[0]).idxmax().values, names = v0.index.names)
	max_j = pd.MultiIndex.from_tuples(v0.astype(float).groupby(v0.index.names[1]).idxmax().values, names = v0.index.names)
	return adj.rc_pd(v0, ('not', ('or', [max_i, max_j])))

class readIO:
	def __init__(self, name = None, db = None, ws = None, file_v = None, kwargs_v = None):
		self.db = GpyDB(name = name, db = db, ws = ws, alias = [('n','nn'),('n','nnn'), ('s','ss'), ('t','tt')])
		self.wb = {'v': DbFromExcel.simpleLoad(file_v)}
		self.IO = {'v': pd.DataFrame(self.wb['v']['IO'].values)}
		self.locs = {}
		self.blocks = {}
		self.s = {}
		self.addSettings_v(**noneInit(kwargs_v,{}))

	@property
	def stdSettings_v(self):
		return {'taxCategories': ['Produktskatter og subsidier, netto', 'Moms', 'Andre produktionsskatter', 'Andre produktionssubsidier'],
				'wageCategory' : 'Aflønning af ansatte',
				'residualIncomeCategory': 'Overskud af produktionen og blandet indkomst',
				'itoryCategories': ['5300','5200'],
				'exportCategory': '6000',
				'rowIndex': self.IO['v'].iloc[:,0].astype(str),
				'colIndex': self.IO['v'].iloc[2,:].astype(str)}

	@property
	def stdRowMarkers_v(self):
		return {'P': {'ref': 'Dansk produktion','offset': {}},
				'M': {'ref': 'Import', 'offset': {}},
				'OT': {'ref': 'Andre udenlandske transaktioner', 'offset': {}},
				'PI': {'ref': 'Primære inputs', 'offset': {}},
				'TI': {'ref': 'Input/ endelig anvendelse i køberpriser', 'offset': {}},
				'PV': {'ref': 'Produktionsværdi', 'offset': {}}
				}

	@property
	def stdColMarkers_v(self):
		return {'In': {'ref': 'Input i produktionen (Transaktionskode 2000)', 'offset': {'colE': -2}},
				'C' : {'ref': 'Privat forbrug (Transaktions-kode 3110)', 'offset': {'colE': -1}},
				'G_NPISH': {'ref': 'NPISH (Transaktionskode 3130)', 'offset': {}},
				'G_MVPC' : {'ref': 'Markedsmæssigt individuelt offentligt forbrug (Transaktionskode 3141)', 'offset': {}},
				'G_NMVPC': {'ref': 'Ikke markedsmæssigt individuelt offentligt forbrug (Transaktionskode 3142)', 'offset': {}},
				'G_CPC':   {'ref': 'Kollektivt offentligt forbrug (Transaktionskode 3200)', 'offset': {}},
				'I': {'ref': 'Faste bruttoinvesteringer', 'offset': {}},
				'Other': {'ref': 'Andre Anvendelser', 'offset':{}},
				'T': {'ref': 'Total'}
				}

	def cleanOtherForeignTransactions(self):
		[self.add_OFT_to_imports(x) for x in self.db.varDom('n')['n'] if not adj.rc_pd(self.db(x), self.db('n_Fother')).empty];

	def add_OFT_to_imports(self,x):
		m, oft = adj.rc_pd(self.db(x), self.db('n_F')), pyDatabases.pdSum(adj.rc_pd(self.db(x), self.db('n_Fother')),'n')
		y = m + oft * m / (pyDatabases.pdSum(m,'n').replace(0,1))
		if max(abs(pyDatabases.pdSum(y,'n')-pyDatabases.pdSum(m,'n')-oft))<1e-6:
			self.db[x] = y.combine_first(adj.rc_pd(self.db(x), ('not', self.db('n_Fother'))))
		else:
			print(f"Warning: The variable {x} could not add 'other foreign transactions' (OFT) to regular imports in a uniform manner. The issue is likely that there is a sector with no 'import', but OFT.")

	def addSettings_i(self,rMarker = None, cMarkers = None, row=0,col=1,rowIndex=3):
		self.s['i'] = {'rMarker': noneInit(rMarker,'Investering i alt, købepriser'), 'cMarkers': noneInit(cMarkers, ['Investerende brancher', 'Total']), 'row': row, 'col': col, 'rowIndex': rowIndex}

	def addSettings_v(self, category = None, rowMarkers = None, colMarkers = None):
		self.s['v'] = mergeNone(self.stdSettings_v, category) | {'rowMarkers': mergeNone(self.stdRowMarkers_v, rowMarkers), 'colMarkers': mergeNone(self.stdColMarkers_v, colMarkers)}
	
	def getBlocks(self, df, rKeys, cKeys, rVals, cVals, rowCategories, colCategories):
		locs = {f"{rKeys[i]}/{cKeys[j]}": getLocs(r=rVals[i], rr = rVals[i+1], c = cVals[j], cc = cVals[j+1], rowCategories = rowCategories, colCategories = colCategories)
					for j in range(len(cKeys)-1) for i in range(len(rKeys)-1)}
		blocks = {k: extractBlock(df, locs[k]) for k in locs}
		return locs, blocks

	def __call__(self):
		self.getIOv()
		return self.db

	def getIOv(self):
		self.locs['v'], self.blocks['v'] = self.getBlocks(self.IO['v'], list(self.s['v']['rowMarkers']), list(self.s['v']['colMarkers']), list(self.s['v']['rowMarkers'].values()), list(self.s['v']['colMarkers'].values()),self.IO['v'].iloc[:,0],self.IO['v'].iloc[0,:])
		self.addIOv

	@property
	def addIOv(self):
		[getattr(self, f'addIOv_{x}') for x in ('production','consumption','investment','other')];	

	@property
	def addIOv_production(self):
		rindex = self.s['v']['rowIndex']
		# Block A
		self.db['s_p'] = pd.Index(rindex.iloc[self.locs['v']['P/In'][0][0]:self.locs['v']['P/In'][0][1]], name = 's')
		self.db['n_p'] = self.db('s_p').rename('n')
		self.blocks['v']['P/In'].index = self.db('n_p')
		self.blocks['v']['P/In'].columns = self.db('s_p')
		# Block B
		self.db['n_F'] = self.db('n_p')+'_F'
		self.blocks['v']['M/In'].index = self.db('n_F')
		self.blocks['v']['M/In'].columns = self.db('s_p')
		# Block C:
		self.db['n_Fother'] = pd.Index(rindex.iloc[self.locs['v']['OT/In'][0][0]:self.locs['v']['OT/In'][0][1]], name = 'n')
		self.blocks['v']['OT/In'].index = self.db('n_Fother')
		self.blocks['v']['OT/In'].columns = self.db('s_p')
		# Block D:
		D = pd.concat([self.blocks['v']['PI/In'], self.blocks['v']['TI/In']])
		self.db['taxTypes'] = pd.Index(self.s['v']['taxCategories'], name = 'taxTypes')
		D.index = pd.Index(rindex.iloc[self.locs['v']['PI/In'][0][0]:self.locs['v']['PI/In'][0][1]]).union(
						   rindex.iloc[self.locs['v']['TI/In'][0][0]:self.locs['v']['TI/In'][0][1]], sort = False).rename('temp')
		D.columns = self.db('s_p')
		self.db.aom(adj.rc_pd(D, self.db('taxTypes').rename('temp')).rename_axis(index={'temp':'taxTypes'}).stack(), name = 'vTax')
		self.db.aom(self.db('vTax').groupby('s').sum(), name = 'TotalTax')
		w = D.xs(self.s['v']['wageCategory'])
		w.index = pd.MultiIndex.from_product([pd.Index(['L'], name = 'n'), w.index])
		res = D.xs(self.s['v']['residualIncomeCategory'])
		res.index = pd.MultiIndex.from_product([pd.Index(['resIncome'], name = 'n'), res.index])
		# Collect values in vector vD:
		self.db.aom(pd.concat([self.blocks['v']['P/In'].stack(), self.blocks['v']['M/In'].stack(), self.blocks['v']['OT/In'].stack(), w, res]), name = 'vD')

	@property
	def addIOv_consumption(self):
		rindex, cindex = self.s['v']['rowIndex'], self.s['v']['colIndex']
		# Block E1-F1: Private consumption
		pc =  pd.concat([self.blocks['v']['P/C'].iloc[:,0].set_axis(self.db('n_p')),
						 self.blocks['v']['M/C'].iloc[:,0].set_axis(self.db('n_F')),
						 self.blocks['v']['OT/C'].iloc[:,0].set_axis(self.db('n_Fother'))])
		self.db['s_HH'] = pd.Index(['HH'], name = 's')
		pc.index = pd.MultiIndex.from_product([pc.index, self.db('s_HH')])
		# Block G1-H1:
		self.blocks['v']['PI/C'].index = pd.Index(rindex.iloc[self.locs['v']['PI/C'][0][0]:self.locs['v']['PI/C'][0][1]], name = 'taxTypes')
		HHTax = self.blocks['v']['PI/C'].iloc[:,0]
		HHTax.index = pd.MultiIndex.from_product([HHTax.index, self.db('s_HH')])
		# Block E2-F2: Government consumption
		self.db['s_G'] = pd.Index(['G'],name='s')
		gcomp = [c for c in self.s['v']['colMarkers'] if c.startswith('G_')]
		gc = pd.Index(cindex.iloc[self.locs['v'][f'P/{gcomp[0]}'][1][0]:self.locs['v'][f'P/{gcomp[-1]}'][1][1]], name = 'gc')
		gc_value = pd.concat([pd.concat([self.blocks['v'][f'P/{g}'] for g in gcomp],axis=1),
							  pd.concat([self.blocks['v'][f'M/{g}'] for g in gcomp],axis=1),
							  pd.concat([self.blocks['v'][f'OT/{g}'] for g in gcomp],axis=1)], axis = 0)
		gc_value.index = pd.Index(np.hstack([self.db(i) for i in ('n_p','n_F','n_Fother')]), name = 'n')
		gc_value.columns = gc
		self.db['gc'] = gc.unique()
		self.db.aom(gc_value.stack().groupby(['n','gc']).sum(), name = 'vC')
		gcTotal = gc_value.sum(axis=1)
		gcTotal.index = pd.MultiIndex.from_product([gcTotal.index, self.db('s_G')])
		# Block G2-H2:
		GovernmentTax = pd.concat([self.blocks['v'][f'PI/{g}'] for g in gcomp],axis=1)
		GovernmentTax.columns = gc
		GovernmentTax.index = pd.Index(rindex.iloc[self.locs['v'][f'PI/{gcomp[0]}'][0][0]:self.locs['v'][f'PI/{gcomp[0]}'][0][1]], name = 'taxTypes')
		self.db.aom(GovernmentTax.stack().groupby(['taxTypes','gc']).sum(), name = 'vC_tax')
		GTax = GovernmentTax.sum(axis=1)
		GTax.index = pd.MultiIndex.from_product([GTax.index, self.db('s_G')])
		# Collect values in vTax, TotalTax, and vD:
		self.db.aom(pd.concat([pc, gcTotal],axis=0), name='vD')
		self.db.aom(pd.concat([HHTax, GTax],axis=0), name='vTax')
		self.db.aom(pd.concat([HHTax.groupby('s').sum(), GTax.groupby('s').sum()],axis=0), name='TotalTax')

	@property
	def addIOv_investment(self):
		# Block I-K:
		self.db['s_i'] = pd.Index(self.s['v']['colIndex'].iloc[self.locs['v']['P/I'][1][0]:self.locs['v']['P/I'][1][1]], name = 's').astype(str)
		vD_inv = pd.concat([self.blocks['v'][f'{x}/I'] for x in ('P','M','OT')], axis = 0)
		vD_inv.columns = self.db('s_i')
		vD_inv.index = pd.Index(np.hstack([self.db(i) for i in ('n_p','n_F','n_Fother')]), name = 'n')
		self.db.aom(vD_inv.stack(), name='vD')
		# Block L:
		self.blocks['v']['PI/I'].index = pd.Index(self.s['v']['rowIndex'].iloc[self.locs['v']['PI/I'][0][0]:self.locs['v']['PI/I'][0][1]], name = 'taxTypes')
		self.blocks['v']['PI/I'].columns = self.db('s_i')
		self.db.aom(self.blocks['v']['PI/I'].stack(), name='vTax')
		self.db.aom(self.blocks['v']['PI/I'].sum(axis=0), name='TotalTax')

	@property
	def addIOv_other(self):
		# Exports and inventories, block M-P (this is very ad hoc)
		self.db['s_f'] = pd.Index(['F'], name = 's')
		M2P = pd.concat([self.blocks['v'][f'{x}/Other'] for x in ('P','M','OT')], axis = 0)
		M2P.columns = pd.Index(self.s['v']['colIndex'].iloc[self.locs['v']['P/Other'][1][0]:self.locs['v']['P/Other'][1][1]], name = 'temp').astype(str)
		M2P.index = pd.Index(np.hstack([self.db(i) for i in ('n_p','n_F','n_Fother')]), name = 'n')
		itory = M2P.loc[:, self.s['v']['itoryCategories']].sum(axis=1).rename('vD')
		itory.index = pd.MultiIndex.from_product([itory.index, pd.Index(['itory'], name = 's')])
		export= adj.rc_pd(M2P[self.s['v']['exportCategory']], self.db('n_p')).rename('vD')
		export.index = pd.MultiIndex.from_product([export.index, self.db('s_f')])
		self.db.aom(pd.concat([itory, export], axis=0), name = 'vD')
		# Taxes:
		self.blocks['v']['PI/Other'].index = pd.Index(self.s['v']['rowIndex'].iloc[self.locs['v']['PI/Other'][0][0]:self.locs['v']['PI/Other'][0][1]], name = 'taxTypes')
		self.blocks['v']['PI/Other'].columns = M2P.columns
		itory_tax  = self.blocks['v']['PI/Other'].loc[:,self.s['v']['itoryCategories']].sum(axis=1)
		export_tax = self.blocks['v']['PI/Other'][self.s['v']['exportCategory']]
		export_tax.index = pd.MultiIndex.from_product([export_tax.index, self.db('s_f')])
		itory_tax.index  = pd.MultiIndex.from_product([itory_tax.index,  itory.index.levels[-1]])
		self.db.aom(pd.concat([itory_tax, export_tax], axis=0), name = 'vTax')
		self.db.aom(pd.concat([export_tax.groupby('s').sum(), itory_tax.groupby('s').sum()],axis=0), name = 'TotalTax')