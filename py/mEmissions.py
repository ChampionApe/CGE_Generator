from auxfuncs import *
from pyDatabases import cartesianProductIndex as cpi
from pyDatabases.gpyDB import MergeDbs
from gmsPython import Group, GModel
import gamsEmissions

class EOP_Simple(GModel):
	def __init__(self, name, techType = 'normal', partial=False, **kwargs):
		super().__init__(name=name, **kwargs)
		# use module in partial or general equilibrium; this affects compilation of groups
		self.partial = partial
		self.techType = techType # the type of technology used

	# Initialize
	def initStuff(self, db=None, gdx=True):
		if db is not None:
			MergeDbs.merge(self.db, db)
		self.initData()
		self.initGroups()
		if gdx:
			self.db.mergeInternal()

	def initData(self):
		self.db.aom(self.db('uCO2'), name='uCO20', priority='first')
		self.db.aom(pd.Series(0, index= cpi([self.db('txE'), self.get('dtauCO2')])), name = 'avgAbateCosts', priority='first')
		self.db.aom(pd.Series(0, index= cpi([self.db('txE'), self.get('dtauCO2')])), name = 'abateCosts', priority='first')
		self.db.aom(pd.Series(0, index=self.db('uCO2').index), name='uAbate', priority='first')
		self.db.aom(pd.Series(0, index=self.db('dqCO2')), name='uCO2Calib', priority='first')
		self.db.aom(pd.Series(self.db('tauCO2agg').xs(self.db('t0')[0])/ 2, index = self.db('t')), name='DACSmooth', priority='first')
		self.db.aom(pd.Series(self.db('tauCO2agg').xs(self.db('t0')[0])/ 2, index=self.db('techPot').index), name='techSmooth', priority='first')
		self.db.aom(1, name='qCO2Base', priority='first')
		self.db.aom(self.db('tauCO2agg').xs(self.db('t0')[0]), name='tauCO2Base', priority='first')
		self.db.aom(1 / 25, name='softConstr', priority='first')
		self.db.aom(0, name='obj')

	@property
	def model_B(self):
		return OrdSet([f"B_{self.name}"])
	@property
	def model_C(self):
		return self.model_B+OrdSet([f"B_{self.name}_calib"])
	@property
	def textBlocks(self):
		return {'emissions': gamsEmissions.EOP_Simple(self.name, cost='techCost[tech,t]')}
	@property
	def textFuncs(self):
		return gamsEmissions.EOPTechFunctions

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
		if not self.partial:
			return Group(f'{self.name}_alwaysExo', v=['techPot', 'techCost', 'techSmooth', 'DACCost', 'DACSmooth', 'tauCO2Base', 'softConstr', 'qCO2Base', 'tauCO2agg',
													  ('tauDist', self.g('dtauCO2')), ('uCO20', self.g('dqCO2'))])
		else:
			self.partial = False
			g = self.group_alwaysExo
			g.v += [('qS', self.g('d_qS'))]
			self.partial = True
			return g

	@property
	def group_alwaysEndo(self):
		return Group(f'{self.name}_alwaysEndo', v=[('qCO2', ('and', [self.g('tx0E'), self.g('dqCO2')])),
												   ('qCO2agg', self.g('txE')),
												   ('tauCO2', self.g('dtauCO2')),
												   ('tauEffCO2', self.g('dtauCO2')),
												   ('uAbate', self.g('dqCO2')),
												   ('avgAbateCosts', self.g('dtauCO2')), 
												   ('abateCosts', self.g('dtauCO2'))])

	@property
	def group_exoInCalib(self):
		return Group(f'{self.name}_exoInCalib', v=[('qCO2', ('and', [self.g('t0'), self.g('dqCO2')]))])

	@property
	def group_endoInCalib(self):
		return Group(f'{self.name}_endoInCalib', v=[('uCO2Calib', self.g('dqCO2')), ('uCO2', self.g('dqCO2'))])


