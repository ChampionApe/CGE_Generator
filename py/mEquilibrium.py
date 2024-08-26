from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs
from gmsPython import Group, GModel

class Equilibrium(GModel):
	def __init__(self, name, **kwargs):
		super().__init__(name = name, **kwargs)

	def initStuff(self, db = None, gdx = True):
		if db is not None:
			MergeDbs.merge(self.db, db)
		self.initData()
		self.initGroups()
		if gdx:
			self.db.mergeInternal()

	def initData(self):
		self.db.aom(pd.Series(1+self.db('R_LR'), index = self.db('t')), name = 'Rrate', priority = 'first')

	@property
	def metaGroup_endo_B(self):
		return Group(f'{self.name}_endo_B', g = [self.groups[f'{self.name}_{k}'] for k in ('alwaysEndo','exoInCalib')])
	@property
	def metaGroup_endo_C(self):
		return Group(f'{self.name}_endo_C', g = [self.groups[f'{self.name}_alwaysEndo']])
	@property
	def metaGroup_exo_B(self):
		return Group(f'{self.name}_exo_B',  g = [self.groups[f'{self.name}_alwaysExo']])
	@property
	def metaGroup_exo_C(self):
		return Group(f'{self.name}_exo_C', g = [self.groups[f'{self.name}_{k}'] for k in ('alwaysExo','exoInCalib')])
	@property
	def group_alwaysExo(self):
		return Group(f'{self.name}_alwaysExo', v = ['Rrate'])
	@property
	def group_alwaysEndo(self):
		return Group(f'{self.name}_alwaysEndo', v = [('qS', ('and', [self.g('tx0E'), self.g('d_qSEqui')])), 
													 ('p',  ('and', [self.g('tx0E'), self.g('d_pEqui')]))])
	@property
	def group_exoInCalib(self):
		return Group(f'{self.name}_exoInCalib', v = [('qS', ('and', [self.g('t0'), self.g('d_qSEqui')])), 
													 ('p',  ('and', [self.g('t0'), self.g('d_pEqui')]))])
	@property
	def textBlocks(self):
		return {'equilibrium': self.equationText}

	@property
	def model_B(self):
		return OrdSet([f"B_{self.name}_baseline"])
	@property
	def model_C(self):
		return OrdSet([f"B_{self.name}_calib"])

	@property
	def equationText(self):
		return f"""
$BLOCK B_{self.name}_baseline
	E_{self.name}_equi[t,n]$(nEqui[n] and txE[t])..	 sum(s$(d_qS[s,n]), qS[t,s,n]) =E= sum(s$(d_qD[s,n]), qD[t,s,n]);
$ENDBLOCK

$BLOCK B_{self.name}_calib
	E_{self.name}_equi_tx0E[t,n]$(nEqui[n] and tx0E[t])..	 sum(s$(d_qS[s,n]), qS[t,s,n]) =E= sum(s$(d_qD[s,n]), qD[t,s,n]);
$ENDBLOCK
"""
