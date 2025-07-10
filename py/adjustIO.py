from auxfuncs import *
from pyDatabases.gpyDB import gpy, GpyDB, AggDB
from gmsPython import gmsWrite, Model

class SimpleBalance(Model):
	""" The class takes IO data defined over (s,n) and balances 
		the system for specific sectors, goods. """
	def __init__(self, name = 'adjIO', **kwargs):
		super().__init__(name = name, alias = [('n','nn'),('s','ss')], **kwargs)

	def initData(self, vD0, vS0, vDBar = None, vSBar = None, vDT = None, vST = None, nEQ = None, sT = None):
		""" vD0::: Original demand over IO goods (parameter) 
			vS0::: Original supply over IO goods (parameter)
			vDBar::: Exogenous levels in demand vector. If None = empty series.
			vSBar::: Exogenous levels in supply vector. If None = empty series.
			vDT::: Target vector of demand. If None = vD0.
			vST::: Target vector of supply. If None = vS0.
			nEQ::: Set of goods to ensure eq. for.
			sEQ::: Set of industries to target profits/markup for.  
		"""
		self.db['vD0'] = gpy(vD0, type = 'par')
		self.db['vS0'] = gpy(vS0, type = 'par')
		# Exogenous elements in the supply/demand vectors: Use specified values or default to empty structures.
		self.db['vDBar'] = gpy(noneInit(vDBar, pd.Series(None, index = vD0.index[0:0], name = 'vDBar')), type = 'par')
		self.db['vSBar'] = gpy(noneInit(vSBar, pd.Series(None, index = vS0.index[0:0], name = 'vSBar')), type = 'par')
		# Target vectors: Use specified values or default to initial vectors:
		self.db['vDT'] = gpy(noneInit(vDT, self.db('vD0').copy().rename('vDT')), type = 'par')
		self.db['vST'] = gpy(noneInit(vST, self.db('vS0').copy().rename('vST')), type = 'par') 
		self.db['vDT'].vals = self.db('vDT').combine_first(self.db('vD0'))
		self.db['vST'].vals = self.db('vST').combine_first(self.db('vS0'))
		# What markets do we check for equilibrium: Use specified or default to all goods from the supply vector.
		self.db['nEQ'] = noneInit(nEQ, self.db('vS0').index.levels[-1])
		# What industries do we include specific targets for profit margins: Use specified or default to all industries in the supply vector.
		self.db['sT'] = noneInit(sT, self.db('vS0').index.levels[0])

		# Initialize other data:
		[self.db.__setitem__(f'd{k}', self.db(k).index) for k in ('vD0','vS0','vDBar','vSBar')];
		AggDB.readSets(self.db) # read set definitions from existing symbols
		self.db['vDsolve'] = self.db('vD0').copy().clip(0) # endogenous var.
		self.db['vSsolve'] = self.db('vS0').copy().clip(0) # endogenous var.
		self.db['obj'] = 0
		self.db['LF_vD'] = gpy(pd.Series(1, index = self.db('vDsolve').index, name = 'LF_vD'), type ='par') # load factor in objective
		self.db['LF_vS'] = gpy(pd.Series(1, index = self.db('vSsolve').index, name = 'LF_vS'), type ='par') # load factor in objective

		# Bounds:
		self.db['vDlo'] = gpy(pd.Series(0, index = self.db('vDsolve').index, name = 'vDlo'), type = 'par')
		self.db['vSlo'] = gpy(pd.Series(0, index = self.db('vSsolve').index, name = 'vSlo'), type = 'par')


	@property
	def text(self):
		return f"""
{gmsWrite.StdArgs.root()}
{gmsWrite.StdArgs.funcs()}
{gmsWrite.FromDB.declare(self.db)}
{gmsWrite.FromDB.load(self.db, gdx = self.db.name)}

$BLOCK B_adjustIO
	E_nBalance[n]$(nEQ[n])..	sum(s$(dvS0[s,n]), vSsolve[s,n]) =E= sum(s$(dvD0[s,n]), vDsolve[s,n]);
	E_sBalance[s]$(sT[s])..		sum(n$(dvS0[s,n]), vSsolve[s,n]) =E= sum(n$(dvD0[s,n]), vDsolve[s,n]);
	E_vDBar[s,n]$(dvDBar[s,n])..	vDsolve[s,n]	=E= vDBar[s,n];
	E_vSBar[s,n]$(dvSBar[s,n])..	vSsolve[s,n]	=E= vSBar[s,n];
	E_obj..	obj =E= sum([s,n]$(dvD0[s,n]),  sqr(LF_vD[s,n] * (vD0[s,n]-vDsolve[s,n])))+sum([s,n]$(dvS0[s,n]), sqr(LF_vS[s,n]*(vS0[s,n]-vSsolve[s,n])));
$ENDBLOCK

vDsolve.lo[s,n]$(dvD0[s,n]) = vDlo[s,n];
vDsolve.up[s,n]$(dvD0[s,n]) = inf;
vSsolve.lo[s,n]$(dvS0[s,n]) = vSlo[s,n];
vSsolve.up[s,n]$(dvS0[s,n]) = inf;
obj.lo = -inf;
obj.up = inf;

solve B_adjustIO using NLP min obj;
"""

	def __call__(self, vD0, vS0, **kwargs):
		self.initData(vD0, vS0, **kwargs)
		self.db.mergeInternal()
		self.job = self.ws.add_job_from_string(self.compiler(self.text))
		self.job.run(databases = self.db.database)
		return GpyDB(self.job.out_db, ws = self.ws)