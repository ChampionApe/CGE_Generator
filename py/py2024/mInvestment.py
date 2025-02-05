from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs
from pyDatabases import cartesianProductIndex as cpi
from gmsPython import Group
import mProduction
import gamsProduction

class NestedCES(mProduction.StaticNCES):
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
	def textBlocks(self):
		return self.nestingBlocks | {'pWedge': self.priceWedgeBlocks, 'taxCalib': self.taxCalibBlocks}	

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