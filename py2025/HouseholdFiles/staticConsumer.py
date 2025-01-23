from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs
from pyDatabases import cartesianProductIndex as cpi
from gmsPython import Group, GModel
import HouseholdFiles.gamsHouseholds as gamsHouseholds

class StaticNCES(GModel):
	def __init__(self, tree, L2C = None, partial = False, initFromGms = None, properties = None, **kwargs):
		super().__init__(name = tree.name, database = tree.db, **kwargs)
		self.readTree(tree)
		self.initFromGms = initFromGms
		self.partial = partial
		self.addL2C(L2C =L2C)
		self.initProperties(self, **noneInit(properties, {}))

	def readTree(self, tree):
		self.ns.update(tree.ns)
		[self.readTree_i(t) for t in tree.trees.values()];
		self.calibrationSubsets(tree)

	def addL2C(self, L2C = None):
		self.ns.update({k: f"{self.name}_{k}" for k in ('L','C','L2C','sm','output_n','input_n')})
		self.db[self.n('L2C')] = L2C
		self.db[self.n('L')] = self.get('L2C').droplevel('nn').unique()
		self.db[self.n('C')] = self.get('L2C').droplevel('n').unique().rename(['s','n'])
		self.db[self.n('output_n')] = self.get('L').levels[-1]
		self.db[self.n('input_n')]  = self.get('input').levels[-1]
		self.db[self.n('sm')] = self.get('output').levels[0]
		self.db['n'] = self.get('n').union(self.get('output_n'))

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
		self.db.aom(pd.Series(1, index = cpi([self.db('txE'), self.get('L')])), name = 'pS', priority = 'first')
		self.db.aom(pd.Series(1, index = cpi([self.db('txE'), self.get('output').union(self.get('int'))])), name = 'pD', priority='first')
		self.db.aom(pd.Series(2, index = self.get('sm')), name = 'crra', priority='second')
		self.db.aom(pd.Series(1, index = cpi([self.db('txE'), self.get('sm')])), name = 'vU', priority = 'first')
		self.db.aom(pd.Series(0,  index = self.get('sm')), name = 'vU_tvc', priority='first')
		self.db.aom(pd.Series(0, index = cpi([self.db('t'), self.get('sm')])), name = 'vA', priority='first')
		self.db.aom(pd.Series((1+self.get('g_LR'))**(self.get('crra'))/self.db('R_LR'), index = self.get('sm')), name = 'discF', priority='first')
		self.db.aom(pd.Series(0, index = self.get('sm')), name = 'jTerm', priority='first')
		self.db.aom(pd.Series(0,  index = self.get('sm')), name = 'taxRevPar')
		self.db.aom((1+self.get('g_LR'))**(1-self.get('crra'))-1, name = 'gadj', priority = 'first')
		self.db.aom(self.get(self.taxInstr).copy(), name = f'{self.taxInstr}0')

	@staticmethod
	def initProperties(self, **kwargs):
		[self.addProperty(k,v) for k,v in ({'incInstr': 'jTerm', 'taxInstr': 'tauLump', 'addInc_tx0': '', 'addInc_t0': ''} | kwargs).items()]
		self.addIncInstr(self, incInstr = self.incInstr)

	@staticmethod
	def addIncInstr(self, incInstr = 'jTerm'):
		if incInstr == 'jTerm':
			self.addInc_tx0 = "+jTerm[s]"
			self.addInc_t0  = "+jTerm[s]"
			self.addProperty('incInstrTuple', ('jTerm', self.g('sm')))
		if incInstr == 'jTerm0':
			self.addInc_tx0 = ""
			self.addInc_t0  = "+jTerm[s]"
			self.addProperty('incInstrTuple', ('jTerm', self.g('sm')))
		elif incInstr == 'vA0':
			self.addInc_tx0 = ''
			self.addInc_t0  = ''
			self.addProperty('incInstrTuple', ('vA', ('and', [self.g('t0'), self.g('sm')])))

	# 2. Model specification:
	@property
	def model_B(self):
		return OrdSet([f"B_{name}" for name in self.m])+OrdSet([f"B_{self.name}_{k}" for k in ('price','vU')])
	@property
	def model_C(self):
		return self.model_B+OrdSet([f'B_{self.name}_taxCalib'])

	# Text blocks
	@property
	def textBlocks(self):
		return self.nestingBlocks | {'price': self.priceBlocks, 'vU': self.CRRA_vU, 'taxCalib': self.taxCalibBlocks}
	@property
	def nestingBlocks(self):
		return {name: getattr(gamsHouseholds, m.f)(name) for name, m in self.m.items()}
	@property
	def priceBlocks(self):
		return gamsHouseholds.priceBlock(f'{self.name}_price', self.name, addInc_t0 = self.addInc_t0, addInc_tx0 = self.addInc_tx0)
	@property
	def CRRA_vU(self):
		return gamsHouseholds.CRRA_vU(f'{self.name}_vU', self.name)
	@property
	def taxCalibBlocks(self):
		return gamsHouseholds.taxCalibBlock(f'{self.name}_taxCalib', self.name, self.g(self.taxInstr), self._taxInstrCondition)

	@property
	def _taxInstrCondition(self):
		if self.taxInstr == 'tauLump':
			return ('and', [self.g('sm'), self.g('txE')])
		elif self.taxInstr == 'tauD':
			return ('and', [self.g('input'), self.g('txE')])
		elif self.taxInstr == 'tauS':
			return ('and', [self.g('L'), self.g('txE')])

	@property
	def textInit(self):
		return "" if self.initFromGms is None else getattr(gamsHouseholds, f'{self.initFromGms}')(self.name)

	# Groups:
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
		g = Group(f'{self.name}_alwaysExo',  v = [('sigma', self.g('kninp')),('mu', self.g('map')), ('crra', self.g('sm')), ('discF', self.g('sm')), ('vU_tvc', self.g('sm')), ('gadj', self.g('sm')),
														 ('tauD', self.g('input')),('tauS', self.g('L')),('tauLump', self.g('sm')), (f'{self.taxInstr}0', self._taxInstrCondition),
														 ('vA', self.g('sm')), ('qS', ('and', [self.g('L'), self.g('txE')]))],
												sub_v = [('mu', self.g('endoMu')),(self.taxInstr, self._taxInstrCondition)])
		if not self.partial:
			return g
		else:
			g.v += [('p', ('or', [self.g('output_n'), self.g('input_n')])), 'Rrate']
			return g

	@property
	def group_alwaysEndo(self):
		return Group(f'{self.name}_alwaysEndo', v = [('pD', ('or',  [self.g('int'), self.g('input')])),
													 ('pD', ('and', [self.g('C'), self.g('tx0E')])),
													 ('qD', ('and', [self.g('input'), self.g('tx0E')])),
													 ('qD', ('or',  [self.g('int'), self.g('output')])),
													 ('pS', ('and', [self.g('L'), self.g('txE')])), 
													 ('vU', self.g('sm')),
													 ('TotalTax', ('and', [self.g('sm'), self.g('tx0E')]))])

	@property
	def group_exoInCalib(self):
		return Group(f'{self.name}_exoInCalib', v = [('qD', ('and', [self.g('input'), self.g('t0')])),
													 ('pD', ('and', [self.g('C'), self.g('t0')])),
													 ('TotalTax', ('and', [self.g('sm'), self.g('t0')]))])

	@property
	def group_endoInCalib(self):
		return Group(f'{self.name}_endoInCalib', v = [('mu', self.g('endoMu')), ('taxRevPar', self.g('sm')), (self.taxInstr, self._taxInstrCondition), self.incInstrTuple])


class StaticGHH(StaticNCES):

	def initData(self):
		super().initData()
		self.db.aom(pd.Series(1, index = self.get('sm')), name = 'Lscale', priority='first')
		self.db.aom(pd.Series(.25, index = self.get('sm')), name = 'frisch', priority = 'first')
		self.db.aom(pd.Series(1, index = cpi([self.db('txE'), self.get('sm')])), name = 'qC', priority = 'first')

	@property
	def CRRA_vU(self):
		return gamsHouseholds.CRRA_GHH_vU(f'{self.name}_vU', self.name)

	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.v += [('frisch', self.g('sm'))]
		g.sub_v += [('qS', ('and', [self.g('L'), self.g('txE')]))]
		return g

	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		g.v += [('qS', ('and', [self.g('L'), self.g('tx0E')])), ('qC', ('and', [self.g('sm'), self.g('txE')]))]
		return g

	@property
	def group_exoInCalib(self):
		g = super().group_exoInCalib
		g.v += [('qS', ('and', [self.g('L'), self.g('t0')]))]
		return g

	@property
	def group_endoInCalib(self):
		g = super().group_endoInCalib
		g.v += [('Lscale', self.g('sm'))]
		return g

