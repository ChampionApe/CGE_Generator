from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs
from pyDatabases import cartesianProductIndex as cpi
from gmsPython import Group
import mProduction
import gamsProduction

class NestedCES(mProduction.NestedCES):
	def initStuff(self, db = None, gdx = True):
		if db is not None:
			MergeDbs.merge(self.db, db)
		self.initData()
		self.initGroups()
		if gdx:
			self.db.mergeInternal()

	def initData(self):
		""" Add initial values to database (only the ones data we do not have from an IO database though)"""
		self.db.aom(pd.Series(1,  index = cpi([self.db('txE'), self.get('output')])), name = 'pS', priority = 'first') # get initial value for pS
		self.db.aom(pd.Series(1,  index = cpi([self.db('txE'), self.get('int')])), name = 'pD', priority = 'first') # prices on intermediate goods
		self.db.aom(pd.Series(.1, index = self.get('sm')), name = 'markup', priority='first') #
		self.db.aom(pd.Series(0,  index = self.get('sm')), name = 'taxRevPar')
		self.db.aom(self.get(self.taxInstr).copy(), name = f'{self.taxInstr}0')

	#### 2. GROUPINGS AND MODEL SPECIFICATIONS:
	# 2. Model specification:
	@property
	def model_B(self):
		return OrdSet([f"B_{name}" for name in self.m])+OrdSet([f"B_{self.name}_{k}" for k in ['pWedge']])
	@property
	def model_C(self):
		return self.model_B+OrdSet([f'B_{self.name}_taxCalib'])

	@property
	def textBlocks(self):
		return self.nestingBlocks | {'pWedge': self.priceWedgeBlocks, 'taxCalib': self.taxCalibBlocks}
	@property
	def priceWedgeBlocks(self):
		return gamsProduction.priceWedge(f'{self.name}_pWedge', self.name)
	
	@property
	def group_alwaysExo(self):
		if not self.partial:
			return Group(f'{self.name}_alwaysExo', 
						v = [('sigma', self.g('kninp')), ('mu', self.g('map')), ('tauD', self.g('input')), ('tauS', self.g('output')), ('tauLump', self.g('sm')), # taxes
							 (f'{self.taxInstr}0', self._taxInstrCondition)],
					sub_v = [(self.taxInstr, self._taxInstrCondition)])
		else:
			self.partial = False
			g = self.group_alwaysExo
			g.v += [('qS', self.g('output')), ('p',self.g('input_n')), 'Rrate']
			g.sub_v += [('p',self.g('output_n'))]
			self.partial = True
			return g

	@property
	def group_alwaysEndo(self):
		return Group(f'{self.name}_alwaysEndo', v = [('pD', ('or', [self.g('int'), self.g('input')])),
													 ('pS', self.g('output')),
													 ('p', ('and', [self.g('output_n'), self.g('tx0')])),
													 ('qD', self.g('int')),
													 ('qD', ('and', [self.g('input'), self.g('tx0')])),
													 ('TotalTax', ('and', [self.g('sm'), self.g('tx0E')]))])

class NestedCES_PC(NestedCES):
	""" Like NestedCES, but with $j$-terms instead of markups to emulate perfect competition"""
	def __init__(self, tree, **kwargs):
		super().__init__(tree, **kwargs)

	def initData(self):
		super().initData()
		self.db.aom(pd.Series(0, index = self.get('sm')), name = 'jTerm', priority='first') 

	@property
	def priceWedgeBlocks(self):
		return gamsProduction.priceWedgePC(f'{self.name}_pWedge', self.name)

	@property
	def group_endoInCalib(self):
		g = super().group_endoInCalib
		g.v += [('jTerm', self.g('sm'))]
		g.sub_v += [('markup', self.g('sm'))]
		return g