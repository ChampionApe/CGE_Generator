from CGEFiles.basicCGE import *

class NCP_CGE(CGE_welfare):
	# Standard load methods:
	def steadyStateDepr(self):
		s = adj.rc_pd(adj.rc_pd(self.db('qD'), self.db('inv_p')), alias = {'n':'nn'})
		return adjMultiIndex.applyMult(s, self.db('dur2inv')).droplevel('nn')/adj.rc_pd(self.db('qD'), self.db('dur_p'))-self.db('g_LR')

	def stdProduction(self, tree, cl = 'DynamicNCES', extension = 'emission', abateCosts = 'SqrAdjCosts', taxInstr = 'tauLump', partial = True, initFromGms = 'initFirmValueBlock', adjCosts = True, **kwargs):
		return self.addProduction(cl, tree, extension = extension, abateCosts = abateCosts, taxInstr = taxInstr, partial = partial, initFromGms = initFromGms, adjCosts = adjCosts, **kwargs)

	def stdInvestment(self, tree, cl = 'StaticNCES', taxInstr = 'tauD', partial = True, initFromGms = 'initFirmValueBlock', **kwargs):
		return self.addProduction(cl, tree, taxInstr = taxInstr, partial = partial, initFromGms = initFromGms, **kwargs)

	def stdHousehold(self, tree, L2C, cl = 'RamseyGHHIdxFund', taxInstr = 'tauS', incInstr = 'jTerm', partial = True, initFromGms = 'init_GHH_vU', **kwargs):
		return self.addHousehold(cl, tree, L2C = L2C, properties = {'taxInstr': taxInstr, 'incInstr': incInstr}, partial = partial, initFromGms = initFromGms, **kwargs)

	def stdGovernment(self, tree, cl = 'SimplePolicy_tx0', taxInstr = 'tauLump', incInstr = 'vA0', partial = True, **kwargs):
		return self.addGovernment(cl, tree, partial = partial, properties = {'taxInstr': taxInstr, 'incInstr': incInstr}, polInstr = 'tauLump', polCond = self.g('s_HH'), **kwargs)

	def stdTrade(self, name, cl = 'Armington', **kwargs):
		return self.addTrade(cl, name, self.db, **kwargs)

	def stdIndexFund(self, name, cl = 'IndexFund', sIdxFund = None, initFromGms = True, **kwargs):
		self.db['sIdxFund'] = noneInit(sIdxFund, self.db('s_p').union(self.db('s_i')))
		self.addModule(getattr(mOther, cl)(name, self.db, 'sIdxFund', initFromGms = initFromGms, **kwargs))
		self.m[name].initStuff(gdx = False)
		return self.m[name]

	def stdInventory(self, name, cl = 'InventoryAR', sInventory = None, **kwargs):
		self.db['sInventory'] = noneInit(sInventory, pd.Index(['itory'], name = 's'))
		self.addModule(getattr(mOther, cl)(name, self.db, 'sInventory',**kwargs))
		self.m[name].initStuff(gdx = False)
		return self.m[name]

	def stdEmissions(self, name, cl = 'AbateCapital', partial = False, initFromGms = True, techType = "'logNorm'", **kwargs):
		self.addModule(getattr(mEmissions, cl)(name, database = self.db, partial = partial, initFromGms = initFromGms, techType = techType, **kwargs))
		self.compiler.locals['techType'] = self.m[name].techType
		self.m[name].initStuff(db = None, gdx = True)
		return self.m[name]

	def stdEmissionTargets(self, name, cl = 'EmissionTargets', regulation = 'SYT_EXO', **kwargs):
		self.addModule(getattr(mEmissions, cl)(name, self, regulation = regulation, **kwargs)) 
		self.regModule = self.m[name] # specify which specific modules has emission regulation
		self.m[name].initStuff(gdx = False)
		return self.m[name]

	def stdEquilibrium(self, name, cl = 'SmallOpenEq', **Kwargs):
		return self.addEquilibriumModule(cl, name)

	def stdWelfare(self, name, cl = 'HouseholdWelfare', policy = None, active = True, **kwargs):
		self.welModule = self.addWelfareModule(cl, name, policy = policy, active = active, **kwargs) # specify which specific modules has the welfare module
		return self.welModule

	# Adjusted methods with welfare and emission regulation:
	def modelName(self, state = 'B'):
		""" Add self.regulation to model name."""
		return '_'.join(['M',self.name,state]) if self.regulation is None else '_'.join(['M',self.name,state,self.regulation])

	def updateRegulation(self, regulation):
		""" Note: If 'opt' is not in regulation type, we still may not adjust self.opt. This is because the module may be on for other reasons."""
		self.regulation = regulation
		self.regModule.initGroups()
		if 'OPT' in noneInit(self.regulation,''):
			self.opt = True
			self.welModule.initGroups()
