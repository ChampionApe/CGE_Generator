from GovernmentFiles.govServices import *

class SimplePolicy(GovNCES):
	def __init__(self, tree, polInstr = None, polCond = None, **kwargs):
		super().__init__(tree, **kwargs)
		SimplePolicy.addProperties(self, polInstr, polCond)

	@staticmethod
	def addProperties(self, polInstr, polCond):
		self.addProperty('polInstr', polInstr)
		self.addProperty('polCond', polCond)

	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		if self.polInstr is not None:
			g.v += [('qD', self.g('output'))]
		return g

	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		if self.polInstr is not None:
			g.v += [(self.polInstr, self.polCond)]
			g.sub_v += [('qD', self.g('output'))]
		return g

class SimplePolicy_tx0(GovNCES):
	def __init__(self, tree, polInstr = None, polCond = None, **kwargs):
		super().__init__(tree, **kwargs)
		SimplePolicy.addProperties(self, polInstr, polCond)

	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		if self.polInstr is not None:
			g.v += [('qD', ('and', [self.g('output'), self.g('tx0E')]))]
		return g

	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		if self.polInstr is not None:
			g.v += [(self.polInstr, ('and', [self.g('tx0E'), self.polCond]))]
			g.sub_v += [('qD', self.g('output'))]
		return g

	@property
	def group_exoInCalib(self):
		g = super().group_exoInCalib
		if self.polInstr is not None:
			g.v += [(self.polInstr, ('and', [self.g('t0'), self.polCond]))]
		return g

	@property
	def group_endoInCalib(self):
		g = super().group_endoInCalib
		if self.polInstr is not None:
			g.v += [('qD', ('and', [self.g('output'), self.g('t0')]))]
		return g


class BalanceLS(GovNCES):
	def __init__(self, tree, sectors = None, **kwargs):
		super().__init__(tree, **kwargs)
		self.ns['sTax'] = f"{self.name}_sTax"
		self.db[self.n('sTax')]  = noneInit(sectors, pd.Index([], name = 's'))

	def initData(self):
		super().initData()
		self.db.aom(pd.Series(1, index = cpi([self.get('txE'), self.get('sTax')])), name = 'uDistTauLump', priority='first')
		self.db.aom(pd.Series(0, index = self.get('t')), name = 'diffTauLump', priority='first')
		self.db.aom(adj.rc_pd(self.get('tauLump'), self.get('sTax')), name = 'tauLump0', priority='first')

	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.v += [('uDistTauLump', self.g('sTax')), ('tauLump0', self.g('sTax'))]
		if not self.get('sTax').empty:
			g.v += [('qD', ('and', [self.g('output'), self.g('tx0E')]))]
		return g

	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		g.v += [('diffTauLump', self.g('tx0E')), ('tauLump', ('and', [self.g('sTax'), self.g('txE')]))]
		if not self.get('sTax').empty:
			g.sub_v += [('qD', self.g('output'))]
		return g

	@property
	def group_exoInCalib(self):
		g = super().group_exoInCalib
		if not self.get('sTax').empty:
			g.v += [('diffTauLump', self.g('t0'))]
		return g

	@property
	def group_endoInCalib(self):
		g = super().group_endoInCalib
		if not self.get('sTax').empty:
			g.v += [('qD', ('and', [self.g('output'), self.g('t0')]))]
		return g

	@property
	def model_B(self):
		return super().model_B+OrdSet([f"B_{self.name}_tauLS"])
	@property
	def model_C(self):
		return super().model_C+OrdSet([f"B_{self.name}_tauLS"])

	# Text blocks
	@property
	def textBlocks(self):
		return super().textBlocks | {'tauLS': gamsGovernment.distrTauLump(f'{self.name}')}


class BalanceLSxGS(GModel):
	""" Balance budget with a lump sum transfer on households - the government does not produce services """
	def __init__(self, sectors = None, **kwargs):
		super().__init__(**kwargs)
		self.ns['sTax'] = f"{self.name}_sTax"
		self.db[self.n('sTax')]  = noneInit(sectors, pd.Index([], name = 's'))

	# initialize
	def initStuff(self, gdx = True):
		self.initData()
		self.initGroups()
		if gdx:
			self.db.mergeInternal()

	def initData(self):
		self.db.aom(0, name = 'jTermGov', priority='first')
		self.db.aom(pd.Series(1, index = cpi([self.get('txE'), self.get('sTax')])), name = 'uDistTauLump', priority='first')
		self.db.aom(pd.Series(0, index = self.get('t')), name = 'diffTauLump', priority='first')
		self.db.aom(adj.rc_pd(self.get('tauLump'), self.get('sTax')), name = 'tauLump0', priority='first')

	@property
	def model_B(self):
		return OrdSet([f"B_{self.name}_tauLS", f"B_{self.name}_BB"])

	# Text blocks
	@property
	def textBlocks(self):
		return {'tauLS': gamsGovernment.distrTauLump(self.name), 'BB': gamsGovernment.BBxGovNCS(self.name)}

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
		g = Group(f'{self.name}_alwaysExo', v = [('uDistTauLump', self.g('sTax')), ('tauLump0', self.g('sTax'))])
		return g

	@property
	def group_alwaysEndo(self):
		g = Group(f'{self.name}_alwaysEndo', v = [('diffTauLump', self.g('tx0E')), ('tauLump', ('and', [self.g('sTax'), self.g('txE')]))])
		return g
	@property
	def group_exoInCalib(self):
		g = Group(f'{self.name}_exoInCalib', v = [('diffTauLump', self.g('t0'))])
		return g

	@property
	def group_endoInCalib(self):
		g = Group(f'{self.name}_endoInCalib', v = ['jTermGov'])
		return g