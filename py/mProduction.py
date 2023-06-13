from gmsPython import gmsPy, GmsPythonSimple, Submodule
import pyDatabases, pandas as pd
from pyDatabases import gpy, OrdSet, adjMultiIndex, adjMultiIndexDB
from pyDatabases.gpyDB_wheels import adj, robust
import gamsProduction

class Production(GmsPythonSimple):
	def __init__(self, f=None, tree=None, ns=None, s=None, glob=None, s_kwargs = None, g_kwargs = None, dur_kwargs = None):
		""" Initialize from a pickle file 'f' or nesting tree 'tree'. """
		super().__init__(checkStates = ['B','C'], **dict(name=tree.name if tree else None, f=f, s=s, glob=glob, ns=ns, s_kwargs = s_kwargs, g_kwargs=g_kwargs))
		if f is None:
			self.readTree(tree)
			self.addDurables(**pyDatabases.noneInit(dur_kwargs, {}))
			self.addPriceWedge()

	@property
	def _symbols(self):
		""" which symbols are initialized when calling self.initDB """
		return ['pS','qS','pD','qD','mu','eta','sigma','qnorm_inp','qnorm_out','qiv_out','qiv_inp','Rrate','rDepr','icpar','K_tvc','ic','p','markup','tauS','tauD','outShare','TotalTax','tauLump']

	def addDurables(self, dur = None, f = None, dur2inv = None):
		self.ns.update({k: f"{k}_{self.name}" for k in ('dur','inv')})
		self.s.db[self.n('dur')] = pyDatabases.noneInit(dur, pd.MultiIndex.from_product([self.get('output').levels[0], []], names = ['s','n']))
		self.s.db[self.n('dur2inv')] = pd.MultiIndex.from_frame(self.get('dur').to_frame(index=False).assign(nn=lambda x: 'I_'+x.n)) if dur2inv is None else dur2inv
		self.s.db[self.n('inv')] = self.get('dur2inv').droplevel(self.ns['n']).unique().rename({self.ns['nn']:self.ns['n']})
		self.s.db['n'] = self.get('n').union(self.get('inv').levels[-1])
		self.s.db[self.n('input')] = self.get('input').difference(self.get('dur')).union(self.get('inv'))
		self.s.db[self.n('input_n')] = self.get('input').levels[-1]
		self.m[f"{self.name}_IC"] = Submodule(**{'f': pyDatabases.noneInit(f, 'sqrAdjCosts')})

	def addPriceWedge(self,f=None):
		self.ns.update({k: f"{k}_{self.name}" for k in ['s','output_n','input_n']})
		self.s.db[self.n('output_n')] = self.get('output').levels[-1]
		self.s.db[self.n('input_n')]  = self.get('input').levels[-1]
		self.s.db[self.n('s')] = self.get('output').levels[0]
		self.m[f"{self.name}_pWedge"] = Submodule(**{'f': pyDatabases.noneInit(f,'priceWedge')})

	def readTree(self,tree):
		robust.robust_merge_dbs(self.s.db,tree.db,priority='second')
		self.ns.update(tree.ns)
		[self.readTree_i(t) for t in tree.trees.values()];
		self.addCalibrationSubsets(tree)

	def readTree_i(self,t):
		self.addModule(t,**{k:v for k,v in t.__dict__.items() if k in ('name','ns','f','io','sp')})

	def addCalibrationSubsets(self,tree):
		self.ns.update({k: k+'_'+self.name for k in ('exomu','endo_qS','endo_qD','endo_pS')})
		exomu_inp, exomu_out = self.getExomuFromTree(tree)
		self.s.db[self.ns['exomu']] = exomu_inp.union(exomu_out)
		self.s.db[self.ns['endo_qD']] = exomu_inp.droplevel('n').rename(['s','n']).union(adj.rc_pd(exomu_out.droplevel('nn'),('not',self.get('output'))))
		self.s.db[self.ns['endo_qS']] = adj.rc_pd(exomu_out.droplevel('nn'),self.get('output'))
		self.s.db[self.ns['endo_pS']] = self.uniqueFromMap(self.get('output'),gb=['s'])

	def TroubleNodes(self,map_spinp, map_spout, output=None):
		""" Identify nodes that are branches in input tree and output tree"""
		return adj.rc_pd(map_spinp.droplevel('n').rename(['s','n']), c = adj.rc_pd(map_spout.droplevel('nn'), c = None if output is None else ('not', output)))

	def uniqueFromMap(self,map_,gb=('s','n')):
		""" MultiIndex-like groupby statement with function 'first' """
		return pd.MultiIndex.from_frame(map_.to_frame(index=False).groupby([s for s in gb]).first().reset_index()).reorder_levels(map_.names)

	def getCleanExoMu(self,map_spinp, map_spout, trouble):
		""" return elements to be added to exomu_inp, exomu_out"""
		return self.uniqueFromMap(adj.rc_pd(map_spinp, c= ('not', trouble.rename(['s','nn'])))), self.uniqueFromMap(adj.rc_pd(map_spout, c= ('not', trouble)),gb=('s','nn'))

	def getExomuFromTree(self,tree,maxiter=10):
		map_spinp = self.get('map_spinp').copy()
		map_spout = self.get('map_spout').copy()
		trouble = self.TroubleNodes(map_spinp, map_spout,output=self.get('output'))
		exomu_inp, exomu_out = self.getCleanExoMu(map_spinp, map_spout, trouble)
		i = 0
		while not trouble.empty:
			map_spinp = adj.rc_pd(map_spinp, ('not', exomu_inp.droplevel('nn')))
			map_spout = adj.rc_pd(map_spout, ('not', exomu_out.droplevel('n')))
			trouble = self.TroubleNodes(map_spinp, map_spout)
			exomu_inp_i, exomu_out_i = self.getCleanExoMu(map_spinp,map_spout,trouble)
			exomu_inp, exomu_out = exomu_inp.union(exomu_inp_i), exomu_out.union(exomu_out_i)
			i += 1
			if i == maxiter:
				print("Algorithm for exomu sets failed; increase maxiter or consider nesting for loops.")
				break
		return exomu_inp, exomu_out

	def _init_pS(self, m = None):
		return self.initSymbolFlat(1, name = 'pS', indices = [self.get('txE'), self.get('output',m=m)])
	def _init_qS(self, m = None):
		return self.initSymbolFlat(1, name = 'qS', indices = [self.get('txE'), self.get('output',m=m)])
	def _init_pD(self, m = None):
		return self.initSymbolFlat(1, name = 'pD', indices = [self.get('txE'), self.get('int',m=m).union(self.get('input',m=m)).union(self.get('dur',m=m))])
	def _init_qD(self, m = None):
		return self.initSymbolFlat(.5, name= 'qD', indices = [self.get('t'),   self.get('int',m=m).union(self.get('input',m=m)).union(self.get('dur',m=m))])
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
	def _init_rDepr(self, m=None):
		return self.initSymbolFlat(.075, name = 'rDepr', indices = [self.get('t'), self.get('dur',m=m)])
	def _init_icpar(self, m=None):
		return self.initSymbolFlat(1, name= 'icpar', indices = self.get('dur',m=m))
	def _init_K_tvc(self, m=None):
		return self.initSymbolFlat(0, name = 'K_tvc', indices = self.get('dur',m=m))
	def _init_ic(self, m=None):
		return self.initSymbolFlat(0, name = 'ic', indices = [self.get('txE'), self.get('s')])
	def _init_p(self, m=None):
		return self.initSymbolFlat(1, name = 'p', indices = [self.get('txE'), self.get('output_n',m=m).union(self.get('input_n',m=m))])
	def _init_markup(self,m=None):
		return self.initSymbolFlat(.5, name = 'markup', indices = self.get('s',m=m))
	def _init_tauS(self, m=None):
		return self.initSymbolFlat(0, name = 'tauS', indices = [self.get('txE'), self.get('output',m=m)])
	def _init_tauD(self, m=None):
		return self.initSymbolFlat(0, name = 'tauD', indices = [self.get('txE'), self.get('input',m=m)])
	def _init_outShare(self,m=None):
		return self.initSymbolFlat(1, name = 'outShare', indices = [self.get('txE'), self.get('output',m=m)])
	def _init_TotalTax(self,m=None):
		return self.initSymbolFlat(0, name = 'TotalTax', indices = [self.get('txE'), self.get('s')])
	def _init_tauLump(self, m=None):
		return self.initSymbolFlat(0, name = 'tauLump', indices = [self.get('txE'), self.get('s')])

	def initDurables(self):
		robust.robust_merge_dbs(self.s.db,
		{self.n('rDepr'): gpy(pd.Series(0.075, index = adjMultiIndexDB.mergeDomains([self.get('t'),self.get('dur')],self.s.db), name = self.n('rDepr'))),
		 self.n('icpar'): gpy(pd.Series(1, index = self.get('dur'), name= self.n('icpar'))),
		 self.n('K_tvc') : gpy(pd.Series(0, index = self.get('dur'), name=self.n('K_tvc')))},
		priority='first')
		self.adjustToSteadyState()

	def adjustToSteadyState(self,m=None):
		robust.robust_merge_dbs(self.s.db,
		{self.n('qD'): gpy(adjMultiIndex.applyMult((self.get('g_LR')+self.get('rDepr',m=m))*adj.rc_pd(self.get('qD'), self.get('dur',m=m)), self.get('dur2inv',m=m)).droplevel('n').rename_axis(index={'nn':'n'}), **{'name': self.n('qD')}),
		 self.n('pD'): gpy(adjMultiIndex.applyMult(adj.rc_pd(self.get('pD'), self.get('dur',m=m))/(self.get('Rrate')/(1+self.get('infl_LR'))-(1-self.get('rDepr',m=m))), self.get('dur2inv',m=m)).droplevel('n').rename_axis(index={'nn':'n'}), **{'name':self.n('pD')})}
		,priority='second')

	def args(self, state):
		return {self.name+'_Blocks': '\n'.join([getattr(gamsProduction, module.f)(name, self.name) for name,module in self.m.items()])}

	def blocks(self, state):
		return OrdSet([f"B_{name}" for name in self.m])

	def g_endo(self, state):
		if state == 'B':
			return OrdSet([f"G_{self.name}_endo_always", f"G_{self.name}_exo_in_calib", f"G_{self.name}_endo_dur"])
		elif state == 'C':
			return OrdSet([f"G_{self.name}_endo_always", f"G_{self.name}_endo_in_calib",f"G_{self.name}_endo_dur"])

	def g_exo(self, state):
		if state == 'B':
			return OrdSet([f"G_{self.name}_exo_always", f"G_{self.name}_endo_in_calib",f"G_{self.name}_exo_dur"])
		elif state == 'C':
			return OrdSet([f"G_{self.name}_exo_always", f"G_{self.name}_exo_in_calib", f"G_{self.name}_exo_dur"])

	def _groups(self,m=None):
		return [gmsPy.Group(f"G_{self.name}_exo_always", 
		v = 	[('qS', self.g('output')), 
				 ('sigma', self.g('kninp')), 
				 ('eta', self.g('knout')), 
				 ('mu', self.g('exomu')),
				 ('tauS', self.g('output')),
				 ('tauD', self.g('input')),
				 ('tauLump', ('and', [self.g('s'), self.g('tx0E')])),
				 ('p', self.g('input_n'))],
		neg_v = [('qS', ('and', [self.g('endo_qS'),self.g('t0')])),
				 ('p', self.g('output_n'))]
				),
				gmsPy.Group(f"G_{self.name}_endo_always",
		v = 	[('pD', self.g('int')),
				 ('pD', self.g('input')),
				 ('pS', self.g('output')),
				 ('p' , ('and', [self.g('output_n'), self.g('tx0')])),
				 ('qD', ('and', [('or', [self.g('int'), self.g('input')]), self.g('tx0')])),
				 ('qD', ('and', [self.g('endo_qD'), self.g('t0')])),
				 ('qiv_inp', self.g('spinp')),
				 ('qiv_out', self.g('spout')),
				 ('outShare', self.g('output')),
				 ('TotalTax', ('and', [self.g('s'), self.g('tx0E')]))]),
				gmsPy.Group(f"G_{self.name}_exo_in_calib",
		v = 	[('qD', ('and', [('or', [self.g('int'), self.g('input')]), self.g('t0')])),
				 ('p' , ('and', [self.g('output_n'), self.g('t0')])),
				 ('TotalTax', ('and', [self.g('s'), self.g('t0')]))],
		neg_v = [('qD', ('and', [self.g('endo_qD'), self.g('t0')]))]),
				gmsPy.Group(f"G_{self.name}_endo_in_calib",
		v = 	[('mu', ('and', [self.g('map'), ('not', self.g('exomu'))])),
				 ('qS', ('and', [self.g('endo_qS'), self.g('t0')])),
				 ('tauLump', ('and', [self.g('s'), self.g('t0')])),
				 ('markup', self.g('s'))]),
				gmsPy.Group(f"G_{self.name}_exo_dur", 
		v = [('Rrate', None),
			 ('rDepr', self.g('dur')),
			 ('icpar', self.g('dur')),
			 ('K_tvc' , self.g('dur')),
			 ('qD', ('and', [self.g('dur'), self.g('t0')]))
			 ]),
				gmsPy.Group(f"G_{self.name}_endo_dur",
		v = [('qD', ('and', [self.g('dur'), self.g('tx0')])),
			 ('pD', ('and', [self.g('dur'), self.g('txE')])),
			 ('ic', ('and', [self.g('s'), self.g('txE')]))
		]
		)]


