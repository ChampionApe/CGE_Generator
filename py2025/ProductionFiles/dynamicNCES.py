from ProductionFiles.staticNCES import *

def DynamicNCES(tree, staticExtension = 'base', **kwargs):
	return getDynamicNCES(staticExtension, tree, **kwargs)

def getDynamicNCES(staticExtension, tree, adjCosts = True, **kwargs):
	ParentClass = globals()[f'StaticNCES_{staticExtension}']
	class DynamicNCES_base(ParentClass):
		def __init__(self, tree, staticExtension = 'base', adjCosts = True, **kwargs):
			super().__init__(tree, **kwargs)
			DynamicNCES_base.addProperties(self, adjCosts = adjCosts)

		@staticmethod
		def addProperties(self, adjCosts = True):
			self.addAdjCosts(adjCosts)

		@staticmethod
		def initProperties(self, adjCosts = True, **kwargs):
			super().initProperties(self, **kwargs)
			DynamicNCES_base.addProperties(self, adjCosts = adjCosts)

		def addDurables(self):
			self.ns.update({k: f'{self.name}_{k}' for k in ('dur','inv', 'dur2inv', 'input_n')})
			self.db[self.n('dur')] = adj.rc_pd(self.get('input'), self.get('dur_p')) # read durables from the inputs included in the nesting tree inputs
			self.db[self.n('dur2inv')] = adjMultiIndex.applyMult(self.get('dur'), self.db('dur2inv')) 
			self.db[self.n('inv')] = adj.rc_pd(self.get('dur2inv').droplevel('n').unique(), alias = {'nn':'n'})
			self.db[self.n('input')] = self.get('input').difference(self.get('dur')).union(self.get('inv'))
			self.db[self.n('input_n')] = self.get('input').levels[-1]
	
		def initStuff(self, db = None, gdx = True):
			if db is not None:
				MergeDbs.merge(self.db, db)
			self.addDurables()
			self.initData()
			self.initGroups()
			if gdx:
				self.db.mergeInternal()
	
		def initData(self):
			super().initData()
			self.db.aom(pd.Series(0,  index = self.get('dur')), name = 'K_tvc', priority='first') # tvc condition for durables
			if self.adjCosts:
				self.db.aom(pd.Series(.1,  index = self.get('dur')), name = 'adjCostPar', priority = 'first') # parameter in investment cost function
				self.db.aom(pd.Series(0,  index = cpi([self.db('txE'), self.get('sm')]), name = 'adjCost'), priority='first') # adjustment costs
	
		def addAdjCosts(self, adjCosts):
			self.addProperty('adjCosts', adjCosts) # add specification of adjustment costs
			if adjCosts:
				self._addCosts += """-adjCost[t,s]"""
	
		@property
		def model_B(self):
			return super().model_B+OrdSet([f"B_{self.name}_adjCost"])
		@property
		def textBlocks(self):
			return super().textBlocks | {'capAcc': self.capAccBlocks}
		@property
		def capAccBlocks(self):
			return gamsProduction.capitalAccumulation(f'{self.name}_adjCost', self.name, adjCosts = self.adjCosts)
	
		@property
		def group_alwaysExo(self):
			g = super().group_alwaysExo
			g.v += [('rDepr', self.g('dur')),('K_tvc', self.g('dur')), ('qD', ('and', [self.g('dur'), self.g('t0')]))]
			if self.adjCosts:
				g.v += [('adjCostPar', self.g('dur'))]
			return g
	
		@property
		def group_alwaysEndo(self):
			g = super().group_alwaysEndo
			g.v += [('qD', ('and', [self.g('dur'), self.g('tx0')])), ('pD', ('and', [self.g('dur'), self.g('txE')]))]
			if self.adjCosts:
				g.v += [('adjCost', ('and', [self.g('sm'), self.g('txE')]))]
			return g

	return DynamicNCES_base(tree, staticExtension = staticExtension, adjCosts = adjCosts, **kwargs)

