from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs, GpyDB
from pyDatabases import cartesianProductIndex as cpi, noneInit
from gmsPython import gmsWrite, Group, Model
import gamsHouseholds

class StaticConsumer(Model):
	def __init__(self, tree, L2C = None, partial = False, **kwargs):
		super().__init__(name = tree.name, database = tree.db, **kwargs)
		self.readTree(tree)
		self.adjustForLaborSupply(L2C = L2C)
		self.partial = partial

	#### 1. INITIALIZE METHODS 
	def adjustForLaborSupply(self, L2C = None):
		""" add mapping from labor component L to top of consumption nest C. """
		self.ns.update({k: f"{self.name}_{k}" for k in ('L','L2C','sm','output_n','input_n')})
		self.db[self.n('L2C')] = noneInit(L2C, pd.MultiIndex.from_tuples([], names = ['s','n','nn']))
		self.db[self.n('L')] = self.get('L2C').droplevel('nn').unique()
		self.db[self.n('output_n')] = self.get('L').levels[-1]
		self.db[self.n('input_n')]  = self.get('input').levels[-1]
		self.db[self.n('sm')] = self.get('output').levels[0]
		self.db['n'] = self.get('n').union(self.get('output_n'))

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
		self.db.aom(pd.Series(1, index = cpi([self.db('txE'), self.get('L')])), name = 'pS', priority = 'first')
		self.db.aom(pd.Series(1, index = cpi([self.db('txE'), self.get('output').union(self.get('int'))])), name = 'pD', priority='first')
		self.db.aom(pd.Series(1, index = self.get('output')), name = 'crra', priority='second')
		self.db.aom(pd.Series(1, index = self.get('L')), name = 'Lscale', priority='first')
		self.db.aom(pd.Series(0, index = self.get('sm')), name = 'jTerm', priority='first')

	#### 2. GROUPINGS AND MODEL SPECIFICATIONS: 
	def models(self, **kwargs):
		return OrdSet([f"B_{name}" for name in self.m])+OrdSet([f"B_{self.name}_{k}" for k in ('isoFrisch','pWedge')])

	def initGroups(self):
		self.groups = {g.name: g for g in (getattr(self, f'group_{k}') for k in ('alwaysExo','alwaysEndo','exoInCalib','endoInCalib'))}
		[grp() for grp in self.groups.values()]; # initialize groups
		metaGroups = ({g.name: g for g in (getattr(self, f'group_{k}') for k in ('endo_B','endo_C','exo_B','exo_C'))})
		[grp() for grp in metaGroups.values()]; # initialize metagroups
		self.groups.update(metaGroups)

	#### 3. SOlUTION METHODS
	def jSolve(self, n, state = 'B', loopName = 'i', ϕ = 1):
		""" Solve model from scratch using the jTerms approach."""
		mainText = self.compiler(self.text, has_read_file = False)
		jModelStr = self.j.jModel(f'M_{self.name}', self.groups.values(), db = self.db) # create string that declares adjusted $j$-terms
		fixUnfix  = self.j.jFixUnfix([self.groups[f'{self.name}_endo_{state}']], db = self.db) + self.j.solve
		loopSolve = self.j.jLoop(n, loopName = loopName, ϕ = ϕ)
		self.job = self.ws.add_job_from_string(mainText+jModelStr+fixUnfix+loopSolve)
		self.job.run(databases = self.db.database)
		return GpyDB(self.job.out_db, ws = self.ws)

	def solve(self, text = None, state = 'B'):
		self.job = self.ws.add_job_from_string(noneInit(text, self.write(state = state)))
		self.job.run(databases = self.db.database)
		self.out_db = GpyDB(self.job.out_db, ws = self.ws)
		return self.out_db	

	def write_gamY(self, state = 'B'):
		""" Write code for solving the model from "scratch" """
		return self.text+self.solveText(state = state)

	def write(self, state = 'B'):
		return self.compiler(self.write_gamY(state = state), has_read_file = False)

	#### 4. WRITING METHODS
	@property
	def textBlocks(self):
		return self.nestingBlocks | {'isoFrisch': self.isoFrisch, 'pWedge': self.priceWedgeBlocks}
	@property
	def nestingBlocks(self):
		return {name: getattr(gamsHouseholds, m.f)(name) for name, m in self.m.items()}
	@property
	def isoFrisch(self):
		return gamsHouseholds.isoFrisch(f'{self.name}_isoFrisch', self.name)
	@property
	def priceWedgeBlocks(self):
		return gamsHouseholds.priceWedgeStatic(f'{self.name}_pWedge', self.name)

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
		if not self.partial:
			return Group(f'{self.name}_alwaysExo', v = [('sigma', self.g('kninp')),
													('mu', self.g('map')),
													('frisch', self.g('L')),
													('crra', self.g('output')),
													('tauD', self.g('input')),
													('tauS', self.g('L')),
													('tauLump', ('and', [self.g('sm'), self.g('tx0E')]))],
											sub_v = [('mu', self.g('endoMu'))])
		else:
			self.partial = False
			g = self.group_alwaysExo
			g.v += [('p', ('or', [self.g('output_n'), self.g('input_n')]))]
			self.partial = True
			return g
	@property
	def group_alwaysEndo(self):
		return Group(f'{self.name}_alwaysEndo', v = [('pD', ('or',  [self.g('int'), self.g('input')])),
													 ('pD', ('and', [self.g('output'), self.g('tx0E')])),
													 ('qS', ('and', [self.g('L'), self.g('tx0E')])),
													 ('qD', ('and', [self.g('input'), self.g('tx0E')])),
													 ('qD', ('or',  [self.g('int'), self.g('output')])),
													 ('pS', self.g('L')),
													 ('TotalTax', ('and', [self.g('sm'), self.g('tx0E')]))])
	@property
	def group_exoInCalib(self):
		return Group(f'{self.name}_exoInCalib', v = [('qD', ('and', [self.g('input'), self.g('t0')])),
													 ('qS', ('and', [self.g('L'), self.g('t0')])),
													 ('pD', ('and', [self.g('output'), self.g('t0')])),
													 ('TotalTax', ('and', [self.g('sm'), self.g('t0')]))])
	@property
	def group_endoInCalib(self):
		return Group(f'{self.name}_endoInCalib', v = [('mu', self.g('endoMu')),
													  ('Lscale', self.g('L')),
													  ('tauLump', ('and', [self.g('sm'), self.g('t0')])),
													  ('jTerm', self.g('sm'))])

