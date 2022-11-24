from gmsPython import gmsPy, GmsPython
import pyDatabases, pandas as pd
from pyDatabases.gpyDB_wheels import adj
from pyDatabases import gpy, OrdSet

class shareRAS(GmsPython):
	def __init__(self, v0, vBar, name=None, s = None, s_kwargs = None, leaveCols = None, leaveRows = None):
		super().__init__(name=pyDatabases.noneInit(name, 'someName'), s=s, s_kwargs = s_kwargs)
		self.initData(v0,vBar, leaveCols = leaveCols, leaveRows = leaveRows)

	def initData(self, v0, vBar, leaveCols = None, leaveRows = None):
		""" v0: Data pre adjustments. vBar: Manual data adjustments"""
		self.s.db['active'] = adj.rc_pd(v0, ('not', vBar)).index.remove_unused_levels()
		self.ns['i'], self.ns['j'] = self.get('active').names
		self.s.db['vD0'] = gpy(adj.rc_pd(v0, self.get('active')), **{'type':'parameter'})
		self.s.db['vD'] = self.get('vD0').rename('vD')
		self.s.db['etaRow'] = pd.Series(1, index = self.get('active'), name = 'etaRow')
		self.s.db['etaCol'] = pd.Series(1, index = self.get('active'), name = 'etaCol')
		self.s.db['deltaRow'] = gpy(((vBar.groupby(self.n('i')).sum()-adj.rc_pd(v0,vBar).groupby(self.n('i')).sum())/self.get('vD0').groupby(self.n('i')).sum()).fillna(0), **{'type': 'parameter'})
		self.s.db['deltaCol'] = gpy(((vBar.groupby(self.n('j')).sum()-adj.rc_pd(v0,vBar).groupby(self.n('j')).sum())/self.get('vD0').groupby(self.n('j')).sum()).fillna(0), **{'type': 'parameter'})
		self.s.db['rowSum'] = gpy(v0.groupby(self.n('i')).sum().add(-vBar.groupby(self.n('i')).sum(),fill_value=0), **{'type':'parameter'})
		self.s.db['colSum'] = gpy(v0.groupby(self.n('j')).sum().add(-vBar.groupby(self.n('j')).sum(),fill_value=0), **{'type':'parameter'})
		self.s.db['object'] = 0
		self.s.db[self.n('i')] = self.get('active').levels[0]
		self.s.db[self.n('j')] = self.get('active').levels[1]
		self.activeRowsandCols(leaveRows = leaveRows, leaveCols = leaveCols)

	def activeRowsandCols(self, leaveRows = None, leaveCols = None):
		self.s.db['activeRow'] = self.get('active').levels[0] if leaveRows is None else adj.rc_pd(self.get('active').levels[0], ('not', leaveRows))
		self.s.db['activeCol'] = self.get('active').levels[1] if leaveCols is None else adj.rc_pd(self.get('active').levels[1], ('not', leaveCols))

	def states(self):
		return {'B': self.s.standardInstance(state='B') | {attr: getattr(self,attr)() for attr in ('g_endo','g_exo','blocks','args','solve')}}
	def solve(self):
		return f"""vD.lo[{self.n('i')},{self.n('j')}]$(active[{self.n('i')},{self.n('j')}]) = 0; solve {self.s['name']} minimizing object using QCP;"""
	def args(self):
		return {'RAS_Blocks': self.rasText}
	def blocks(self):
		return OrdSet(['B_RAS'])
	def g_endo(self):
		return OrdSet([f"G_endo"])
	def g_exo(self):
		return OrdSet()
	def groups(self):
		return {g.name: g for g in self.groups_()}
	def groups_(self):
		return [gmsPy.Group(f"G_endo",
				v = [('vD', self.g('active')), ('etaRow', self.g('active')), ('etaCol', self.g('active'))])]

	@property
	def rasText(self):
		i,j = self.n('i'), self.n('j')
		return f"""
$BLOCK B_RAS
	E_object..							object	 =E= sum([{i},{j}]$(active[{i},{j}]), Sqr(etaRow[{i},{j}]-1)+Sqr(etaCol[{i},{j}]-1));
	E_vD[{i},{j}]$(active[{i},{j}])..	vD[{i},{j}]	 =E= vD0[{i},{j}]*(1-etaRow[{i},{j}]*deltaRow[{i}]-etaCol[{i},{j}]*deltaCol[{j}]);
	E_colSum[{j}]$(activeCol[{j}])..	colSum[{j}]=E= sum({i}$(active[{i},{j}]), vD[{i},{j}]);
	E_rowSum[{i}]$(activeRow[{i}])..	rowSum[{i}]=E= sum({j}$(active[{i},{j}]), vD[{i},{j}]);
$ENDBLOCK
"""
