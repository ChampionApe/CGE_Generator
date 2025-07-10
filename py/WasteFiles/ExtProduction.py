from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs
from pyDatabases import cartesianProductIndex as cpi
from gmsPython import Group, GModel, gmsWrite
import WasteFiles.gamsWaste as gamsWaste
import ProductionFiles.gamsProduction as gamsProduction
import mProduction

class DynamicNCES_emission_WG(mProduction.DynamicNCES_emission_multOut):
	""" Add waste generation, no recycling"""
	def __init__(self, tree, wasteCosts = False, **kwargs):
		""" Note: Currently only one implementation of wasteCosts - thus wasteCosts doesn't do anything yet"""
		super().__init__(tree, **kwargs)
		self.extendNestingStructure()
		DynamicNCES_emission_WG.addProperties(self, wasteCosts = wasteCosts)

	def extendNestingStructure(self):
		""" Extend subset of "inputs" to cover demand for relevant waste management services"""
		self.g('input').vals = self.get('input').union(adj.rc_pd(reduce(pd.Index.union, [self.db('dWTn'), self.db('dWTy'), self.db('dWTyF')]), self.get('sm')))

	def initData(self):
		super().initData()
		self.db.aom(self.get('uWS_D').copy(), name = 'uWS_D0', type = 'par', priority = 'first')
		self.db.aom(pd.Series(0, index = adj.rc_pd(self.get('dWTn'), self.get('nw_D'))), name = 'WTDpar', priority='first')
		self.db.aom(pd.Series(0, index = adj.rc_pd(self.get('dWTn'), self.get('nw_F'))), name = 'WTFpar', priority='first')

	@staticmethod
	def initProperties(self, wasteCosts = False, **kwargs):
		super().initProperties(self, **kwargs)
		DynamicNCES_emission_WG.addProperties(self, wasteCosts = wasteCosts)

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

class DynamicNCES_emission_ExoIntRC(DynamicNCES_emission_WG):
	""" Waste generation and exogenous, internal recycling """
	@property
	def wasteGen(self):
		return gamsWaste.wasteGen_ExoIntRC(f'{self.name}_WS', self.name)+gamsWaste.wasteGenCalib_ExoIntRC(f'{self.name}_WSCal', self.name)

	def initData(self):
		""" Add initial values to database (only the ones data we do not have from an IO database though)"""
		super().initData()
		self.db.aom(self.get('uWS_int').copy(), name = 'uWS_int0', type = 'par', priority = 'first')
		self.db.aom(pd.Series(0, index = adj.rc_pd(self.get('dqSR'), self.get('sm'))), name = 'qSRpar', priority='first')

	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.v += [('intRcEff', ('and', [self.g('sm'), self.g('dWS_int')]))]
		return g

	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		g.v += [('pWext', ('and', [self.g('dWS'), self.g('sm')]))]
		return g

	@property
	def group_endoInCalib(self):
		g = super().group_endoInCalib
		g.v += [('uWS_int', ('and', [self.g('dWS_int'), self.g('sm')])), ('qSRpar', ('and', [self.g('dqSR'), self.g('sm')]))]
		return g


