from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs, GpyDB
from gmsPython import gmsWrite, Group, Model
from gamsSnippets import techEOP

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
		self.db.aom(pd.Series(0, index = self.db('uCO2').index), name = 'uAbate', priority = 'first')
		self.db.aom(pd.Series(0, index = self.db('dqCO2')), name = 'uCO2Calib', priority= 'first')
		self.db.aom(self.db('tauCO2agg').xs(self.db('t0')[0])/2, name = 'DACSmooth', priority='first')
		self.db.aom(pd.Series(self.db('DACSmooth'), index = self.db('techPot').index.levels[0]), name = 'techSmooth', priority='first')
		self.db.aom(1, name = 'qCO2Base', priority='first')
		self.db.aom(self.db('tauCO2agg').xs(self.db('t0')[0]), name = 'tauCO2Base', priority = 'first')
		self.db.aom(1/25, name = 'softConstr', priority = 'first')
		self.db.aom(0, name = 'obj')

	def initGroups(self):
		self.groups = {g.name: g for g in (getattr(self, f'group_{k}') for k in ('alwaysExo','alwaysEndo','exoInCalib','endoInCalib'))}
		[grp() for grp in self.groups.values()]; # initialize groups
		metaGroups = {g.name: g for g in (getattr(self, f'group_{k}') for k in ('endo_B','endo_C','exo_B','exo_C'))}
		[grp() for grp in metaGroups.values()]; # initialize metagroups
		self.groups.update(metaGroups)

	def models(self, state = 'B', **kwargs):
		if state == 'B':
			return OrdSet([f"B_{self.name}"])
		elif state == 'C':
			return OrdSet([f"B_{self.name}", f"B_{self.name}_calib"])

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

	@property
	def funcsText(self):
		return techEOP

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
{techEOP}
{gmsWrite.FromDB.declare(self.db)}
{gmsWrite.FromDB.load(self.db, gdx = self.db.name)}

{''.join(self.textBlocks.values())}
$Model M_{self.name}_B {','.join(self.models(state = 'B'))};
$Model M_{self.name}_C {','.join(self.models(state = 'C'))};
""" 

	@property
	def equationText(self):
		return f"""
$BLOCK B_{self.name}
	E_uAbate[t,s,n]$(dqCO2[s,n] and txE[t])..		uAbate[t,s,n]		=E= sum(tech, techPot[tech,t] * @EOP_Tech(tauCO2[t,s,n], techCost[tech,t], techSmooth[tech]));
	E_tauCO2Eff[t,s,n]$(dtauCO2[s,n] and txE[t])..	tauEffCO2[t,s,n]	=E= tauCO2[t,s,n]*(1-uAbate[t,s,n])+sum(tech, techPot[tech,t] * @EOP_Cost(tauCO2[t,s,n], techCost[tech,t], techSmooth[tech]));
	E_tauCO2[t,s,n]$(dtauCO2[s,n] and txE[t])..		tauCO2[t,s,n]		=E= tauCO2agg[t] * tauDist[t,s,n];
	E_qCO2[t,s,n]$(dqCO2[s,n] and txE[t])..			qCO2[t,s,n]			=E= uCO2[t,s,n] * (1-uAbate[t,s,n]) * qS[t,s,n];
	E_qCO2agg[t]$(txE[t])..							qCO2agg[t]			=E= sum([s,n]$(dqCO2[s,n]), qCO2[t,s,n])-qCO2Base * @EOP_Tech(tauCO2agg[t], DACCost[t], DACSmooth);
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
													 ('tauCO2',  self.g('dtauCO2')),
													 ('tauEffCO2', self.g('dtauCO2')),
													 ('uAbate', self.g('dqCO2'))])
	@property
	def group_exoInCalib(self):
		return Group(f'{self.name}_exoInCalib', v= [('qCO2', ('and', [self.g('t0'), self.g('dqCO2')]))])
	@property
	def group_endoInCalib(self):
		return Group(f'{self.name}_endoInCalib', v = [('uCO2Calib', self.g('dqCO2')),
													  ('uCO2', self.g('dqCO2'))])

