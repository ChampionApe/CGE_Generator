from gamsSnippets import *


# 1. Map between sector-specific prices and equilibrium ones (policy). Specify total tax revenue. 
def priceWedge(name, m, addMarginal = '', addTax = ''):
	return f"""
$BLOCK B_{name}
	E_{name}_pwInp[t,s,n]$({m}_input[s,n] and txE[t])..			pD[t,s,n]		=E= p[t,n]*(1+tauD[t,s,n]);
	E_{name}_pwOut[t,s,n]$({m}_output[s,n] and txE[t])..		p[t,n] 			=E= (1+markup[s])*(pS[t,s,n]+p[t,n]*tauS[t,s,n]{addMarginal});
	E_{name}_taxRev[t,s]$({m}_sm[s] and txE[t])..				TotalTax[t,s]	=E= tauLump[t,s]+sum(n$({m}_input[s,n]), tauD[t,s,n] * p[t,n] * qD[t,s,n])+sum(n$({m}_output[s,n]), tauS[t,s,n]*p[t,n]*qS[t,s,n]){addTax};
$ENDBLOCK
"""

# 2. Add block of equations used to balance tax revenue using permanent adjustments:
def taxCalibration(name, m, taxInstr, taxCond):
	""" taxInstr is a gpy symbol, taxCond is a condition"""
	return f"""
$BLOCK B_{name}
	E_{name}_taxCal{Syms.gpyDomains(taxInstr)}{Syms.gpyCondition(taxCond)}..	{Syms.gpy(taxInstr)} =E= {Syms.gpy(taxInstr).replace(taxInstr.name, taxInstr.name+'0')}+taxRevPar[s];
$ENDBLOCK
"""

# 3. Value of the firm
def firmValue(name, m, addCosts = ''):
	return f"""
$BLOCK B_{name}
	E_{name}_vA[t,s]$({m}_sm[s] and tx0[t])..		vA[t,s]	=E= (vA[t-1,s]*Rrate[t-1]-divd[t-1,s])/((1+g_LR)*(1+infl_LR));
	E_{name}_divd[t,s]$({m}_sm[s] and txE[t])..		divd[t,s] =E= sum(n$({m}_output[s,n]), p[t,n] * qS[t,s,n])-sum(n$({m}_input[s,n]), p[t,n] * qD[t,s,n])-TotalTax[t,s]{addCosts};
	E_{name}_vAT[t,s]$({m}_sm[s] and tE[t])..		vA[t,s]	  =E= (1+vA_tvc[s])*vA[t-1,s];
$ENDBLOCK
"""

# 4. Dynamic equations for capital accumulation:
def capitalAccumulation(name, m, adjCosts = False):
	return capitalAccumulationSimple(name,m) if not adjCosts else capitalAccumulationSqrAdjCosts(name,m)

