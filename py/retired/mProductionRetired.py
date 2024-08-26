from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs, GpyDB
from pyDatabases import cartesianProductIndex as cpi
from gmsPython import gmsWrite, Group, Model
import gamsProduction

class NestedCES(Model):
	def __init__(self, tree, partial = False, **kwargs):
		super().__init__(name = tree.name, database = tree.db, **kwargs)
		self.readTree(tree)
		self.partial = partial # use module in partial or general equilibrium; this affects compilation of groups 

	#### 1. INITIALIZE METHODS 
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

	def uniqueFromMap(self,map_,gb=('s','n')):
		""" MultiIndex-like groupby statement with function 'first' """
		return pd.MultiIndex.from_frame(map_.to_frame(index=False).groupby([s for s in gb]).first().reset_index()).reorder_levels(map_.names)

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
		# self.db.aom(pd.Series(.5, index = cpi([self.db('txE'), self.get('int')])), name = 'qD', priority = 'first') # quantities of intermediate goods
		self.db.aom(pd.Series(1,  index = self.get('dur')), name = 'adjCostPar', priority = 'first') # parameter in investment cost function
		self.db.aom(pd.Series(0,  index = self.get('dur')), name = 'K_tvc', priority='first') # tvc condition for durables
		self.db.aom(pd.Series(0,  index = cpi([self.db('txE'), self.get('sm')]), name = 'adjCost'), priority='first') # adjustment costs
		self.db.aom(pd.Series(.1, index = self.get('sm')), name = 'markup', priority='first') #
		self.db.aom(pd.Series(0,  index = self.get('sm')), name = 'taxRevPar')

	#### 2. GROUPINGS AND MODEL SPECIFICATIONS: 
	def models(self, state = 'B', **kwargs):
		if state == 'B':
			return OrdSet([f"B_{name}" for name in self.m])+OrdSet([f"B_{self.name}_{k}" for k in ('adjCost','pWedge')])
		elif state == 'C':
			return self.models(state = 'B')+OrdSet([f'B_{self.name}_taxCalib'])

	def initGroups(self):
		self.groups = {g.name: g for g in (getattr(self, f'group_{k}') for k in ('alwaysExo','alwaysEndo','exoInCalib','endoInCalib'))}
		[grp() for grp in self.groups.values()]; # initialize groups
		metaGroups = {g.name: g for g in (getattr(self, f'group_{k}') for k in ('endo_B','endo_C','exo_B','exo_C'))}
		[grp() for grp in metaGroups.values()]; # initialize metagroups
		self.groups.update(metaGroups)

	#### 3. SOlUTION METHODS
	def jSolve(self, n, state = 'B', loopName = 'i', ϕ = 1):
		""" Solve model from scratch using the jTerms approach."""
		mainText = self.compiler(self.text, has_read_file = False)
		jModelStr = self.j.jModel(f'M_{self.name}_{state}', self.groups.values(), db = self.db) # create string that declares adjusted $j$-terms
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
		return self.nestingBlocks | {'adjCost': self.adjCostBlocks, 'pWedge': self.priceWedgeBlocks, 'taxCalib': self.taxCalibBlocks}
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
	def taxCalibBlocks(self):
		return gamsProduction.taxCalibration(f'{self.name}_taxCalib', self.name)

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

solve M_{self.name}_{state} using CNS;
"""

	@property
	def text(self):
		return f"""
{gmsWrite.StdArgs.root()}
{gmsWrite.StdArgs.funcs()}
{gmsWrite.FromDB.declare(self.db)}
{gmsWrite.FromDB.load(self.db, gdx = self.db.name)}

{''.join(self.textBlocks.values())}
$Model M_{self.name}_B {','.join(self.models(state='B'))};
$Model M_{self.name}_C {','.join(self.models(state='C'))};
""" 

	### AUX: SPECIFICATION OF INDIVIDUAL AND METAGROUPS
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
											('tauNonEnv0', self.g('output')),
											('tauD', self.g('input')),
											('tauLump', self.g('sm')),
											('tauCO2', ('and', [self.g('output'), self.g('dqCO2')])),
											('rDepr', self.g('dur')),
											('adjCostPar', self.g('dur')),
											('K_tvc', self.g('dur')),
											('qD', ('and', [self.g('dur'), self.g('t0')]))],
										sub_v = [('mu', self.g('endoMu'))])
		else:
			self.partial = False
			g = self.group_alwaysExo
			g.v += [('qS', self.g('output')), ('p', self.g('input_n')), ('qCO2', ('and', [self.g('output'), self.g('dqCO2')])), ('Rrate', None)]
			g.sub_v += [('p', self.g('output_n'))]
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
													 ('tauS', self.g('output')),
													 ('TotalTax', ('and', [self.g('sm'), self.g('tx0E')]))])

	@property
	def group_exoInCalib(self):
		return Group(f'{self.name}_exoInCalib', v = [('qD', ('and', [self.g('input'), self.g('t0')])),
													 ('p',  ('and', [self.g('output_n'), self.g('t0')])),
													 ('TotalTax', ('and', [self.g('sm'), self.g('t0')]))])

	@property
	def group_endoInCalib(self):
		return Group(f'{self.name}_endoInCalib', v = [('mu', self.g('endoMu')),
													  ('tauNonEnv', self.g('output')),
													  ('taxRevPar', self.g('sm')),
													  ('markup', self.g('sm'))])


