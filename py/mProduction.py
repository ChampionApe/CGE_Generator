from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs
from pyDatabases import cartesianProductIndex as cpi
from gmsPython import Group, GModel 
import gamsProduction

class NestedCES(GModel):
	def __init__(self, tree, partial = False, initFromGms = None, taxInstr = 'tauLump', **kwargs):
		super().__init__(name = tree.name, database = tree.db, **kwargs)
		self.readTree(tree)
		self.partial = partial # use module in partial or general equilibrium; this affects compilation of groups 
		self.initFromGms = initFromGms
		self.taxInstr = taxInstr

	# 1. Specialized init methods:
	def readTree(self,tree):
		self.ns.update(tree.ns)
		self.ns.update({k: f'{self.name}_{k}' for k in ('sm','output_n','input_n')})
		self.db[self.n('sm')] = tree.db('s').copy()
		self.db[self.n('output_n')] = self.get('output').levels[-1]
		self.db[self.n('input_n')]  = self.get('input').levels[-1]
		[self.readTree_i(t) for t in tree.trees.values()];
		self.calibrationSubsets(tree)

	def readTree_i(self,t):
		self.addModule(t,**{k:v for k,v in t.__dict__.items() if k in ('name','ns','f','io','scalePreserving')})

	def calibrationSubsets(self, tree):
		self.ns.update({k: f'{self.name}_{k}' for k in ['endoMu']})
		self.db[self.n('endoMu')] = adj.rc_pd(self.get('map'), self.get('input').rename({'n':'nn'}))

	def addDurables(self):
		self.ns.update({k: f'{self.name}_{k}' for k in ('dur','inv', 'dur2inv', 'input_n')})
		self.db[self.n('dur')] = adj.rc_pd(self.get('input'), self.get('dur_p')) # read durables from the inputs included in the nesting tree inputs
		self.db[self.n('dur2inv')] = adjMultiIndex.applyMult(self.get('dur'), self.db('dur2inv')) 
		self.db[self.n('inv')] = adj.rc_pd(self.get('dur2inv').droplevel('n').unique(), alias = {'nn':'n'})
		self.db[self.n('input')] = self.get('input').difference(self.get('dur')).union(self.get('inv'))
		self.db[self.n('input_n')] = self.get('input').levels[-1]

	def initStuff(self, db = None, gdx = True):
		if db is not None:
			MergeDbs.merge(self.db, db)
		self.addDurables()
		self.initData()
		self.initGroups()
		if gdx:
			self.db.mergeInternal()

	def initData(self):
		""" Add initial values to database (only the ones data we do not have from an IO database though)"""
		self.db.aom(pd.Series(1,  index = cpi([self.db('txE'), self.get('output')])), name = 'pS', priority = 'first') # get initial value for pS
		self.db.aom(pd.Series(1,  index = cpi([self.db('txE'), self.get('int')])), name = 'pD', priority = 'first') # prices on intermediate goods
		self.db.aom(pd.Series(.5,  index = self.get('dur')), name = 'adjCostPar', priority = 'first') # parameter in investment cost function
		self.db.aom(pd.Series(0,  index = self.get('dur')), name = 'K_tvc', priority='first') # tvc condition for durables
		self.db.aom(pd.Series(0,  index = cpi([self.db('txE'), self.get('sm')]), name = 'adjCost'), priority='first') # adjustment costs
		self.db.aom(pd.Series(.1, index = self.get('sm')), name = 'markup', priority='first') #
		self.db.aom(pd.Series(0, index = cpi([self.db('t'), self.get('sm')])), name = 'vA', priority = 'first')
		self.db.aom(pd.Series(0, index = cpi([self.db('txE'), self.get('sm')])), name = 'divd', priority='first')
		self.db.aom(pd.Series(0,  index = self.get('sm')), name = 'taxRevPar')
		self.db.aom(self.get(self.taxInstr).copy(), name = f'{self.taxInstr}0')


	# 2. Model specification:
	@property
	def model_B(self):
		return OrdSet([f"B_{name}" for name in self.m])+OrdSet([f"B_{self.name}_{k}" for k in ('adjCost','pWedge','firmValue')])
	@property
	def model_C(self):
		return self.model_B+OrdSet([f'B_{self.name}_taxCalib'])

	@property
	def textBlocks(self):
		return self.nestingBlocks | {'adjCost': self.adjCostBlocks, 'pWedge': self.priceWedgeBlocks, 'firmValue': self.firmValueBlocks, 'taxCalib': self.taxCalibBlocks}
	@property
	def nestingBlocks(self):
		return {name: getattr(gamsProduction, m.f)(name) for name, m in self.m.items()}
	@property
	def adjCostBlocks(self):
		return gamsProduction.sqrAdjCosts(f'{self.name}_adjCost', self.name)
	@property
	def priceWedgeBlocks(self):
		return gamsProduction.priceWedgeEmissions(f'{self.name}_pWedge', self.name)
	@property
	def firmValueBlocks(self):
		return gamsProduction.firmValueWithAdjCosts(f'{self.name}_firmValue', self.name)
	@property
	def taxCalibBlocks(self):
		return gamsProduction.taxCalibration(f'{self.name}_taxCalib', self.name, self.g(self.taxInstr), self._taxInstrCondition)

	# 3. Groups
	@property
	def _taxInstrCondition(self):
		if self.taxInstr == 'tauLump':
			return self.g('sm')
		elif self.taxInstr == 'tauS':
			return self.g('output')
		elif self.taxInstr == 'tauD':
			return self.g('input')

	# Group properties:
	@property
	def metaGroup_endo_B(self):
		return Group(f'{self.name}_endo_B', g = [self.groups[f'{self.name}_{k}'] for k in ('alwaysEndo','exoInCalib')])
	@property
	def metaGroup_endo_C(self):
		return Group(f'{self.name}_endo_C', g = [self.groups[f'{self.name}_{k}'] for k in ('alwaysEndo', 'endoInCalib')])
	@property
	def metaGroup_exo_B(self):
		return Group(f'{self.name}_exo_B', g = [self.groups[f'{self.name}_{k}'] for k in ('alwaysExo','endoInCalib')])
	@property
	def metaGroup_exo_C(self):
		return Group(f'{self.name}_exo_C', g = [self.groups[f'{self.name}_{k}'] for k in ('alwaysExo','exoInCalib')])

	@property
	def group_alwaysExo(self):
		if not self.partial:
			return Group(f'{self.name}_alwaysExo', 
						v = [('sigma', self.g('kninp')), ('mu', self.g('map')), ('rDepr', self.g('dur')), ('adjCostPar', self.g('dur')), ('K_tvc', self.g('dur')), # parameters
							 ('tauD', self.g('input')), ('tauS', self.g('output')), ('tauLump', self.g('sm')), ('tauCO2', ('and', [self.g('output'), self.g('dqCO2')])), # taxes
							 ('qD', ('and', [self.g('dur'), self.g('t0')])), (f'{self.taxInstr}0', self._taxInstrCondition)],
					sub_v = [(self.taxInstr, self._taxInstrCondition)])
		else:
			self.partial = False
			g = self.group_alwaysExo
			g.v += [('qS', self.g('output')), ('p',self.g('input_n')), ('qCO2', ('and', [self.g('output'), self.g('dqCO2')])), 
					('uCO2', ('and', [self.g('output'), self.g('dqCO2')])), ('tauEffCO2', ('and', [self.g('output'), self.g('dqCO2')])), 'Rrate']
			g.sub_v += [('p',self.g('output_n'))]
			self.partial = True
			return g

	@property
	def group_alwaysEndo(self):
		return Group(f'{self.name}_alwaysEndo', v = [('pD', ('or', [self.g('int'), self.g('input')])),
													 ('pS', self.g('output')),
													 ('p', ('and', [self.g('output_n'), self.g('tx0')])),
													 ('qD', self.g('int')),
													 ('qD', ('and', [self.g('input'), self.g('tx0')])),
													 ('qD', ('and', [self.g('dur'), self.g('tx0')])),
													 ('pD', ('and', [self.g('dur'), self.g('txE')])),
													 ('adjCost', ('and', [self.g('sm'), self.g('txE')])),
													 ('TotalTax', ('and', [self.g('sm'), self.g('tx0E')])),
													 ('vA', self.g('sm')), ('divd', self.g('sm'))])

	@property
	def group_exoInCalib(self):
		return Group(f'{self.name}_exoInCalib', v = [('qD', ('and', [self.g('input'), self.g('t0')])),
													 ('p',  ('and', [self.g('output_n'), self.g('t0')])),
													 ('TotalTax', ('and', [self.g('sm'), self.g('t0')]))])

	@property
	def group_endoInCalib(self):
		return Group(f'{self.name}_endoInCalib', v = [('mu', self.g('endoMu')),
													  ('markup', self.g('sm')),
													  ('taxRevPar', self.g('sm')),
													  (self.taxInstr, self._taxInstrCondition)])


class NestedCES_PC(NestedCES):
	""" Like NestedCES, but with $j$-terms instead of markups to emulate perfect competition"""
	def __init__(self, tree, partial = False, **kwargs):
		super().__init__(tree, partial = partial,**kwargs)

	def initData(self):
		super().initData()
		self.db.aom(pd.Series(0, index = self.get('sm')), name = 'jTerm', priority='first') 

	@property
	def priceWedgeBlocks(self):
		return gamsProduction.priceWedgeEmissionsPC(f'{self.name}_pWedge', self.name)

	@property
	def group_endoInCalib(self):
		g = super().group_endoInCalib
		g.v += [('jTerm', self.g('sm'))]
		g.sub_v += [('markup', self.g('sm'))]
		return g