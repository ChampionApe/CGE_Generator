from auxfuncs import *
from pyDatabases import pdSum
from pyDatabases.gpyDB import gpy, GpyDB, AggDB
from gmsPython import gmsWrite
from gmsPython.gamY import Precompiler

def simpleRAS(v0, vBar, row = 's', col = 'n', leaveCols = None, leaveRows = None, tol = 1e-6, iterMax = 1000):
	cond_n = leaveCols if leaveCols is None else ('not', leaveCols) # what types of goods do we not care abount balancing
	cond_s = leaveRows if leaveRows is None else ('not', leaveRows)
	vD = vBar.combine_first(v0)
	# Check feasibility - do we need to open up some of the vBar restrictions?
	sum_s = adj.rc_pd(pdSum(v0, col), cond_s) # sector sums
	sum_n = adj.rc_pd(pdSum(v0, row), cond_n) # goods sums
	# Find sectors / goods where summing yields zero:
	zero_s = sum_s[sum_s==0]
	zero_n = sum_n[sum_n==0]
	# For infeasible sectors/goods re-open the largest value from vBar that we had otherwise fixed at zero:
	idxMax_s = pd.MultiIndex.from_tuples(adj.rc_pd(v0, zero_s).groupby(zero_s.index.names).idxmax().values, names = v0.index.names) 
	idxMax_n = pd.MultiIndex.from_tuples(adj.rc_pd(v0, zero_n).groupby(zero_n.index.names).idxmax().values, names = v0.index.names)
	vBar = adj.rc_pd(vBar, ('not', idxMax_s.union(idxMax_n))) # remove largest values in otherwise infeasible sector/goods combinations
	vD = vBar.combine_first(v0) # redefine vD

	# Adjust to make sure that sector sums work out:
	sum_si = adj.rc_pd(pdSum(vD,col), cond_s)
	vD = (adj.rc_pd(vD, sum_si) * (sum_s/sum_si)).reorder_levels(vD.index.names).combine_first(vD)
	# Adjust to make sure that goods' sums work out:
	sum_ni = adj.rc_pd(pdSum(vD,row), cond_n)
	vD = (adj.rc_pd(vD, sum_ni) * (sum_n/sum_ni)).reorder_levels(vD.index.names).combine_first(vD)
	# Now, loop through adjustments and exit if/when deviations are less than tolerance level:
	for i in range(iterMax):
		sum_si = adj.rc_pd(pdSum(vD,col), cond_s)
		if max(abs(sum_si-sum_s))<tol:
			break
		else:
			vD = (adj.rc_pd(vD, sum_si) * (sum_s/sum_si)).reorder_levels(vD.index.names).combine_first(vD)
		sum_ni = adj.rc_pd(pdSum(vD, row), cond_n)
		if max(abs(sum_ni-sum_n))<tol:
			break
		else:
			vD = (adj.rc_pd(vD, sum_ni) * (sum_n/sum_ni)).reorder_levels(vD.index.names).combine_first(vD)
	print(f"""Largest deviation summing over {col}: {max(abs(adj.rc_pd(pdSum(vD,col), cond_s)-sum_s))}
Largest deviation summing over {row}: {max(abs(adj.rc_pd(pdSum(vD,row), cond_n)-sum_n))}""")
	return vD


class absRAS:
	def __init__(self, v0, vBar, row = None, col = None, db = None, ws = None, name = "dbRAS", leaveCols=None, leaveRows =None):
		self.db = GpyDB(db, ws = ws, name = name)
		self.col = noneInit(col, v0.index.names[-1])
		self.row = noneInit(row, v0.index.names[-2])
		self.v0 = v0
		self.vBar = vBar
		self.condCol = None if leaveCols is None else ('not', leaveCols)
		self.condRow = None if leaveRows is None else ('not', leaveRows)
		self.checkFeasibility()
		self.initData()

	def __call__(self):
		return Precompiler()(self.rasText)

	@property
	def vD(self):
		return self.vBar.combine_first(self.v0 if 'vD' not in self.db.symbols else self.db('vD'))

	def checkFeasibility(self):
		sum_s = adj.rc_pd(pdSum(self.v0, self.col), self.condRow) # sector sums
		sum_n = adj.rc_pd(pdSum(self.v0, self.row), self.condCol) # goods sums
		# Find sectors / goods where summing yields zero:
		zero_s = sum_s[sum_s==0]
		zero_n = sum_n[sum_n==0]
		# For infeasible sectors/goods re-open the largest value from vBar that we had otherwise fixed at zero:
		idxMax_s = pd.MultiIndex.from_tuples(adj.rc_pd(self.v0, zero_s).groupby(zero_s.index.names).idxmax().values, names = self.v0.index.names) 
		idxMax_n = pd.MultiIndex.from_tuples(adj.rc_pd(self.v0, zero_n).groupby(zero_n.index.names).idxmax().values, names = self.v0.index.names)
		self.vBar = adj.rc_pd(self.vBar, ('not', idxMax_s.union(idxMax_n))) # remove largest values in otherwise infeasible sector/goods combinations

	def initData(self):
		self.db['active'] = adj.rc_pd(self.v0, ('not', self.vBar)).index
		self.db['vD0'] = gpy(adj.rc_pd(self.v0, self.db('active')), type = 'par')
		self.db['vD'] = self.db('vD0').rename('vD') # save as variable
		self.db['rowSum'] = gpy( pdSum(self.v0, self.col).add(-pdSum(self.vBar, self.col), fill_value = 0), type = 'par')
		self.db['colSum'] = gpy( pdSum(self.v0, self.row).add(-pdSum(self.vBar, self.row), fill_value = 0), type = 'par')
		self.db['object'] = 0
		self.db['activeRow'] = adj.rc_pd(self.db('active').droplevel(self.col).unique(), self.condRow)
		self.db['activeCol'] = adj.rc_pd(self.db('active').droplevel(self.row).unique(), self.condCol)
		self.db['adjTerm'] = gpy( pd.Series(0, index = self.db('active'), name = 'adjTerm'))
		AggDB.readSets(self.db)

	@property
	def rasText(self):
		doms = gmsWrite.Syms.gpyDomains(self.db['active'])
		def w(k, c = None, l = ""):
			return gmsWrite.Syms.gpy(self.db[k], c = self.db[c] if c else None, l = l)
		return f"""
{gmsWrite.StdArgs.root()}
{gmsWrite.FromDB.declare(self.db)}
{gmsWrite.FromDB.load(self.db, gdx = self.db.name)}

$BLOCK B_RAS
	E_object..			object	 	 =E= sum({doms}$({w('active')}), Sqr({w('adjTerm')}));
	E_{w('vD')}$({w('active')})..	{w('vD')}	 =E= {w('vD0')}*(1+{w('adjTerm')});
	E_{w('colSum')}$({w('activeCol')})..	{w('colSum')}=E= sum({self.row}$({w('active')}), {w('vD')});
	E_{w('rowSum')}$({w('activeRow')})..	{w('rowSum')}=E= sum({self.col}$({w('active')}), {w('vD')});
$ENDBLOCK

$GROUP G_RAS_endo
	{w('vD', 'active')}
	{w('adjTerm','active')}
	object
;

$UNFIX G_RAS_endo;
{w('vD','active', l = ".lo")} = 0;

solve B_RAS minimizing object using NLP;
"""