class Production_ExoMu(Production):
	def __init__(self, f=None, tree=None, ns=None, s=None, glob=None, s_kwargs = None, g_kwargs = None, dur_kwargs = None):
		super().__init__(f=f, tree=tree, ns = ns, s = s, glob=glob, s_kwargs = s_kwargs, g_kwargs = g_kwargs, dur_kwargs=dur_kwargs)

	def addDurables(self, dur = None, f = None, dur2inv = None):
		self.ns.update({k: f"{k}_{self.name}" for k in ('dur','inv')})
		self.s.db[self.n('dur')] = pyDatabases.noneInit(dur, pd.MultiIndex.from_product([self.get('output').levels[0], []], names = ['s','n']))
		self.s.db[self.n('dur2inv')] = pd.MultiIndex.from_frame(self.get('dur').to_frame(index=False).assign(nn=lambda x: 'I_'+x.n)) if dur2inv is None else dur2inv
		self.s.db[self.n('inv')] = self.get('dur2inv').droplevel(self.ns['n']).unique().rename({self.ns['nn']:self.ns['n']})
		self.s.db['n'] = self.get('n').union(self.get('inv').levels[-1])
		self.s.db[self.n('input')] = self.get('input').difference(self.get('dur')).union(self.get('inv'))
		self.s.db[self.n('input_n')] = self.get('input').levels[-1]
		self.m[f"{self.name}_IC"] = Submodule(**{'f': pyDatabases.noneInit(f, 'sqrAdjCosts')})

	def addPriceWedge(self,f=None):
		self.ns.update({k: f"{k}_{self.name}" for k in ['s','output_n','input_n']})
		self.s.db[self.n('output_n')] = self.get('output').levels[-1]
		self.s.db[self.n('input_n')]  = self.get('input').levels[-1]
		self.s.db[self.n('s')] = self.get('output').levels[0]
		self.m[f"{self.name}_pWedge"] = Submodule(**{'f': pyDatabases.noneInit(f,'priceWedge')})

	def readTree(self,tree):
		robust.robust_merge_dbs(self.s.db,tree.db,priority='second')
		self.ns.update(tree.ns)
		[self.readTree_i(t) for t in tree.trees.values()];
		self.addCalibrationSubsets(tree)

	def readTree_i(self,t):
		self.addModule(t,**{k:v for k,v in t.__dict__.items() if k in ('name','ns','f','io','sp')})

	def addCalibrationSubsets(self,tree):
		""" endo_mu is a subset of share parameters to endogenize when calibrating to IO data. 
			endo_qD is a subset of demand variables to keep endogeonus when calibrating, even though they might be a part the 'inputs' subset """
		self.ns.update({k: k+'_'+self.name for k in ('endo_mu','endo_qD')})
		endo_mu_all = adj.rc_pd(self.get('map'), self.get('input').rename(['s','nn'])) # identify all elements that can be endogenized
		spinp_Trouble =adj.rc_pd(self.get('map_spinp'), ('not', self.get('map_spinp').difference(endo_mu_all).droplevel('nn').unique())) # all nests that might be an issue
		mu_out = adj.rc_pd(self.get('map'), self.get('output')) # All potentially endogenizeable share parameters on the output side - the ones with multiple outputs:
		s_numberOut = mu_out.to_frame(index=False).groupby('s').nunique()['n']
		mout_s =s_numberOut[s_numberOut>1].index
		mu_out = adj.rc_pd(mu_out, mout_s)
		endo_mu = self.uniqueFromMap(endo_mu_all.difference(mu_out), gb = ['s','nn']) # suggest endogenous combination that does not include elements  from mu_out
		x = self.uniqueFromMap(endo_mu_all, gb = ['s','nn']) # suggest endogenous combination from all endo_mu_all
		endo_mu = endo_mu.union(adj.rc_pd(x, ('not', endo_mu.droplevel('n')))) # if there is a combination of (s,nn) in x that is missing, add it here. 
		exo_mu  = self.uniqueFromMap(spinp_Trouble, gb = ['s','n']) # suggest making this element exogenous
		exo_mu_out = self.uniqueFromMap(mu_out.intersection(endo_mu), gb ='s') # suggest NOT making this endogenous. 
		y = self.uniqueFromMap(mu_out, gb = 's') # suggest not making this endogenous either - selecting one for each
		exo_mu_out = exo_mu_out.union(adj.rc_pd(y, ('not', exo_mu_out.droplevel('nn')))) # if there is a combination of (s,n) in y that is missing, add it here.
		endo_mu_out = self.uniqueFromMap(adj.rc_pd(mu_out, ('not', exo_mu_out.droplevel('nn'))), gb = ['s','n'])
		if not len(endo_mu_out) == sum(mu_out.to_frame(index=False).groupby('s').nunique()['n']-1):
			print(f"Check that grouping of endogenous/exogenous mu parameters in {self.name}; unexpected number of parameters were endogenized")
		self.s.db[self.ns['endo_mu']] = endo_mu.union(endo_mu_out).difference(exo_mu)
		self.s.db[self.ns['endo_qD']] = exo_mu.droplevel('n').rename(['s','n'])
		
	def uniqueFromMap(self,map_,gb=('s','n')):
		""" MultiIndex-like groupby statement with function 'first' """
		return pd.MultiIndex.from_frame(map_.to_frame(index=False).groupby([s for s in gb]).first().reset_index()).reorder_levels(map_.names)

	def _groups(self,m=None):
		return [gmsPy.Group(f"G_{self.name}_exo_always", 
		v = 	[('qS', self.g('output')),
				 ('sigma', self.g('kninp')), 
				 ('eta', self.g('knout')),
				 ('mu', self.g('map')),
				 ('tauS', self.g('output')),
				 ('tauD', self.g('input')),
				 ('tauLump', ('and', [self.g('s'), self.g('tx0E')])),
				 ('p', self.g('input_n'))],
		neg_v = [('mu', self.g('endo_mu')),
				 ('p', self.g('output_n'))]
				),
				gmsPy.Group(f"G_{self.name}_endo_always",
		v = 	[('pD', self.g('int')),
				 ('pD', self.g('input')),
				 ('pS', self.g('output')),
				 ('p' , ('and', [self.g('output_n'), self.g('tx0')])),
				 ('qD', self.g('int')),
				 ('qD', ('and', [self.g('input'), self.g('tx0')])),
				 ('qD', ('and', [self.g('endo_qD'), self.g('t0')])),
				 ('qiv_inp', self.g('spinp')),
				 ('qiv_out', self.g('spout')),
				 ('outShare', self.g('output')),
				 ('TotalTax', ('and', [self.g('s'), self.g('tx0E')]))]),
				gmsPy.Group(f"G_{self.name}_exo_in_calib",
		v = 	[('qD', ('and', [self.g('input'), self.g('t0')])),
				 ('p' , ('and', [self.g('output_n'), self.g('t0')])),
				 ('TotalTax', ('and', [self.g('s'), self.g('t0')]))],
		neg_v = [('qD', ('and', [self.g('endo_qD'), self.g('t0')]))]),
				gmsPy.Group(f"G_{self.name}_endo_in_calib",
		v = 	[('mu', self.g('endo_mu')),
				 ('tauLump', ('and', [self.g('s'), self.g('t0')])),
				 ('markup', self.g('s'))]),
				gmsPy.Group(f"G_{self.name}_exo_dur", 
		v = [('Rrate', None),
			 ('rDepr', self.g('dur')),
			 ('icpar', self.g('dur')),
			 ('K_tvc' , self.g('dur')),
			 ('qD', ('and', [self.g('dur'), self.g('t0')]))
			 ]),
				gmsPy.Group(f"G_{self.name}_endo_dur",
		v = [('qD', ('and', [self.g('dur'), self.g('tx0')])),
			 ('pD', ('and', [self.g('dur'), self.g('txE')])),
			 ('ic', ('and', [self.g('s'), self.g('txE')]))
		]
		)]

