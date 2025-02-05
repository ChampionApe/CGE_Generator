from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs, GpyDB
from gmsPython import gmsWrite, Group, Model

class AR(Model):
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

	def initGroups(self):
		self.groups = {g.name: g for g in (getattr(self, f'group_{k}') for k in ('endo','exo'))}
		[grp() for grp in self.groups.values()]; # initialize groups
	@property
	def group_endo(self):
		return Group(f'{self.name}_endo', v = [('qD', ('and', [self.g('d_itory'), self.g('tx0E')]))])
	@property
	def group_exo(self):
		return Group(f'{self.name}_exo',  v = [('qD', ('and', [self.g('d_itory'), self.g('t0')]))])

	def solve(self, text = None):
		self.job = self.ws.add_job_from_string(noneInit(text, self.write()))
		self.job.run(databases = self.db.database)
		self.out_db = GpyDB(self.job.out_db, ws = self.ws)
		return self.out_db

	def write(self):
		return self.compiler(self.write_gamY(), has_read_file = False)

	def write_gamY(self):
		return self.text+self.solveText()

	def models(self, **kwargs):
		return OrdSet([f"B_{self.name}"])

	@property
	def textBlocks(self):
		return {'inventory': self.equationText}

	def fixText(self, **kwargs):
		return self.groups[f'{self.name}_exo'].fix(db = self.db)
	def unfixText(self, **kwargs):
		return self.groups[f'{self.name}_endo'].unfix(db = self.db)

	def solveText(self, **kwargs):
		return f"""
# Fix exogenous variables:
{self.fixText()}

# Unfix endogenous variables:
{self.unfixText()}

solve M_{self.name} using CNS;
"""

	@property
	def text(self):
		return f"""
{gmsWrite.StdArgs.root()}
{gmsWrite.StdArgs.funcs()}
{gmsWrite.FromDB.declare(self.db)}
{gmsWrite.FromDB.load(self.db, gdx = self.db.name)}

{''.join(self.textBlocks.values())}
$Model M_{self.name} {','.join(self.models())};
""" 

	@property
	def equationText(self):
		return f"""
$BLOCK B_{self.name}
	E_{self.name}[t,s,n]$(d_itory[s,n] and tx0E[t])..	qD[t,s,n] =E= itoryAR[s,n] * qD[t-1,s,n];
$ENDBLOCK
"""
