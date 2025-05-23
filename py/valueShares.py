from auxfuncs import *
from pyDatabases.gpyDB import GpyDB, AggDB
from gmsPython import gmsWrite, stackIndices, Group, Model
from gamsSnippets import valueShares
from gamsSnippets_noOut import valueShares as valueShares_noOut

class InitTree(Model):
	def __init__(self, tree, name = 'initTree', **kwargs):
		super().__init__(name = name, alias = [('n','nn')], **kwargs)
		self.tree = tree
		self.readFromTrees()

	def readFromTrees(self):
		types = [ti.io for ti in self.tree.trees.values()]
		if 'output' in types:
			self.db['mapOut']     = stackIndices([ti.get('map') for ti in self.tree.trees.values() if ti.io == 'output'])
			self.db['knotOutTree']= stackIndices([ti.get('knot') for ti in self.tree.trees.values() if ti.io == 'output'])
			self.db['branchOut']  = stackIndices([ti.get('branch_o') for ti in self.tree.trees.values() if ti.io == 'output'])
			self.db['branchNOut'] = stackIndices([ti.get('branch_no') for ti in self.tree.trees.values() if ti.io == 'output'])
		else:
			self.db['mapOut']     = pd.MultiIndex.from_tuples([], names = ['s','n','nn'])
			self.db['knotOutTree']= pd.MultiIndex.from_tuples([], names = ['s','n'])
			self.db['branchOut']  = pd.MultiIndex.from_tuples([], names = ['s','n'])
			self.db['branchNOut'] = pd.MultiIndex.from_tuples([], names = ['s','n'])
		if 'input' in types:
			self.db['mapInp']     = stackIndices([ti.get('map') for ti in self.tree.trees.values() if ti.io == 'input'])
			self.db['knotOut']	= stackIndices([ti.get('knot_o') for ti in self.tree.trees.values() if ti.io == 'input'])
			self.db['knotNOut']	= stackIndices([ti.get('knot_no') for ti in self.tree.trees.values() if ti.io == 'input'])
			self.db['branch2Out'] = stackIndices([ti.get('branch2o') for ti in self.tree.trees.values() if ti.io == 'input'])
			self.db['branch2NOut']= stackIndices([ti.get('branch2no') for ti in self.tree.trees.values() if ti.io == 'input'])
		else:
			self.db['mapInp']      = pd.MultiIndex.from_tuples([], names = ['s','n','nn'])
			self.db['knotOut']	 = pd.MultiIndex.from_tuples([], names = ['s','n'])
			self.db['knotNOut']	 = pd.MultiIndex.from_tuples([], names = ['s','n'])
			self.db['branch2Out']  = pd.MultiIndex.from_tuples([], names = ['s','n'])
			self.db['branch2NOut'] = pd.MultiIndex.from_tuples([], names = ['s','n'])
		[self.db.__setitem__(k, self.tree.get(k)) for k in ('map','output','input','int')];
		self.db['countInp'] = self.db('mapInp').to_frame(index=False).groupby(['s','n']).count()['nn']
		self.db['countOut'] = self.db('mapOut').to_frame(index = False).groupby(['s','nn']).count()['n'].rename_axis(['s','n'])
		AggDB.readSets(self.db, types = ['var','par','map'], ignore_alias = True) # read set definitions from other symbols
		if self.tree.namespace:
			AggDB.updSetElements(self.db, 'n', self.tree.namespace, rul = True)

	def defaultPD(self, dbIO):
		return adj.rc_pd(dbIO('pD').xs(dbIO('t0')[0]), self.get('input'))
	def defaultPS(self, dbIO):
		return stdSort(adjMultiIndex.bc(adj.rc_pd(dbIO('p').xs(dbIO('t0')[0]), self.get('output')), self.get('input').levels[0]))
	def defaultQD(self, dbIO):
		return adj.rc_pd(dbIO('qD').xs(dbIO('t0')[0]), self.get('input'))
	def defaultQS(self, dbIO):
		return adj.rc_pd(dbIO('qS').xs(dbIO('t0')[0]), self.get('output'))

	def __call__(self, dbIO = None, pD = None, qD = None, pS = None, qS = None, maxIter = 20, balancePS = True):
		""" Get full vectors of pD, qD, and parameters μ. """
		mInp, mOut = self.get('mapInp').copy(), self.get('mapOut').copy()
		if qD is None:
			qD = self.defaultQD(dbIO)
		if pD is None:
			pD = self.defaultPD(dbIO)
		if qS is None:
			qS = self.defaultQS(dbIO)
		if pS is None:
			pS = self.defaultPS(dbIO)
		if balancePS is True:
			pS = pS * ((qD*pD).groupby('s').sum()/(qS * pS).groupby('s').sum())
		μ = pd.Series(1, index = self.get('map'), name = 'mu', dtype = float)
		i = 0
		while not (mInp.empty & mOut.empty):
			if not mInp.empty:
				d = self.getInput(mInp, qD, pD)
				qD = qD.combine_first(d['qD'])
				pD = pD.combine_first(d['pD'])
				μ.loc[d['mu'].index] = d['mu'].astype(float)
				mInp = adj.rc_pd(mInp, ('not', d['qD']))
				# mOut = adj.rc_pd(mOut, ('not', d['qD'].rename_axis(['s','nn'])))
			if not mOut.empty:
				d = self.getOutput(mOut, pD, qD, pS, qS)
				qD = qD.combine_first(d['qD'])
				pD = pD.combine_first(d['pD'])
				μ.loc[d['mu'].index] = d['mu'].astype(float)
				# mInp = adj.rc_pd(mInp, ('not', d['qD']))
				mOut = adj.rc_pd(mOut, ('not', d['qD'].rename_axis(['s','nn'])))
			if i == maxIter:
				break
			else:
				i += 1
		assert i<maxIter, f""" Did not reach convergence, consider increasing maxIter or check nesting structure """
		return {'pD': pD, 'qD': qD, 'pS': pS, 'qS': qS, 'mu': μ}

	def get_qNorm(self, solDict):
		qNormInp = 1/adj.rc_pd(solDict['mu'], self.db('mapInp')).droplevel('n').rename_axis(['s','n'])
		qNormOut = 1/adj.rc_pd(solDict['mu'], self.db('mapOut')).droplevel('nn')
		return {'qDnorm': pd.concat([qNormInp, adj.rc_pd(qNormOut, ('not', self.db('output')))], axis = 0), 
				'qSnorm': adj.rc_pd(qNormOut, self.db('output'))}

	def checkInp(self, m, qD):
		count = adj.rc_pd(m, qD.rename_axis(['s','nn'])).to_frame(index=False).groupby(['s','n']).count()['nn']
		relevantCount = adj.rc_pd(self.db('countInp'), count)
		return relevantCount[relevantCount == count]

	def checkOut(self, m, qi, pi):
		count = adj.rc_pd(m, qi).to_frame(index=False).groupby(['s','nn']).count()['n'].rename_axis(['s','n'])
		relevantCount = adj.rc_pd(self.db('countOut'), count)
		return relevantCount[relevantCount == count]

	def getOutput(self,m,pD,qD,pS,qS, f = 'CET'):
		pi, qi = self.priceQuantOut(m, pD, qD, pS, qS)
		x = self.checkOut(m, qi, pi)
		mx = adj.rc_pd(m, x.rename_axis(['s','nn']))
		q = adj.rc_pd(qi, mx)
		p = adj.rc_pd(pi, mx)
		valuesKnots = adjMultiIndex.applyMult(p * q, mx).groupby(['s','nn']).sum().rename_axis(index = ['s','n'])
		return {'qD': valuesKnots.rename('qD'), 'pD': pd.Series(1, index = valuesKnots.index, name = 'pD'), 'mu': getattr(self, f'μ{f}')(self, q, p, valuesKnots, x, mx)}

	def priceQuantOut(self, m, pD,qD,pS,qS):
		return (pd.concat([adj.rc_pd(pS, adj.rc_pd(m, self.get('output'))), adj.rc_pd(pD, adj.rc_pd(m, ('not', self.get('output'))))], axis = 0), 
				pd.concat([adj.rc_pd(qS, adj.rc_pd(m, self.get('output'))), adj.rc_pd(qD, adj.rc_pd(m, ('not', self.get('output'))))], axis = 0))

	def getInput(self,m,qD,pD, f = 'CES'):
		x = self.checkInp(m,qD) # knots with full information
		mx = adj.rc_pd(m, x) # mapping with relevant knots
		qDi = adj.rc_pd(qD.rename_axis(index = {'n':'nn'}),mx)
		pDi = adj.rc_pd(pD.rename_axis(index = {'n':'nn'}), mx)
		valuesKnots = adjMultiIndex.applyMult(qDi*pDi, mx).groupby(['s','n']).sum()
		return {'qD': valuesKnots.rename('qD'), 'pD': pd.Series(1, index = valuesKnots.index,name='pD'), 'mu': getattr(self, f'μ{f}')(self, qDi, pDi, valuesKnots, x ,mx)}

	@staticmethod
	def μCES(self, qDi, pDi, valuesKnots, x, mx):
		return stdSort(qDi * adjMultiIndex.applyMult(pDi, mx).pow(adj.rc_pd(self.db('sigma'), x)) / valuesKnots)

	@staticmethod
	def μCET(self, q, p, valuesKnots, x, mx):
		return stdSort((q*adjMultiIndex.applyMult(p, mx).pow(-adj.rc_pd(self.db('eta'),x).rename_axis(['s','nn'])))/valuesKnots.rename_axis(['s','nn']))

