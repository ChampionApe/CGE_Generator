from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs, GpyDB
from gmsPython import gmsWrite, Group, Model

class EmissionEOP(Model):
	def __init__(self, name, partial = False,  **kwargs):
		super().__init__(name = name, **kwargs)
		self.partial = partial # use module in partial or general equilibrium; this affects compilation of groups 

	# Initialize
	def initStuff(self, db = None, gdx = True):
		if db is not None:
			MergeDbs.merge(self.db, db)
		self.initData()
		self.initGroups()
		if gdx:
			self.db.mergeInternal()

	def initData(self):
		self.db.aom(self.db('uCO2'), name = 'uCO20', priority = 'first')
		self.db.aom(pd.Series(0, index = self.db('dqCO2')), name = 'uCO2Calib', priority= 'first')
		self.db.aom(self.db('tauCO2agg').xs(self.db('t0')[0])/25, name = 'DACSmooth', priority='first')
		self.db.aom(pd.Series(self.db('DACSmooth'), index = self.db('techPot').index.levels[0]), name = 'techSmooth', priority='first')
		self.db.aom(1, name = 'qCO2Base', priority='first')
		self.db.aom(self.db('tauCO2agg').xs(self.db('t0')[0]), name = 'tauCO2Base')
		self.db.aom(1/25, name = 'softConstr')

	def initGroups(self):
		self.groups = {g.name: g for g in (getattr(self, f'group_{k}') for k in ('alwaysExo','alwaysEndo','exoInCalib','endoInCalib'))}
		[grp() for grp in self.groups.values()]; # initialize groups
		metaGroups = {g.name: g for g in (getattr(self, f'group_{k}') for k in ('endo_B','endo_C','exo_B','exo_C'))}
		[grp() for grp in metaGroups.values()]; # initialize metagroups
		self.groups.update(metaGroups)

	def models(self, state = 'B', **kwargs):
		if state == 'B':
			return OrdSet([f"B_{self.name}_account"])
		elif state == 'C':
			return OrdSet([f"B_{self.name}_{k}" for k in ('account', 'calib')])

	# Solve methods:
	def jSolve(self, n, state = 'B', loopName = 'i', ϕ = 1):
		""" Solve model from scratch using the jTerms approach."""
		mainText = self.compiler(self.text, has_read_file = False)
		jModelStr = self.j.jModel(f'M_{self.name}_{state}', self.groups.values(), db = self.db) # create string that declares adjusted $j$-terms
		fixUnfix  = self.j.jFixUnfix([self.groups[f'{self.name}_endo_{state}']], db = self.db) + self.j.solve
		loopSolve = self.j.jLoop(n, loopName = loopName, ϕ = ϕ)
		self.job = self.ws.add_job_from_string(mainText+jModelStr+fixUnfix+loopSolve)
		self.job.run(databases = self.db.database)
		return GpyDB(self.job.out_db, ws = self.ws)

	def solve(self, text = None, state = 'B'):
		self.job = self.ws.add_job_from_string(noneInit(text, self.write(state = state)))
		self.job.run(databases = self.db.database)
		self.out_db = GpyDB(self.job.out_db, ws = self.ws)
		return self.out_db	

	# Writing methods:
	def write_gamY(self, state = 'B'):
		""" Write code for solving the model from "scratch" """
		return self.text+self.solveText(state = state)

	def write(self, state = 'B'):
		return self.compiler(self.write_gamY(state = state), has_read_file = False)

	@property
	def textBlocks(self):
		return {'emissions': self.equationText}

	def fixText(self, state ='B'):
		return self.groups[f'{self.name}_exo_{state}'].fix(db = self.db)
	def unfixText(self, state = 'B'):
		return self.groups[f'{self.name}_endo_{state}'].unfix(db = self.db)

	def solveText(self, state = 'B'):
		return f"""
# Fix exogenous variables in state {state}:
{self.fixText(state=state)}

# Unfix endogenous variables in state {state}:
{self.unfixText(state=state)}

solve M_{self.name}_{state} using CNS;
"""

	@property
	def text(self):
		return f"""
{gmsWrite.StdArgs.root()}
{gmsWrite.StdArgs.funcs()}
{gmsWrite.FromDB.declare(self.db)}
{gmsWrite.FromDB.load(self.db, gdx = self.db.name)}

{''.join(self.textBlocks.values())}
$Model M_{self.name}_B {','.join(self.models(state = 'B'))};
$Model M_{self.name}_C {','.join(self.models(state = 'C'))};
""" 

	@property
	def equationText(self):
		return f"""
$BLOCK B_{self.name}_account
	E_qCO2[t,s,n]$(dqCO2[s,n] and txE[t])..		qCO2[t,s,n]		=E= uCO2[t,s,n] * qS[t,s,n] * (1-sum(tech, techPot[tech,t] * errorf((tauCO2[t,s,n]-techCost[tech,t])/techSmooth[tech])));
	E_qCO2agg[t]$(txE[t])..						qCO2agg[t]		=E= sum([s,n]$(dqCO2[s,n]), qCO2[t,s,n])-qCO2Base * errorf((tauCO2agg[t]- DACCost[t])/DACSmooth);
	E_tauCO2[t,s,n]$(dtauCO2[s,n] and txE[t])..	tauCO2[t,s,n]	=E= tauCO2agg[t] * tauDist[t,s,n];
$ENDBLOCK

$BLOCK B_{self.name}_calib
	E_qCO2calib[t,s,n]$(dqCO2[s,n] and txE[t])..	uCO2[t,s,n]	=E= uCO20[t,s,n] * (1+uCO2calib[s,n]);
$ENDBLOCK
"""

	@property
	def group_endo_B(self):
		return Group(f'{self.name}_endo_B', g = [self.groups[f'{self.name}_{k}'] for k in ('alwaysEndo','exoInCalib')])
	@property
	def group_endo_C(self):
		return Group(f'{self.name}_endo_C', g = [self.groups[f'{self.name}_{k}'] for k in ('alwaysEndo', 'endoInCalib')])
	@property
	def group_exo_B(self):
		return Group(f'{self.name}_exo_B', g = [self.groups[f'{self.name}_{k}'] for k in ('alwaysExo','endoInCalib')])
	@property
	def group_exo_C(self):
		return Group(f'{self.name}_exo_C', g = [self.groups[f'{self.name}_{k}'] for k in ('alwaysExo','exoInCalib')])
	@property
	def group_alwaysExo(self):
		if not self.partial:
			return Group(f'{self.name}_alwaysExo', v = ['techPot','techCost','techSmooth','DACCost','DACSmooth', 'tauCO2Base','softConstr','qCO2Base','tauCO2agg',
														('tauDist', self.g('dtauCO2')),
														('uCO20', self.g('dqCO2'))])
		else:
			self.partial = False
			g = self.group_alwaysExo
			g.v += [('qS',self.g('d_qS'))]
			self.partial = True
			return g

	@property
	def group_alwaysEndo(self):
		return Group(f'{self.name}_alwaysEndo', v = [('qCO2', ('and', [self.g('tx0E'), self.g('dqCO2')])),
													 ('qCO2agg', self.g('txE')),
													 ('tauCO2',  self.g('dtauCO2'))])
	@property
	def group_exoInCalib(self):
		return Group(f'{self.name}_exoInCalib', v= [('qCO2', ('and', [self.g('t0'), self.g('dqCO2')]))])
	@property
	def group_endoInCalib(self):
		return Group(f'{self.name}_endoInCalib', v = [('uCO2Calib', self.g('dqCO2')),
													  ('uCO2', self.g('dqCO2'))])


class EmissionTargets(EmissionEOP):
	def __init__(self, name, partial = False, **kwargs):
		super().__init__(name = name, partial=partial, **kwargs)

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
