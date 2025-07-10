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
		[self.db.__setitem__(k, getattr(self.tree, k)) for k in ('mapOut','knotOutTree','branchOut','branchNOut',
																 'mapInp','knotOut','knotNOut', 'branch2Out','branch2NOut')];
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

	def getInputIte(self, mInp, pD, qD, pS, qS, f = 'CES'):
		x = self.checkInp(mInp, qD) # returns knots in the nesting structure with data on all relevant branches.
		mx = adj.rc_pd(mInp, x) # mapping with relevant knots
		mx2Out = adj.rc_pd(mx, self.get('output')) # part of mapping that maps to outputs
		mx2Inp = mx.difference(mx2Out) # part of mapping that maps to intermediate nests
		# Get quantities and prices for all branches - separate those with outputs/inputs in relevant knots: 
		qDi2Out = adj.rc_pd(qD.rename_axis(index = {'n':'nn'}),mx2Out) # vector of branch quantities in relevant nests
		pDi2Out = adj.rc_pd(pD.rename_axis(index = {'n':'nn'}),mx2Out) # vector of branch prices in relevant nests
		qDi2Inp = adj.rc_pd(qD.rename_axis(index = {'n':'nn'}),mx2Inp) # vector of branch quantities in relevant nests 
		pDi2Inp = adj.rc_pd(pD.rename_axis(index = {'n':'nn'}),mx2Inp) # vector of branch prices in relevant nests
		# Get prices or use default = 1 for knots:
		pKnotsInp = adjMultiIndex.applyMult(adj.rc_pd(pD, mx2Inp), mx2Inp).combine_first(pd.Series(1, index = mx2Inp))
		pKnotsOut = adjMultiIndex.applyMult(adj.rc_pd(pS, mx2Out), mx2Out).combine_first(pd.Series(1, index = mx2Out))
		# Define value of knots from sum of branches: 
		valueKnotsInp = adjMultiIndex.applyMult(qDi2Inp * pDi2Inp, mx2Inp).groupby(['s','n']).sum()
		valueKnotsOut = adjMultiIndex.applyMult(qDi2Out * pDi2Out, mx2Out).groupby(['s','n']).sum()
		# Imply quantities of knots from value / prices (thus, assumes CRS technology):
		qKnotsInp = valueKnotsInp / pKnotsInp # note these are mapped to [s,n,nn]
		qKnotsOut = valueKnotsOut / pKnotsOut # note these are mapped to [s,n,nn]
		return {'qD': qKnotsInp.groupby(['s','n']).first(), 'qS': qKnotsOut.groupby(['s','n']).first(), 
				'pD': pKnotsInp.groupby(['s','n']).first(), 'pS': pKnotsOut.groupby(['s','n']).first(), 
				'mu': pd.concat([getattr(self, f'μ{f}')(self, qDi2Inp, pDi2Inp, pKnotsInp, qKnotsInp, mx2Inp), 
								 getattr(self, f'μ{f}')(self, qDi2Out, pDi2Out, pKnotsOut, qKnotsOut, mx2Out)], axis = 0), 'mx': mx}

	def inputIte(self, mInp, pD, qD, pS, qS,μ):
		""" Returns True if changes are made - else False."""
		i0 = len(mInp)
		if not mInp.empty:
			d = self.getInputIte(mInp, pD, qD, pS, qS)
			qD = qD.combine_first(d['qD'])
			pD = pD.combine_first(d['pD'])
			qS = qS.combine_first(d['qS'])
			pS = pS.combine_first(d['pS'])
			μ.loc[d['mu'].index] = d['mu'].astype(float)
			mInp = adj.rc_pd(mInp, ('not', d['mx']))
		status = False if len(mInp) == i0 else True
		return mInp, pD, qD, pS, qS, μ, status

	def checkInp(self, m, qD):
		count = adj.rc_pd(m, qD.rename_axis(['s','nn'])).to_frame(index=False).groupby(['s','n']).count()['nn']
		relevantCount = adj.rc_pd(self.db('countInp'), count)
		return relevantCount[relevantCount == count]

	@staticmethod
	def μCES(self, qDi, pDi, pKnots, qKnots, mx):
		return stdSort(qDi * (pDi/pKnots).pow(adj.rc_pd(self.db('sigma'), mx)) / qKnots)

	def getOutputIte(self, mOut, pD, qD, pS, qS, f = 'CET'):
		pi, qi = self.priceQuantOut(mOut, pD, qD, pS, qS) # get relevant parts of quantity/price vectors.
		x = self.checkOut(mOut, qi) # mapping with relevant knots
		mx = adj.rc_pd(mOut, x.rename_axis(['s','nn'])) # part of mapping with relevant knots
		q = adj.rc_pd(qi, mx) # part of q vector with relevant knots
		p = adj.rc_pd(pi, mx) # part of p vector with relevant knots
		# Get prices for knots or use default = 1:
		pKnots = stdSort(adjMultiIndex.applyMult(adj.rc_pd(pD.rename_axis(['s','nn']), mx), mx)).combine_first(pd.Series(1, index = mx))
		# Define value of knots from sum of branches:
		valueKnots = adjMultiIndex.applyMult((p*q), mx).groupby(['s','nn']).sum() # note this is mapped to [s,n,nn]
		# Implied quantities of knots:
		qKnots = stdSort(valueKnots/pKnots)
		return {'qD': qKnots.groupby(['s','nn']).first().rename_axis(['s','n']), 
				'pD': pKnots.groupby(['s','nn']).first().rename_axis(['s','n']),
				'mu': getattr(self, f'μ{f}')(self, q, p, pKnots, qKnots, mx, x), 'mx': mx}

	def outputIte(self, mOut, pD, qD, pS, qS,μ):
		""" Returns True if changes are made - else False."""
		i0 = len(mOut)
		if not mOut.empty:
			d = self.getOutputIte(mOut, pD, qD, pS, qS)
			qD = qD.combine_first(d['qD'])
			pD = pD.combine_first(d['pD'])
			μ.loc[d['mu'].index] = d['mu'].astype(float)
			mOut = adj.rc_pd(mOut, ('not', d['mx']))
		status = False if len(mOut) == i0 else True
		return mOut, pD, qD, pS, qS, μ, status

	def priceQuantOut(self, m, pD,qD,pS,qS):
		return (pd.concat([adj.rc_pd(pS, adj.rc_pd(m, self.get('output'))), adj.rc_pd(pD, adj.rc_pd(m, ('not', self.get('output'))))], axis = 0), 
				pd.concat([adj.rc_pd(qS, adj.rc_pd(m, self.get('output'))), adj.rc_pd(qD, adj.rc_pd(m, ('not', self.get('output'))))], axis = 0))

	def checkOut(self, m, qi):
		count = adj.rc_pd(m, qi).to_frame(index=False).groupby(['s','nn']).count()['n'].rename_axis(['s','n'])
		relevantCount = adj.rc_pd(self.db('countOut'), count)
		return relevantCount[relevantCount == count]

	@staticmethod
	def μCET(self, q, p, pKnots, qKnots, mx, x):
		return stdSort(q * (pKnots/p).pow(adj.rc_pd(self.db('eta'), x).rename_axis(['s','nn'])) / qKnots)

	def getTroubleNestIte(self, mOut, pD, qD, pS, qS, μ, f = 'CET'):
		# Identify nests:
		x = adj.rc_pd(mOut, ('not', self.db('output'))).droplevel('n').unique().rename(['s','n']) # Knots in trouble nests 
		x = adj.rc_pd(x, qD) # knots that we also have data on
		mx = adj.rc_pd(mOut, x.rename(['s','nn'])) # part of mapping with relevant knots
		# Data on relevant knots:
		pKnots = stdSort(adjMultiIndex.applyMult(adj.rc_pd(pD.rename_axis(['s','nn']), mx), mx)) # note this is mapped to [s,n,nn]
		qKnots = stdSort(adjMultiIndex.applyMult(adj.rc_pd(qD.rename_axis(['s','nn']), mx), mx)) # note this is mapped to [s,n,nn]
		# Get price/quantity points on branches that we may have data on:
		p0 = adj.rc_pd(pD, mx).combine_first(adj.rc_pd(pS, mx))
		q0 = adj.rc_pd(qD, mx).combine_first(adj.rc_pd(qS, mx))
		# Specify the part of the nesting tree with data on branches:
		mx0 = adj.rc_pd(mx, q0) # map
		x0  = adj.rc_pd(x, mx0.droplevel('n').rename(['s','n'])) # relevant knots
		# For branches where we have prices/quantities, we can calculate μ directly using CET formula:
		μ0 = getattr(self, f'μ{f}')(self, q0, p0, adj.rc_pd(pKnots, x0), adj.rc_pd(qKnots, x0), mx0, x0)
		# Other μ parameters, not yet determined - get initial values (default ones):
		μOth = adj.rc_pd(μ, mx.difference(μ0.index)) # free μ parameters in calibration
		# Get elasticities for relevant nests:
		η = adj.rc_pd(self.db('eta'), x).rename_axis(['s','nn'])
		η0 = adj.rc_pd(self.db('eta'), x0)
		# Compute μOth that is consistent with CRS technology and value of relevant knots:
		ΔpKnot_p0 = pKnots.pow(1-η).sub((μ0*p0.pow(η0)).groupby(['s','nn']).sum(), fill_value=0) 
		μOthsum = μOth.groupby(['s','nn']).sum()
		μbar = ΔpKnot_p0 / μOthsum
		μOth = μOth * μbar # rescale μs to ensure CRS constraint holds
		# add default prices = 1 where we do not have data on branches. 
		pOth = pd.Series(1, index = mx.difference(mx0).droplevel('nn'))
		# Compute quantities for the final branches using CET formula:
		qOth = μOth * (pOth / adj.rc_pd(pKnots, pOth))**(adj.rc_pd(η, μOth)) * adj.rc_pd(qKnots, pOth)
		return {'qD': qOth.droplevel('nn'), 'pD': pOth, 'mu': pd.concat([μ0, μOth], axis = 0), 'mx': mx}

	def troubleNestIte(self, mOut, pD, qD, pS, qS, μ):
		i0 = len(mOut)
		if not mOut.empty:
			d = self.getTroubleNestIte(mOut, pD, qD, pS, qS, μ)
			qD = qD.combine_first(d['qD'])
			pD = pD.combine_first(d['pD'])
			μ.loc[d['mu'].index] = d['mu'].astype(float)
			mOut = adj.rc_pd(mOut, ('not', d['mx']))
		status = False if len(mOut) == i0 else True
		return mOut, pD, qD, pS, qS, μ, status

	def __call__(self, dbIO = None, pD = None, qD = None, pS = None, qS = None, maxIter = 20, μ = None, balancePS = True):
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
		if μ is not None:
			μ = μ.combine_first(pd.Series(1, index = self.get('map'), name = 'mu', dtype = float))
		else:
			μ = pd.Series(1, index = self.get('map'), name = 'mu', dtype = float)
		counter = 0
		progress = True
		while progress:
			mInp, pD, qD, pS, qS, μ, progressInp = self.inputIte( mInp, pD, qD, pS, qS, μ)
			mOut, pD, qD, pS, qS, μ, progressOut = self.outputIte(mOut, pD, qD, pS, qS, μ)
			if not any((progressInp, progressOut)):
				mOut, pD, qD, pS, qS, μ, progressTN = self.troubleNestIte(mOut, pD, qD, pS, qS, μ)
			else:
				progressTN = False
			progress = any((progressInp, progressOut, progressTN))
			if counter == maxIter:
				break
			else:
				counter += 1
		if not all((mOut.empty, mInp.empty)):
			print("WARNING: Did not populate entire nesting tree")
		return {'pD': pD, 'qD': qD, 'pS': pS, 'qS': qS, 'mu': μ}


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

