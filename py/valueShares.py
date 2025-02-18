from auxfuncs import *
from pyDatabases.gpyDB import GpyDB, AggDB
from gmsPython import gmsWrite, stackIndices, Group, Model
from gamsSnippets import valueShares
from gamsSnippets_noOut import valueShares as valueShares_noOut


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

