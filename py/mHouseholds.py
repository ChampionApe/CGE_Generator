from gmsPython import gmsPy, GmsPythonSimple, Submodule
import pyDatabases, pandas as pd
from pyDatabases import OrdSet, noneInit
from pyDatabases.gpyDB_wheels import adj, robust
import gamsHouseholds

class staticConsumer(GmsPythonSimple):
	def __init__(self, f=None, tree=None, ns=None, s=None, glob=None, s_kwargs = None, g_kwargs = None, kwargs = None):
		""" Initialize from a pickle file 'f' or nesting tree 'tree'. """
		super().__init__(checkStates = ['B','C'], name=tree.name if tree else None, f=f, s=s, glob=glob, ns=ns, s_kwargs = s_kwargs, g_kwargs=g_kwargs)
		if f is None:
			self.readTree(tree)
			self.adjust(**noneInit(kwargs,{}))

	def adjust(self, L2C = None, f = None):
		""" add mapping from labor component L to top of consumption nest C. """
		self.ns.update({k: f"{k}_{self.name}" for k in ('labor','L2C','s','output_n','input_n')})
		self.s.db[self.n('L2C')] = pyDatabases.noneInit(L2C, pd.MultiIndex.from_tuples([], names = ['s','n','nn']))
		self.s.db[self.n('labor')] = L2C.droplevel('nn').unique()
		self.s.db[self.n('output_n')] = self.get('labor').levels[-1]
		self.s.db[self.n('input_n')]  = self.get('input').levels[-1]
		self.s.db[self.n('s')] = self.get('output').levels[0]
		self.s.db['n'] = self.get('n').union(self.get('output_n'))
		self.m[f"{self.name}_labor"] = Submodule(**{'f': pyDatabases.noneInit(f, 'IsoFrisch')})
		self.m[f"{self.name}_pw"] = Submodule(**{'f': 'priceWedgeStatic'})

	def readTree(self,tree):
		robust.robust_merge_dbs(self.s.db,tree.db,priority='second')
		self.ns.update(tree.ns)
		[self.readTree_i(t) for t in tree.trees.values()];
		self.addCalibrationSubsets(tree)

	def readTree_i(self,t):
		self.addModule(t,**{k:v for k,v in t.__dict__.items() if k in ('name','ns','f','io','sp')})

	def addCalibrationSubsets(self,tree):
		self.ns.update({k: k+'_'+self.name for k in ['endo_mu']})
		self.s.db[self.n('endo_mu')] = adj.rc_pd(self.get('map'), self.get('input').rename({'n':'nn'}))

	@property
	def _symbols(self):
		""" which symbols are initialized when calling self.initDB """
		return ['pS','qS','pD','qD','mu','eta','sigma','qnorm_inp','qnorm_out','qiv_out','qiv_inp','crra','frisch','Lscale','tauLump','tauS','tauD','TotalTax','p','jTerm']

	def _init_pS(self, m = None):
		return self.initSymbolFlat(1, name = 'pS', indices = [self.get('txE'), self.get('labor')])
	def _init_qS(self, m = None):
		return self.initSymbolFlat(1, name = 'qS', indices = [self.get('txE'), self.get('labor')])
	def _init_pD(self, m = None):
		return self.initSymbolFlat(1, name = 'pD', indices = [self.get('txE'), self.get('input').union(self.get('int')).union(self.get('output'))])
	def _init_qD(self, m = None):
		return self.initSymbolFlat(.5, name= 'qD', indices = [self.get('t'),   self.get('input').union(self.get('int')).union(self.get('output'))])
	def _init_mu(self, m = None):
		return self.initSymbolFlat(1, name = 'mu', indices = self.get('map',m=m))
	def _init_eta(self, m = None):
		return self.initSymbolFlat(.5, name= 'eta',indices = self.get('knout',m=m))
	def _init_sigma(self, m = None):
		return self.initSymbolFlat(.5, name= 'sigma', indices = self.get('kninp',m=m))
	def _init_qnorm_out(self, m = None):
		return self.initSymbolFlat(.5, name= 'qnorm_out',indices = [self.get('txE'),self.get('knout',m=m)], **{'type':'parameter'})
	def _init_qnorm_inp(self, m = None):
		return self.initSymbolFlat(.5, name= 'qnorm_inp',indices =[self.get('txE'),self.get('kninp',m=m)], **{'type':'parameter'})
	def _init_qiv_out(self, m = None):
		return self.initSymbolFlat(1, name = 'qiv_out', indices = [self.get('txE'),self.get('spout',m=m)])
	def _init_qiv_inp(self, m = None):
		return self.initSymbolFlat(1, name = 'qiv_inp', indices = [self.get('txE'),self.get('spinp',m=m)])
	def _init_crra(self, m = None):
		return self.initSymbolFlat(2, name = 'crra', indices = self.get('output'))
	def _init_frisch(self, m = None):
		return self.initSymbolFlat(0, name = 'frisch', indices = self.get('labor'))
	def _init_Lscale(self, m = None):
		return self.initSymbolFlat(1, name = 'Lscale', indices = self.get('labor'))
	def _init_tauLump(self, m=None):
		return self.initSymbolFlat(0, name = 'tauLump', indices = [self.get('txE'), self.get('s')])
	def _init_tauS(self, m= None):
		return self.initSymbolFlat(0, name = 'tauS', indices = [self.get('txE'), self.get('labor')])
	def _init_tauD(self, m=None):
		return self.initSymbolFlat(0, name = 'tauD', indices = [self.get('txE'), self.get('input')])
	def _init_TotalTax(self, m = None):
		return self.initSymbolFlat(0, name = 'TotalTax', indices = [self.get('txE'), self.get('s')])
	def _init_jTerm(self, m= None):
		return self.initSymbolFlat(0, name = 'jTerm', indices = self.get('s'))
	def _init_p(self, m = None):
		return self.initSymbolFlat(1, name = 'p', indices = [self.get('txE'), self.get('output_n').union(self.get('input_n'))])

	def args(self, state):
		return {self.name+'_Blocks': '\n'.join([getattr(gamsHouseholds, module.f)(name, self.name) for name,module in self.m.items()])}

	def blocks(self, state):
		return OrdSet([f"B_{name}" for name in self.m])

	def g_endo(self, state):
		if state == 'B':
			return OrdSet([f"G_{self.name}_endo_always", f"G_{self.name}_exo_in_calib"])
		elif state == 'C':
			return OrdSet([f"G_{self.name}_endo_always", f"G_{self.name}_endo_in_calib"])

	def g_exo(self, state):
		if state == 'B':
			return OrdSet([f"G_{self.name}_exo_always", f"G_{self.name}_endo_in_calib"])
		elif state == 'C':
			return OrdSet([f"G_{self.name}_exo_always", f"G_{self.name}_exo_in_calib"])

	def _groups(self,m=None):
		return [gmsPy.Group(f"G_{self.name}_exo_always", 
			v =[('sigma', self.g('kninp')),
				('eta', self.g('knout')),
				('mu', ('and', [self.g('map'), ('not', self.g('endo_mu'))])),
				('frisch', self.g('labor')),
				('crra', self.g('output')), 
				('tauD', self.g('input')), ('tauS', self.g('labor')), ('tauLump', ('and', [self.g('s'), self.g('tx0E')])), 
				('p', ('or', [self.g('output_n'), self.g('input_n')])),
				]),
				gmsPy.Group(f"G_{self.name}_endo_always",
			v =[('pD', ('or', [self.g('int'), self.g('input')])),
				('pD', ('and', [self.g('output'), self.g('tx0E')])),
				('qS', ('and',[self.g('labor'), self.g('tx0E')])),
				('qD', ('and',[self.g('input'), self.g('tx0E')])),
				('qD', ('or', [self.g('int'), self.g('output')])),
				('qiv_inp', self.g('spinp')),
				('qiv_out', self.g('spout')),
				('pS', self.g('labor')),
				('TotalTax', ('and', [self.g('s'), self.g('tx0E')]))
				]
			),
				gmsPy.Group(f"G_{self.name}_exo_in_calib", 
			v =[('qD', ('and', [self.g('input'), self.g('t0')])),
				('qS', ('and', [self.g('labor'), self.g('t0')])),
				('pD', ('and', [self.g('output'),self.g('t0')])),
				('TotalTax', ('and', [self.g('s'), self.g('t0')]))]),
				gmsPy.Group(f"G_{self.name}_endo_in_calib",
			v =[('mu', self.g('endo_mu')),
				('Lscale', self.g('labor')),
				('tauLump', ('and', [self.g('s'), self.g('t0')])),
				('jTerm', self.g('s'))
				])
			]