class DynamicNCES_emission_WT(DynamicNCES_emission_WG):
	def __init__(self, *args, RCTech = "'power'", **kwargs):
		super().__init__(*args, **kwargs)
		self.RCTech = RCTech
		self.compiler.locals['RCTech'] = self.RCTech

	def extendNestingStructure(self):
		super().extendNestingStructure()
		self.g('endoMu').vals = self.get('endoMu').union(adj.rc_pd(self.get('map'), ('and', [self.g('sm'), self.db('n_ZW')])))

	def initData(self):
		""" Add initial values to database (only the ones data we do not have from an IO database though)"""
		super().initData()
		self.db.aom(pd.Series(0, index = self.get('mw_D')), name = 'alphauCal', priority = 'first') # 
		self.db.aom(pd.Series(0, index = self.get('mw_D')), name = 'gammarCal', priority = 'first') # 
		self.db.aom(pd.Series(0, index = self.get('nw_D')), name = 'WTD_qSnwCal', priority = 'first') # 
		self.db.aom(pd.Series(0, index = self.get('nm_D')), name = 'WTD_qSnmCal', priority='first') #
		self.db.aom(pd.Series(0, index = self.get('mw_D')), name = 'WTD_pSnwCal', priority='first') #
		self.db.aom(pd.Series(0, index = self.get('n_wasteE')), name = 'WTD_qSWECal', priority='first') #
		self.db.aom(self.get('WTD_alphau').copy(), name = 'WTD_alphau0', priority='first')
		self.db.aom(self.get('WTD_gr').copy(), name = 'WTD_gr0', priority='first')
		self.db.aom(self.get('WTD_ge').copy(), name = 'WTD_ge0', priority='first')
		self.db.aom(self.get('WTD_gd').copy(), name = 'WTD_gd0', priority='first')

	@property
	def textFuncs(self):
		return gamsWaste.recyclTech
	@property
	def model_B(self):
		return super().model_B+OrdSet([f"B_{self.name}_Treat",f"B_{self.name}_Prod"])
	@property
	def model_C(self):
		return super().model_C+OrdSet([f"B_{self.name}_Treat",f"B_{self.name}_Prod", f"B_{self.name}_Calib"])

	@property
	def textBlocks(self):
		return super().textBlocks | self.treatmentBlocks
	@property
	def treatmentBlocks(self):
		return {'treatment': gamsWaste.wasteTreatment(f'{self.name}_Treat', self.name), 'production': gamsWaste.wasteTreatProd(f'{self.name}_Prod', self.name), 'calib': gamsWaste.wasteTreatCalib(f'{self.name}_Calib', self.name)}

	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		g.v += [('WTD_W', ('and', [self.g('mw_D'), self.g('txE')])),
				('WTD_d', ('and', [self.g('mw_D'), self.g('txE')])),
				('WTD_zetaE', ('and', [self.g('mw_D'), self.g('txE')])),
				('WTD_r', ('and', [self.g('mw_D'), self.g('tx0E')])),
				('WTD_a', ('and', [self.g('mw_D'), self.g('tx0E')])),
				('WTD_e', ('and', [self.g('mw_D'), self.g('txE')])),
				('qD', ('and', [self.g('sm'), self.g('n_ZW'), self.g('txE')])),
				('pD', ('and', [self.g('sm'), self.g('n_ZW'), self.g('tx0E')]))]
		return g

	@property
	def group_exoInCalib(self):
		g = super().group_exoInCalib
		g.v += [('WTD_r', ('and', [self.g('mw_D'), self.g('t0')])),
				('WTD_a', ('and', [self.g('mw_D'), self.g('t0')])),
				('pD', ('and', [self.g('sm'), self.g('n_ZW'), self.g('t0')]))]
		return g

	@property
	def group_endoInCalib(self):
		g = super().group_endoInCalib
		g.v += [('WTD_alphau', ('and', [self.g('mw_D'), self.g('txE')])), ('alphauCal', self.g('mw_D')), ('gammarCal', self.g('mw_D')), 
				('WTD_gr', ('and', [self.g('mw_D'), self.g('txE')])), ('WTD_ge', ('and', [self.g('mw_D'), self.g('txE')])), ('WTD_gd', ('and', [self.g('mw_D'), self.g('txE')])),
				('WTD_qSnwCal', self.g('nw_D')), ('WTD_qSnmCal', self.g('nm_D')), ('WTD_qSWECal', self.g('n_wasteE')), ('WTD_pSnwCal', self.g('mw_D'))]
		return g

	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.v += [('WTD_dmin', ('and', [self.g('mw_D'), self.g('txE')])), ('WTD_alphal', ('and', [self.g('mw_D'), self.g('txE')])), ('WTD_beta', self.g('mw_D')), ('WTD_smooth', self.g('mw_D')), 
				('WTD_gwe', self.g('mw_D')), ('WTD_alphau0', ('and', [self.g('mw_D'), self.g('txE')])), ('WTD_gr0', ('and', [self.g('mw_D'), self.g('txE')])),('WTD_ge0', ('and', [self.g('mw_D'), self.g('txE')])),('WTD_gd0', ('and', [self.g('mw_D'), self.g('txE')]))] 
		if self.partial:
			g.v += [('qWS', ('and', [self.g('dWS'), ('not', self.g('sm'))])), ('uWS_D', ('and', [self.g('dWS'), ('not', self.g('sm')), self.g('txE')]))]
		return g