class EOP_EconWideCapital(EOP_Simple):
	def __init__(self, name, partial=False, initFromGms = None, ctype = 'AdHocCosts', **kwargs):
		""" ctype indicates the module """
		super().__init__(name, partial=partial, **kwargs)
		self.initFromGms = initFromGms
		self.ctype = ctype

	def initData(self):
		super().initData()
		self.db.aom(.05, name='rDepr_EOP', priority='first')
		if self.ctype == 'AdHocCosts':
			self.db.aom(25, name='adjCostPar_EOP', priority='first')
		elif self.ctype == 'SqrUtilCosts':
			self.db.aom(25, name='adjCostPar_EOP', priority='first')			
		elif self.ctype == 'SqrAdjCosts':
			self.db.aom(.1, name='adjCostPar_EOP', priority='first')			
		self.db.aom(0, name='Ktvc_EOP', priority='first')
		self.db.aom(pd.Series(self.db('R_LR')+self.db('rDepr_EOP')-1, index = self.db('t')), name = 'pK_EOP', priority='first')
		self.db.aom(pd.Series(1, index = self.db('t')), name = 'qK_EOP', priority='first')
		self.db.aom(self.db('rDepr_EOP')*self.db('qK_EOP'), name = 'qI_EOP', priority='first')
		if self.ctype == 'SqrAdjCosts':
			self.db.aom(pd.Series(0, index = cpi([self.db('txE'), self.db('dqCO2')])), name='adjCostEOP', priority='first')
			self.db.aom(pd.Series(1, index = cpi([self.db('txE'), self.db('dqCO2')])), name='muAdjCostEOP', priority='first')
		elif self.ctype == 'AdHocCosts':
			self.db.aom(pd.Series(1, index = self.db('t')), name = 'qK_EOPopt', priority='first')
			self.db.aom(pd.Series(1, index = self.db('t')), name = 'qK_EOPMax', priority='first')
		elif self.ctype == 'SqrUtilCosts':
			self.db.aom(pd.Series(0, index = cpi([self.db('txE'), self.db('dqCO2')])), name='adjCostEOP', priority='first')
			self.db.aom(pd.Series(1, index = cpi([self.db('txE'), self.db('dqCO2')])), name='muAdjCostEOP', priority='first')
			self.db.aom(pd.Series(1, index = self.db('t')), name = 'qK_EOPopt', priority='first')
			self.db.aom(pd.Series(1, index = self.db('t')), name = 'qK_EOPMax', priority='first')

	@property
	def model_B(self):
		return OrdSet([f"B_{self.name}", f"B_{self.name}_adjCost", f"B_{self.name}_Equi"])
	@property
	def model_C(self):
		return self.model_B+OrdSet([f"B_{self.name}_calib", f"B_{self.name}_calibK0"])

	@property
	def textInit(self):
		return "" if self.initFromGms is None else getattr(gamsEmissions, f'init_{self.ctype}')

	@property
	def textBlocks(self):
		return {'emissions': getattr(gamsEmissions, f'EOP_EWC_{self.ctype}')(self.name)}
	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.v += ['rDepr_EOP', 'adjCostPar_EOP', 'Rrate', 'Ktvc_EOP']
		return g
	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		g.v += [('qK_EOP', self.g('tx0')), ('pK_EOP', self.g('txE')), ('qI_EOP', self.g('txE'))]
		if self.ctype == 'SqrAdjCosts':
			g.v += [('adjCostEOP', ('and', [self.g('txE'), self.g('dqCO2')])), ('muAdjCostEOP', ('and', [self.g('txE'), self.g('dqCO2')]))]
		elif self.ctype == 'AdHocCosts':
			g.v += ['qK_EOPopt', 'qK_EOPMax']
		elif self.ctype == 'SqrUtilCosts':
			g.v += [('adjCostEOP', ('and', [self.g('txE'), self.g('dqCO2')])), ('muAdjCostEOP', ('and', [self.g('txE'), self.g('dqCO2')])), 'qK_EOPopt', 'qK_EOPMax']
		return g

	@property
	def group_endoInCalib(self):
		g = super().group_endoInCalib
		g.v += [('qK_EOP', self.g('t0'))]
		return g

def EmRegTargetsFromSYT(targets, tIdx, q0):
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

def EmRegTargetsFromSYT_xt0(targets, tIdx, q0):
	d = EmRegTargetsFromSYT(targets, tIdx, q0)
	t0 = tIdx[0:1] 
	removeT0 = ('not', ('or', [t0, t0.rename('tt')])) # remove t0 if defined over t0 (also if the set is aliased with name tt)
	[d.__setitem__(k,adj.rc_pd(d[k], removeT0, pm = False)) for k in ('t_SYT_NB','qCO2_LRP', 't_LRP', 't2tt_EB', 't_EB_NB')];
	d['qCO2_EB'] = adjMultiIndex.applyMult(d['qCO2_LRP'], d['t2tt_EB'].rename(['tt','t'])).groupby('tt').sum().rename_axis('t') # recompute the emission budget without t0
	return d

