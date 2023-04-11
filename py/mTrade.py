from gmsPython import gmsPy, GmsPythonSimple, Submodule
import pyDatabases, pandas as pd
from pyDatabases import OrdSet
from pyDatabases.gpyDB_wheels import adj, robust

class armington(GmsPythonSimple):
	def __init__(self, f = None, name = None, ns = None, s = None, glob = None, s_kwargs = None, g_kwargs = None, kwargs=None):
		""" Initialize from a pickle file 'f' or nesting tree 'tree'. """
		super().__init__(checkStates = ['B','C'], name=name, f=f, s=s, glob=glob, ns=ns, s_kwargs = s_kwargs, g_kwargs=g_kwargs)
		if f is None:
			self.adjust(**kwargs)

	@property
	def _symbols(self):
		""" which symbols are initialized when calling self.initDB """
		return ['p','qD','pD','Fscale','tauD','tauLump','TotalTax','sigma']

	def adjust(self, dExport=None, dom2for = None):
		""" The mapping dExport is a local mapping for this module """
		self.ns.update({k: f"{k}_{self.name}" for k in ['s','dExport', 'nOut']})
		self.s.db[self.n('dExport')] = dExport
		if 'dom2for' not in self.s.db.symbols:
			self.s.db['dom2for'] = dom2for
		self.s.db[self.n('nOut')] = self.get('dom2for').levels[0].union(self.get('dom2for').levels[1]).rename('n')
		self.s.db[self.n('s')] = self.get('dExport').levels[0]

	def _init_p(self, m= None):
		return self.initSymbolFlat(1, name = 'p', indices = [self.get('txE'), self.get('nOut')])
	def _init_qD(self, m = None):
		return self.initSymbolFlat(1, name = 'qD', indices = [self.get('txE'), self.get('dExport')])
	def _init_pD(self, m = None):
		return self.initSymbolFlat(1, name = 'pD', indices = [self.get('txE'), self.get('dExport')])
	def _init_Fscale(self, m =None):
		return self.initSymbolFlat(1, name = 'Fscale', indices = self.get('dExport'))
	def _init_tauD(self, m = None):
		return self.initSymbolFlat(0, name = 'tauD', indices = [self.get('txE'), self.get('dExport')])
	def _init_tauLump(self, m = None):
		return self.initSymbolFlat(0, name = 'tauLump', indices = [self.get('txE'), self.get('s')])
	def _init_TotalTax(self,m=None):
		return self.initSymbolFlat(0, name = 'TotalTax', indices = [self.get('txE'), self.get('s')])
	def _init_sigma(self,m=None):
		return self.initSymbolFlat(5, name = 'sigma', indices = self.get('dExport'))

	@property
	def equationText(self):
		return f"""
$BLOCK B_{self.name}
	E_armington_{self.name}[t,s,n]$(dExport_{self.name}[s,n] and txE[t])..	qD[t,s,n]		=E= sum(nn$(dom2for[n,nn]), Fscale[s,n] * (p[t,nn]/pD[t,s,n]))**(sigma[s,n]);
	E_pwInp_{self.name}[t,s,n]$(dExport_{self.name}[s,n] and txE[t])..		pD[t,s,n]		=E= p[t,n] + tauD[t,s,n];
	E_TaxRev_{self.name}[t,s]$(s_{self.name}[s] and txE[t])..				TotalTax[t,s]	=E= tauLump[t,s]+sum(n$(dExport_{self.name}[s,n]), tauD[t,s,n]*qD[t,s,n]);
$ENDBLOCK
"""
	def args(self, state):
		return {f"{self.name}_Blocks": self.equationText}
	def blocks(self, state):
		return OrdSet([f"B_{self.name}"])
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
			v =[('p', self.g('nOut')), ('sigma', self.g('dExport')), ('tauD', self.g('dExport')), ('tauLump', ('and', [self.g('s'), self.g('tx0E')]))]),
				gmsPy.Group(f"G_{self.name}_endo_always", 
			v =[('qD', ('and', [self.g('dExport'), self.g('tx0E')])), ('TotalTax', ('and', [self.g('s'), self.g('tx0E')])), ('pD', self.g('dExport'))]),
				gmsPy.Group(f"G_{self.name}_exo_in_calib", 
			v =[('qD', ('and', [self.g('dExport'), self.g('t0')])), ('TotalTax', ('and', [self.g('s'), self.g('t0')]))]),
				gmsPy.Group(f"G_{self.name}_endo_in_calib",
			v =[('Fscale', self.g('dExport')), ('tauLump', ('and', [self.g('s'), self.g('t0')]))])
			]

