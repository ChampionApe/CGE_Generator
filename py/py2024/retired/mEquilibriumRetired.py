from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs
from gmsPython import Group, Model

class Equilibrium(Model):
	def __init__(self, name, **kwargs):
		super().__init__(name, **kwargs)

	def initStuff(self, db = None, gdx = True):
		if db is not None:
			MergeDbs.merge(self.db, db)
		self.initData()
		self.initGroups()
		if gdx:
			self.db.mergeInternal()

	def initData(self):
		self.db.aom(pd.Series(1+self.db('R_LR'), index = self.db('t')), name = 'Rrate', priority = 'first')

	def initGroups(self):
		self.groups = {g.name: g for g in (getattr(self, f'group_{k}') for k in ('alwaysExo','alwaysEndo','exoInCalib'))}
		[grp() for grp in self.groups.values()]; # initialize groups
		metaGroups = {g.name: g for g in (getattr(self, f'group_{k}') for k in ('endo_B','endo_C','exo_B','exo_C'))}
		[grp() for grp in metaGroups.values()]; # initialize metagroups
		self.groups.update(metaGroups)

	@property
	def group_endo_B(self):
		return Group(f'{self.name}_endo_B', g = [self.groups[f'{self.name}_{k}'] for k in ('alwaysEndo','exoInCalib')])
	@property
	def group_endo_C(self):
		return Group(f'{self.name}_endo_C', g = [self.groups[f'{self.name}_alwaysEndo']])
	@property
	def group_exo_B(self):
		return Group(f'{self.name}_exo_B',  g = [self.groups[f'{self.name}_alwaysExo']])
	@property
	def group_exo_C(self):
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

	def fixText(self, state ='B'):
		return self.groups[f'{self.name}_exo_{state}'].fix(db = self.db)
	def unfixText(self, state = 'B'):
		return self.groups[f'{self.name}_endo_{state}'].unfix(db = self.db)

	def models(self, state = 'B', **kwargs):
		if state == 'B':
			return OrdSet([f"B_{self.name}_baseline"])
		elif state == 'C':
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
