from gmsPython import gmsPy, GmsPythonSimple
from pyDatabases import OrdSet, noneInit

class Equilibrium(GmsPythonSimple):
	def __init__(self, f = None, name = None, db_IO = None, s=None, glob=None, s_kwargs = None, g_kwargs = None):
		""" Initialize from name, io data, """
		super().__init__(checkStates = ['B','C'], name=f"{name}_equi", f=f, s=s, glob=glob, g_kwargs=g_kwargs, s_kwargs = noneInit(s_kwargs, {}) | {'db': db_IO})

	def args(self, state):
		return {self.name+'_Blocks': self.equationText}
	def blocks(self, state):
		if state == 'B':
			return OrdSet([f"B_{self.name}_baseline"])
		elif state == 'C':
			return OrdSet([f"B_{self.name}_calibration"])
	def g_endo(self, state):
		if state == 'B':
			return OrdSet([f"G_{self.name}_tx0E", f"G_{self.name}_t0"])
		elif state == 'C':
			return OrdSet([f"G_{self.name}_tx0E"])
	def g_exo(self, state):
		if state == 'B':
			return OrdSet()
		elif state == 'C':
			return OrdSet([f"G_{self.name}_t0"])

	def _groups(self,m=None):
		return [gmsPy.Group(f"G_{self.name}_tx0E", 
			v = [('qS', ('and', [self.g('d_qSEqui'), self.g('tx0E')])), ('p', ('and', [self.g('d_pEqui'), self.g('tx0E')]))]),
				gmsPy.Group(f"G_{self.name}_t0", 
			v = [('qS', ('and', [self.g('d_qSEqui'), self.g('t0')])),   ('p', ('and', [self.g('d_pEqui'), self.g('t0')]))])]

	@property
	def equationText(self):
		return f"""
$BLOCK B_{self.name}_baseline
	E_equi_{self.name}[t,n]$(nEqui[n] and txE[t])..	 sum(s$(d_qS[s,n]), qS[t,s,n]) =E= sum(s$(d_qD[s,n]), qD[t,s,n]);
$ENDBLOCK
$BLOCK B_{self.name}_calibration
	E_equi_{self.name}_tx0E[t,n]$(nEqui[n] and tx0E[t])..	 sum(s$(d_qS[s,n]), qS[t,s,n]) =E= sum(s$(d_qD[s,n]), qD[t,s,n]);
$ENDBLOCK
"""