class SimpleRamsey(GmsPythonSimple):
	def __init__(self, f=None, tree=None, ns=None, s=None, glob=None, s_kwargs = None, g_kwargs = None, kwargs = None):
		""" Initialize from a pickle file 'f' or nesting tree 'tree'. """
		super().__init__(checkStates = ['B','C'],name=tree.name if tree else None, f=f, s=s, glob=glob, ns=ns, s_kwargs = s_kwargs, g_kwargs=g_kwargs)
		if f is None:
			self.readTree(tree)
			self.adjust(**kwargs)

	def adjust(self, L2C = None, f = None):
		""" add mapping from labor component L to top of consumption nest C. """
		self.ns.update({k: f"{k}_{self.name}" for k in ('labor','L2C','s','output_n','input_n')})
		self.s.db[self.n('L2C')] = pyDatabases.noneInit(L2C, pd.MultiIndex.from_tuples([], names = ['s','n','nn']))
		self.s.db[self.n('labor')] = L2C.droplevel('nn').unique()
		self.s.db[self.n('output_n')] = self.get('labor').levels[-1]
		self.s.db[self.n('input_n')]  = self.get('input').levels[-1]
		self.s.db[self.n('s')] = self.get('output').levels[0]
		self.s.db['n'] = self.get('n').union(self.get('output_n'))
		self.m[f"{self.name}_labor"] = Submodule(**{'f': pyDatabases.noneInit(f, 'IsoFrisch')})
		self.m[f"{self.name}_dynamic"] = Submodule(**{'f': 'simpleDynamic'})
		self.m[f"{self.name}_pw"] = Submodule(**{'f': 'priceWedge'})

	def readTree(self,tree):
		robust.robust_merge_dbs(self.s.db,tree.db,priority='second')
		self.ns.update(tree.ns)
		[self.readTree_i(t) for t in tree.trees.values()];
		self.addCalibrationSubsets(tree)

	def readTree_i(self,t):
		self.addModule(t,**{k:v for k,v in t.__dict__.items() if k in ('name','ns','f','io','sp')})

	def addCalibrationSubsets(self,tree):
		self.ns.update({k: k+'_'+self.name for k in ['endo_mu']})
		self.s.db[self.n('endo_mu')] = adj.rc_pd(self.get('map'), self.get('input').rename({'n':'nn'}))

	@property
	def _symbols(self):
		""" which symbols are initialized when calling self.initDB """
		return ['pS','qS','pD','qD','mu','eta','sigma','qnorm_inp','qnorm_out','qiv_out','qiv_inp','Rrate','iRate','crra','frisch','Lscale','disc','vAssets','h_tvc','tauLump','tauS','tauD','TotalTax','sp','p']

	def _init_pS(self, m = None):
		return self.initSymbolFlat(1, name = 'pS', indices = [self.get('txE'), self.get('labor')])
	def _init_qS(self, m = None):
		return self.initSymbolFlat(1, name = 'qS', indices = [self.get('txE'), self.get('labor')])
	def _init_pD(self, m = None):
		return self.initSymbolFlat(1, name = 'pD', indices = [self.get('txE'), self.get('input').union(self.get('int')).union(self.get('output'))])
	def _init_qD(self, m = None):
		return self.initSymbolFlat(.5, name= 'qD', indices = [self.get('t'),   self.get('input').union(self.get('int')).union(self.get('output'))])
	def _init_mu(self, m = None):
		return self.initSymbolFlat(1, name = 'mu', indices = self.get('map',m=m))
	def _init_eta(self, m = None):
		return self.initSymbolFlat(.5, name= 'eta',indices = self.get('knout',m=m))
	def _init_sigma(self, m = None):
		return self.initSymbolFlat(.5, name= 'sigma', indices = self.get('kninp',m=m))
	def _init_qnorm_out(self, m = None):
		return self.initSymbolFlat(.5, name= 'qnorm_out',indices = [self.get('txE'),self.get('knout',m=m)], **{'type':'parameter'})
	def _init_qnorm_inp(self, m = None):
		return self.initSymbolFlat(.5, name= 'qnorm_inp',indices =[self.get('txE'),self.get('kninp',m=m)], **{'type':'parameter'})
	def _init_qiv_out(self, m = None):
		return self.initSymbolFlat(1, name = 'qiv_out', indices = [self.get('txE'),self.get('spout',m=m)])
	def _init_qiv_inp(self, m = None):
		return self.initSymbolFlat(1, name = 'qiv_inp', indices = [self.get('txE'),self.get('spinp',m=m)])
	def _init_Rrate(self, m = None):
		return self.initSymbolFlat(self.get('R_LR'), name= 'Rrate',indices = self.get('t'))
	def _init_iRate(self, m = None):
		return self.initSymbolFlat(self.get('R_LR')*(1+self.get('infl_LR')), name = 'iRate', indices = self.get('t'))
	def _init_crra(self, m = None):
		return self.initSymbolFlat(2, name = 'crra', indices = self.get('output'))
	def _init_frisch(self, m = None):
		return self.initSymbolFlat(0, name = 'frisch', indices = self.get('labor'))
	def _init_Lscale(self, m = None):
		return self.initSymbolFlat(1, name = 'Lscale', indices = self.get('labor'))
	def _init_disc(self, m = None):
		return self.initSymbolFlat(1/self.get('R_LR'), name = 'disc', indices = self.get('s'))
	def _init_vAssets(self,m=None):
		return self.initSymbolFlat(1, name = 'vAssets', indices = pd.MultiIndex.from_product([self.get('t'), self.get('s'), pd.Index(['total'], name = 'a')]))
	def _init_h_tvc(self,m=None):
		return self.initSymbolFlat(0, name = 'h_tvc', indices = self.get('s'))
	def _init_tauLump(self, m=None):
		return self.initSymbolFlat(0, name = 'tauLump', indices = [self.get('txE'), self.get('s')])
	def _init_tauS(self, m= None):
		return self.initSymbolFlat(0, name = 'tauS', indices = [self.get('txE'), self.get('labor')])
	def _init_tauD(self, m=None):
		return self.initSymbolFlat(0, name = 'tauD', indices = [self.get('txE'), self.get('input')])
	def _init_TotalTax(self, m = None):
		return self.initSymbolFlat(0, name = 'TotalTax', indices = [self.get('txE'), self.get('s')])
	def _init_sp(self, m = None):
		return self.initSymbolFlat(0, name = 'sp', indices = [self.get('txE'), self.get('s')])
	def _init_p(self, m = None):
		return self.initSymbolFlat(1, name = 'p', indices = [self.get('txE'), self.get('output_n').union(self.get('input_n'))])

	def args(self, state):
		return {self.name+'_Blocks': '\n'.join([getattr(gamsHouseholds, module.f)(name, self.name) for name,module in self.m.items()])}

	def blocks(self, state):
		return OrdSet([f"B_{name}" for name in self.m])

	def g_endo(self, state):
		if state == 'B':
			return OrdSet([f"G_{self.name}_endo_always", f"G_{self.name}_exo_in_calib"])
		elif state == 'C':
			return OrdSet([f"G_{self.name}_endo_always", f"G_{self.name}_endo_in_calib"])

	def g_exo(self, state):
		if state == 'B':
			return OrdSet([f"G_{self.name}_exo_always", f"G_{self.name}_endo_in_calib"])
		elif state == 'C':
			return OrdSet([f"G_{self.name}_exo_always", f"G_{self.name}_exo_in_calib"])

	def _groups(self,m=None):
		return [gmsPy.Group(f"G_{self.name}_exo_always", 
			v =[('sigma', self.g('kninp')),
				('eta', self.g('knout')),
				('crra', self.g('output')),
				('h_tvc', self.g('s')),
				('mu', ('and', [self.g('map'), ('not', self.g('endo_mu'))])),
				('Rrate', None), ('iRate', None), ('frisch', self.g('labor')), 
				('tauD', self.g('input')), ('tauS', self.g('labor')), ('tauLump', ('and', [self.g('s'), self.g('tx0E')])), 
				('vAssets', ('and', [self.g('s'), self.g('t0')])),
				('p', ('or', [self.g('output_n'), self.g('input_n')])),
				]),
				gmsPy.Group(f"G_{self.name}_endo_always",
			v =[('pD', ('or', [self.g('int'), self.g('input')])),
				('pD', ('and', [self.g('output'), self.g('tx0E')])),
				('qS', ('and',[self.g('labor'), self.g('tx0E')])),
				('qD', ('and',[self.g('input'), self.g('tx0E')])),
				('qD', ('or', [self.g('int'), self.g('output')])),
				('qiv_inp', self.g('spinp')),
				('qiv_out', self.g('spout')),
				('sp', self.g('s')),
				('pS', self.g('labor')),
				('TotalTax', ('and', [self.g('s'), self.g('tx0E')])),
				('vAssets', ('and', [self.g('s'), self.g('tx0')]))]
			),
				gmsPy.Group(f"G_{self.name}_exo_in_calib", 
			v =[('qD', ('and', [self.g('input'), self.g('t0')])),
				('qS', ('and', [self.g('labor'), self.g('t0')])),
				('pD', ('and', [self.g('output'),self.g('t0')])),
				('TotalTax', ('and', [self.g('s'), self.g('t0')]))]),
				gmsPy.Group(f"G_{self.name}_endo_in_calib",
			v =[('mu', self.g('endo_mu')),
				('Lscale', self.g('labor')),
				('tauLump', ('and', [self.g('s'), self.g('t0')])),
				('disc', self.g('s'))
				])
			]
