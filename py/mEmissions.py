from gmsPython import gmsPy, GmsPythonSimple, Submodule
from pyDatabases import OrdSet, noneInit
import numpy as np, pandas as pd
# import pyDatabases, pandas as pd
# from pyDatabases.gpyDB_wheels import adj, robust

class emissionTarget(GmsPythonSimple):
	def __init__(self, f = None, name = None, ns = None, s = None, glob = None, s_kwargs = None, g_kwargs = None, kwargs=None):
		""" Initialize from a pickle file 'f' or nesting tree 'tree'. """
		super().__init__(checkStates = ['B','C','Mbinding','MsoftConstr'], name=name, f=f, s=s, glob=glob, ns=ns, s_kwargs = s_kwargs, g_kwargs=g_kwargs)
		self.adjust(**noneInit(kwargs,{}))

	def adjust(self,**kwargs):
		pass

	def readTargetSubsets(self):
		""" Defines the target subsets from the vector of targets """
		self.s.db['tTarget']= self.get('qCO2Target').index
		t = self.get('tTarget').to_frame(index = False) 
		t = t.assign(n = t.apply(np.roll, shift = -1))
		self.s.db['targetSpell0'] = pd.Index([t['t'].iloc[0]] + t['t'][(t['n']-t['t'])>1].to_list(), name = 't')

	def args(self, state):
		return {f"{self.name}_Blocks": self.equationText}

	def blocks(self, state):
		if state == 'B':
			return OrdSet(['B_Emissions'])
		elif state == 'C':
			return OrdSet(['B_Emissions','B_EmissionsCalib'])
		elif state == 'Mbinding':
			return OrdSet(['B_Emissions','B_EmissionsBinding'])
		elif state == 'MsoftConstr':
			return OrdSet(['B_Emissions','B_EmissionsSoftConstr'])

	def g_endo(self, state):
		if state == 'B':
			return OrdSet([f"G_{self.name}_endo_always", f"G_{self.name}_exo_in_calib"])
		elif state in ['Mbinding','MsoftConstr']:
			return self.g_endo('B')+OrdSet([f"G_{self.name}_endoRegulation"])
		elif state == 'C':
			return OrdSet([f"G_{self.name}_endo_always", f"G_{self.name}_endo_in_calib"])

	def g_exo(self, state):
		if state == 'B':
			return OrdSet([f"G_{self.name}_exo_always", f"G_{self.name}_endo_in_calib", f"G_{self.name}_endoRegulation"])
		elif state in ['Mbinding','MsoftConstr']:
			return self.g_exo('B')-OrdSet([f"G_{self.name}_endoRegulation"])
		elif state == 'C':
			return OrdSet([f"G_{self.name}_exo_always", f"G_{self.name}_exo_in_calib", f"G_{self.name}_endoRegulation"])

	def _groups(self,m=None):
		return [gmsPy.Group(f"G_{self.name}_exo_always",
			v =[('qS', self.g('d_qS')), # check
				('techPot', None), # check
				('techCost', None), # check
				('techSmooth', None), # check
				('DACCost', None), # check
				('DACSmooth', None), # check
				('tauDist', self.g('dtauCO2')), # check
				('Rrate', None), # check
				('qCO2Target', self.g('tTarget')), # check
				('uCO20', self.g('dqCO2')), # check
				('tauCO2Base', None), # check
				('softConstr', None), # check
				('qCO2Base', None)]), # check
			gmsPy.Group(f"G_{self.name}_endo_always",
			v = [('qCO2', ('and', [self.g('tx0E'), self.g('dqCO2')])), # check
				 ('qCO2agg', self.g('txE')),  # check
				 ('tauCO2', self.g('dtauCO2'))]), # check
			gmsPy.Group(f"G_{self.name}_exo_in_calib",
			v = [('qCO2', ('and', [self.g('t0'), self.g('dqCO2')]))]), # check
			gmsPy.Group(f"G_{self.name}_endo_in_calib",
			v = [('uCO2Calib', self.g('dqCO2')), 
				 ('uCO2', self.g('dqCO2'))]),
			gmsPy.Group(f"G_{self.name}_endoRegulation", # check
			v = [('tauCO2agg', self.g('txE'))]) # check
 		]

	@property
	def equationText(self):
		return f"""
$BLOCK B_Emissions
	E_qCO2[t,s,n]$(dqCO2[s,n] and txE[t])..		qCO2[t,s,n]		=E= uCO2[t,s,n] * qS[t,s,n] * (1-sum(tech, techPot[tech,t] * errorf((tauCO2[t,s,n]-techCost[tech,t])/techSmooth[tech])));
	E_qCO2agg[t]$(txE[t])..						qCO2agg[t]		=E= sum([s,n]$(dqCO2[s,n]), qCO2[t,s,n])-qCO2Base * errorf((tauCO2agg[t]- DACCost[t])/DACSmooth);
	E_tauCO2[t,s,n]$(dtauCO2[s,n] and txE[t])..	tauCO2[t,s,n]	=E= tauCO2agg[t] * tauDist[t,s,n];
$ENDBLOCK

$BLOCK B_EmissionsCalib
	E_qCO2calib[t,s,n]$(dqCO2[s,n] and txE[t])..	uCO2[t,s,n]	=E= uCO20[t,s,n] * (1+uCO2calib[s,n]);
$ENDBLOCK

$BLOCK B_EmissionsBinding
	E_qCO2_binding[t]$(tTarget[t] and not tE[t])..									qCO2agg[t]		=E= qCO2Target[t];
	E_tauCO2_binding1[t]$(tx20E[t] and not (tTarget[t] and not targetSpell0[t]))..	tauCO2agg[t]	=E= tauCO2agg[t-1]*Rrate[t];
	E_tauCO2_binding2[t]$(t0[t] and not tTarget[t])..								tauCO2agg[t]	=E= tauCO2agg[t+1]/Rrate[t];
$ENDBLOCK

$BLOCK B_EmissionsSoftConstr
	E_qCO2_softConstr[t]$(tTarget[t] and not tE[t])..									tauCO2agg[t]	=E= tauCO2Base * (1 / (errorf( (qCO2Target[t]-qCO2agg[t]) / softConstr)+0.0000001)-1);
	E_tauCO2_softConstr1[t]$(tx20E[t] and not (tTarget[t] and not targetSpell0[t]))..	tauCO2agg[t]	=E= tauCO2agg[t-1]*Rrate[t];
	E_tauCO2_softConstr2[t]$(t0[t] and not tTarget[t])..								tauCO2agg[t]	=E= tauCO2agg[t+1]/Rrate[t];
$ENDBLOCK
"""
