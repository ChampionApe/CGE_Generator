from gamsSnippets_noOut import *

############################################################
################	1. StaticConsumer		################
############################################################
# 1.1. Simple CRRA value:
def CRRA_vU(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_vU[t,s]$({m}_sm[s] and txE[t])..	vU[t,s]		=E= sum(n$({m}_C[s,n]), qD[t,s,n])**(1-crra[s])/(1-crra[s])+(1+gadj[s])*discF[s]*vU[t+1,s];
	E_{name}_vUT[t,s]$({m}_sm[s] and tE[t])..	vU[t,s]		=E= vU[t-1,s]*(1+vU_tvc[s])/(1+gadj[s]);
$ENDBLOCK
"""

# 1.2. Price/tax blocks: 
def priceBlock(name, m, addInc_tx0 = '', addInc_t0 = ''):
	return f"""
$BLOCK B_{name}
	E_{name}_pD[t,s,n]$({m}_input[s,n] and txE[t])..	pD[t,s,n]		=E= p[t,n]*(1+tauD[t,s,n]); # effective input prices
	E_{name}_w[t,s,n]$({m}_L[s,n] and txE[t])..			pS[t,s,n]		=E= p[t,n]*(1-tauS[t,s,n]); # effective wage rate after taxes
	E_{name}_TotalTax[t,s]$({m}_sm[s] and txE[t])..		TotalTax[t,s]	=E= tauLump[t,s]+sum(n$({m}_input[s,n]), tauD[t,s,n] * p[t,n] * qD[t,s,n])+sum(n$({m}_L[s,n]), tauS[t,s,n]*p[t,n]*qS[t,s,n]); # total tax transfers
	E_{name}_vA0[t,s]$({m}_sm[s] and t0[t])..			vA[t+1,s]		=E= (vA[t,s] * Rrate[t] + sum(n$({m}_L[s,n]), p[t,n]*qS[t,s,n])-sum(n$({m}_input[s,n]), p[t,n]*qD[t,s,n])-TotalTax[t,s]{addInc_t0})/(1+g_LR); # law of motion for household assets, initial year
	E_{name}_vA[t,s]$({m}_sm[s] and tx0E[t])..			vA[t+1,s]		=E= (vA[t,s] * Rrate[t] + sum(n$({m}_L[s,n]), p[t,n]*qS[t,s,n])-sum(n$({m}_input[s,n]), p[t,n]*qD[t,s,n])-TotalTax[t,s]{addInc_tx0})/(1+g_LR); # law of motion for household assets
$ENDBLOCK
"""

# 1.3. Block for calibration of taxes using permannet adjustments. Can accept different tax instruments.
def taxCalibBlock(name, m, taxInstr, taxCond):
	""" taxInstr is a gpy symbol, taxCond is a condition"""
	return f"""
$BLOCK B_{name}
	E_{name}_taxRevPar{Syms.gpyDomains(taxInstr)}{Syms.gpyCondition(taxCond)}..	{Syms.gpy(taxInstr)} =E= {Syms.gpy(taxInstr).replace(taxInstr.name, taxInstr.name+'0')}+taxRevPar[s];
$ENDBLOCK
"""

# 1.4 Init method:
def init_vU(m):
	""" Initialize variables for CRRA-GHH model as in steady state"""
	return f"""
vU.l[t,s]$({m}_sm[s] and txE[t]) = (sum(n$({m}_C[s,n]), qD.l[t,s,n])**(1-crra.l[s])/(1-crra.l[s]))/(1-discF.l[s]*(1+gadj.l[s]));
vU.l[t,s]$({m}_sm[s] and tE[t])  = vU.l[t-1,s];
"""


# 1.5. With GHH preferences
def CRRA_GHH_vU(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_qC[t,s]$({m}_sm[s] and txE[t])..	qC[t,s]		=E= sum([n,nn]$({m}_L2C[s,n,nn]), qD[t,s,nn]-frisch[s]*Lscale[s]*(qS[t,s,n]/Lscale[s])**((1+frisch[s])/frisch[s])/(1+frisch[s]));	
	E_{name}_vU[t,s]$({m}_sm[s] and txE[t])..	vU[t,s]		=E= (qC[t,s]**(1-crra[s]))/(1-crra[s])+(1+gadj[s])*discF[s]*vU[t+1,s];
	E_{name}_vUT[t,s]$({m}_sm[s] and tE[t])..	vU[t,s]		=E= vU[t-1,s]*(1+vU_tvc[s])/(1+gadj[s]);
	E_{name}_qL[t,s,n]$({m}_L[s,n] and txE[t]).. qS[t,s,n]	=E= Lscale[s] * sum(nn$({m}_L2C[s,n,nn]), pS[t,s,n]/pD[t,s,nn])**(frisch[s]);
$ENDBLOCK
"""

def init_GHH_vU(m):
	""" Initialize variables for CRRA-GHH model as in steady state"""
	return f"""
Lscale.l[s]$({m}_sm[s])	= sum([t,n,nn]$(t0[t] and {m}_L2C[s,n,nn]), qS.l[t,s,n] * (pD.l[t,s,nn]/pS.l[t,s,n])**(frisch.l[s]));
qC.l[t,s]$({m}_sm[s] and txE[t]) = sum([n,nn]$({m}_L2C[s,n,nn]), qD.l[t,s,nn]-frisch.l[s]*Lscale.l[s]*(qS.l[t,s,n]/Lscale.l[s])**((1+frisch.l[s])/frisch.l[s])/(1+frisch.l[s]));
vU.l[t,s]$({m}_sm[s] and txE[t]) = (qC.l[t,s]**(1-crra.l[s])/(1-crra.l[s]))/(1-discF.l[s]);
vU.l[t,s]$({m}_sm[s] and tE[t])  = vU.l[t-1,s];
"""

############################################################
################		2. Ramsey			################
############################################################

def CRRA_Euler(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_Euler[t,s,n]$({m}_C[s,n] and tx0E[t])..	qD[t,s,n]	=E= qD[t-1,s,n]*(discF[s]*Rrate[t]*(pD[t-1,s,n]/pD[t,s,n]))**(1/crra[s])/(1+g_LR);
	E_{name}_TVC[t,s]$({m}_sm[s] and tE[t])..			vA[t,s]		=E= vA[t-1,s]*(1+vA_tvc[s])/(1+g_LR);
$ENDBLOCK
"""

############################################################
################		3. IdxFund			################
############################################################

def idxFund(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_vAt0[t,s]$({m}_sm[s] and t0[t])..	vA[t,s]	=E= uIdxFund[s] * vIdxFund[t]+vA_F[s];
$ENDBLOCK
"""
