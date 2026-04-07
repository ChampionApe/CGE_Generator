from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs, GpyDB, AggDB, gpy
from pyDatabases import cartesianProductIndex as cpi
from gmsPython import gmsWrite, Model
import WasteFiles.gamsWaste as gamsWaste

class EstimateTreatCosts(Model):
	def __init__(self, db, RCTech = "'power'", **kwargs):
		super().__init__(name = db.name, database = db, **kwargs)
		self.RCTech = RCTech
		self.compiler.locals['RCTech'] = self.RCTech

	def initData(self):
		AggDB.readSets(self.db, types = ['var','par'])
		self.db['vhat'] = self.db('vDtarget').copy()
		self.db['pWTD'] = pd.Series(1, index = self.db('m'))
		self.db['gamma_d'] = pd.Series(1, index = self.db('m'))
		self.db['gamma_e'] = pd.Series(1, index = self.db('m'))
		self.db['gamma_r'] = pd.Series(1, index = self.db('m'))
		self.db['zetaE'] = pd.Series(1, index = self.db('m'))
		self.db['alpha_l'] = gpy(pd.Series(0, index = self.db('m')), type = 'par')
		self.db['alpha_u'] = pd.Series(1, index = self.db('m'))
		self.db['beta'] = pd.Series(2, index = self.db('m'))
		self.db['gammaAvg'] = 0 # aux. variable in initialization
		self.db['obj'] = 0

	@property
	def writeInit(self):
		return """
# Init
beta.l[m] = 5; # fix at some level
alpha_u.l[m] = (A[m]/R[m])/(1-((R[m]/Rbar[m])**beta.l[m])/(1+beta.l[m]));
gammaAvg.l = (sum(s, vDtarget[s])-sum(m, R[m] * (alpha_u.l[m] *(1-(R[m]/Rbar[m])**beta.l[m])*pm[m]-gamma_we.l[m] * pe)))/sum(m, W[m]); 
gamma_d.l[m] = gammaAvg.l;
gamma_e.l[m] = gammaAvg.l;
gamma_r.l[m] = gamma_e.l[m] + alpha_u.l[m] *(1-(R[m]/Rbar[m])**beta.l[m])*pm[m]-gamma_we.l[m] * pe;
pWTD.l[m] = gamma_d.l[m] * D[m]/W[m]+gamma_e.l[m] * E[m]/W[m] + gamma_r.l[m] * R[m]/W[m] -pm[m] * A[m]/W[m] - gamma_we.l[m] * pe;
zetaE.l[m] = [gamma_r.l[m]-gamma_e.l[m]+gamma_we.l[m]*pe]/pm[m];
vhat.l[s] = sum(m, pWTD.l[m] * WGen2WTD[s,m]);
obj.l = sum(s, sqr((vhat.l[s]-vDtarget[s])/vDtarget[s]));
"""

	def solveText(self, model = 'Main'):
		return f"""
# Bounds:
beta.lo[m] = 0;
beta.up[m] = inf;
alpha_u.lo[m] = 0;
alpha_u.up[m] = 1;
gamma_d.lo[m] = 0;
gamma_e.lo[m] = 0;
gamma_r.lo[m] = 0;
gamma_d.up[m] = inf;
gamma_e.up[m] = inf;
gamma_r.up[m] = inf;
zetaE.lo[m] = -inf;
zetaE.up[m] = inf;
obj.lo = -inf;
obj.up = inf;

# Fix gamma_we or use in estimation?
gamma_we.fx[m] = gamma_we.l[m];
# gamma_we.lo[m] = 0;
# gamma_we.up[m] = inf;

solve M_{model} using NLP min obj;
"""

	def text(self, init = True, model = 'Main'):
		initText = self.writeInit if init else ""
		return f"""
{gmsWrite.StdArgs.root()}
{gmsWrite.StdArgs.funcs()}
{gamsWaste.recyclTech}
{gmsWrite.FromDB.declare(self.db)}
{gmsWrite.FromDB.load(self.db, gdx = self.db.name)}
{initText}

$BLOCK B_Main
	E_vhat[s]..		vhat[s]		=E= sum(m, pWTD[m] * WGen2WTD[s,m]);
	E_pWTD[m]..		pWTD[m] 	=E= gamma_d[m] * D[m]/W[m]+gamma_e[m] * E[m]/W[m] + gamma_r[m] * R[m]/W[m] -pm[m] * A[m]/W[m] - gamma_we[m] * pe * E[m]/W[m];
	E_obj..			obj 		=E= sum(s, sqr((vhat[s]-vDtarget[s])/vDtarget[s]));
	E_alpha_u[m]..	alpha_u[m]	=E= (A[m]/R[m])/(1-((R[m]/Rbar[m])**beta[m])/(1+beta[m]));
	E_zetaE[m]..	zetaE[m]	=E= [gamma_r[m]-gamma_e[m]+gamma_we[m]*pe]/pm[m];
	# E_valueWE..		valueWE 	=E= sum(m, gamma_we[m] * E[m]) * pe;
$ENDBLOCK

$BLOCK B_gamma_r
	E_gamma_r[m]..	gamma_r[m]	=E= gamma_e[m]+alpha_u[m] *(1-(R[m]/Rbar[m])**beta[m])*pm[m]-gamma_we[m] * pe;
$ENDBLOCK
$BLOCK B_Smooth_gamma_r
	E_Smooth_gamma_r[m].. 	R[m]	=E= @RC_ur(alpha_l[m], alpha_u[m], beta[m], zetaE[m], smooth[m]) * Rbar[m];
$ENDBLOCK

$Model M_Main B_Main, B_gamma_r;
$Model M_Smooth B_Main, B_Smooth_gamma_r;

{self.solveText(model=model)}
solve M_Smooth using NLP min obj;
"""

	def __call__(self, init = True, model = 'Main'):
		self.initData()
		self.db.mergeInternal()
		self.job = self.ws.add_job_from_string(self.compiler(self.text(init = init, model = model)))
		self.job.run(databases = self.db.database)
		return GpyDB(self.job.out_db, ws = self.ws)


