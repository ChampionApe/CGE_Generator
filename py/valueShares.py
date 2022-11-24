from gmsPython import gmsPy, GmsPython, stackIndices
import pyDatabases, pandas as pd
from pyDatabases import OrdSet, adjMultiIndex
from pyDatabases.gpyDB_wheels import aggregateDB, adj
import gamsProduction, gamsHouseholds

class valueShares(GmsPython):
	def __init__(self, tree, db_IO, s=None, s_kwargs = None, valueFromQP = True):
		""" Initialize from nesting tree 'tree'. """
		super().__init__(name=f"valueShare_{tree.name}", s=s, s_kwargs = pyDatabases.noneInit(s_kwargs, {}) | {'db': db_IO})
		self.setsFromTree(tree)
		self.initValues(tree, valueFromQP = valueFromQP)
	def states(self):
		return {'B': self.s.standardInstance(state='B') | {attr: getattr(self,attr)() for attr in ('g_endo','g_exo','blocks','args','solve')}}
	def solve(self):
		return f"""@SolveEmptyNLP({self.s['name']})"""
	def args(self):
		return {'valueShare_Blocks': gamsProduction.valueShares()}
	def blocks(self):
		return OrdSet(['B_ValueShares'])
	def g_endo(self):
		return OrdSet([f"G_{self.name}_endo"])
	def g_exo(self):
		return OrdSet([f"G_{self.name}_exo"])
	def groups(self):
		return {g.name: g for g in self.groups_()}
	def groups_(self):
		return [gmsPy.Group(f"G_{self.name}_exo",
				v = [('vS', self.g('output')), ('vD', self.g('input'))]
				),
				gmsPy.Group(f"G_{self.name}_endo",
				v = [('mu', self.g('map')), ('vD', self.g('int'))])]
	def setsFromTree(self,Tree):
		types = [ti.io for ti in Tree.trees.values()]
		if 'output' in types:
			self.s.db['mapOut']     = stackIndices([ti.get('map') for ti in Tree.trees.values() if ti.io == 'output'])
			self.s.db['knotOutTree']= stackIndices([ti.get('knot') for ti in Tree.trees.values() if ti.io == 'output'])
			self.s.db['branchOut']  = stackIndices([ti.get('branch_o') for ti in Tree.trees.values() if ti.io == 'output'])
			self.s.db['branchNOut'] = stackIndices([ti.get('branch_no') for ti in Tree.trees.values() if ti.io == 'output'])
		else:
			self.s.db['mapOut']     = pd.MultiIndex.from_tuples([], names = ['s','n','nn'])
			self.s.db['knotOutTree']= pd.MultiIndex.from_tuples([], names = ['s','n'])
			self.s.db['branchOut']  = pd.MultiIndex.from_tuples([], names = ['s','n'])
			self.s.db['branchNOut'] = pd.MultiIndex.from_tuples([], names = ['s','n'])
		if 'input' in types:
			self.s.db['mapInp']     = stackIndices([ti.get('map') for ti in Tree.trees.values() if ti.io == 'input'])
			self.s.db['knotOut']	= stackIndices([ti.get('knot_o') for ti in Tree.trees.values() if ti.io == 'input'])
			self.s.db['knotNOut']	= stackIndices([ti.get('knot_no') for ti in Tree.trees.values() if ti.io == 'input'])
			self.s.db['branch2Out'] = stackIndices([ti.get('branch2o') for ti in Tree.trees.values() if ti.io == 'input'])
			self.s.db['branch2NOut']= stackIndices([ti.get('branch2no') for ti in Tree.trees.values() if ti.io == 'input'])
		else:
			self.s.db['mapInp']      = pd.MultiIndex.from_tuples([], names = ['s','n','nn'])
			self.s.db['knotOut']	 = pd.MultiIndex.from_tuples([], names = ['s','n'])
			self.s.db['knotNOut']	 = pd.MultiIndex.from_tuples([], names = ['s','n'])
			self.s.db['branch2Out']  = pd.MultiIndex.from_tuples([], names = ['s','n'])
			self.s.db['branch2NOut'] = pd.MultiIndex.from_tuples([], names = ['s','n'])
		[self.s.db.__setitem__(k, Tree.get(k)) for k in ('map','output','input','int')];
		aggregateDB.readSets(self.s.db, types = ['variable','parameter','mapping'])
		if Tree.namespace:
			aggregateDB.updateSetValues(self.s.db,'n',Tree.namespace, remove_unused_levels = True)

	def initValues(self, Tree, valueFromQP = True):
		tIndex = self.s.db.get('vD').index.levels[0]
		self.s.db['mu'] = adjMultiIndex.bc(pd.Series(1, index = tIndex), Tree.get('map'))
		self.s.db['vD'] = self.initvD(valueFromQP=valueFromQP).combine_first(adjMultiIndex.bc(pd.Series(1, index = tIndex), Tree.get('int')))
		self.s.db['vS'] = self.initvS()
	def initvD(self, valueFromQP=True):
		return self.s.db.get('qD') * self.s.db.get('pD') if valueFromQP else self.s.db.get('vD')
	def initvS(self):
		""" Balance value of outputs to value of inputs"""
		return self.get('vS') * (adj.rc_pd(self.get('vD'), self.get('input')).groupby(['t','s']).sum() / self.get('vS'))


class SimpleRamsey(valueShares):
	def __init__(self, tree, db_IO, s=None, s_kwargs = None):
		""" Initialize from nesting tree 'tree'. """
		super().__init__(tree, db_IO, s = s, s_kwargs = s_kwargs, valueFromQP = False)

	def initValues(self, Tree, valueFromQP = False):
		tIndex = self.s.db.get('vD').index.levels[0]
		self.s.db['mu'] = adjMultiIndex.bc(pd.Series(1, index = tIndex), Tree.get('map'))
		self.s.db['vD'] = self.initvD(valueFromQP=valueFromQP).combine_first(adjMultiIndex.bc(pd.Series(1, index = tIndex), Tree.get('int').union(Tree.get('output'))))

	def args(self):
		return {'valueShare_Blocks': gamsHouseholds.valueShares()}

	def groups_(self):
		return [gmsPy.Group(f"G_{self.name}_exo",
				v = [('vD', self.g('input'))]
				),
				gmsPy.Group(f"G_{self.name}_endo",
				v = [('mu', self.g('map')), ('vD', ('or', [self.g('int'), self.g('output')]))]
				)]