class Inventory(GmsPythonSimple):
	def __init__(self, f = None, name = None, db_IO = None, itory = None, s=None, glob=None, s_kwargs = None, g_kwargs = None):
		""" Initialize from name, io data, and subset of inventory"""
		super().__init__(name=name, f=f, s=s, glob=glob, g_kwargs=g_kwargs, s_kwargs = pyDatabases.noneInit(s_kwargs, {}) | {'db': db_IO})
		if f is None:
			self.initItory(itory = itory)

	def initItory(self, itory = None):
		self.s.db['s_itory'] = pyDatabases.noneInit(itory, pd.Index(['itory'], name = 's'))
		self.s.db['d_itory'] = adj.rc_pd(self.s.db.get('qD'), self.get('s_itory')).index.droplevel('t').unique()
		self.s.db['inventoryAR'] = gpy(pd.Series(1, index = self.get('d_itory'), name = 'inventoryAR'), **{'type': 'parameter'})

	def args(self, state):
		return {f"{self.name}_Blocks": self.equationText}
	def blocks(self, state):
		return OrdSet([f"B_{self.name}"])
	def g_endo(self, state):
		return OrdSet([f"G_{self.name}_endo"])
	def g_exo(self, state):
		return OrdSet([f"G_{self.name}_exo"])
	def groups(self,m=None):
		return {g.name: g for g in [gmsPy.Group(f"G_{self.name}_exo",  v = [('qD', ('and', [self.g('t0'), self.g('d_itory')]))]), 
									gmsPy.Group(f"G_{self.name}_endo", v = [('qD', ('and', [self.g('tx0E'), self.g('d_itory')]))])]}
	@property
	def equationText(self):
		return f"""
$BLOCK B_{self.name}
	E_{self.name}[t,s,n]$(d_itory[s,n] and tx0E[t])..	qD[t,s,n] =E= inventoryAR[s,n] * qD[t-1,s,n];
$ENDBLOCK
"""