class CalibFromPWTD(Model):
	def __init__(self, db, RCTech = "'power'", **kwargs):
		super().__init__(name = db.name, database = db, **kwargs)
		self.RCTech = RCTech
		self.compiler.locals['RCTech'] = self.RCTech

	def initData(self):
		AggDB.readSets(self.db, types = ['var','par'])
		self.db['gamma_d'] = pd.Series(1, index = self.db('m'))
		self.db['gamma_e'] = pd.Series(1, index = self.db('m'))
		self.db['gamma_r'] = pd.Series(1, index = self.db('m'))
		self.db['zetaE'] = pd.Series(1, index = self.db('m'))
		self.db['alpha_l'] = gpy(pd.Series(0, index = self.db('m')), type = 'par')
		self.db['alpha_u'] = pd.Series(1, index = self.db('m'))
		self.db['gammaAvg'] = 0 # aux. variable in initialization
		self.db['obj'] = 0 # only used if we need to turn the problem into an NLP problem

	@property
	def writeInit(self):
		return """
# Init
alpha_u.l[m] = (A[m]/R[m])/(1-((R[m]/Rbar[m])**beta.l[m])/(1+beta.l[m]));
gammaAvg.l = (sum(s, vDtarget[s])-sum(m, R[m] * (alpha_u.l[m] *(1-(R[m]/Rbar[m])**beta.l[m])*pm[m]-gamma_we.l[m] * pe)))/sum(m, W[m]); 
gamma_d.l[m] = gammaAvg.l;
gamma_e.l[m] = gammaAvg.l;
gamma_r.l[m] = gamma_e.l[m] + alpha_u.l[m] *(1-(R[m]/Rbar[m])**beta.l[m])*pm[m]-gamma_we.l[m] * pe;
zetaE.l[m] = [gamma_r.l[m]-gamma_e.l[m]+gamma_we.l[m]*pe]/pm[m];
"""

	def text(self, init = True, model = 'Main'):
		initText = self.writeInit if init else ""
		return f"""
{gmsWrite.StdArgs.root()}
{gmsWrite.StdArgs.funcs()}
{gamsWaste.recyclTech}
{gmsWrite.FromDB.declare(self.db)}
{gmsWrite.FromDB.load(self.db, gdx = self.db.name)}
{initText}

$BLOCK B_Main
	E_alpha_u[m]..	alpha_u[m]	=E= (A[m]/R[m])/(1-((R[m]/Rbar[m])**beta[m])/(1+beta[m]));
	E_gamma_d[m]..	gamma_d[m]	=E= gamma_e[m]; # ADHOC CONDITION - WE DO NOT CURRENTLY HAVE IDENTIFICATION.
	E_pWTD[m]..		pWTD[m] 	=E= gamma_d[m] * D[m]/W[m]+gamma_e[m] * E[m]/W[m] + gamma_r[m] * R[m]/W[m] -pm[m] * A[m]/W[m] - gamma_we[m] * pe * E[m]/W[m];
	E_zetaE[m]..	zetaE[m]	=E= [gamma_r[m]-gamma_e[m]+gamma_we[m]*pe]/pm[m];
	# E_obj..			obj 		=E= sum(s, sqr((vhat[s]-vDtarget[s])/vDtarget[s]));
$ENDBLOCK

$BLOCK B_gamma_r
	E_gamma_r[m]..	gamma_r[m]	=E= gamma_e[m]+alpha_u[m] *(1-(R[m]/Rbar[m])**beta[m])*pm[m]-gamma_we[m] * pe;
$ENDBLOCK
$BLOCK B_Smooth_gamma_r
	E_Smooth_gamma_r[m].. 	R[m]	=E= @RC_ur(alpha_l[m], alpha_u[m], beta[m], zetaE[m], smooth[m]) * Rbar[m];
$ENDBLOCK

$Model M_Main B_Main, B_gamma_r;
$Model M_Smooth B_Main, B_Smooth_gamma_r;

{self.solveText(model = model)}
solve M_Smooth using CNS;
"""


	def solveText(self, model = 'Main'):
		return f"""
# Bounds:
beta.fx[m] = beta.l[m];
pWTD.fx[m] = pWTD.l[m];
alpha_u.lo[m] = 0;
alpha_u.up[m] = 1;
gamma_d.lo[m] = 0;
gamma_e.lo[m] = 0;
gamma_r.lo[m] = 0;
gamma_d.up[m] = inf;
gamma_e.up[m] = inf;
gamma_r.up[m] = inf;
zetaE.lo[m] = -inf;
zetaE.up[m] = inf;
# obj.lo = -inf;
# obj.up = inf;

# Fix gamma_we or use in estimation?
gamma_we.fx[m] = gamma_we.l[m];
# gamma_we.lo[m] = 0;
# gamma_we.up[m] = inf;

solve M_{model} using CNS;
"""


	def __call__(self, init = True, model = 'Main'):
		self.initData()
		self.db.mergeInternal()
		self.job = self.ws.add_job_from_string(self.compiler(self.text(init = init, model = model)))
		self.job.run(databases = self.db.database)
		return GpyDB(self.job.out_db, ws = self.ws)


