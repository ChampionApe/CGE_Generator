from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs
from pyDatabases import cartesianProductIndex as cpi
from gmsPython import Group, GModel, gmsWrite
import WasteFiles.gamsWaste as gamsWaste
import HouseholdFiles.gamsHouseholds as gamsHouseholds
import mHousehold

class StaticGHH_WG(mHousehold.StaticGHH):
	def __init__(self, tree, wasteCosts = False, **kwargs):
		""" Note: Currently only one implementation of wasteCosts - thus wasteCosts doesn't do anything yet"""
		super().__init__(tree, **kwargs)
		self.extendNestingStructure()
		StaticGHH_WG.addProperties(self, wasteCosts = wasteCosts)

	def extendNestingStructure(self):
		""" Extend subset of "inputs" to cover demand for relevant waste management services"""
		self.g('input').vals = self.get('input').union(adj.rc_pd(reduce(pd.Index.union, [self.db('dWTn'), self.db('dWTy'), self.db('dWTyF')]), self.get('sm')))
		self.g('input_n').vals = self.get('input').levels[-1]

	def initData(self):
		super().initData()
		self.db.aom(self.get('uWS_D').copy(), name = 'uWS_D0', type = 'par', priority = 'first')
		self.db.aom(pd.Series(0, index = adj.rc_pd(self.get('dWTn'), self.get('nw_D'))), name = 'WTDpar', priority='first')
		self.db.aom(pd.Series(0, index = adj.rc_pd(self.get('dWTn'), self.get('nw_F'))), name = 'WTFpar', priority='first')


	@staticmethod
	def initProperties(self, wasteCosts = False, **kwargs):
		super().initProperties(self, **kwargs)
		StaticGHH_WG.addProperties(self, wasteCosts = wasteCosts)

	@staticmethod
	def addProperties(self, wasteCosts = False):
		self._addMargCostInp += """+pW[t,s,n]$(dWSn[s,n])"""
		self.addWasteCosts(wasteCosts)

	def addWasteCosts(self, wasteCosts):
		self.addProperty('wasteCosts', wasteCosts) # add specification of wasteCosts

	@property
	def model_B(self):
		return super().model_B+OrdSet([f"B_{self.name}_WS"])
	@property
	def model_C(self):
		return super().model_C+OrdSet([f"B_{self.name}_WSCal"])

	@property
	def textBlocks(self):
		return super().textBlocks | {'wasteGeneration': self.wasteGen}
	@property
	def wasteGen(self):
		return gamsWaste.wasteGen(f'{self.name}_WS', self.name)+gamsWaste.wasteGenCalib(f'{self.name}_WSCal', self.name)

	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.v += [('uWS', ('and', [self.g('dWSnm'), self.g('sm')]))]
		return g

	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		g.v += [('pW', ('and', [self.g('dWSn'), self.g('sm')])), ('qWS', ('and', [self.g('dWS'), self.g('sm')]))]
		return g

	@property
	def group_endoInCalib(self):
		g = super().group_endoInCalib
		g.v += [('uWS_D', ('and', [self.g('dWS'), self.g('sm')])), ('uWTy', ('and', [self.g('dWTy'), self.g('sm')])), ('uWTyF', ('and', [self.g('dWTyF'), self.g('sm')])), 
				('WTFpar',('and', [self.g('dWTn'), self.g('nw_F'), self.g('sm')])),('WTDpar', ('and', [self.g('dWTn'), self.g('nw_D'), self.g('sm')]))]
		return g


class RamseyGHH_WG(mHousehold.RamseyGHH):
	def __init__(self, tree, wasteCosts = False, **kwargs):
		""" Note: Currently only one implementation of wasteCosts - thus wasteCosts doesn't do anything yet"""
		super().__init__(tree, **kwargs)
		self.extendNestingStructure()
		RamseyGHH_WG.addProperties(self, wasteCosts = wasteCosts)

	def extendNestingStructure(self):
		""" Extend subset of "inputs" to cover demand for relevant waste management services"""
		self.g('input').vals = self.get('input').union(adj.rc_pd(reduce(pd.Index.union, [self.db('dWTn'), self.db('dWTy'), self.db('dWTyF')]), self.get('sm')))
		self.g('input_n').vals = self.get('input').levels[-1]

	def initData(self):
		super().initData()
		self.db.aom(self.get('uWS_D').copy(), name = 'uWS_D0', type = 'par', priority = 'first')
		self.db.aom(pd.Series(0, index = adj.rc_pd(self.get('dWTn'), self.get('nw_D'))), name = 'WTDpar', priority='first')
		self.db.aom(pd.Series(0, index = adj.rc_pd(self.get('dWTn'), self.get('nw_F'))), name = 'WTFpar', priority='first')

	@staticmethod
	def initProperties(self, wasteCosts = False, **kwargs):
		super().initProperties(self, **kwargs)
		RamseyGHH_WG.addProperties(self, wasteCosts = wasteCosts)

	@staticmethod
	def addProperties(self, wasteCosts = False):
		self._addMargCostInp += """+pW[t,s,n]$(dWSn[s,n])"""
		self.addWasteCosts(wasteCosts)

	def addWasteCosts(self, wasteCosts):
		self.addProperty('wasteCosts', wasteCosts) # add specification of wasteCosts

	@property
	def model_B(self):
		return super().model_B+OrdSet([f"B_{self.name}_WS"])
	@property
	def model_C(self):
		return super().model_C+OrdSet([f"B_{self.name}_WSCal"])
	@property
	def textBlocks(self):
		return super().textBlocks | {'wasteGeneration': self.wasteGen}
	@property
	def wasteGen(self):
		return gamsWaste.wasteGen(f'{self.name}_WS', self.name)+gamsWaste.wasteGenCalib(f'{self.name}_WSCal', self.name)

	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.v += [('uWS', ('and', [self.g('dWSnm'), self.g('sm')]))]
		return g

	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		g.v += [('pW', ('and', [self.g('dWSn'), self.g('sm')])), ('qWS', ('and', [self.g('dWS'), self.g('sm')]))]
		return g

	@property
	def group_endoInCalib(self):
		g = super().group_endoInCalib
		g.v += [('uWS_D', ('and', [self.g('dWS'), self.g('sm')])), ('uWTy', ('and', [self.g('dWTy'), self.g('sm')])), ('uWTyF', ('and', [self.g('dWTyF'), self.g('sm')])), 
				('WTFpar',('and', [self.g('dWTn'), self.g('nw_F'), self.g('sm')])),('WTDpar', ('and', [self.g('dWTn'), self.g('nw_D'), self.g('sm')]))]
		return g


