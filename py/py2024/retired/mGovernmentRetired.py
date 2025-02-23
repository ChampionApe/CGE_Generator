from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs
from pyDatabases import cartesianProductIndex as cpi, noneInit
from gmsPython import gmsWrite, Group, Model
import gamsGovernment

class BalancedBudget(Model):
	def __init__(self, tree, L = None, partial = False, **kwargs):
		super().__init__(name = tree.name, database = tree.db, **kwargs)
		self.readTree(tree)
		self.adjustForLaborSupply(L = L)
		self.partial = partial

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

	def adjustForLaborSupply(self, L = None):
		self.ns.update({k: f"{self.name}_{k}" for k in ('L','sm','output_n','input_n')})
		self.db[self.n('L')] = noneInit(L, pd.MultiIndex.from_tuples([], names = ['s','n']))
		self.db[self.n('input_n')]  = self.get('input').levels[-1]
		self.db[self.n('sm')] = self.get('output').levels[0]

	def initData(self):
		self.db.aom(pd.Series(1, index = cpi([self.db('txE'), self.get('output').union(self.get('int'))])), name = 'pD', priority='first')
		self.db.aom(adj.rc_pd(self.db('tauD'), self.get('input')), name = 'tauD0')
		self.db.aom(pd.Series(0, index = self.get('sm')), name ='taxRevPar')
		self.db.aom(pd.Series(0, index = self.get('sm')), name = 'jTerm')

	def models(self, **kwargs):
		return OrdSet([f"B_{name}" for name in self.m])+OrdSet([f"B_{self.name}_{k}" for k in ('bb','taxCalib')])

	def initGroups(self):
		self.groups = {g.name: g for g in (getattr(self, f'group_{k}') for k in ('alwaysExo','alwaysEndo','exoInCalib','endoInCalib'))}
		[grp() for grp in self.groups.values()]; # initialize groups
		metaGroups = ({g.name: g for g in (getattr(self, f'group_{k}') for k in ('endo_B','endo_C','exo_B','exo_C'))})
		[grp() for grp in metaGroups.values()]; # initialize metagroups
		self.groups.update(metaGroups)

	#### 4. WRITING METHODS
	@property
	def textBlocks(self):
		return self.nestingBlocks | {'bb': self.balancedBudget, 'taxCalib': self.taxCalib}
	@property
	def nestingBlocks(self):
		return {name: getattr(gamsGovernment, m.f)(name) for name, m in self.m.items()}
	@property
	def balancedBudget(self):
		return gamsGovernment.balancedBudget(f'{self.name}_bb', self.name)
	@property
	def taxCalib(self):
		return gamsGovernment.taxCalibration(f'{self.name}_taxCalib', self.name)

	def fixText(self, state ='B'):
		return self.groups[f'{self.name}_exo_{state}'].fix(db = self.db)
	def unfixText(self, state = 'B'):
		return self.groups[f'{self.name}_endo_{state}'].unfix(db = self.db)

	def solveText(self, state = 'B'):
		return f"""
# Fix exogenous variables in state {state}:
{self.fixText(state=state)}

# Unfix endogenous variables in state {state}:
{self.unfixText(state=state)}

solve M_{self.name} using CNS;
"""

	@property
	def text(self):
		return f"""
{gmsWrite.StdArgs.root()}
{gmsWrite.StdArgs.funcs()}
{gmsWrite.FromDB.declare(self.db)}
{gmsWrite.FromDB.load(self.db, gdx = self.db.name)}

{''.join(self.textBlocks.values())}
$Model M_{self.name} {','.join(self.models())};
""" 

	@property
	def group_endo_B(self):
		return Group(f'{self.name}_endo_B', g = [self.groups[f'{self.name}_{k}'] for k in ('alwaysEndo','exoInCalib')])
	@property
	def group_endo_C(self):
		return Group(f'{self.name}_endo_C', g = [self.groups[f'{self.name}_{k}'] for k in ('alwaysEndo', 'endoInCalib')])
	@property
	def group_exo_B(self):
		return Group(f'{self.name}_exo_B', g = [self.groups[f'{self.name}_{k}'] for k in ('alwaysExo','endoInCalib')])
	@property
	def group_exo_C(self):
		return Group(f'{self.name}_exo_C', g = [self.groups[f'{self.name}_{k}'] for k in ('alwaysExo','exoInCalib')])

	@property
	def group_alwaysExo(self):
		return Group(f'{self.name}_alwaysExo', v = [('sigma', self.g('kninp')),
													('mu', self.g('map')),
													('tauD0', self.g('input')),
													('qD', self.g('output'))],
												sub_v = [('mu', self.g('endoMu'))])
	@property
	def group_alwaysEndo(self):
		return Group(f'{self.name}_alwaysEndo', v = [('pD', ('or', [self.g('int'), self.g('input'), self.g('output')])),
													 ('qD', ('and', [self.g('input'), self.g('tx0E')])),
													 ('qD', self.g('int')),
													 ('tauD', self.g('input')),
													 ('TotalTax', ('and', [self.g('sm'), self.g('tx0E')])),
													 # ('tauS', ('and', [self.g('L'), self.g('tx0E')])), # use labor tax to balance budget
													 ('tauLump', ('and', [self.g('s_HH'), self.g('tx0E')]))] # use lump-sum tax on households to balance budget
													 )
	@property
	def group_exoInCalib(self):
		return Group(f'{self.name}_exoInCalib', v = [('TotalTax', ('and', [self.g('sm'), self.g('t0')])),
													 ('qD', ('and', [self.g('input'), self.g('t0')])),
													 ('tauLump', ('and', [self.g('s_HH'), self.g('t0')]))]
													 )
	@property
	def group_endoInCalib(self):
		return Group(f'{self.name}_endoInCalib', v = [('mu', self.g('endoMu')),
													  ('taxRevPar', self.g('sm')),
													  ('jTerm', self.g('sm'))])