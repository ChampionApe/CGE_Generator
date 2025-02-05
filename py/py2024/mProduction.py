from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs
from pyDatabases import cartesianProductIndex as cpi
from gmsPython import gmsWrite, Group, GModel
import gamsProduction

class StaticNCES(GModel):
	""" Static Production Module with Nested CES Structure"""
	def __init__(self, tree, partial = False, initFromGms = None, taxInstr = 'tauLump', **kwargs):
		super().__init__(name = tree.name, database = tree.db, **kwargs)
		self.readTree(tree)
		self.partial = partial # use module in partial or general equilibrium; this affects compilation of groups 
		self.initFromGms = initFromGms
		self.taxInstr = taxInstr
		self.initProperties()

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
		self.db.aom(pd.Series(0,  index = self.get('sm')), name = 'vA_tvc', priority='first') # tvc condition for durables
		self.db.aom(pd.Series(0, index = cpi([self.db('txE'), self.get('sm')])), name = 'divd', priority='first')
		self.db.aom(pd.Series(0,  index = self.get('sm')), name = 'taxRevPar')
		self.db.aom(self.get(self.taxInstr).copy(), name = f'{self.taxInstr}0')

	def initProperties(self, **kwargs):
		[self.addProperty(k,v) for k,v in ({'addMarginal': '', 'addCosts': '', 'addTax': '', 'emissionReg': False, 'abateCosts': False} | kwargs).items()]

	# 2. Model specification:
	@property
	def model_B(self):
		return OrdSet([f"B_{name}" for name in self.m])+OrdSet([f"B_{self.name}_{k}" for k in ('pWedge','firmValue')])
	@property
	def model_C(self):
		return self.model_B+OrdSet([f'B_{self.name}_taxCalib'])

	@property
	def textBlocks(self):
		return self.nestingBlocks | {'pWedge': self.priceWedgeBlocks, 'firmValue': self.firmValueBlocks, 'taxCalib': self.taxCalibBlocks}
	@property
	def nestingBlocks(self):
		return {name: getattr(gamsProduction, m.f)(name) for name, m in self.m.items()}
	@property
	def priceWedgeBlocks(self):
		return gamsProduction.priceWedge(f'{self.name}_pWedge', self.name, addMarginal = self.addMarginal, addTax = self.addTax)
	@property
	def firmValueBlocks(self):
		return gamsProduction.firmValue(f'{self.name}_firmValue', self.name, addCosts = self.addCosts)
	@property
	def taxCalibBlocks(self):
		return gamsProduction.taxCalibration(f'{self.name}_taxCalib', self.name, self.g(self.taxInstr), self._taxInstrCondition)


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

	# add emission regulation and abatement costs
	def addEmissions(self, abateCosts = False):
		self.emissionReg = True
		self._addMarginal += """+(tauEffCO2[t,s,n]*uCO2[t,s,n])$(dqCO2[s,n])"""
		self._addTax += f"""+sum(n$({self.name}_output[s,n] and dqCO2[s,n]), tauCO2[t,s,n]*qCO2[t,s,n])"""
		if abateCosts:
			self.abateCosts = abateCosts
			if abateCosts in ('SqrAdjCosts', 'SqrUtilCosts'):
				self._addCosts += """-sum(n$(dqCO2[s,n]), abateCosts[t,s,n]+adjCostEOP[t,s,n])"""
				self.db.aom(pd.Series(0, index= cpi([self.db('txE'), self.get('dqCO2')])), name = 'adjCostEOP', priority='first')
			else:
				self._addCosts += """-sum(n$(dqCO2[s,n]), abateCosts[t,s,n])"""
			self.db.aom(pd.Series(0, index= cpi([self.db('txE'), self.get('dqCO2')])), name = 'abateCosts', priority='first')

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
		if not self.partial:
			g = Group(f'{self.name}_alwaysExo', 
						v = [('sigma', self.g('kninp')), ('mu', self.g('map')), ('vA_tvc', self.g('sm')), # parameters
							 ('tauD', self.g('input')), ('tauS', self.g('output')), ('tauLump', self.g('sm')), # taxes
							 (f'{self.taxInstr}0', self._taxInstrCondition)],
					sub_v = [(self.taxInstr, self._taxInstrCondition)])
			if self.emissionReg:
				g.v += [('tauCO2', ('and', [self.g('output'), self.g('dqCO2')]))]
			return g
		else:
			self.partial = False
			g = self.group_alwaysExo
			g.v += [('qS', self.g('output')), ('p',self.g('input_n')), 'Rrate']
			g.sub_v += [('p',self.g('output_n'))]
			if self.emissionReg:
				g.v += [('qCO2', ('and', [self.g('output'), self.g('dqCO2')])), ('uCO2', ('and', [self.g('output'), self.g('dqCO2')])), ('tauEffCO2', ('and', [self.g('output'), self.g('dqCO2')]))]
			if self.abateCosts:
				g.v += [('abateCosts', self.g('dtauCO2'))]
				if self.abateCosts in ('SqrAdjCosts', 'SqrUtilCosts'):
					g.v += [('adjCostEOP', ('and', [self.g('txE'), self.g('dqCO2')]))]
			self.partial = True
			return g

	@property
	def group_alwaysEndo(self):
		return Group(f'{self.name}_alwaysEndo', v = [('pD', ('or', [self.g('int'), self.g('input')])),
													 ('pS', self.g('output')),
													 ('p', ('and', [self.g('output_n'), self.g('tx0')])),
													 ('qD', self.g('int')),
													 ('qD', ('and', [self.g('input'), self.g('tx0')])),
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


class DynamicNCES(StaticNCES):
	""" Version with durables, but no adjustment costs. """ 
	def initProperties(self, **kwargs):
		[self.addProperty(k,v) for k,v in ({'addMarginal': '', 'addCosts': '', 'addTax': '', 'emissionReg' : False, 'abateCosts': False, 'adjCosts': False} | kwargs).items()]

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
		super().initData()
		self.db.aom(pd.Series(0,  index = self.get('dur')), name = 'K_tvc', priority='first') # tvc condition for durables
		if self.adjCosts:
			self.db.aom(pd.Series(.1,  index = self.get('dur')), name = 'adjCostPar', priority = 'first') # parameter in investment cost function
			self.db.aom(pd.Series(0,  index = cpi([self.db('txE'), self.get('sm')]), name = 'adjCost'), priority='first') # adjustment costs

	def addAdjCosts(self):
		self.adjCosts = True
		self._addCosts += """-adjCost[t,s]"""

	@property
	def model_B(self):
		return super().model_B+OrdSet([f"B_{self.name}_adjCost"])
	@property
	def textBlocks(self):
		return super().textBlocks | {'capAcc': self.capAccBlocks}
	@property
	def capAccBlocks(self):
		return gamsProduction.capitalAccumulation(f'{self.name}_adjCost', self.name, adjCosts = self.adjCosts)

	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.v += [('rDepr', self.g('dur')),('K_tvc', self.g('dur')), ('qD', ('and', [self.g('dur'), self.g('t0')]))]
		if self.adjCosts:
			g.v += [('adjCostPar', self.g('dur'))]
		return g

	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		g.v += [('qD', ('and', [self.g('dur'), self.g('tx0')])), ('pD', ('and', [self.g('dur'), self.g('txE')]))]
		if self.adjCosts:
			g.v += [('adjCost', ('and', [self.g('sm'), self.g('txE')]))]
		return g

class IndexFund(GModel):
	def __init__(self, name, database, s_idxFund = 's_p',initFromGms = None, **kwargs):
		super().__init__(name = name, database = database, **kwargs)
		self.ns['s_idxFund'] = s_idxFund # the subset of sectors that are included in the "index fund"

	def initStuff(self):
		self.initData()
		self.initGroups()
	def initData(self):
		self.db.aom(pd.Series(0, index = self.db('t')), name = 'vIdxFund', priority='first')
	@property
	def group_endo(self):
		return Group(f'{self.name}_endo', v = ['vIdxFund'])
	def modelName(self, state = 'B'):
		return '_'.join(['M',self.name])
	@property
	def model_B(self):
		return OrdSet([f"B_{self.name}"])
	@property
	def textBlocks(self):
		return {'idxFund': self.equationText}
	@property
	def textInit(self):
		return "" if self.initFromGms is None else f"""vIdxFund.l[t] = sum(s$({gmsWrite.Syms.gpy(self.g('s_idxFund'))}), vA.l[t,s]);"""
	def fixText(self, **kwargs):
		return ""
	def unfixText(self, **kwargs):
		return self.groups[f'{self.name}_endo'].unfix(db = self.db)

	@property
	def equationText(self):
		return f"""
$BLOCK B_{self.name}
	E_{self.name}[t]$(txE[t])..	vIdxFund[t] =E= sum(s$({gmsWrite.Syms.gpy(self.g('s_idxFund'))}), vA[t,s]);
$ENDBLOCK
"""
