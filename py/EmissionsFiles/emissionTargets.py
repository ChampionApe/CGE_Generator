from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs
from pyDatabases import cartesianProductIndex as cpi
from gmsPython import Group, GModel
import EmissionsFiles.gamsEmissions as gamsEmissions

class EmissionAccounts(GModel):
	def __init__(self, name, partial = False, **kwargs):
		super().__init__(name = name, **kwargs)
		self.partial = partial

	def initData(self):
		self.db.aom(self.db('uCO2'), name='uCO20', priority='first')
		self.db.aom(pd.Series(0, index=self.db('dqCO2')), name='uCO2Calib', priority='first')

	# Initialize
	def initStuff(self, db=None, gdx=True):
		if db is not None:
			MergeDbs.merge(self.db, db)
		self.initData()
		self.initGroups()
		if gdx:
			self.db.mergeInternal()

	@property
	def textBlocks(self):
		return {'emissions': gamsEmissions.AccountSimple(self.name)}
	@property
	def model_B(self):
		return OrdSet([f"B_{self.name}"])
	@property
	def model_C(self):
		return self.model_B+OrdSet([f"B_{self.name}_calib"])
	@property
	def metaGroup_endo_B(self):
		return Group(f'{self.name}_endo_B', g=[self.groups[f'{self.name}_{k}'] for k in ('alwaysEndo', 'exoInCalib')])
	@property
	def metaGroup_endo_C(self):
		return Group(f'{self.name}_endo_C', g=[self.groups[f'{self.name}_{k}'] for k in ('alwaysEndo', 'endoInCalib')])
	@property
	def metaGroup_exo_B(self):
		return Group(f'{self.name}_exo_B', g=[self.groups[f'{self.name}_{k}'] for k in ('alwaysExo', 'endoInCalib')])
	@property
	def metaGroup_exo_C(self):
		return Group(f'{self.name}_exo_C', g=[self.groups[f'{self.name}_{k}'] for k in ('alwaysExo', 'exoInCalib')])

	@property
	def group_alwaysExo(self):
		g = Group(f'{self.name}_alwaysExo', v=['tauCO2agg', ('tauDist', self.g('dtauCO2')), ('uCO20', self.g('dqCO2'))])
		if not self.partial:
			return g
		else:
			g.v += [('qS', self.g('d_qS'))]
			return g
	@property
	def group_alwaysEndo(self):
		return Group(f'{self.name}_alwaysEndo', v=[('qCO2', ('and', [self.g('tx0E'), self.g('dqCO2')])),
												   ('qCO2agg', self.g('txE')),
												   ('tauCO2', self.g('dtauCO2')),
												   ('tauEffCO2', self.g('dtauCO2'))])
	@property
	def group_exoInCalib(self):
		return Group(f'{self.name}_exoInCalib', v=[('qCO2', ('and', [self.g('t0'), self.g('dqCO2')]))])
	@property
	def group_endoInCalib(self):
		return Group(f'{self.name}_endoInCalib', v=[('uCO2Calib', self.g('dqCO2')), ('uCO2', self.g('dqCO2'))])


class EmissionTargets(GModel):
	def __init__(self, name, CGE, regulation = 'SYT_EXO', **kwargs):
		""" Add emission target to CGE model. """
		super().__init__(name = name, database = CGE.db, **kwargs)
		self.CGE = CGE # 
		self.CGE.regulation = regulation
		self.db = self.CGE.db

	def initData(self):
		self.db.aom(pd.Series(1e-4, index = self.db('t')), name = 'tauCO2agg0', priority = 'first')

	# Initialize
	def initStuff(self, gdx=True):
		self.initData()
		self.initGroups()
		if gdx:
			self.db.mergeInternal()

	@property
	def textBlocks(self):
		return {'emissionRegulation': ''.join([getattr(gamsEmissions, k)(self.name) for k in ('SYT','LRP','EB')])}

	@property
	def metaGroup_endo_B(self):
		return Group(f'{self.name}_endo_B', g=[self.groups[f'{self.name}_{k}'] for k in ('alwaysEndo', 'exoInCalib')])
	@property
	def metaGroup_endo_C(self):
		return Group(f'{self.name}_endo_C', g=[self.groups[f'{self.name}_{k}'] for k in ['alwaysEndo']])
	@property
	def metaGroup_exo_B(self):
		return Group(f'{self.name}_exo_B', g=[self.groups[f'{self.name}_{k}'] for k in ['alwaysExo']])
	@property
	def metaGroup_exo_C(self):
		return Group(f'{self.name}_exo_C', g=[self.groups[f'{self.name}_{k}'] for k in ('alwaysExo', 'exoInCalib')])

	@property
	def group_alwaysExo(self):
		return Group(f'{self.name}_alwaysExo', v= [(f'qCO2_{k}', self.g(f't_{k}')) for k in ('SYT','LRP','EB','EB_SYT')]+['tauCO2agg0'])
	@property
	def group_alwaysEndo(self):
		return Group(f'{self.name}_alwaysEndo', v= [('tauCO2agg', ('or', [self.g(f't_{k}') for k in ('SYT','LRP','EB')]+[self.g(f't_{k}_NB') for k in ('SYT','EB')]))])
	@property
	def group_exoInCalib(self):
		return Group(f'{self.name}_exoInCalib', v=[('tauCO2agg', self.g(f"t_{self.CGE.regulation.split('_')[0]}"))])
	@property
	def model_B(self):
		return OrdSet([f"B_{self.name}_{self.CGE.regulation}"])
	@property
	def model_C(self):
		return OrdSet([f"B_{self.name}_{self.CGE.regulation}_Calib"])

	# Adjust some of the standard writing methods: Add regulation statement. 
	def modelName(self, state = 'B'):
		return '_'.join(['M',self.name,state,self.CGE.regulation])
	@property
	def writeModels(self):
		return '\n'.join([self.defineModel(state = k) for k in ('B','C')])


#### Some additional data methods:
def targetsFromSYT(targets, tIdx, q0):
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

def targetsFromSYT_xt0(targets, tIdx, q0):
	d = targetsFromSYT(targets, tIdx, q0)
	t0 = tIdx[0:1] 
	removeT0 = ('not', ('or', [t0, t0.rename('tt')])) # remove t0 if defined over t0 (also if the set is aliased with name tt)
	[d.__setitem__(k,adj.rc_pd(d[k], removeT0, pm = False)) for k in ('t_SYT_NB','qCO2_LRP', 't_LRP', 't2tt_EB', 't_EB_NB')];
	d['qCO2_EB'] = adjMultiIndex.applyMult(d['qCO2_LRP'], d['t2tt_EB'].rename(['tt','t'])).groupby('tt').sum().rename_axis('t') # recompute the emission budget without t0
	return d
