from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs
from pyDatabases import cartesianProductIndex as cpi
from gmsPython import Group, GModel, gmsWrite
import ProductionFiles.gamsProduction as gamsProduction

# def StaticNCES(tree, extension = 'base', **kwargs):
# 	""" Convenience function to initialize classes based on 'extension' """
# 	return globals()[f'StaticNCES_{extension}'](tree, **kwargs)

class StaticNCES(GModel):
	""" Static Production Module with Nested CES Structure"""
	def __init__(self, tree, partial = False, initFromGms = None, taxInstr = 'tauLump', properties = None, **kwargs):
		super().__init__(name = tree.name, database = tree.db, **kwargs)
		self.readTree(tree)
		self.partial = partial # use module in partial or general equilibrium; this affects compilation of groups 
		self.initFromGms = initFromGms
		self.taxInstr = taxInstr
		StaticNCES.initProperties(self, **noneInit(properties, {}))

	# 1. Specialized init methods:
	def readTree(self,tree):
		self.ns.update(tree.ns)
		self.ns.update({k: f'{self.name}_{k}' for k in ('sm','endoP','input_n')})
		self.db[self.n('sm')] = tree.db('s').copy()
		self.db[self.n('endoP')] = self.get('output').levels[-1] # prices that are endogenous, also in partial eq.
		self.db[self.n('input_n')]  = self.get('input').levels[-1]
		[self.readTree_i(t) for t in tree.trees.values()];
		self.calibrationSubsets(tree)

	def readTree_i(self,t):
		self.addModule(t,**{k:v for k,v in t.__dict__.items() if k in ('name','ns','f','io','scalePreserving')})

	def calibrationSubsets(self, tree):
		self.ns.update({k: f'{self.name}_{k}' for k in ['endoMu']})
		self.db[self.n('endoMu')] = adj.rc_pd(self.get('map'), self.get('input').rename({'n':'nn'}))

	def initStuff(self, db = None, gdx = True):
		if db is not None:
			MergeDbs.merge(self.db, db)
		self.initData()
		self.initGroups()
		if gdx:
			self.db.mergeInternal()

	def initData(self):
		""" Add initial values to database (only the ones data we do not have from an IO database though)"""
		self.db.aom(pd.Series(1,  index = cpi([self.db('txE'), self.get('output')])), name = 'pS', priority = 'first') # get initial value for pS
		self.db.aom(pd.Series(1,  index = cpi([self.db('txE'), self.get('int')])), name = 'pD', priority = 'first') # prices on intermediate goods
		self.db.aom(pd.Series(0, index = self.get('sm')), name = 'markup', priority='first') #
		self.db.aom(pd.Series(0, index = cpi([self.db('t'), self.get('sm')])), name = 'vA', priority = 'first')
		self.db.aom(pd.Series((1+self.get('g_LR'))*(1+self.get('infl_LR'))-1,  index = self.get('sm')), name = 'vA_tvc', priority='first') # tvc condition for durables
		self.db.aom(pd.Series(0, index = cpi([self.db('txE'), self.get('sm')])), name = 'divd', priority='first')
		self.db.aom(pd.Series(0,  index = self.get('sm')), name = 'taxRevPar')
		self.db.aom(self.get(self.taxInstr).copy(), name = f'{self.taxInstr}0')

	@staticmethod
	def initProperties(self, **kwargs):
		[self.addProperty(k,v) for k,v in ({'addMarginal': '', 'addCosts': '', 'addTax': ''} | kwargs).items()]

	# 2. Model specification:
	@property
	def model_B(self):
		return OrdSet([f"B_{name}" for name in self.m])+OrdSet([f"B_{self.name}_{k}" for k in ('price','firmValue')])
	@property
	def model_C(self):
		return self.model_B+OrdSet([f'B_{self.name}_taxCalib'])
	@property
	def textBlocks(self):
		return self.nestingBlocks | {'price': self.priceBlocks, 'firmValue': self.firmValueBlocks, 'taxCalib': self.taxCalibBlocks}
	@property
	def nestingBlocks(self):
		return {name: getattr(gamsProduction, m.f)(name) for name, m in self.m.items()}
	@property
	def priceBlocks(self):
		return gamsProduction.priceBlock(f'{self.name}_price', self.name, addMarginal = self.addMarginal, addTax = self.addTax)
	@property
	def firmValueBlocks(self):
		return gamsProduction.firmValueBlock(f'{self.name}_firmValue', self.name, addCosts = self.addCosts)
	@property
	def taxCalibBlocks(self):
		return gamsProduction.taxCalibBlock(f'{self.name}_taxCalib', self.name, self.g(self.taxInstr), self._taxInstrCondition)

	# 3. Prespecified modes of the module: Add emission regulation. Add emission regulation with abatement costs. Specify tax instrument used in calibration.
	# change between different tax instruments used to ensure correct total of taxes are collected in calibration stage:
	@property
	def _taxInstrCondition(self):
		if self.taxInstr == 'tauLump':
			return self.g('sm')
		elif self.taxInstr == 'tauS':
			return self.g('output')
		elif self.taxInstr == 'tauD':
			return self.g('input')

	@property
	def textInit(self):
		return "" if self.initFromGms is None else getattr(gamsProduction, f'{self.initFromGms}')(self.name)

	# 4. Group properties:
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
		g = Group(f'{self.name}_alwaysExo', v = [('sigma', self.g('kninp')), ('mu', self.g('map')), ('vA_tvc', self.g('sm')), # parameters
												 ('tauD', self.g('input')), ('tauS', self.g('output')), ('tauLump', self.g('sm')), # taxes
												 (f'{self.taxInstr}0', self._taxInstrCondition)],
											sub_v = [(self.taxInstr, self._taxInstrCondition), ('mu', self.g('endoMu'))])
		if not self.partial:
			return g
		else:
			g.v += [('qS', self.g('output')), ('p',self.g('input_n')), 'Rrate']
			g.sub_v += [('p',self.g('endoP'))]
			return g

	@property
	def group_alwaysEndo(self):
		return Group(f'{self.name}_alwaysEndo', v = [('pD', ('or', [self.g('int'), self.g('input')])),
													 ('pS', self.g('output')),
													 ('p', ('and', [self.g('endoP'), self.g('tx0')])),
													 ('qD', self.g('int')),
													 ('qD', ('and', [self.g('input'), self.g('tx0')])),
													 ('TotalTax', ('and', [self.g('sm'), self.g('tx0E')])),
													 ('vA', self.g('sm')), ('divd', self.g('sm'))])

	@property
	def group_exoInCalib(self):
		return Group(f'{self.name}_exoInCalib', v = [('qD', ('and', [self.g('input'), self.g('t0')])),
													 ('p',  ('and', [self.g('endoP'), self.g('t0')])),
													 ('TotalTax', ('and', [self.g('sm'), self.g('t0')]))])

	@property
	def group_endoInCalib(self):
		return Group(f'{self.name}_endoInCalib', v = [('mu', self.g('endoMu')),
													  ('markup', self.g('sm')),
													  ('taxRevPar', self.g('sm')),
													  (self.taxInstr, self._taxInstrCondition)])


