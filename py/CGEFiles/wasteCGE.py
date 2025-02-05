from CGEFiles.basicCGE import *

class WasteCGE(CGE_base):
	# Production:
	def steadyStateDepr(self):
		s = adj.rc_pd(adj.rc_pd(self.db('qD'), self.db('inv_p')), alias = {'n':'nn'})
		return adjMultiIndex.applyMult(s, self.db('dur2inv')).droplevel('nn')/adj.rc_pd(self.db('qD'), self.db('dur_p'))-self.db('g_LR')

	def stdProduction(self, tree, cl = 'DynamicNCES', extension = 'emission', abateCosts = False, taxInstr = 'tauLump', partial = True, initFromGms = 'initFirmValueBlock', adjCosts = True, **kwargs):
		return self.addProduction(cl, tree, extension = extension, abateCosts = abateCosts, taxInstr = taxInstr, partial = partial, initFromGms = initFromGms, adjCosts = adjCosts, **kwargs)

	def stdInvestment(self, tree, cl = 'StaticNCES', taxInstr = 'tauD', partial = True, initFromGms = 'initFirmValueBlock', **kwargs):
		return self.addProduction(cl, tree, taxInstr = taxInstr, partial = partial, initFromGms = initFromGms, **kwargs)

	def stdHousehold(self, tree, L2C, cl = 'StaticNCES', taxInstr = 'tauS', incInstr = 'vA0', partial = True, initFromGms = 'init_vU', **kwargs):
		return self.addHousehold(cl, tree, L2C = L2C, properties = {'taxInstr': taxInstr, 'incInstr': incInstr}, partial = partial, initFromGms = initFromGms, **kwargs)

	def stdGovernment(self, tree, cl = 'SimplePolicy_tx0', taxInstr = 'tauLump', incInstr = 'vA0', partial = True, **kwargs):
		return self.addGovernment(cl, tree, partial = partial, properties = {'taxInstr': taxInstr, 'incInstr': incInstr}, polInstr = 'tauLump', polCond = self.g('s_HH'), **kwargs)

	def stdTrade(self, name, cl = 'Armington', **kwargs):
		return self.addTrade(cl, name, self.db, **kwargs)

	def stdInventory(self, name, cl = 'InventoryAR', sInventory = None, **kwargs):
		self.db['sInventory'] = noneInit(sInventory, pd.Index(['itory'], name = 's'))
		self.addModule(getattr(mOther, cl)(name, self.db, 'sInventory',**kwargs))
		self.m[name].initStuff(gdx = False)
		return self.m[name]

	def stdEmissions(self, name, cl = 'EmissionAccounts', **kwargs):
		self.addModule(getattr(mEmissions, cl)(name, database = self.db, **kwargs))
		self.m[name].initStuff(db = None, gdx = False)
		return self.m[name]

	def stdEquilibrium(self, name, cl = 'SmallOpenEq', **Kwargs):
		return self.addEquilibriumModule(cl, name)

