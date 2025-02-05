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
		self.db.aom(pd.Series(0, index= cpi([self.db('txE'), self.get('dTechTau')])), name = 'uAbateC', priority = 'first')
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
		g.v += [('techPot', self.g('dtech')), ('techCost', self.g('dtech')), ('techSmooth', self.g('dtech')), 'DACCost', 'DACSmooth', 'qCO2Base', 'tauCO2agg']
		return g
	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		g.v += [('uAbate', self.g('dqCO2')), ('uAbateC', self.g('dTechTau')), ('avgAbateCosts', self.g('dtauCO2')), ('abateCosts', self.g('dtauCO2'))]
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
		self.addProperty('addCosts', """-sum(tech$(dtech[s,tech]), divdEOP[t,s,tech])""")

	def initData(self):
		super().initData()
		techIdx = cpi([self.get('t'), self.get('dtech')])
		self.db.aom(pd.Series(.05, index = self.get('dtech')), name='rDeprEOP', priority='first')
		self.db.aom(pd.Series(1, index = self.get('dtech')), name = 'adjCostParEOP', priority='first')
		self.db.aom(pd.Series(self.get('g_LR'), index = self.get('dtech')), name = 'KtvcEOP', priority='first')
		self.db.aom(pd.Series(0, index = techIdx), name = 'pKEOP', priority='first')
		self.db.aom(pd.Series(1, index = techIdx), name = 'qKEOP', priority='first')
		self.db.aom(pd.Series(0, index = techIdx), name = 'qIEOP', priority='first')
		self.db.aom(pd.Series(0, index = techIdx), name = 'divdEOP', priority = 'first')
		self.db.aom(self.get('techCost')/(stdSort(adjMultiIndex.applyMult(self.get('rDeprEOP'), techIdx))+self.get('Rrate')-1), name = 'uKEOP', priority='first')
		self.db.aom(pd.Series(0, index = techIdx), name = 'qKmin', priority='first')
		self.db.aom(.05, name = 'qKminRate', type = 'par', priority='first')

	@property
	def model_B(self):
		return OrdSet([f"B_{self.name}", f"B_{self.name}_adjCost"])
	@property
	def model_C(self):
		return self.model_B+OrdSet([f"B_{self.name}_calib", f"B_{self.name}_calibK0"])
	@property
	def textInit(self):
		return "" if self.initFromGms is None else getattr(gamsAbatement, f'init_{self.ctype}')
	@property
	def textBlocks(self):
		return super().textBlocks | {'abateCapital': getattr(gamsAbatement, f'EOP_{self.ctype}')(self.name)}

	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.v += [('rDeprEOP', self.g('dtech')), ('adjCostParEOP', self.g('dtech')), 'Rrate', ('KtvcEOP', self.g('dtech')), ('uKEOP', self.g('dtech')), ('qKmin', self.g('dtech'))]
		g.sub_v += [('techCost', self.g('dtech'))]
		return g

	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		g.v += [('qKEOP', ('and', [self.g('dtech'), self.g('tx0')])), ('pKEOP', self.g('dtech')), ('qIEOP', self.g('dtech')), ('techCost', self.g('dtech')), ('divdEOP', self.g('dtech'))]
		return g

	@property
	def group_endoInCalib(self):
		g = super().group_endoInCalib
		g.v += [('qKEOP', ('and', [self.g('dtech'), self.g('t0')]))]
		return g


class AbateCapital_KWedge(AbateCapital):
	def __init__(self, name, ctype = 'SqrAdjCosts_Kwedge', **kwargs):
		super().__init__(name, ctype = ctype, **kwargs)

	def initData(self):
		super().initData()
		self.db.aom(pd.Series(0, index = cpi([self.get('t'), self.get('dtech')])), name = 'qKEOPwedge', priority='first')

	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.v += [('qKEOPwedge', self.g('dtech'))]
		return g



# class AbateCapitalMix(AbateCapital):
# 	def __init__(self, name, **kwargs):
# 		super().__init__(name, **kwargs)

# 	def initData(self):
# 		super().initData()
# 		self.db.aom(.05, name = 'uTechUni', priority='first')
# 		self.db.aom(200/self.get('techCost'), name = 'uniTechMax', priority='first')

# 	@property
# 	def textBlocks(self):
# 		return {'emissions': gamsAbatement.EOP_MixedDistr(self.name, addCosts = self.addCosts),
# 				'abateCapital': getattr(gamsAbatement, f'EOP_{self.ctype}')(self.name)}

# 	@property
# 	def group_alwaysExo(self):
# 		g = super().group_alwaysExo
# 		g.v += ['uTechUni', ('uniTechMax', self.g('dtech'))]
# 		return g
