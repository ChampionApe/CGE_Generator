import os, pickle
from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs, GpyDB
from gmsPython import gmsWrite, Model
from mProduction import NestedCES
from mHousehold import StaticConsumer
from mGovernment import BalancedBudget
from mInventory import AR
from mTrade import Armington
from mEmissions import EmissionEOP
from mEquilibrium import Equilibrium

class CGE(Model):
	def __init__(self, name = None, database = None, **kwargs):
		super().__init__(name = name, database = database, **kwargs)

	@property
	def groups(self):
		return {k:v for d in [m.groups for m in self.m.values()] for k,v in d.items()}

	def steadyStateDepr(self):
		s = adj.rc_pd(adj.rc_pd(self.db('qD'), self.db('inv_p')), alias = {'n':'nn'})
		return adjMultiIndex.applyMult(s, self.db('dur2inv')).droplevel('nn')/adj.rc_pd(self.db('qD'), self.db('dur_p'))-self.db('g_LR')
	### ADD MODULES

	def addProductionModule(self, tree, partial = False):
		self.addModule(NestedCES(tree, partial = partial))
		m = self.m[tree.name]
		MergeDbs.merge(self.db, tree.db)
		m.db = self.db # point to main database when operating
		m.initStuff(db = None, gdx = False)
		return m

	def addConsumerModule(self, tree, L2C = None, partial = False):
		self.addModule(StaticConsumer(tree, L2C = L2C, partial = partial))
		m = self.m[tree.name]
		MergeDbs.merge(self.db, tree.db)
		m.db = self.db
		m.initStuff(db = None, gdx = False)
		return m

	def addGovernmentModule(self, tree, L = None, partial = False):
		self.addModule(BalancedBudget(tree, L = L), partial = partial)
		m = self.m[tree.name]
		MergeDbs.merge(self.db, tree.db)
		m.db = self.db
		m.initStuff(db = None, gdx = False)
		return m

	def addInventoryModule(self, name, itory = 'itory'):
		self.addModule(AR(name, self.db, itory = itory))
		self.m[name].initStuff(db = None, gdx = False)
		return self.m[name]

	def addTradeModule(self, name, partial = False, dExport = None):
		self.addModule(Armington(name, self.db, partial = partial, dExport=dExport))
		self.m[name].initStuff(db = None, gdx = False)
		return self.m[name]

	def addEmissionsModule(self, name, partial = False):
		self.addModule(EmissionEOP(name, database = self.db, partial = partial))
		self.m[name].initStuff(db = None, gdx = False)
		return self.m[name]

	def addEquilibriumModule(self, name):
		self.addModule(Equilibrium(name, database = self.db))
		self.m[name].initStuff(db = None, gdx = False)
		return self.m[name]

	### SOLUTION METHODS:
	def jSolve(self, n, state = 'B', loopName = 'i', ϕ = 1, solve = None):
		""" Solve model from scratch using the jTerms approach."""
		mainText = self.compiler(self.text, has_read_file = False)
		jModelStr = self.j.jModel(f'M_{self.name}_{state}', self.groups.values(), db = self.db, solve = solve) # create string that declares adjusted $j$-terms
		fixUnfix = self.j.group.fix()+self.unfixText(state=state)+self.j.solve
		loopSolve = self.j.jLoop(n, loopName = loopName, ϕ = ϕ)
		self.job = self.ws.add_job_from_string(mainText+jModelStr+fixUnfix+loopSolve)
		self.job.run(databases = self.db.database)
		return GpyDB(self.job.out_db, ws = self.ws)

	def solve(self, text = None, state = 'B'):
		self.job = self.ws.add_job_from_string(noneInit(text, self.write(state = state)))
		self.job.run(databases = self.db.database)
		self.out_db = GpyDB(self.job.out_db, ws = self.ws)
		return self.out_db	

	def write(self, state = 'B'):
		return self.compiler(self.write_gamY(state = state), has_read_file = False)

	def write_gamY(self, state = 'B'):
		""" Write code for solving the model from "scratch" """
		return self.text+self.solveText(state = state)

	### WRITING METHODS:
	def fixText(self, state = 'B'):
		return '\n'.join([m.fixText(state=state) for m in self.m.values()])

	def unfixText(self, state = 'B'):
		return '\n'.join([m.unfixText(state=state) for m in self.m.values()])

	def models(self, state = 'B'):
		return OrdSet.union(*[m.models(state=state) for m in self.m.values()])

	@property
	def writeBlocks(self):
		return '\n'.join([''.join(m.textBlocks.values()) for m in self.m.values()])

	def solveText(self, state = 'B'):
		return f"""
# Fix exogenous variables in state {state}:
{self.fixText(state=state)}

# Unfix endogenous variables in state {state}:
{self.unfixText(state=state)}

# @SolveEmptyNLP(M_{self.name}_{state});

solve M_{self.name}_{state} using CNS;
"""

	@property
	def text(self):
		return f"""
{gmsWrite.StdArgs.root()}
{gmsWrite.StdArgs.funcs()}
# DECLARE SYMBOLS FROM DATABASE:
{gmsWrite.FromDB.declare(self.db)}
# LOAD SYMBOLS FROM DATABASE:
{gmsWrite.FromDB.load(self.db, gdx = self.db.name)}

# WRITE BLOCKS OF EQUATIONS:
{self.writeBlocks}

# DEFINE MODELS:
$Model M_{self.name}_B {','.join(self.models(state='B'))};
$Model M_{self.name}_C {','.join(self.models(state='C'))};
""" 