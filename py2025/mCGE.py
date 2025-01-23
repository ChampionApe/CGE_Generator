from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs
from gmsPython import Group, GModel
import mProduction, mInvestment, mHousehold, mEmissions, mTrade, mGovernment, mInventory, mEquilibrium

class CGE(GModel):
	def __init__(self, name = None, database = None, solveWithNLP = False, **kwargs):
		super().__init__(name = name, database = database, **kwargs)
		self.solveWithNLP = solveWithNLP

	@property
	def groups(self):
		return {k:v for d in [m.groups for m in self.m.values()] for k,v in d.items()}

	def steadyStateDepr(self):
		s = adj.rc_pd(adj.rc_pd(self.db('qD'), self.db('inv_p')), alias = {'n':'nn'})
		return adjMultiIndex.applyMult(s, self.db('dur2inv')).droplevel('nn')/adj.rc_pd(self.db('qD'), self.db('dur_p'))-self.db('g_LR')

	### ADD MODULES
	def addStaticProdModule(self, tree, partial = False, mtype = 'StaticNCES', addEmissions = False, abateCosts = False, **kwargs):
		self.addModule(getattr(mProduction, mtype)(tree, partial = partial, **kwargs))
		m = self.m[tree.name]
		MergeDbs.merge(self.db, tree.db)
		m.db = self.db
		if addEmissions:
			m.addEmissions(abateCosts = abateCosts)
		m.initStuff(db = None, gdx = False)
		return m

	def addDynamicProdModule(self, tree, partial = False, mtype = 'DynamicNCES', addEmissions = False, abateCosts = False, addAdjCosts = False, **kwargs):
		self.addModule(getattr(mProduction, mtype)(tree, partial = partial, **kwargs))
		m = self.m[tree.name]
		MergeDbs.merge(self.db, tree.db)
		m.db = self.db
		if addEmissions:
			m.addEmissions(abateCosts = abateCosts)
		if addAdjCosts:
			m.addAdjCosts()
		m.initStuff(db = None, gdx = False)
		return m

	def addIndexFundModule(self, name, s_idxFund = 's_p', initFromGms = True, **kwargs):
		self.addModule(mProduction.IndexFund(name, self.db, s_idxFund = s_idxFund, initFromGms = initFromGms, **kwargs))
		m = self.m[name]
		m.initStuff()
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

	def solveStatement(self, **kwargs):
		if self.solveWithNLP:
			return f"""@SolveEmptyNLP({self.modelName(**kwargs)})"""
		else:
			return super().solveStatement(**kwargs)

class CGE_OPT(CGE):
	""" CGE model with potential for switching to optimizing welfare """
	def __init__(self, name = None, database = None, opt = True, **kwargs):
		super().__init__(name = name, database = database, **kwargs)
		self.opt = opt # if this is true and OptWelfare is a module --> switch solve statement and maximize welfare statement		

	def addOptWelfareModule(self, name, endogenousPol = None, **kwargs):
		self.addModule(OptWelfare(name, database = self.db, endogenousPol = endogenousPol, active = self.opt, **kwargs))
		self.m[name].initStuff(gdx = False)
		return self.m[name]

	def addSimulateEVModule(self, name, instrument = None, active = False, **kwargs):
		self.addModule(SimulateEV(name, database = self.db, instrument = instrument, active = active, **kwargs))
		self.m[name].initStuff(gdx = False)
		return self.m[name]

	def solveStatement(self, **kwargs):
		""" Add special solve method for when self.opt = True"""
		if any([isinstance(m, OptWelfare) for m in self.m.values()]) and self.opt:
			return f"""solve {self.modelName(**kwargs)} using NLP max OptWelObj"""
		else:
			return super().solveStatement(**kwargs)

class NCP_CGE(CGE_OPT):
	""" CGE model with different CO2 regulation schemes from NationalClimateProject (NCP)"""
	def __init__(self, name = None, database = None, opt = True, regulation = None, **kwargs):
		super().__init__(name = name, database = database, opt = opt, **kwargs)
		self.updateRegulation(regulation)

	def updateRegulation(self, regulation):
		self.regulation = regulation
		[setattr(m, 'regulation', regulation) for m in self.m.values() if isinstance(m, mEmissions.EOP_Simple)]
		if 'OPT' in noneInit(self.regulation,''):
			self.opt = True
			# [setattr(m, 'active', True) for m in self.m.values() if isinstance(m, OptWelfare)];

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
		""" Define models using the 'defineModel' method instead of working off of the self.models property. """
		return '\n'.join([self.defineModel(state = k) for k in ('B','C')])

