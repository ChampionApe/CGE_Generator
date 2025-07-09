from EmissionsFiles.emissionTargets import *
import EmissionsFiles.gamsAbatement as gamsAbatement

class AbateSimple(EmissionAccounts):
	def __init__(self, name, techType = "'logNorm'", properties = None, **kwargs):
		super().__init__(name = name, **kwargs)
		self.techType = techType # the type of technology used
		AbateSimple.initProperties(self, **noneInit(properties, {}))

	@staticmethod
	def initProperties(self, **kwargs):
		[self.addProperty(k,v) for k,v in ({'addCosts': ''} | kwargs).items()]

	def initData(self):
		super().initData()
		self.db.aom(pd.Series(0, index= cpi([self.db('txE'), self.get('dtauCO2')])), name = 'avgAbateCosts', priority='first')
		self.db.aom(pd.Series(0, index= cpi([self.db('txE'), self.get('dtauCO2')])), name = 'abateCosts', priority='first')
		self.db.aom(pd.Series(0, index= self.get('dTechSN')), name = 'uAbateC', priority = 'first')
		self.db.aom(pd.Series(0, index=self.db('uCO2').index), name='uAbate', priority='first')
		self.db.aom(pd.Series(self.db('tauCO2agg').xs(self.db('t0')[0])/ 2, index = self.db('t')), name='DACSmooth', priority='first')
		self.db.aom(pd.Series(.5, index = self.db('techPot').index), name='techSmooth', priority='first') # this for lognormal
		self.db.aom(1, name='qCO2Base', priority='first')

	@property
	def textBlocks(self):
		return {'emissions': gamsAbatement.EOP_Simple(self.name, addCosts = self.addCosts)}
	@property
	def textFuncs(self):
		return gamsAbatement.EOPTechFunctions

	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.v += [('techPot', self.g('dTechS')), ('techCost', self.g('dTechS')), ('techSmooth', self.g('dTechS')), 'DACCost', 'DACSmooth', 'qCO2Base', 'tauCO2agg']
		return g
	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		g.v += [('uAbate', self.g('dqCO2')), ('uAbateC', self.g('dTechSN')), ('avgAbateCosts', self.g('dtauCO2')), ('abateCosts', self.g('dtauCO2'))]
		return g

class AbateCapital(AbateSimple):
	def __init__(self, name, techType = "'normal'", initFromGms = None, ctype = 'SqrAdjCosts', **kwargs):
		""" ctype indicates type of adjustment costs. Currently only SqrAdjCosts are specified """
		super().__init__(name, techType = techType, **kwargs)
		self.initFromGms = initFromGms
		AbateCapital.addProperties(self, ctype = ctype)

	@staticmethod
	def addProperties(self, ctype = 'SqrAdjCosts'):
		self.addCtype(ctype)

	def addCtype(self, ctype):
		self.addProperty('ctype', ctype) # add specification of adjustment costs
		self.addProperty('addCosts', """-sum(tech$(dTechS[t,s,tech]), divdEOP[t,tech]*uEOP[t,s,tech])""")

	def initData(self):
		super().initData()
		self.db.aom(pd.Series(.05, index = self.get('tech')), name='rDeprEOP', priority='first')
		self.db.aom(pd.Series(5, index = self.get('tech')), name = 'adjCostParEOP', priority='first')
		self.db.aom(pd.Series(self.get('g_LR'), index = self.get('tech')), name = 'KtvcEOP', priority='first')
		self.db.aom(pd.Series(0, index = self.get('dTech')), name = 'qKmin', priority='first')
		self.db.aom(.1, name = 'qKminRate', type = 'par', priority='first')
		self.db.aom(pd.Series(0, index = self.get('dTech')), name = 'pKEOP', priority='first')
		self.db.aom(pd.Series(1, index = self.get('dTech')), name = 'qKEOP', priority='first')
		self.db.aom(pd.Series(0, index = self.get('dTech')), name = 'qIEOP', priority='first')
		self.db.aom(pd.Series(0, index = self.get('dTech')), name = 'divdEOP', priority = 'first')
		self.db.aom(pd.Series(1, index = self.get('dTechS')), name = 'uEOP', priority='first')
		self.db.aom(stdSort((self.get('techCostEst')/(adjMultiIndex.bc(self.get('rDeprEOP'), self.get('t'))+self.get('Rrate')-1))), name = 'uKEOP')

	@property
	def model_B(self):
		return OrdSet([f"B_{self.name}", f"B_{self.name}_adjCost"])
	@property
	def model_C(self):
		return self.model_B+OrdSet([f"B_{self.name}_calibD", f"B_{self.name}_calibS"])
	@property
	def textInit(self):
		return "" if self.initFromGms is None else getattr(gamsAbatement, f'init_{self.ctype}')

	@property
	def textBlocks(self):
		return {'emissions': gamsAbatement.EOP_CapDemand(self.name, addCosts = self.addCosts), 
				'abateCap' : getattr(gamsAbatement, f'EOP_{self.ctype}')(self.name)}


	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.v += ['rDeprEOP', 'adjCostParEOP', 'Rrate', 'KtvcEOP', ('uKEOP', self.g('dTech')), ('qKmin', self.g('dTech')), ('techCostEst', self.g('dTech'))]
		g.sub_v += [('techCost', self.g('dTechS'))]
		return g

	@property
	def group_alwaysEndo(self):
		g = EmissionAccounts.group_alwaysEndo.__get__(self)
		g.v += [('qKEOP', ('and', [self.g('dTech'), self.g('tx0')])), ('pKEOP', ('and', [self.g('dTech'), self.g('tx0')])), ('uAbate', ('and', [self.g('dqCO2'), self.g('tx0')])), ('uAbateC', ('and', [self.g('dTechSN'), self.g('tx0')])),
				('qIEOP', self.g('dTech')), ('techCost', self.g('dTechS')), ('divdEOP', self.g('dTech')), ('uEOP',self.g('dTechS')), ('avgAbateCosts', self.g('dtauCO2')), ('abateCosts', self.g('dtauCO2'))]
		return g

	@property
	def group_endoInCalib(self):
		g = super().group_endoInCalib
		g.v += [('qKEOP', ('and', [self.g('dTech'), self.g('t0')])), ('pKEOP', ('and', [self.g('dTech'), self.g('t0')])), ('uAbate', ('and', [self.g('dqCO2'), self.g('t0')])), ('uAbateC', ('and', [self.g('dTechSN'), self.g('t0')]))]
		return g