class EmRegSimpleEOP(EOP_Simple):
	def __init__(self, name, partial = False, regulation = None, **kwargs):
		super().__init__(name, partial = partial, **kwargs)
		self.regulation = regulation

	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		if self.regulation is None:
			g.v += ['obj']
			return g
		else:
			g.v += [(f'qCO2_{k}', self.g(f't_{k}')) for k in ('SYT','LRP','EB','EB_SYT')] # add all target variables
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
		g.v += ['obj']
		return g

	@property
	def group_exoInCalib(self):
		g = super().group_exoInCalib
		if self.regulation is None:
			return g
		else:
			g.v += [('tauCO2agg', ('and', [self.g('t0'), self.g(f"t_{self.regulation.split('_')[0]}")]))]
			return g

	# Model blocks
	@property
	def textBlocks(self):
		return super().textBlocks | {'emReg': ''.join([getattr(gamsEmissions, k)(self.name) for k in ('SYT','LRP','EB')])}
	@property
	def model_B(self):
		return super().model_B+self.addRegulationBlocks('B', self.regulation)
	@property
	def model_C(self):
		return super().model_C+self.addRegulationBlocks('C', self.regulation)

	def addRegulationBlocks(self, state, regulation):
		if regulation is None:
			return OrdSet([])
		else:
			return OrdSet([f"B_{self.name}_{self.regulation}_Calib" if state == 'C' else f"B_{self.name}_{self.regulation}"])

	# Adjust some of the standard writing methods:
	def modelName(self, state = 'B'):
		return '_'.join(['M',self.name,state]) if self.regulation is None else '_'.join(['M',self.name,state,self.regulation])
	@property
	def writeModels(self):
		return '\n'.join([self.defineModel(state = k) for k in ('B','C')])
	def solveStatement(self, **kwargs):
		if 'OPT' in noneInit(self.regulation, ''):
			return f"""solve {self.modelName(**kwargs)} using NLP max obj;"""
		else:
			return super().solveStatement(**kwargs)


class EmRegEOP_EconWideCapital(EOP_EconWideCapital):
	def __init__(self, name, partial = False, regulation = None, ctype = 'AdHocCosts', **kwargs):
		super().__init__(name, partial = partial, ctype = ctype, **kwargs)
		self.regulation = regulation

	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		if self.regulation is None:
			g.v += ['obj']
			return g
		else:
			g.v += [(f'qCO2_{k}', self.g(f't_{k}')) for k in ('SYT','LRP','EB','EB_SYT')] # add all target variables
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
		g.v += ['obj']
		return g

	@property
	def group_exoInCalib(self):
		g = super().group_exoInCalib
		if self.regulation is None:
			return g
		else:
			g.v += [('tauCO2agg', self.g(f"t_{self.regulation.split('_')[0]}"))]
			return g

	# Model blocks
	@property
	def textBlocks(self):
		return super().textBlocks | {'emReg': ''.join([getattr(gamsEmissions, k)(self.name) for k in ('SYT','LRP','EB')])}

	@property
	def model_B(self):
		return super().model_B+self.addRegulationBlocks('B', self.regulation)
	@property
	def model_C(self):
		return super().model_C+self.addRegulationBlocks('C', self.regulation)

	def addRegulationBlocks(self, state, regulation):
		if regulation is None:
			return OrdSet([])
		else:
			return OrdSet([f"B_{self.name}_{self.regulation}_Calib" if state == 'C' else f"B_{self.name}_{self.regulation}"])

	# Adjust some of the standard writing methods:
	def modelName(self, state = 'B'):
		return '_'.join(['M',self.name,state]) if self.regulation is None else '_'.join(['M',self.name,state,self.regulation])
	@property
	def writeModels(self):
		return '\n'.join([self.defineModel(state = k) for k in ('B','C')])
	def solveStatement(self, **kwargs):
		if 'OPT' in noneInit(self.regulation, ''):
			return f"""solve {self.modelName(**kwargs)} using NLP max obj;"""
		else:
			return super().solveStatement(**kwargs)