class OptWelfare(GModel):
	""" Small class used to change objective and solve statement in CGE model """
	def __init__(self, name, database = None, endogenousPol = None, active = True, **kwargs):
		""" Maximizes weighted sum of welfare (vU) from households. """
		super().__init__(name = name, database = database, **kwargs)
		self.endogenousPol = endogenousPol # argument parsed to endogenous grouping
		self.active = active

	def initStuff(self, gdx = True):
		self.initData()
		self.initGroups()
		if gdx:
			self.db.mergeInternal()

	def initData(self):
		self.db.aom(0, name = 'OptWelObj', priority='first')
		self.db.aom(pd.Series(1, index = self.db('s_HH')), name = 'welWeights', priority='first')

	@property
	def equationText(self):
		return f"""
$BLOCK B_{self.name}
	E_{self.name}_obj..	OptWelObj =E= sum([t,s]$(t0[t] and s_HH[s]), welWeights[s]*vU[t,s]);
$ENDBLOCK
"""

	@property
	def group_alwaysEndo(self):
		return Group(f'{self.name}_endo', v = ['OptWelObj'])
	@property
	def group_endoWhenActive(self):
		return Group(f'{self.name}_endoWhenActive', v = noneInit(self.endogenousPol, []))
	@property
	def group_exo(self):
		return Group(f'{self.name}_exo',  v = [('welWeights', self.g('s_HH'))])
	def modelName(self, state = 'B'):
		return '_'.join(['M',self.name])
	@property
	def model_B(self):
		return OrdSet([f"B_{self.name}"])
	@property
	def textBlocks(self):
		return {'obj': self.equationText}
	def fixText(self, **kwargs):
		text = self.groups[f'{self.name}_exo'].fix(db = self.db)
		return text if self.active else text+self.groups[f'{self.name}_endoWhenActive'].fix(db=self.db)
	def unfixText(self, **kwargs):
		text = self.groups[f'{self.name}_endo'].unfix(db = self.db)
		return text if not self.active else text+self.groups[f'{self.name}_endoWhenActive'].unfix(db=self.db)

class SimulateEV(GModel):
	""" Only works alongside CGE with OptWelfare module that is not active """
	def __init__(self, name, database = None, instrument = None, active = True, **kwargs):
		""" Maximizes weighted sum of welfare (vU) from households. """
		super().__init__(name = name, database = database, **kwargs)
		self.instrument = noneInit(instrument, [('vA_F', self.g('s_HH'))]) # argument parsed to endogenous group. This is the one to use with RamseyIdxFund household class
		self.active = active

	def initStuff(self, gdx = True):
		self.initData()
		self.initGroups()
		if gdx:
			self.db.mergeInternal()

	def initData(self):
		self.db.aom(0, name = 'OptWelObj', priority='first')
		self.db.aom(0, name = 'OptWelObj0', priority='first')
		self.db.aom(0, name = 'DeltaWelfare', priority='first')

	@property
	def equationText(self):
		return f"""
$BLOCK B_{self.name}
	E_{self.name}_EV..	DeltaWelfare  =E= OptWelObj-OptWelObj0;
$ENDBLOCK
"""

	@property
	def group_endoWhenActive(self):
		return Group(f'{self.name}_endoWhenActive', v = self.instrument)
	@property
	def group_exoWhenActive(self):
		return Group(f'{self.name}_exoWhenActive', v = ['DeltaWelfare'])
	@property
	def group_exo(self):
		return Group(f'{self.name}_exo',  v = ['OptWelObj0'])
	def modelName(self, state = 'B'):
		return '_'.join(['M',self.name])
	@property
	def model_B(self):
		return OrdSet([f"B_{self.name}"])
	@property
	def textBlocks(self):
		return {'obj': self.equationText}
	def fixText(self, **kwargs):
		text = self.groups[f'{self.name}_exo'].fix(db = self.db)
		return text+self.groups[f'{self.name}_exoWhenActive'].fix(db=self.db) if self.active else text
	def unfixText(self, **kwargs):
		return self.groups[f'{self.name}_endoWhenActive'].unfix(db = self.db) if self.active else self.groups[f'{self.name}_exoWhenActive'].unfix(db=self.db)
