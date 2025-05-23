from HouseholdFiles.staticConsumer import *

class Ramsey(StaticNCES):
	@staticmethod
	def addIncInstr(self, incInstr = 'jTerm'):
		StaticNCES.addIncInstr(self, incInstr = incInstr) # go through parent class options first
		if incInstr == 'discF':
			self.addInc_tx0 = ''
			self.addInc_t0  = ''
			self.addProperty('incInstrTuple', ('discF', self.g('sm')))
		elif incInstr == 'vA_tvc':
			self.addInc_tx0 = ''
			self.addInc_t0  = ''
			self.addProperty('incInstrTuple', ('vA_tvc', self.g('sm')))


	def initData(self):
		super().initData()
		self.db.aom(pd.Series(self.get('g_LR'), index = self.get('sm')), name = 'vA_tvc', priority = 'first')

	# blocks
	@property
	def model_B(self):
		return super().model_B+OrdSet([f"B_{self.name}_Euler"])
	@property
	def textBlocks(self):
		return super().textBlocks | {'Euler': self.EulerBlocks}
	@property
	def EulerBlocks(self):
		return gamsHouseholds.CRRA_Euler(f'{self.name}_Euler', self.name)	

	# Groups
	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.v = [x for x in g.v if x != ('vA', self.g('sm'))] # remove specific element in v-tuples
		g.v += [('vA', ('and', [self.g('sm'), self.g('t0')])), ('vA_tvc', self.g('sm'))]
		return g
	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		g.v += [('vA', ('and', [self.g('sm'), self.g('tx0')]))]
		return g

class RamseyGHH(Ramsey):
	def initData(self):
		super().initData()
		self.db.aom(pd.Series(1, index = self.get('sm')), name = 'Lscale', priority='first')
		self.db.aom(pd.Series(.25, index = self.get('sm')), name = 'frisch', priority = 'first')
		self.db.aom(pd.Series(1, index = cpi([self.db('txE'), self.get('sm')])), name = 'qC', priority = 'first')

	@property
	def CRRA_vU(self):
		return gamsHouseholds.CRRA_GHH_vU(f'{self.name}_vU', self.name)

	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.v += [('frisch', self.g('sm'))]
		g.sub_v += [('qS', ('and', [self.g('L'), self.g('txE')]))]
		return g

	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		g.v += [('qS', ('and', [self.g('L'), self.g('tx0E')])), ('qC', ('and', [self.g('sm'), self.g('txE')]))]
		return g

	@property
	def group_exoInCalib(self):
		g = super().group_exoInCalib
		g.v += [('qS', ('and', [self.g('L'), self.g('t0')]))]
		return g

	@property
	def group_endoInCalib(self):
		g = super().group_endoInCalib
		g.v += [('Lscale', self.g('sm'))]
		return g


class RamseyGHH_waste(RamseyGHH):
	def __init__(self, tree, wasteCosts = False, **kwargs):
		""" Note: Currently only one implementation of wasteCosts - thus wasteCosts doesn't do anything yet"""
		super().__init__(tree, **kwargs)
		self.extendNestingStructure()
		RamseyGHH_waste.addProperties(self, wasteCosts = wasteCosts)

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
		RamseyGHH_waste.addProperties(self, wasteCosts = wasteCosts)

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
		return gamsHouseholds.wasteGeneration(f'{self.name}_WS', self.name)+gamsHouseholds.wasteGenerationCalib(f'{self.name}_WSCal', self.name)

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


