from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs
from pyDatabases import cartesianProductIndex as cpi, noneInit
from gmsPython import Group, GModel
import gamsHouseholds

class StaticConsumer(GModel):
	def __init__(self, tree, L2C = None, partial = False, initFromGms = None, **kwargs):
		super().__init__(name = tree.name, database = tree.db, **kwargs)
		self.readTree(tree)
		self.adjustForLaborSupply(L2C = L2C)
		self.partial = partial
		self.initFromGms = initFromGms

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
		self.db.aom(pd.Series(2, index = self.get('sm')), name = 'crra', priority='second')
		self.db.aom(pd.Series(1, index = cpi([self.db('txE'), self.get('sm')])), name = 'qC', priority = 'first')
		self.db.aom(pd.Series(1, index = cpi([self.db('txE'), self.get('sm')])), name = 'vU', priority = 'first')
		self.db.aom(pd.Series(.25, index = self.get('sm')), name = 'frisch', priority = 'first')
		self.db.aom(pd.Series(1/self.db('R_LR'), index = self.get('sm')), name = 'discF', priority='first')
		self.db.aom(pd.Series(1, index = self.get('sm')), name = 'Lscale', priority='first')
		self.db.aom(pd.Series(0, index = self.get('sm')), name = 'jTerm', priority='first')

	#### 2. GROUPINGS AND MODEL SPECIFICATIONS:
	@property
	def model_B(self):
		return OrdSet([f"B_{name}" for name in self.m])+OrdSet([f"B_{self.name}_{k}" for k in ('pWedge','vU')])
	@property
	def model_C(self):
		return self.model_B

	# Text blocks
	@property
	def textBlocks(self):
		return self.nestingBlocks | {'pWedge': self.priceWedgeBlocks, 'vU': self.CRRA_GHH_Blocks}
	@property
	def nestingBlocks(self):
		return {name: getattr(gamsHouseholds, m.f)(name) for name, m in self.m.items()}
	@property
	def priceWedgeBlocks(self):
		return gamsHouseholds.priceWedgeStatic(f'{self.name}_pWedge', self.name)
	@property
	def CRRA_GHH_Blocks(self):
		return gamsHouseholds.CRRA_GHH_vU(f'{self.name}_vU', self.name)

	# Methods for levels in variables
	@property
	def textInit(self):
		return "" if self.initFromGms is None else getattr(gamsHouseholds, f'{self.initFromGms}')(self.name)

	# Groups:
	@property
	def metaGroup_endo_B(self):
		return Group(f'{self.name}_endo_B', g = [self.groups[f'{self.name}_{k}'] for k in ('alwaysEndo','exoInCalib')])
	@property
	def metaGroup_endo_C(self):
		return Group(f'{self.name}_endo_C', g = [self.groups[f'{self.name}_{k}'] for k in ('alwaysEndo', 'endoInCalib')])
	@property
	def metaGroup_exo_B(self):
		return Group(f'{self.name}_exo_B', g = [self.groups[f'{self.name}_{k}'] for k in ('alwaysExo','endoInCalib')])
	@property
	def metaGroup_exo_C(self):
		return Group(f'{self.name}_exo_C', g = [self.groups[f'{self.name}_{k}'] for k in ('alwaysExo','exoInCalib')])
	@property
	def group_alwaysExo(self):
		if not self.partial:
			return Group(f'{self.name}_alwaysExo', v = [('sigma', self.g('kninp')),
													('mu', self.g('map')),
													('frisch', self.g('sm')),
													('crra', self.g('sm')),
													('discF', self.g('sm')),
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
													 ('pS', ('and', [self.g('L'), self.g('txE')])),
													 ('qC', ('and', [self.g('sm'), self.g('txE')])), 
													 ('vU', self.g('sm')),
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
													  ('Lscale', self.g('sm')),
													  ('tauLump', ('and', [self.g('sm'), self.g('t0')])),
													  ('jTerm', self.g('sm'))])

