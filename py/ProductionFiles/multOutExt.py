
from ProductionFiles.dynamicNCES import *

class StaticNCES_multOut(StaticNCES):
	def __init__(self, *args, exoP = None, exoQS = None, **kwargs):
		self.exoP = exoP # prices that are exogenous in partial equilibrium
		self.exoQS = exoQS # supply quantities that are exogenous in partial equilibrium 
		super().__init__(*args, **kwargs)

	def calibrationSubsets(self, tree):
		self.ns.update({k: f'{self.name}_{k}' for k in ['endoMu','exoQS','exoP']})
		self.db[self.n('exoQS')] = self.exoQS
		self.db[self.n('exoP')] = self.exoP 
		self.db[self.n('endoP')] = adj.rc_pd(self.get('endoP'), ('not', self.exoP))
		inputs = adj.rc_pd(self.get('map'), self.get('input').rename({'n':'nn'}))
		outputs = adj.rc_pd(self.get('map'), ('and', [self.get('output'), ('not', self.get('exoQS'))]))
		self.db[self.n('endoMu')] = inputs.union(outputs) # share parameters endogenous in calibration

	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.v += [('eta', self.g('knout'))]
		if not self.partial:
			return g
		else:
			g.sub_v += [('qS', self.g('output'))]
			g.v += [('qS', ('and', [self.g('output'), self.g('exoQS')])), ('p', self.g('exoP'))]
			return g

	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		g.v += [('qS', ('and', [self.g('output'), ('not', self.g('exoQS')), self.db['tx0']]))]
		return g

	@property
	def group_exoInCalib(self):
		g = super().group_exoInCalib
		g.v += [('qS', ('and', [self.g('output'), ('not', self.g('exoQS')), self.db['t0']]))]
		return g


class StaticNCES_emission_multOut(StaticNCES_emission):
	def __init__(self, *args, exoP = None, exoQS = None, **kwargs):
		self.exoP = exoP # prices that are exogenous in partial equilibrium
		self.exoQS = exoQS # supply quantities that are exogenous in partial equilibrium 
		super().__init__(*args, **kwargs)

	def calibrationSubsets(self, tree):
		self.ns.update({k: f'{self.name}_{k}' for k in ['endoMu','exoQS','exoP']})
		self.db[self.n('exoQS')] = self.exoQS 
		self.db[self.n('exoP')] = self.exoP 
		self.db[self.n('endoP')] = adj.rc_pd(self.get('endoP'), ('not', self.exoP))
		inputs = adj.rc_pd(self.get('map'), self.get('input').rename({'n':'nn'}))
		outputs = adj.rc_pd(self.get('map'), ('and', [self.get('output'), ('not', self.get('exoQS'))]))
		self.db[self.n('endoMu')] = inputs.union(outputs) # share parameters endogenous in calibration

	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.v += [('eta', self.g('knout'))]
		if not self.partial:
			return g
		else:
			g.sub_v += [('qS', self.g('output'))]
			g.v += [('qS', ('and', [self.g('output'), self.g('exoQS')])), ('p', self.g('exoP'))]
			return g

	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		g.v += [('qS', ('and', [self.g('output'), ('not', self.g('exoQS')), self.db['tx0']]))]
		return g

	@property
	def group_exoInCalib(self):
		g = super().group_exoInCalib
		g.v += [('qS', ('and', [self.g('output'), ('not', self.g('exoQS')), self.db['t0']]))]
		return g


class DynamicNCES_multOut(DynamicNCES):
	def __init__(self, *args, exoP = None, exoQS = None, **kwargs):
		self.exoP = exoP # prices that are exogenous in partial equilibrium
		self.exoQS = exoQS # supply quantities that are exogenous in partial equilibrium 
		super().__init__(*args, **kwargs)

	def calibrationSubsets(self, tree):
		self.ns.update({k: f'{self.name}_{k}' for k in ['endoMu','exoQS','exoP']})
		self.db[self.n('exoQS')] = self.exoQS 
		self.db[self.n('exoP')] = self.exoP 
		self.db[self.n('endoP')] = adj.rc_pd(self.get('endoP'), ('not', self.exoP))
		inputs = adj.rc_pd(self.get('map'), self.get('input').rename({'n':'nn'}))
		outputs = adj.rc_pd(self.get('map'), ('and', [self.get('output'), ('not', self.get('exoQS'))]))
		self.db[self.n('endoMu')] = inputs.union(outputs) # share parameters endogenous in calibration

	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.v += [('eta', self.g('knout'))]
		if not self.partial:
			return g
		else:
			g.sub_v += [('qS', self.g('output'))]
			g.v += [('qS', ('and', [self.g('output'), self.g('exoQS')])), ('p', self.g('exoP'))]
			return g

	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		g.v += [('qS', ('and', [self.g('output'), ('not', self.g('exoQS')), self.db['tx0']]))]
		return g

	@property
	def group_exoInCalib(self):
		g = super().group_exoInCalib
		g.v += [('qS', ('and', [self.g('output'), ('not', self.g('exoQS')), self.db['t0']]))]
		return g


class DynamicNCES_emission_multOut(DynamicNCES_emission):
	def __init__(self, *args, exoP = None, exoQS = None, **kwargs):
		self.exoP = exoP # prices that are exogenous in partial equilibrium
		self.exoQS = exoQS # supply quantities that are exogenous in partial equilibrium 
		super().__init__(*args, **kwargs)

	def calibrationSubsets(self, tree):
		self.ns.update({k: f'{self.name}_{k}' for k in ['endoMu','exoQS','exoP']})
		self.db[self.n('exoQS')] = self.exoQS 
		self.db[self.n('exoP')] = self.exoP 
		self.db[self.n('endoP')] = adj.rc_pd(self.get('endoP'), ('not', self.exoP))
		inputs = adj.rc_pd(self.get('map'), self.get('input').rename({'n':'nn'}))
		outputs = adj.rc_pd(self.get('map'), ('and', [self.get('output'), ('not', self.get('exoQS'))]))
		self.db[self.n('endoMu')] = inputs.union(outputs) # share parameters endogenous in calibration

	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.v += [('eta', self.g('knout'))]
		if not self.partial:
			return g
		else:
			g.sub_v += [('qS', self.g('output'))]
			g.v += [('qS', ('and', [self.g('output'), self.g('exoQS')])), ('p', self.g('exoP'))]
			return g

	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		g.v += [('qS', ('and', [self.g('output'), ('not', self.g('exoQS')), self.db['tx0']]))]
		return g

	@property
	def group_exoInCalib(self):
		g = super().group_exoInCalib
		g.v += [('qS', ('and', [self.g('output'), ('not', self.g('exoQS')), self.db['t0']]))]
		return g




def _getExt(extension):
	if extension is None:
		return ''
	elif type(extension) is str:
		return f'_{extension}'
	else:
		return '_'+'_'.join(list(extension))

def getStaticNCES(tree, *args, extension = None, **kwargs):
	return globals()[f'StaticNCES{_getExt(extension)}'](tree, *args, **kwargs)

def getDynamicNCES(tree, *args, extension = None, **kwargs):
	return globals()[f'DynamicNCES{_getExt(extension)}'](tree, *args, **kwargs)


