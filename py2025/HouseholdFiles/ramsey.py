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
		self.db.aom(pd.Series(0, index = self.get('sm')), name = 'vA_tvc', priority = 'first')

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

def RamseyIdxFund(*args, parent = 'Ramsey', **kwargs):
	return getIdxFund(parent, *args, **kwargs)

def getIdxFund(parent, *args, **kwargs):
	ParentClass = globals()[f'{parent}']
	global IdxFundBase
	class IdxFundBase(ParentClass):
		def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)

		def initData(self):
			super().initData()
			self.db.aom(pd.Series(1, index = self.get('t')), name ='vIdxFund', priority='first')
			self.db.aom(pd.Series(.1, index = self.get('sm')), name = 'uIdxFund', priority = 'first')
			self.db.aom(pd.Series(0, index = self.get('sm')), name = 'vA_F', priority='first')

		# Specify new blocks of equations (the self.nestingBlocks are the same)
		@property
		def model_B(self):
			return super().model_B+OrdSet([f"B_{self.name}_idxFund"])
		@property
		def model_C(self):
			return super().model_C+OrdSet([f"B_{self.name}_idxFund"])
		@property
		def textBlocks(self):
			return super().textBlocks | {'idxFund': self.idxFundBlocks}
		@property
		def idxFundBlocks(self):
			return gamsHouseholds.idxFund(f'{self.name}_idxFund', self.name)

		# Specify new groups of variables
		@property
		def group_alwaysExo(self):
			g = super().group_alwaysExo
			g.v += [('vA_F', self.g('sm')), ('uIdxFund', self.g('sm'))]
			g.sub_v += [('vA', ('and', [self.g('sm'), self.g('t0')]))]
			if self.partial:
				g.v += [('vIdxFund', self.g('t0'))]
			return g

		@property
		def group_alwaysEndo(self):
			g = super().group_alwaysEndo
			g.v += [('vA', ('and', [self.g('sm'), self.g('t0')]))]
			return g

	return IdxFundBase(*args, **kwargs)

# class RamseyIdxFund(Ramsey):
# 	# Add a bit more data:
# 	def initData(self):
# 		super().initData()
# 		self.db.aom(pd.Series(1, index = self.get('t')), name ='vIdxFund', priority='first')
# 		self.db.aom(pd.Series(.1, index = self.get('sm')), name = 'uIdxFund', priority = 'first')
# 		self.db.aom(pd.Series(0, index = self.get('sm')), name = 'vA_F', priority='first')

# 	# Specify new blocks of equations (the self.nestingBlocks are the same)
# 	@property
# 	def model_B(self):
# 		return super().model_B+OrdSet([f"B_{self.name}_idxFund"])
# 	@property
# 	def model_C(self):
# 		return self.model_B
# 	@property
# 	def textBlocks(self):
# 		return super().textBlocks | {'idxFund': self.idxFundBlocks}
# 	@property
# 	def idxFundBlocks(self):
# 		return gamsHouseholds.idxFund(f'{self.name}_idxFund', self.name)

# 	# Specify new groups of variables
# 	@property
# 	def group_alwaysExo(self):
# 		g = super().group_alwaysExo
# 		g.v += [('vA_F', self.g('sm')), ('uIdxFund', self.g('sm'))]
# 		g.sub_v += [('vA', ('and', [self.g('sm'), self.g('t0')]))]
# 		if self.partial:
# 			g.v += [('vIdxFund', self.g('t0'))]
# 		return g

# 	@property
# 	def group_alwaysEndo(self):
# 		g = super().group_alwaysEndo
# 		g.v += [('vA', ('and', [self.g('sm'), self.g('t0')]))]
# 		return g
