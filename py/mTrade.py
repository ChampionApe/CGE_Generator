from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs, GpyDB
from gmsPython import gmsWrite, Group, Model

class Armington(Model):
	def __init__(self, name, database, partial = False, dExport = None, **kwargs):
		super().__init__(name = name, database = database, **kwargs)
		self.partial = partial # use module in partial or general equilibrium; this affects compilation of groups 
		self.ns.update({k: f'{self.name}_{k}' for k in ('sm','dExport','nF','nD')})
		self.db[self.n('dExport')] = noneInit(dExport, self.db['dExport']) 
		dom2for_subset = adj.rc_pd(self.db('dom2for'), self.get('dExport')) # subset of full mapping dom2for that current module covers 
		self.db[self.n('nF')] = dom2for_subset.get_level_values('nn').rename('n') # foreign good types covered in the module
		self.db[self.n('nD')] = dom2for_subset.get_level_values('n') # domestic good types included in the module
		self.db[self.n('sm')] = self.get('dExport').get_level_values('s').unique() # relevant foreign sectors covered in this module

	def initStuff(self, db = None, gdx = True):
		if db is not None:
			MergeDbs.merge(self.db, db)
		self.initData()
		self.initGroups()
		if gdx:
			self.db.mergeInternal()

	def initData(self):
		""" Add initial values to database (only the ones data we do not have from an IO database though)"""
		self.db.aom(pd.Series(1, index = self.get('dExport')), name = 'Fscale', priority='first')

	def initGroups(self):
		self.groups = {g.name: g for g in (getattr(self, f'group_{k}') for k in ('alwaysExo','alwaysEndo','exoInCalib','endoInCalib'))}
		[grp() for grp in self.groups.values()]; # initialize groups
		metaGroups = ({g.name: g for g in (getattr(self, f'group_{k}') for k in ('endo_B','endo_C','exo_B','exo_C'))})
		[grp() for grp in metaGroups.values()]; # initialize metagroups
		self.groups.update(metaGroups)

	def solve(self, text = None, state = 'B'):
		self.job = self.ws.add_job_from_string(noneInit(text, self.write(state = state)))
		self.job.run(databases = self.db.database)
		self.out_db = GpyDB(self.job.out_db, ws = self.ws)
		return self.out_db

	def write(self, state = 'B'):
		return self.compiler(self.write_gamY(state = state), has_read_file = False)

	def write_gamY(self, state = 'B'):
		return self.text+self.solveText(state = 'B')

	def models(self, **kwargs):
		return OrdSet([f"B_{self.name}"])

	@property
	def textBlocks(self):
		return {'trade': self.equationText}

	def fixText(self, state ='B'):
		return self.groups[f'{self.name}_exo_{state}'].fix(db = self.db)
	def unfixText(self, state = 'B'):
		return self.groups[f'{self.name}_endo_{state}'].unfix(db = self.db)

	def solveText(self, state = 'B'):
		return f"""
# Fix exogenous variables in state {state}:
{self.fixText(state=state)}

# Unfix endogenous variables in state {state}:
{self.unfixText(state=state)}

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
	E_{self.name}_armington[t,s,n]$({self.name}_dExport[s,n] and txE[t])..	qD[t,s,n]		=E= sum(nn$(dom2for[n,nn]), Fscale[s,n] * (p[t,nn]/pD[t,s,n])**(sigma[s,n]));
	E_{self.name}_pwInp[t,s,n]$({self.name}_dExport[s,n] and txE[t])..		pD[t,s,n]		=E= p[t,n] + tauD[t,s,n];
	E_{self.name}_TaxRev[t,s]$({self.name}_sm[s] and txE[t])..				TotalTax[t,s]	=E= tauLump[t,s]+sum(n$({self.name}_dExport[s,n]), tauD[t,s,n]*qD[t,s,n]);
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
			return Group(f'{self.name}_alwaysExo', v = [('p', self.g('nF')),
														('sigma', self.g('dExport')),
														('tauD', self.g('dExport')),
														('tauLump', ('and', [self.g('sm'), self.g('tx0E')]))])
		else:
			self.partial = False
			g = self.group_alwaysExo
			g.v += [('p', self.g('nD'))]
			self.partial = True
			return g
	@property
	def group_alwaysEndo(self):
		return Group(f'{self.name}_alwaysEndo', v = [('qD', ('and', [self.g('dExport'), self.g('tx0E')])),
													 ('TotalTax', ('and', [self.g('sm'), self.g('tx0E')])),
													 ('pD', self.g('dExport'))])
	@property
	def group_exoInCalib(self):
		return Group(f'{self.name}_exoInCalib', v = [('qD', ('and', [self.g('dExport'), self.g('t0')])), 
													 ('TotalTax', ('and', [self.g('sm'), self.g('t0')]))])
	@property
	def group_endoInCalib(self):
		return Group(f'{self.name}_endoInCalib', v = [('Fscale', self.g('dExport')), ('tauLump', ('and', [self.g('sm'), self.g('t0')]))])