class Ramsey(StaticConsumer):
	# Data
	def initData(self):
		super().initData()
		self.db.aom(pd.Series(0, index = cpi([self.db('txE'), self.get('sm')])), name = 'sp', priority = 'first')
		self.db.aom(pd.Series(0, index = self.get('sm')), name = 'h_tvc', priority = 'first')

	# blocks
	@property
	def model_B(self):
		return OrdSet([f"B_{name}" for name in self.m])+OrdSet([f"B_{self.name}_{k}" for k in ('vU','Euler','pWedge')])
	@property
	def textBlocks(self):
		return self.nestingBlocks | {'vU': self.CRRA_GHH_Blocks, 'Euler': self.CRRA_EulerBlocks, 'pWedge': self.priceWedgeBlocks}
	@property
	def CRRA_GHH_Blocks(self):
		return gamsHouseholds.CRRA_GHH_vU(f'{self.name}_vU', self.name)
	@property
	def CRRA_EulerBlocks(self):
		return gamsHouseholds.CRRA_Euler(f'{self.name}_Euler', self.name)	
	@property
	def priceWedgeBlocks(self):
		return gamsHouseholds.priceWedge(f'{self.name}_pWedge', self.name)

	# Groups
	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.v += [('h_tvc', self.g('sm')), ('vA', ('and', [self.g('sm'), self.g('t0')]))]
		if self.partial:
			g.v += ['Rrate']
		return g

	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		g.v += [('sp', ('and', [self.g('sm'), self.g('txE')])), 
				('vA', ('and', [self.g('sm'), self.g('tx0')]))]
		return g


class RamseyIdxFund(Ramsey):
	def __init__(self, tree, targetvA0 = True, **kwargs):
		""" If not targetvA0 --> fix vA_F, uIdxFund and solve for vA[t0,s].  
			if targetvA0 --> fix vA[t0,s], uIdxFund and adjust only vA_F."""
		super().__init__(tree, **kwargs)
		self.targetvA0 = targetvA0 

	# Add a bit more data:
	def initData(self):
		super().initData()
		self.db.aom(pd.Series(.1, index = self.get('sm')), name = 'uIdxFund', priority = 'first')
		self.db.aom(pd.Series(0, index = self.get('sm')), name = 'vA_F', priority='first')
		self.db.aom(pd.Series(1, index = self.get('sm')), name = 'uA_Dom', priority='first')

	# Specify new blocks of equations (the self.nestingBlocks are the same)
	@property
	def model_B(self):
		return super().model_B+OrdSet([f"B_{self.name}_vA0"])
	@property
	def model_C(self):
		return self.model_B+OrdSet([f'B_{self.name}_vA0_Calib']) if self.targetvA0 else self.model_B

	@property
	def textBlocks(self):
		return super().textBlocks | {'vA0': self.idxFundBlocks}
	@property
	def idxFundBlocks(self):
		return gamsHouseholds.indexFundInvest(f'{self.name}_vA0', self.name)
	# Specify new groups of variables

	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.v += [('uA_Dom', self.g('sm'))]
		g.sub_v += [('vA', ('and', [self.g('sm'), self.g('t0')]))]
		if self.partial:
			g.v += [('vIdxFund', self.g('t0'))]
		if not self.targetvA0:
			g.v += [('vA_F', self.g('sm')), ('uIdxFund', self.g('sm'))]
		return g

	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		if not self.targetvA0:
			g.v += [('vA', ('and', [self.g('sm'), self.g('t0')]))]
		return g

	@property
	def group_exoInCalib(self):
		g = super().group_exoInCalib
		if self.targetvA0:
			g.v += [('vA', ('and', [self.g('sm'), self.g('t0')]))]
		return g

	@property
	def group_endoInCalib(self):
		g = super().group_endoInCalib
		if self.targetvA0:
			g.v += [('vA_F', self.g('sm')), ('uIdxFund', self.g('sm'))]
		return g