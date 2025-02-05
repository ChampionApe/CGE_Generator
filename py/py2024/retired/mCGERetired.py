import os, pickle
from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs, GpyDB
from gmsPython import gmsWrite, Model
import mProduction
from mHousehold import Ramsey, StaticConsumer
from mGovernment import BalancedBudget
from mInventory import AR
from mTrade import Armington
import mEmissionsNew as mEmissions
from mEquilibrium import Equilibrium

class CGE(Model):
	def __init__(self, name = None, database = None, **kwargs):
		super().__init__(name = name, database = database, **kwargs)

	def modelName(self, state = 'B'):
		return '_'.join(['M',self.name,state])

	@property
	def groups(self):
		return {k:v for d in [m.groups for m in self.m.values()] for k,v in d.items()}

	def steadyStateDepr(self):
		s = adj.rc_pd(adj.rc_pd(self.db('qD'), self.db('inv_p')), alias = {'n':'nn'})
		return adjMultiIndex.applyMult(s, self.db('dur2inv')).droplevel('nn')/adj.rc_pd(self.db('qD'), self.db('dur_p'))-self.db('g_LR')
	### ADD MODULES

	def addProductionModule(self, tree, partial = False, mtype = 'NestedCES'):
		self.addModule(getattr(mProduction, mtype)(tree, partial = partial))
		# self.addModule(NestedCES(tree, partial = partial))
		m = self.m[tree.name]
		MergeDbs.merge(self.db, tree.db)
		m.db = self.db # point to main database when operating
		m.initStuff(db = None, gdx = False)
		return m

	def addRamseyModule(self, tree, L2C = None, partial = False, initFromGms = None):
		self.addModule(Ramsey(tree, L2C = L2C, partial = partial, initFromGms = initFromGms))
		m = self.m[tree.name]
		MergeDbs.merge(self.db, tree.db)
		m.db = self.db
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

	def addEmissionsModule(self, name, partial = False, mtype = 'EOP_Simple', **kwargs):
		self.addModule(getattr(mEmissions, mtype)(name, database = self.db, partial = partial, **kwargs))
		# self.addModule(EmissionEOP(name, database = self.db, partial = partial))
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
		jModelStr = self.j.jModel(self.modelName(state=state), self.groups.values(), db = self.db, solve = noneInit(solve, self.solveStatement(state = state))) # create string that declares adjusted $j$-terms
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
	@property
	def writeInit(self):
		return '\n'.join([m.initText for m in self.m.values() if hasattr(m, 'initText')])
	@property
	def writeFuncs(self):
		return '\n'.join([m.funcsText for m in self.m.values() if hasattr(m, 'funcsText')])
	def defineModel(self, state = 'B'):
		return f"""$Model {self.modelName(state = state)} {','.join(self.models(state=state))}"""
	def solveStatement(self, state = 'B'):
		return f"""solve {self.modelName(state = state)} using CNS;"""

	def solveText(self, state = 'B'):
		return f"""
# Fix exogenous variables in state {state}:
{self.fixText(state=state)}

# Unfix endogenous variables in state {state}:
{self.unfixText(state=state)}

# @SolveEmptyNLP({self.modelName(state = state)});
{self.solveStatement(state = state)}
"""

	@property
	def text(self):
		return f"""
{gmsWrite.StdArgs.root()}
{gmsWrite.StdArgs.funcs()}
# DEFINE LOCAL FUNCTIONS/MACROS:
{self.writeFuncs}

# DECLARE SYMBOLS FROM DATABASE:
{gmsWrite.FromDB.declare(self.db)}
# LOAD SYMBOLS FROM DATABASE:
{gmsWrite.FromDB.load(self.db, gdx = self.db.name)}
# WRITE INIT STATEMENTS FROM MODULES:
{self.writeInit}

# WRITE BLOCKS OF EQUATIONS:
{self.writeBlocks}

# DEFINE MODELS:
{self.defineModel(state = 'B')};
{self.defineModel(state = 'C')};
"""

class NCP_CGE(CGE):
	""" CGE model with different CO2 regulation schemes"""
	def __init__(self, name = None, database = None, regulation = None, **kwargs):
		super().__init__(name = name, database = database, **kwargs)
		self.regulation = regulation

	def modelName(self, state = 'B', regulation = None):
		return '_'.join(['M',self.name,state] if noneInit(regulation, self.regulation) is None else ['M',self.name,state, noneInit(regulation, self.regulation)])

	def models(self, state = 'B', regulation = None):
		return OrdSet.union(*[m.models(state=state, regulation = noneInit(regulation, self.regulation)) for m in self.m.values()])

	def addEmissionsModule(self, name, partial = False, mtype = 'EmRegSimpleEOP', **kwargs):
		self.addModule(getattr(mEmissions, mtype)(name, database = self.db, partial = partial, regulation = self.regulation,**kwargs))
		self.m[name].initStuff(db = None, gdx = False)
		return self.m[name]

	def solveStatement(self, state = 'B'):
		if (any([isinstance(m, mEmissions.EOP_Simple) for m in self.m.values()]) and 'OPT' in noneInit(self.regulation,'')):
			return f"""solve {self.modelName(state = state, regulation = self.regulation)} using NLP max obj;"""
		else:
			return f"""solve {self.modelName(state = state, regulation = self.regulation)} using CNS;"""