class EmissionTargetEOP(EmissionEOP):
	def __init__(self, name, partial = False, regulation = None, **kwargs):
		super().__init__(name, partial = partial, **kwargs)
		self.regulation = regulation

	@staticmethod
	def createTargetsFromSYT(targets, tIdx, q0):
		""" Based on single-year targets, return full range of targets and relevant subsets for all variation of emission regulation below"""
		d = {}
		target_T = targets.index.max()
		targets_ = pd.concat([pd.Series(q0, index = tIdx[0:1]), targets], axis = 0)
		impliedTargets = pd.Series(targets.loc[target_T], index = tIdx[tIdx>target_T])
		d['qCO2_SYT'] = targets.combine_first(impliedTargets)
		d['t_SYT'] = d['qCO2_SYT'].index # which years have single year targets
		d['t_SYT_NB'] = tIdx.difference(d['t_SYT']) # which years does not have single year targets
		def linInterp(x,i):
			return pd.Series(np.linspace(x.iloc[i], x.iloc[i+1], x.index[i+1]-x.index[i]+1)[:-1], index = pd.Index(range(x.index[i], x.index[i+1]), name = 't'))
		d['qCO2_LRP'] = pd.concat([linInterp(targets_, i) for i in range(len(targets_)-1)], axis = 0).combine_first(pd.Series(targets.loc[target_T], index = tIdx[tIdx>=target_T]))
		d['t_LRP'] = d['qCO2_LRP'].index
		d['t_EB'] = targets.index
		t2tt = [None] * len(targets) 
		for i in range(len(t2tt)):
		    if i == 0:
		        t2tt[i] = np.full(targets.index[i]-targets_.index[i]+1, targets.index[i])
		    else:
		        t2tt[i] = np.full(targets.index[i]-targets_.index[i], targets.index[i])
		d['t2tt_EB'] = pd.MultiIndex.from_arrays([np.hstack(t2tt), range(tIdx[0], target_T+1)], names = ['t','tt'])
		d['qCO2_EB'] = adjMultiIndex.applyMult(d['qCO2_LRP'], d['t2tt_EB'].rename(['tt','t'])).groupby('tt').sum().rename_axis('t')
		d['qCO2_EB_SYT'] = impliedTargets
		d['t_EB_SYT'] = impliedTargets.index
		d['t_EB_NB'] = adj.rc_pd(d['t2tt_EB'].rename(['tt','t']), ('not', targets)).droplevel('tt')
		return d

	### GROUPS
	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		if self.regulation is None:
			g.v += [('obj', None)]
			return g
		else:
			g.v += [(f'qCO2_{k}', self.g(f't_{k}')) for k in ('SYT','LRP','EB','EB_SYT')] # add all target variables
			# if 'OPT' not in self.regulation:
				# g.v += [('obj', None)]
			return g

	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		if self.regulation is None:
			return g
		else:
			if 'SYT' in self.regulation:
				g.v += [('tauCO2agg', ('or', [self.g('t_SYT'), self.g('t_SYT_NB')]))]
			elif 'LRP' in self.regulation:
				g.v += [('tauCO2agg', self.g('t_LRP'))]
			elif 'EB' in self.regulation:
				g.v += [('tauCO2agg', ('or', [self.g('t_EB'), self.g('t_EB_NB'), self.g('t_EB_SYT')]))]
			# if 'OPT' in self.regulation:
		g.v += [('obj', None)]
		# g.sub_v += [('tauCO2agg', self.g('t0'))]
		return g

	@property
	def group_exoInCalib(self):
		g = super().group_exoInCalib
		if self.regulation is None:
			return g
		else:
			# g.v += [('tauCO2agg', self.g('t0'))]
			g.v += [('tauCO2agg', ('and', [self.g('t0'), self.g(f"t_{self.regulation.split('_')[0]}")]))]
			return g

	### EQUATIONS
	@property
	def equationText(self):
		return super().equationText+'\n'.join([getattr(self, f'eqText_{k}') for k in ('SYT','SYT_HR','SYT_OPT','LRP','EB_HR','EB_OPT')])

	def models(self, state = 'B', regulation = None, **kwargs):
		m = super().models(state = state)
		return m+self.addRegulationBlocks(state, noneInit(regulation,self.regulation))

	def addRegulationBlocks(self, state, regulation):
		if regulation is None:
			return OrdSet([])
		else:
			return OrdSet([f"B_{self.name}_{self.regulation}_Calib" if state == 'C' else f"B_{self.name}_{self.regulation}"])

	@property
	def eqText_SYT(self):
		""" Single Year Targets with zero rates in non-binding years """
		return f"""
$BLOCK B_{self.name}_SYT_Calib
	E_SYT_qCO2agg[t]$(t_SYT[t] and tx0E[t]).. 	qCO2agg[t]		=E= qCO2_SYT[t];
	E_SYT_tauCO2agg[t]$(t_SYT_NB[t])..			tauCO2agg[t]	=E= 0;
$ENDBLOCK
$BLOCK B_{self.name}_SYT_t0
	E_SYT_t0[t]$(t_SYT[t] and t0[t])..	qCO2agg[t]	=E= qCO2_SYT[t];
$ENDBLOCK
$MODEL B_{self.name}_SYT
	B_{self.name}_SYT_Calib
	B_{self.name}_SYT_t0
;
"""

	@property
	def eqText_SYT_HR(self):
		""" Single Year Targets with Hotelling Rule """
		return f"""
$BLOCK B_{self.name}_SYT_HR_Calib
	E_SYT_HR_qCO2agg[t]$(t_SYT[t] and tx0E[t])..	 	qCO2agg[t]		=E= qCO2_SYT[t];
	E_SYT_HR_tauCO2agg[t]$(t_SYT_NB[t])..				tauCO2agg[t]	=E= tauCO2agg[t+1]/Rrate[t];
$ENDBLOCK
$MODEL B_{self.name}_SYT_HR
	B_{self.name}_SYT_HR_Calib
	B_{self.name}_SYT_t0
;
"""

	@property
	def eqText_SYT_OPT(self):
		""" Single Year Targets with numerical OPTimization of tax rates"""
		return f"""
$BLOCK B_{self.name}_SYT_OPT_Calib
	E_SYT_OPT_qCO2agg[t]$(t_SYT[t] and tx0E[t]).. 	qCO2agg[t]		=E= qCO2_SYT[t];
	# E_SYT_OPT_obj..									obj =E= 1;
	E_SYT_OPT_obj..									obj =E= sum([t,s]$(t0[t] and s_HH[s]), discUtil[t,s]);
$ENDBLOCK
$MODEL B_{self.name}_SYT_OPT
	B_{self.name}_SYT_OPT_Calib
	B_{self.name}_SYT_t0
;
"""

	@property
	def eqText_LRP(self):
		""" Single Year Targets with numerical OPTimization of tax rates"""
		return f"""
$BLOCK B_{self.name}_LRP_Calib
	E_LRP_qCO2agg[t]$(t_LRP[t] and tx0E[t]).. 		qCO2agg[t]		=E= qCO2_LRP[t];
$ENDBLOCK
$BLOCK B_{self.name}_LRP_t0
	E_LRP_t0[t]$(t_LRP[t] and t0[t])..	qCO2agg[t]	=E= qCO2_LRP[t];
$ENDBLOCK
$MODEL B_{self.name}_LRP
	B_{self.name}_LRP_Calib
	B_{self.name}_LRP_t0
;
"""

	@property
	def eqText_EB_HR(self):
		""" Emission Budget with Hotelling Rule"""
		return f"""
$BLOCK B_{self.name}_EB_HR_Calib
	E_EB_HR_qCO2agg[t]$(t_EB[t] and tx0E[t]).. 		qCO2_EB[t]		=E= sum(tt$(t2tt_EB[t, tt]), qCO2agg[tt]);
	E_EB_HR_SYT_qCO2agg[t]$(t_EB_SYT[t])..			qCO2agg[t]		=E= qCO2_EB_SYT[t];
	E_EB_HR_tauCO2agg[t]$(t_EB_NB[t])..				tauCO2agg[t]	=E= tauCO2agg[t+1]/Rrate[t];
$ENDBLOCK
$BLOCK B_{self.name}_EB_t0
	E_EB_t0[t]$(t_EB[t] and t0[t])..	qCO2_EB[t]		=E= sum(tt$(t2tt_EB[t, tt]), qCO2agg[tt]);
$ENDBLOCK
$MODEL B_{self.name}_EB_HR
	B_{self.name}_EB_HR_Calib
	B_{self.name}_EB_t0
;
"""

	@property
	def eqText_EB_OPT(self):
		""" Emissions Budget with numerical OPTimization of tax rates """
		return f"""
$BLOCK B_{self.name}_EB_OPT_Calib
	E_EB_OPT_qCO2agg[t]$(t_EB[t] and tx0E[t]).. 	qCO2_EB[t]	=E= sum(tt$(t2tt_EB[t, tt]), qCO2agg[tt]);
	E_EB_OPT_SYT_qCO2agg[t]$(t_EB_SYT[t])..			qCO2agg[t]	=E= qCO2_EB_SYT[t];
	E_EB_OPT_obj..									obj =E= sum([t,s]$(t0[t] and s_HH[s]), discUtil[t,s]);
$ENDBLOCK
$MODEL B_{self.name}_EB_OPT
	B_{self.name}_EB_OPT_Calib
	B_{self.name}_EB_t0
;
"""