class CalibToGR(Model):
	def __init__(self, db, RCTech = "'power'", **kwargs):
		super().__init__(name = db.name, database = db, **kwargs)
		self.RCTech = RCTech
		self.compiler.locals['RCTech'] = self.RCTech

	def initData(self):
		AggDB.readSets(self.db, types = ['var','par'])
		self.db.aom(pd.Series(1, index = self.db('m')), name = 'beta', priority = 'first')
		self.db.aom(pd.Series(1, index = self.db('m')), name = 'gamma_d', priority='first')
		self.db.aom(pd.Series(1, index = self.db('m')), name = 'gamma_e', priority='first')
		self.db.aom(pd.Series(1, index = self.db('m')), name = 'gamma_r', priority='first')
		self.db.aom(pd.Series(1, index = self.db('m')), name = 'zetaE', priority='first')
		self.db.aom(pd.Series(0, index = self.db('m')), name = 'alpha_l', priority='first')
		self.db.aom(pd.Series(0, index = self.db('m')), name = 'alpha_lTarget', priority='first')
		self.db.aom(pd.Series(1, index = self.db('m')), name = 'alpha_u', priority='first')
		self.db['gammaAvg'] = 0 # aux. variable in initialization
		self.db['obj'] = 0 # only used if we need to turn the problem into an NLP problem
		# Exogenous parameters:
		self.db.aom(gpy(self.db('beta').copy(), type = 'par', name = 'betaTarget'), priority='first')
		# self.db.aom(gpy(pd.Series(1, index = self.db('m'), name = 'betaTarget'), type = 'par'), priority='first')
		self.db.aom(gpy(pd.Series(.1, index = self.db('m'), name = 'dAdR'), type = 'par'), priority='first')
		self.db.aom(gpy(pd.Series(1, index = self.db('m'), name = 'parAlpha_l'), type = 'par'), priority='first')
		self.db.aom(gpy(pd.Series(1/100, index = self.db('m'), name = 'parBeta'), type = 'par'), priority='first')

	@property
	def writeInit(self):
		return """
# Init
alpha_lTarget.l[m] = ((1+beta.l[m]-(R[m]/Rbar[m])**beta.l[m])/(beta.l[m]*(R[m]/Rbar[m])**beta.l[m]))*(dAdR[m]-(A[m]/R[m])*(1-(R[m]/Rbar[m])**beta.l[m])/(1-(R[m]/Rbar[m])**beta.l[m] /(1+beta.l[m])));
alpha_l.l[m] = max(1e-3, alpha_lTarget.l[m]);
alpha_u.l[m] = alpha_l.l[m]+(A[m]/R[m]-alpha_l.l[m])/(1-(R[m]/Rbar[m])**beta.l[m] /(1+beta.l[m]));
gammaAvg.l = (sum(s, vDtarget[s])-sum(m, R[m] * ( (alpha_u.l[m] +(alpha_l.l[m]-alpha_u.l[m])*(R[m]/Rbar[m])**beta.l[m])*pm[m]-gamma_we.l[m] * pe)))/sum(m, W[m]); 
gamma_d.l[m] = gammaAvg.l;
gamma_e.l[m] = gammaAvg.l;
gamma_r.l[m] = gamma_e.l[m] + (alpha_u.l[m]+(alpha_l.l[m]-alpha_u.l[m])*(R[m]/Rbar[m])**beta.l[m])*pm[m]-gamma_we.l[m] * pe;
zetaE.l[m] = [gamma_r.l[m]-gamma_e.l[m]+gamma_we.l[m]*pe]/pm[m];
obj.l = sum(m, parAlpha_l[m] * Sqr(alpha_l.l[m]-alpha_lTarget.l[m])+parBeta[m]*Sqr(beta.l[m]-betaTarget[m]));
"""

	def text(self, init = True, model = 'Main'):
		initText = self.writeInit if init else ""
		return f"""
{gmsWrite.StdArgs.root()}
{gmsWrite.StdArgs.funcs()}
{gamsWaste.recyclTech}
{gmsWrite.FromDB.declare(self.db)}
{gmsWrite.FromDB.load(self.db, gdx = self.db.name)}
{initText}

$BLOCK B_Main
	E_alphalTarget[m]..	alpha_lTarget[m] =E= ((1+beta[m]-(R[m]/Rbar[m])**beta[m])/(beta[m]*(R[m]/Rbar[m])**beta[m]))*(dAdR[m]-(A[m]/R[m])*(1-(R[m]/Rbar[m])**beta[m])/(1-(R[m]/Rbar[m])**beta[m] /(1+beta[m])));
	E_alpha_u[m]..	alpha_u[m]	=E= alpha_l[m]+(A[m]/R[m]-alpha_l[m])/(1-(R[m]/Rbar[m])**beta[m] /(1+beta[m]));
	E_gamma_d[m]..	gamma_d[m]	=E= gamma_e[m]; # ADHOC CONDITION - WE DO NOT CURRENTLY HAVE IDENTIFICATION.
	E_pWTD[m]..		pWTD[m] 	=E= gamma_d[m] * D[m]/W[m]+gamma_e[m] * E[m]/W[m] + gamma_r[m] * R[m]/W[m] -pm[m] * A[m]/W[m] - gamma_we[m] * pe * E[m]/W[m];
	E_zetaE[m]..	zetaE[m]	=E= [gamma_r[m]-gamma_e[m]+gamma_we[m]*pe]/pm[m];
	E_obj..			obj 		=E= sum(m, parAlpha_l[m] * Sqr(alpha_l[m]-alpha_lTarget[m])+parBeta[m]*Sqr(beta[m]-betaTarget[m]));
$ENDBLOCK


$BLOCK B_gamma_r
	E_gamma_r[m]..	gamma_r[m]	=E= gamma_e[m]+(alpha_u[m]+(alpha_l[m]-alpha_u[m])*(R[m]/Rbar[m])**beta[m])*pm[m]-gamma_we[m] * pe;
$ENDBLOCK
$BLOCK B_Smooth_gamma_r
	E_Smooth_gamma_r[m].. 	R[m]	=E= @RC_ur(alpha_l[m], alpha_u[m], beta[m], zetaE[m], smooth[m]) * Rbar[m];
$ENDBLOCK

$Model M_Main B_Main, B_gamma_r;
$Model M_Smooth B_Main, B_Smooth_gamma_r;

{self.solveText(model = model)}
solve M_Smooth using NLP min obj;
"""


	def solveText(self, model = 'Main'):
		return f"""
# Bounds:
pWTD.fx[m] = pWTD.l[m];

beta.lo[m] = 0;
alpha_l.lo[m] = 0;
alpha_l.up[m] = 1;
alpha_lTarget.lo[m] = -inf;
alpha_lTarget.up[m] = inf;
alpha_u.lo[m] = 0;
alpha_u.up[m] = 1;
gamma_d.lo[m] = 0;
gamma_e.lo[m] = 0;
gamma_r.lo[m] = 0;
gamma_d.up[m] = inf;
gamma_e.up[m] = inf;
gamma_r.up[m] = inf;
zetaE.lo[m] = -inf;
zetaE.up[m] = inf;
obj.lo = -inf;
obj.up = inf;

# Fix gamma_we or use in estimation?
gamma_we.fx[m] = gamma_we.l[m];
# gamma_we.lo[m] = 0;
# gamma_we.up[m] = inf;

solve M_{model} using NLP min obj;
"""


	def __call__(self, init = True, model = 'Main'):
		self.initData()
		self.db.mergeInternal()
		self.job = self.ws.add_job_from_string(self.compiler(self.text(init = init, model = model)))
		self.job.run(databases = self.db.database)
		return GpyDB(self.job.out_db, ws = self.ws)