class nestedShares(Model):
	def __init__(self, tree, name = 'valueshares', **kwargs):
		super().__init__(name = name, alias = [('n','nn')], **kwargs)
		self.tree = tree
		self.f = valueShares

	def initData(self, db_IO, valueFromQP=True):
		types = [ti.io for ti in self.tree.trees.values()]
		if 'output' in types:
			self.db['mapOut']     = stackIndices([ti.get('map') for ti in self.tree.trees.values() if ti.io == 'output'])
			self.db['knotOutTree']= stackIndices([ti.get('knot') for ti in self.tree.trees.values() if ti.io == 'output'])
			self.db['branchOut']  = stackIndices([ti.get('branch_o') for ti in self.tree.trees.values() if ti.io == 'output'])
			self.db['branchNOut'] = stackIndices([ti.get('branch_no') for ti in self.tree.trees.values() if ti.io == 'output'])
		else:
			self.db['mapOut']     = pd.MultiIndex.from_tuples([], names = ['s','n','nn'])
			self.db['knotOutTree']= pd.MultiIndex.from_tuples([], names = ['s','n'])
			self.db['branchOut']  = pd.MultiIndex.from_tuples([], names = ['s','n'])
			self.db['branchNOut'] = pd.MultiIndex.from_tuples([], names = ['s','n'])
		if 'input' in types:
			self.db['mapInp']     = stackIndices([ti.get('map') for ti in self.tree.trees.values() if ti.io == 'input'])
			self.db['knotOut']	= stackIndices([ti.get('knot_o') for ti in self.tree.trees.values() if ti.io == 'input'])
			self.db['knotNOut']	= stackIndices([ti.get('knot_no') for ti in self.tree.trees.values() if ti.io == 'input'])
			self.db['branch2Out'] = stackIndices([ti.get('branch2o') for ti in self.tree.trees.values() if ti.io == 'input'])
			self.db['branch2NOut']= stackIndices([ti.get('branch2no') for ti in self.tree.trees.values() if ti.io == 'input'])
		else:
			self.db['mapInp']      = pd.MultiIndex.from_tuples([], names = ['s','n','nn'])
			self.db['knotOut']	 = pd.MultiIndex.from_tuples([], names = ['s','n'])
			self.db['knotNOut']	 = pd.MultiIndex.from_tuples([], names = ['s','n'])
			self.db['branch2Out']  = pd.MultiIndex.from_tuples([], names = ['s','n'])
			self.db['branch2NOut'] = pd.MultiIndex.from_tuples([], names = ['s','n'])
		[self.db.__setitem__(k, self.tree.get(k)) for k in ('map','output','input','int')];
		self.initValues(db_IO, valueFromQP = valueFromQP)
		AggDB.readSets(self.db, types = ['var','par','map'], ignore_alias = True) # read set definitions from other symbols
		if self.tree.namespace:
			AggDB.updSetElements(self.db, 'n', self.tree.namespace, rul = True)

	def initValues(self, db_IO, valueFromQP=True):
		tIndex = db_IO('vD').index.get_level_values(0).unique()
		self.db['mu'] = adjMultiIndex.bc(pd.Series(1, index = tIndex), self.tree.get('map'))
		vD = db_IO('qD').mul(db_IO('pD'), fill_value=1) if valueFromQP else db_IO('vD')
		self.db['vD'] = vD.combine_first(adjMultiIndex.bc(pd.Series(1, index = tIndex), self.tree.get('int'))).dropna()
		self.db['vS'] = (db_IO('vS') * (adj.rc_pd(self.db('vD'), self.db('input')).groupby(['t','s']).sum()/ db_IO('vS'))).dropna()

	def initGroups(self):
		def g(x):
			return self.db[x]
		self.groups = {'endo': Group('endo', v = [('mu', g('map')),
												  ('vD', g('int'))]),
						'exo': Group('exo' , v = [('vD', g('input')),
												  ('vS', g('output'))])}
		[grp() for grp in self.groups.values()]; # initialize groups

	def __call__(self, db, valueFromQP = True):
		self.initData(db, valueFromQP = valueFromQP)
		self.db.mergeInternal()
		self.initGroups()
		self.job = self.ws.add_job_from_string(self.compiler(self.text))
		self.job.run(databases = self.db.database)
		return GpyDB(self.job.out_db, ws = self.ws)

	@property
	def text(self):
		return f"""
{gmsWrite.StdArgs.root()}
{gmsWrite.StdArgs.funcs()}
{gmsWrite.FromDB.declare(self.db)}
{gmsWrite.FromDB.load(self.db, gdx = self.db.name)}

{self.f()}

{self.groups['exo'].fix(db = self.db)}
{self.groups['endo'].unfix(db = self.db)}

@SolveEmptyNLP(B_ValueShares);
"""

class nestedShares_noOutputs(nestedShares):
	def __init__(self, tree, name = 'valueshares', **kwargs):
		super().__init__(tree, name = name, **kwargs)
		self.f = valueShares_noOut

	def initValues(self, db_IO, valueFromQP = False):
		tIndex = db_IO('vD').index.get_level_values(0).unique()
		self.db['mu'] = adjMultiIndex.bc(pd.Series(1, index = tIndex), self.tree.get('map'))
		vD = db_IO('qD').mul(db_IO('pD'), fill_value=1) if valueFromQP else db_IO('vD')
		self.db['vD'] = vD.combine_first(adjMultiIndex.bc(pd.Series(1, index = tIndex), self.tree.get('int').union(self.tree.get('output')))).dropna()

	def initGroups(self):
		def g(x):
			return self.db[x]
		self.groups = {'endo': Group('endo', v = [('mu', g('map')),
												  ('vD', ('or', [g('int'), g('output')]))]),
						'exo': Group('exo' , v = [('vD', g('input'))])}
		[grp() for grp in self.groups.values()]; # initialize groups

