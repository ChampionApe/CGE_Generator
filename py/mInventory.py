from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs
from gmsPython import Group, GModel

class AR(GModel):
	def __init__(self, name, database, itory = 'itory', **kwargs):
		super().__init__(name = name, database = database, **kwargs)
		self.db['s_itory'] = pd.Index([itory], name = 's')
		self.db['d_itory'] = adj.rc_pd(self.db('qD'), self.db('s_itory')).index.droplevel('t').unique()

	# initialize
	def initStuff(self, db = None, gdx = True):
		if db is not None:
			MergeDbs.merge(self.db, db)
		self.initData()
		self.initGroups()
		if gdx:
			self.db.mergeInternal()

	def initData(self):
		self.db.aom(pd.Series(1, index = self.db('d_itory')), name = 'itoryAR', type = 'par')

	@property
	def group_endo(self):
		return Group(f'{self.name}_endo', v = [('qD', ('and', [self.g('d_itory'), self.g('tx0E')]))])
	@property
	def group_exo(self):
		return Group(f'{self.name}_exo',  v = [('qD', ('and', [self.g('d_itory'), self.g('t0')]))])

	def modelName(self, state = 'B'):
		return '_'.join(['M',self.name])
	@property
	def model_B(self):
		return OrdSet([f"B_{self.name}"])
	@property
	def textBlocks(self):
		return {'inventory': self.equationText}

	def fixText(self, **kwargs):
		return self.groups[f'{self.name}_exo'].fix(db = self.db)
	def unfixText(self, **kwargs):
		return self.groups[f'{self.name}_endo'].unfix(db = self.db)

	@property
	def equationText(self):
		return f"""
$BLOCK B_{self.name}
	E_{self.name}[t,s,n]$(d_itory[s,n] and tx0E[t])..	qD[t,s,n] =E= itoryAR[s,n] * qD[t-1,s,n];
$ENDBLOCK
"""