class StaticNCES_emission(StaticNCES):
	""" Static Production Module with Nested CES Structure"""
	def __init__(self, tree, abateCosts = False, **kwargs):
		super().__init__(tree, **kwargs)
		StaticNCES_emission.addProperties(self, abateCosts = abateCosts)

	@staticmethod
	def initProperties(self, abateCosts = False, **kwargs):
		super().initProperties(self, **kwargs)
		StaticNCES_emission.addProperties(self, abateCosts = abateCosts)

	@staticmethod
	def addProperties(self, abateCosts = False):
		self._addMarginal += """+(tauEffCO2[t,s,n]*uCO2[t,s,n])$(dqCO2[s,n])"""
		self._addTax += f"""+sum(n$({self.name}_output[s,n] and dqCO2[s,n]), tauCO2[t,s,n]*qCO2[t,s,n])"""
		self.addAbatementCosts(abateCosts)

	def addAbatementCosts(self, abateCosts):
		self.addProperty('abateCosts', abateCosts) # add specification of abatement costs
		if abateCosts:
			self.db.aom(pd.Series(0, index= cpi([self.db('txE'), self.get('dqCO2')])), name = 'abateCosts', priority='first')
			if abateCosts in ('SqrAdjCosts','SqrUtilCosts'):
				self._addCosts += """-sum(n$(dqCO2[s,n]), abateCosts[t,s,n]+adjCostEOP[t,s,n])"""
				self.db.aom(pd.Series(0, index= cpi([self.db('txE'), self.get('dqCO2')])), name = 'adjCostEOP', priority='first')
			elif abateCosts is True:
				self._addCosts += """-sum(n$(dqCO2[s,n]), abateCosts[t,s,n])"""

	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.v += [('tauCO2', ('and', [self.g('output'), self.g('dqCO2')]))]
		if not self.partial:
			return g
		else:
			g.v += [('qCO2', ('and', [self.g('output'), self.g('dqCO2')])), ('uCO2', ('and', [self.g('output'), self.g('dqCO2')])), ('tauEffCO2', ('and', [self.g('output'), self.g('dqCO2')]))]
			if self.abateCosts:
				g.v += [('abateCosts', self.g('dtauCO2'))]
				if self.abateCosts in ('SqrAdjCosts', 'SqrUtilCosts'):
					g.v += [('adjCostEOP', ('and', [self.g('txE'), self.g('dqCO2')]))]
			return g


class InvestNCES(StaticNCES):
	def initData(self):
		""" Add initial values to database (only the ones data we do not have from an IO database though)"""
		self.db.aom(pd.Series(1,  index = cpi([self.db('txE'), self.get('output')])), name = 'pS', priority = 'first') # get initial value for pS
		self.db.aom(pd.Series(1,  index = cpi([self.db('txE'), self.get('int')])), name = 'pD', priority = 'first') # prices on intermediate goods
		self.db.aom(pd.Series(0, index = self.get('sm')), name = 'markup', priority='first') #
		self.db.aom(pd.Series(0,  index = self.get('sm')), name = 'taxRevPar')
		self.db.aom(self.get(self.taxInstr).copy(), name = f'{self.taxInstr}0')

	#### 2. GROUPINGS AND MODEL SPECIFICATIONS:
	# 2. Model specification:
	@property
	def model_B(self):
		return super().model_B - OrdSet([f"B_{self.name}_firmValue"])
	@property
	def textBlocks(self):
		d = super().textBlocks
		d.pop('firmValue')
		return d

	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.sub_v = [('vA_tvc', self.g('sm'))]
		return g

	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		g.sub_v = [('vA', self.g('sm')), ('divd',self.g('sm'))]
		return g
