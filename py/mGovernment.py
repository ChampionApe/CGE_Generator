from gmsPython import gmsPy, GmsPythonSimple, Submodule
import pyDatabases, pandas as pd
from pyDatabases import OrdSet, noneInit
from pyDatabases.gpyDB_wheels import adj, robust
import gamsGovernment

class balancedBudget(GmsPythonSimple):
	def __init__(self, f=None, tree=None, ns=None, s=None, glob=None, s_kwargs = None, g_kwargs = None, kwargs = None):
		""" Initialize from a pickle file 'f' or nesting tree 'tree'. 
			Note: This module can only run alone in the calibration state. It does not have access to balancing instruments in stand-alone, baseline version. """
		super().__init__(checkStates = ['B','C','B_standAlone','C_standAlone'], name=tree.name if tree else None, f=f, s=s, glob=glob, ns=ns, s_kwargs = s_kwargs, g_kwargs=g_kwargs)
		if f is None:
			self.readTree(tree)
			self.adjust(**noneInit(kwargs,{}))

	@property
	def _symbols(self):
		""" which symbols are initialized when calling self.initDB """
		return ['pD','qD','mu','sigma','qnorm_inp','qiv_inp','tauS','tauD','tauD0','tauG_calib','TotalTax','p','jTerm']

	def adjust(self, standAlone=True):
		self.ns.update({k: f"{k}_{self.name}" for k in ('s', 'input_n')})
		self.s.db[self.n('input_n')] = self.get('input').levels[-1]
		self.s.db[self.n('s')] = self.get('input').levels[0]
		self.m[f"{self.name}_BSA"] = Submodule(**{'f': 'standAloneBaseline'})
		self.m[f"{self.name}_CSA"] = Submodule(**{'f': 'standAloneCalibrate'})
		self.m[f"{self.name}_bb"] = Submodule(**{'f': 'balancedBudget'})
	
	def readTree(self, tree):
		robust.robust_merge_dbs(self.s.db, tree.db, priority='second')
		self.ns.update(tree.ns)
		[self.readTree_i(t) for t in tree.trees.values()]
		self.addCalibrationSubsets(tree)

	def readTree_i(self, t):
		self.addModule(t, **{k: v for k, v in t.__dict__.items() if k in ('name', 'ns', 'f', 'io', 'sp')})

	def addCalibrationSubsets(self, tree):
		self.ns.update({k: k + '_' + self.name for k in ['endo_mu']})
		self.s.db[self.n('endo_mu')] = adj.rc_pd(self.get('map'), self.get('input').rename({'n': 'nn'}))

	def _init_pD(self, m = None):
		return self.initSymbolFlat(1, name = 'pD', indices = [self.get('txE'), self.get('input').union(self.get('int')).union(self.get('output'))])
	def _init_qD(self,m=None):
		return self.initSymbolFlat(.5, name = 'qD', indices = [self.get('txE'), self.get('input').union(self.get('int')).union(self.get('output'))])
	def _init_mu(self,m=None):
		return self.initSymbolFlat(1, name = 'mu', indices = self.get('map'))
	def _init_sigma(self, m=None):
		return self.initSymbolFlat(0.5, name = 'sigma', indices = self.get('kninp'))
	def _init_qnorm_inp(self,m=None):
		return self.initSymbolFlat(0, name = 'qnorm_inp', indices = [self.get('txE'), self.get('kninp')], **{'type': 'parameter'})
	def _init_qiv_inp(self,m=None):
		return self.initSymbolFlat(1, name = 'qiv_inp', indices = [self.get('txE'), self.get('spinp')])
	def _init_tauS(self,m=None):
		return self.initSymbolFlat(0, name = 'tauS', indices = [self.get('txE'), self.get('labor')])
	def _init_tauD(self, m = None):
		return self.initSymbolFlat(1, name = 'tauD', indices = [self.get('txE'), self.get('input')])
	def _init_tauD0(self, m = None):
		return self.initSymbolFlat(0.01, name = 'tauD0', indices = [self.get('txE'), self.get('input')])
	def _init_tauG_calib(self, m=None):
		return pyDatabases.gpy(1, **{'name': 'tauG_calib'})
	def _init_TotalTax(self,m=None):
		return self.initSymbolFlat(0.1, name = 'TotalTax', indices = [self.get('txE'), self.get('d_TotalTax')])
	def _init_p(self,m=None):
		return self.initSymbolFlat(1, name = 'p', indices = [self.get('txE'), self.get('input_n')])
	def _init_jTerm(self, m= None):
		return self.initSymbolFlat(0, name = 'jTerm', indices = self.get('s'))

	def args(self, state):
		return {self.name+'_Blocks': '\n'.join([getattr(gamsGovernment, module.f)(name, self.name) for name,module in self.m.items()])}

	def blocks(self, state):
		if state == 'B_standAlone':
			return OrdSet([f"B_{name}" for name in self.m])-OrdSet([f"B_{self.name}_bb",f"B_{self.name}_CSA"])
		elif state == 'B':
			return OrdSet([f"B_{name}" for name in self.m])-OrdSet([f"B_{self.name}_CSA"])
		elif state == 'C_standAlone':
			return OrdSet([f"B_{name}" for name in self.m])-OrdSet([f"B_{self.name}_bb"])
		if state == 'C':
			return OrdSet([f"B_{name}" for name in self.m])

	def g_endo(self, state):
		if state == 'B_standAlone':
			return OrdSet([f"G_{self.name}_endo_always", f"G_{self.name}_CSA_exo"])
		elif state == 'C_standAlone':
			return OrdSet([f"G_{self.name}_endo_always", f"G_{self.name}_CSA_endo"])
		elif state == 'B':
			return OrdSet([f"G_{self.name}_endo_always", f"G_{self.name}_CSA_exo",f"G_{self.name}_balanceBudget_tx0",f"G_{self.name}_balanceBudget_t0"])
		elif state == 'C':
			return OrdSet([f"G_{self.name}_endo_always", f"G_{self.name}_CSA_endo",f"G_{self.name}_balanceBudget_tx0",f"G_{self.name}_jTerm"])

	def g_exo(self,state):
		if state == 'B_standAlone':
			return OrdSet([f"G_{self.name}_exo_always", f"G_{self.name}_CSA_endo"])
		elif state == 'C_standAlone':
			return OrdSet([f"G_{self.name}_exo_always", f"G_{self.name}_CSA_exo"])
		elif state == 'B':
			return OrdSet([f"G_{self.name}_exo_always", f"G_{self.name}_CSA_endo",f"G_{self.name}_jTerm"])
		elif state == 'C':
			return OrdSet([f"G_{self.name}_exo_always", f"G_{self.name}_CSA_exo",f"G_{self.name}_jTerm",f"G_{self.name}_balanceBudget_t0"])

	def _groups(self, m=None):
		return [gmsPy.Group(f"G_{self.name}_exo_always",
			v = [('sigma', self.g('kninp')), 
				 ('mu', ('and', [self.g('map'), ('not', self.g('endo_mu'))])), 
				 ('tauD0', self.g('input')), 
				 ('TotalTax', ('and', [self.g('d_TotalTax'), ('not', self.g('s'))])),
				 ('qD', self.g('output')),
				 ('p', self.g('input_n'))
				 ]),
				gmsPy.Group(f"G_{self.name}_endo_always",
			v = [('pD', ('or', [self.g('int'), self.g('input'), self.g('output')])),
				 ('qD', ('and', [self.g('input'), self.g('tx0E')])),
				 ('qD', self.g('int')),
				 ('qiv_inp', self.g('spinp')),
				 ('TotalTax', ('and', [self.g('s'), self.g('tx0E')]))
				]),
				gmsPy.Group(f"G_{self.name}_CSA_exo",
			v = [('TotalTax', ('and', [self.g('s'), self.g('t0')])),
				 ('qD', ('and', [self.g('input'), self.g('t0')]))]),
				gmsPy.Group(f"G_{self.name}_CSA_endo",
			v = [('mu', self.g('endo_mu')),
				 ('tauG_calib', None),
				 ('tauD', self.g('input'))
				]),
				gmsPy.Group(f"G_{self.name}_balanceBudget_tx0",
					v=[('tauS', ('and', [self.g('labor'),self.g('tx0E')]))]),
				gmsPy.Group(f"G_{self.name}_balanceBudget_t0",
					v=[('tauS', ('and', [self.g('labor'),self.g('t0')]))]),
				gmsPy.Group(f"G_{self.name}_jTerm",
					v=[('jTerm', self.g('s'))])
				]