def capitalAccumulationSimple(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_lom[t,s,n]$({m}_dur[s,n] and txE[t])..		qD[t+1,s,n]	=E= (qD[t,s,n]*(1-rDepr[t,s,n])+sum(nn$({m}_dur2inv[s,n,nn]), qD[t,s,nn]))/(1+g_LR);
	E_{name}_pk[t,s,n]$({m}_dur[s,n] and tx0E[t])..		pD[t,s,n]	=E= sum(nn$({m}_dur2inv[s,n,nn]), Rrate[t]*pD[t-1,s,nn]+(rDepr[t,s,n]-1)*pD[t,s,nn]);
	E_{name}_K_tvc[t,s,n]$({m}_dur[s,n] and tE[t])..	qD[t,s,n]	=E= (1+K_tvc[s,n])*qD[t-1,s,n];
$ENDBLOCK
"""
# With adjustment costs: 
def capitalAccumulationSqrAdjCosts(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_lom[t,s,n]$({m}_dur[s,n] and txE[t])..		qD[t+1,s,n]	=E= (qD[t,s,n]*(1-rDepr[t,s,n])+sum(nn$({m}_dur2inv[s,n,nn]), qD[t,s,nn]))/(1+g_LR);
	E_{name}_pk[t,s,n]$({m}_dur[s,n] and tx02E[t])..	pD[t,s,n]	=E= sum(nn$({m}_dur2inv[s,n,nn]), Rrate[t]*(pD[t-1,s,nn]+adjCostPar[s,n]*(qD[t-1,s,nn]/qD[t-1,s,n]-(rDepr[t-1,s,n]+g_LR)))/(1+infl_LR)+(adjCostPar[s,n]*0.5*(sqr(rDepr[t,s,n]+g_LR)-sqr(qD[t,s,nn]/qD[t,s,n]))-(1-rDepr[t,s,n])*(pD[t,s,nn]+adjCostPar[s,n]*(qD[t,s,nn]/qD[t,s,n]-(rDepr[t,s,n]+g_LR)))));
	E_{name}_pkT[t,s,n]$({m}_dur[s,n] and t2E[t])..		pD[t,s,n]	=E= sum(nn$({m}_dur2inv[s,n,nn]), Rrate[t]*(pD[t-1,s,nn]+adjCostPar[s,n]*(qD[t-1,s,nn]/qD[t-1,s,n]-(rDepr[t-1,s,n]+g_LR)))/(1+infl_LR)+(rDepr[t,s,n]-1)*pD[t,s,nn]);
	E_{name}_K_tvc[t,s,n]$({m}_dur[s,n] and tE[t])..	qD[t,s,n]	=E= (1+K_tvc[s,n])*qD[t-1,s,n];
	E_{name}_adjCost[t,s]$({m}_sm[s] and txE[t])..		adjCost[t,s] 	=E= sum([n,nn]$({m}_dur2inv[s,n,nn]), adjCostPar[s,n]*0.5*qD[t,s,n]*sqr(qD[t,s,nn]/qD[t,s,n]-(rDepr[t,s,n]+g_LR)));
$ENDBLOCK
"""

def initFirmValue(m, addCosts = ''):
	return f"""
	divd.l[t,s]$({m}_sm[s] and txE[t]) = sum(n$({m}_output[s,n]), p.l[t,n] * qS.l[t,s,n])-sum(n$({m}_input[s,n]), p.l[t,n]*qD.l[t,s,n])-TotalTax.l[t,s]{addCosts};
	vA.l[t,s]$({m}_sm[s] and txE[t]) = divd.l[t,s]/(R_LR-1);
	vA.l[t,s]$({m}_sm[s] and tE[t])	= divd.l[t-1,s]/(R_LR-1);
"""


# X: System of value shares
def valueShares():
	return f"""
$BLOCK B_ValueShares
	E_Out_knot[t,s,n]$(knotOutTree[s,n])..								vD[t,s,n]	=E= sum(nn$(map[s,nn,n] and branchOut[s,nn]), vS[t,s,n])+sum(nn$(map[s,nn,n] and branchNOut[s,nn]), vD[t,s,n]);
	E_Out_shares_o[t,s,n,nn]$(mapOut[s,n,nn] and branchOut[s,n])..		mu[t,s,n,nn]=E= vS[t,s,n]/vD[t,s,nn];
	E_Out_shares_no[t,s,n,nn]$(mapOut[s,n,nn] and branchNOut[s,n])..	mu[t,s,n,nn]=E= vD[t,s,n]/vD[t,s,nn];
	E_Inp_knot_o[t,s,n]$(knotOut[s,n])..								vS[t,s,n]	=E= sum(nn$(map[s,n,nn]), vD[t,s,nn]);
	E_Inp_knot_no[t,s,n]$(knotNOut[s,n])..								vD[t,s,n]	=E= sum(nn$(map[s,n,nn]), vD[t,s,nn]);
	E_Inp_shares2o[t,s,n,nn]$(mapInp[s,n,nn] and branch2Out[s,nn])..	mu[t,s,n,nn]=E= vD[t,s,nn]/vS[t,s,n];
	E_Inp_shares2no[t,s,n,nn]$(mapInp[s,n,nn] and branch2NOut[s,nn])..	mu[t,s,n,nn]=E= vD[t,s,nn]/vD[t,s,n];
$ENDBLOCK
"""
