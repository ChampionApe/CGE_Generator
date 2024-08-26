from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs
from gmsPython import GModel
import mProduction, mInvestment, mHousehold, mEmissions, mTrade, mGovernment, mInventory, mEquilibrium

class CGE(GModel):
	def __init__(self, name = None, database = None, **kwargs):
		super().__init__(name = name, database = database, **kwargs)

	@property
	def groups(self):
		return {k:v for d in [m.groups for m in self.m.values()] for k,v in d.items()}

	def steadyStateDepr(self):
		s = adj.rc_pd(adj.rc_pd(self.db('qD'), self.db('inv_p')), alias = {'n':'nn'})
		return adjMultiIndex.applyMult(s, self.db('dur2inv')).droplevel('nn')/adj.rc_pd(self.db('qD'), self.db('dur_p'))-self.db('g_LR')

	### ADD MODULES
	def addProductionModule(self, tree, partial = False, mtype = 'NestedCES',**kwargs):
		self.addModule(getattr(mProduction, mtype)(tree, partial = partial, **kwargs))
		m = self.m[tree.name]
		MergeDbs.merge(self.db, tree.db)
		m.db = self.db # point to main database when operating
		m.initStuff(db = None, gdx = False)
		return m

	def addInvestmentModule(self, tree, partial = False, mtype = 'NestedCES', **kwargs):
		self.addModule(getattr(mInvestment, mtype)(tree, partial = partial, **kwargs))
		m = self.m[tree.name]
		MergeDbs.merge(self.db, tree.db)
		m.db = self.db # point to main database when operating
		m.initStuff(db = None, gdx = False)
		return m

	def addConsumerModule(self, tree, L2C = None, partial = False, mtype = 'Ramsey', **kwargs):
		self.addModule(getattr(mHousehold, mtype)(tree, L2C = L2C, partial=partial,**kwargs))
		m = self.m[tree.name]
		MergeDbs.merge(self.db, tree.db)
		m.db = self.db
		m.initStuff(db = None, gdx = False)
		return m

	def addGovernmentModule(self, tree, L = None, partial = False, mtype = 'BalancedBudget', **kwargs):
		self.addModule(getattr(mGovernment, mtype)(tree, L = L, partial = partial, **kwargs))
		m = self.m[tree.name]
		MergeDbs.merge(self.db, tree.db)
		m.db = self.db
		m.initStuff(db = None, gdx = False)
		return m

	def addInventoryModule(self, name, itory = 'itory', mtype = 'AR', **kwargs):
		self.addModule(getattr(mInventory, mtype)(name, self.db, itory = itory, **kwargs))
		self.m[name].initStuff(db = None, gdx = False)
		return self.m[name]

	def addTradeModule(self, name, partial = False, dExport = None, mtype = 'Armington', **kwargs):
		self.addModule(getattr(mTrade, mtype)(name, self.db, partial = partial, dExport=dExport, **kwargs))
		self.m[name].initStuff(db = None, gdx = False)
		return self.m[name]

	def addEmissionsModule(self, name, partial = False, mtype = 'EOP_Simple', **kwargs):
		self.addModule(getattr(mEmissions, mtype)(name, database = self.db, partial = partial, **kwargs))
		self.m[name].initStuff(db = None, gdx = False)
		return self.m[name]

	def addEquilibriumModule(self, name, mtype = 'Equilibrium'):
		self.addModule(getattr(mEquilibrium, mtype)(name, database = self.db))
		self.m[name].initStuff(db = None, gdx = False)
		return self.m[name]

	### WRITING METHODS:
	def fixText(self, state = 'B'):
		return '\n'.join([m.fixText(state=state) for m in self.m.values()])
	def unfixText(self, state = 'B'):
		return '\n'.join([m.unfixText(state=state) for m in self.m.values()])

	@property
	def model_B(self):
		return OrdSet.union(*[m.getModel(state='B') for m in self.m.values()])
	@property
	def model_C(self):
		return OrdSet.union(*[m.getModel(state='C') for m in self.m.values()])

	@property
	def writeBlocks(self):
		return '\n'.join([''.join(m.textBlocks.values()) for m in self.m.values()])
	@property
	def writeInit(self):
		return '\n'.join([m.writeInit for m in self.m.values() if hasattr(m, 'writeInit')])
	@property
	def writeFuncs(self):
		return '\n'.join([m.writeFuncs for m in self.m.values() if hasattr(m, 'writeFuncs')])


class NCP_CGE(CGE):
	""" CGE model with different CO2 regulation schemes from NationalClimateProject (NCP)"""
	def __init__(self, name = None, database = None, regulation = None, **kwargs):
		super().__init__(name = name, database = database, **kwargs)
		self.regulation = regulation

	def modelName(self, state = 'B'):
		""" Add self.regulation to model name."""
		return '_'.join(['M',self.name,state]) if self.regulation is None else '_'.join(['M',self.name,state,self.regulation])

	def addEmissionsModule(self, name, partial = False, mtype = 'EmRegSimpleEOP', **kwargs):
		""" Specify that emissions module follows regulation specified in CGE. """
		self.addModule(getattr(mEmissions, mtype)(name, database = self.db, partial = partial, regulation = self.regulation,**kwargs))
		self.m[name].initStuff(db = None, gdx = False)
		return self.m[name]

	@property
	def writeModels(self):
		""" Define models using the 'defineModel' method instead of working off of the self._models property. """
		return '\n'.join([self.defineModel(state = k) for k in ('B','C')])

	def solveStatement(self, **kwargs):
		""" Add special solve method when the regulation type has 'OPT' in it. """
		if any([isinstance(m, mEmissions.EOP_Simple) for m in self.m.values()]) and 'OPT' in noneInit(self.regulation, ''):
			return f"""solve {self.modelName(**kwargs)} using NLP max obj;"""
		else:
			return super().solveStatement(**kwargs)
