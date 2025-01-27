from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs
from pyDatabases import cartesianProductIndex as cpi
from gmsPython import Group, GModel
import GovernmentFiles.gamsGovernment as gamsGovernment

class GovNCES(GModel):
	def __init__(self, tree, partial = False, properties = None, **kwargs):
		super().__init__(name = tree.name, database = tree.db, **kwargs)
		self.readTree(tree)
		self.partial = partial
		self.initNames()
		GovNCES.initProperties(self, **noneInit(properties, {}))

	def initNames(self):
		self.ns.update({k: f"{self.name}_{k}" for k in ('sm','input_n')})
		self.db[self.n('input_n')]  = self.get('input').levels[-1]
		self.db[self.n('sm')] = self.get('output').levels[0]

	def readTree(self, tree):
		self.ns.update(tree.ns)
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
		self.db.aom(pd.Series(1, index = cpi([self.db('txE'), self.get('output').union(self.get('int'))])), name = 'pD', priority='first')
		self.db.aom(pd.Series(0, index = cpi([self.db('t'), self.get('sm')])), name = 'vA', priority='first')
		self.db.aom(pd.Series(0, index = self.get('sm')), name = 'jTerm', priority='first')
		self.db.aom(pd.Series(0,  index = self.get('sm')), name = 'taxRevPar')
		self.db.aom(self.get(self.taxInstr).copy(), name = f'{self.taxInstr}0')

	@staticmethod
	def initProperties(self, **kwargs):
		[self.addProperty(k,v) for k,v in ({'incInstr': 'jTerm', 'taxInstr': 'tauLump', 'addInc_tx0': '', 'addInc_t0': ''} | kwargs).items()]
		GovNCES.addIncInstr(self, incInstr = self.incInstr)

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

	@property
	def _taxInstrCondition(self):
		if self.taxInstr == 'tauLump':
			return ('and', [self.g('sm'), self.g('txE')])
		elif self.taxInstr == 'tauD':
			return ('and', [self.g('input'), self.g('txE')])

	# 2. Model specification:
	@property
	def model_B(self):
		return OrdSet([f"B_{name}" for name in self.m])+OrdSet([f"B_{self.name}_price"])
	@property
	def model_C(self):
		return self.model_B+OrdSet([f'B_{self.name}_taxCalib'])

	# Text blocks
	@property
	def textBlocks(self):
		return self.nestingBlocks | {'price': self.priceBlocks, 'taxCalib': self.taxCalibBlocks}
	@property
	def nestingBlocks(self):
		return {name: getattr(gamsGovernment, m.f)(name) for name, m in self.m.items()}
	@property
	def priceBlocks(self):
		return gamsGovernment.priceBlock(f'{self.name}_price', self.name, addInc_t0 = self.addInc_t0, addInc_tx0 = self.addInc_tx0)
	@property
	def taxCalibBlocks(self):
		return gamsGovernment.taxCalibBlock(f'{self.name}_taxCalib', self.name, self.g(self.taxInstr), self._taxInstrCondition)

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
		g = Group(f'{self.name}_alwaysExo',  v = [('sigma', self.g('kninp')),('mu', self.g('map')), ('tauD', self.g('input')), ('tauLump', self.g('sm')), (f'{self.taxInstr}0', self._taxInstrCondition), ('vA', self.g('sm'))],
												sub_v = [('mu', self.g('endoMu')),(self.taxInstr, self._taxInstrCondition)])
		if not self.partial:
			return g
		else:
			g.v += [('p', self.g('input_n')), 'Rrate']
			return g

	@property
	def group_alwaysEndo(self):
		return Group(f'{self.name}_alwaysEndo', v = [('pD', ('or',  [self.g('int'), self.g('input')])),
													 ('pD', ('and', [self.g('output'), self.g('tx0E')])),
													 ('qD', ('and', [self.g('input'), self.g('tx0E')])),
													 ('qD', self.g('output')), ('qD', self.g('int')),
													 ('TotalTax', ('and', [self.g('sm'), self.g('tx0E')]))])

	@property
	def group_exoInCalib(self):
		return Group(f'{self.name}_exoInCalib', v = [('qD', ('and', [self.g('input'), self.g('t0')])),
													 ('pD', ('and', [self.g('output'), self.g('t0')])),
													 ('TotalTax', ('and', [self.g('sm'), self.g('t0')]))])

	@property
	def group_endoInCalib(self):
		return Group(f'{self.name}_endoInCalib', v = [('mu', self.g('endoMu')), ('taxRevPar', self.g('sm')), (self.taxInstr, self._taxInstrCondition), self.incInstrTuple])