class shareRAS:
	def __init__(self, v0, vBar, row = None, col = None, db = None, ws = None, name = "dbRAS", leaveCols = None, leaveRows = None):
		self.db = GpyDB(db, ws = ws, name = name)
		self.col = noneInit(col, v0.index.names[-1])
		self.row = noneInit(row, v0.index.names[-2])
		self.v0 = v0
		self.vBar = vBar
		self.leaveCols = leaveCols
		self.leaveRows = leaveRows

	def __call__(self):
		self.initData()
		return Precompiler()(self.rasText)

	def initData(self):
		self.db['active'] = adj.rc_pd(self.v0, ('not', self.vBar)).index
		self.db['vD0'] = gpy(adj.rc_pd(self.v0, self.db('active')), type = 'par')
		self.db['vD'] = self.db('vD0').rename('vD') # save as variable
		self.db['etaRow'] = pd.Series(1, index = self.db('active'), name = 'etaRow')
		self.db['etaCol'] = pd.Series(1, index = self.db('active'), name = 'etaCol')
		self.db['deltaRow'] = gpy( ((pdSum(self.vBar, self.col)-pdSum(adj.rc_pd(self.v0, self.vBar), self.col))/pdSum(self.db('vD0'), self.col)).fillna(0), type = 'par')
		self.db['deltaCol'] = gpy( ((pdSum(self.vBar, self.row)-pdSum(adj.rc_pd(self.v0, self.vBar), self.row))/pdSum(self.db('vD0'), self.row)).fillna(0), type = 'par')
		self.db['rowSum'] = gpy( pdSum(self.v0, self.col).add(-pdSum(self.vBar, self.col), fill_value = 0), type = 'par')
		self.db['colSum'] = gpy( pdSum(self.v0, self.row).add(-pdSum(self.vBar, self.row), fill_value = 0), type = 'par')
		self.db['object'] = 0
		self.db['activeRow'] = self.db('active').droplevel(self.col).unique() if self.leaveRows is None else adj.rc_pd(self.db('active').droplevel(self.col).unique(), ('not', self.leaveRows))
		self.db['activeCol'] = self.db('active').droplevel(self.row).unique() if self.leaveCols is None else adj.rc_pd(self.db('active').droplevel(self.row).unique(), ('not', self.leaveCols))
		AggDB.readSets(self.db)

	@property
	def rasText(self):
		doms = gmsWrite.Syms.gpyDomains(self.db['active'])
		def w(k, c = None, l = ""):
			return gmsWrite.Syms.gpy(self.db[k], c = self.db[c] if c else None, l = l)
		return f"""
{gmsWrite.StdArgs.root()}
{gmsWrite.FromDB.declare(self.db)}
{gmsWrite.FromDB.load(self.db, gdx = self.db.name)}

$BLOCK B_RAS
	E_object..			object	 	 =E= sum({doms}$({w('active')}), Sqr(({w('etaRow')}-1)/1000)+Sqr(({w('etaCol')}-1)/1000));
	E_{w('vD')}$({w('active')})..	{w('vD')}	 =E= {w('vD0')}*(1-{w('etaRow')}*{w('deltaRow')}-{w('etaCol')}*{w('deltaCol')});
	E_{w('colSum')}$({w('activeCol')})..	{w('colSum')}=E= sum({self.row}$({w('active')}), {w('vD')});
	E_{w('rowSum')}$({w('activeRow')})..	{w('rowSum')}=E= sum({self.col}$({w('active')}), {w('vD')});
$ENDBLOCK

$GROUP G_RAS_endo
	{w('vD', 'active')}
	{w('etaRow', 'active')}
	{w('etaCol','active')}
	object
;

$UNFIX G_RAS_endo;
{w('vD','active', l = ".lo")} = 0;

solve B_RAS minimizing object using QCP;
"""

