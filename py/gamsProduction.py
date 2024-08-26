from gamsSnippets import *

# 1: Dynamic equations for capital accumulation, firm value and dividends 
def sqrAdjCosts(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_lom[t,s,n]$({m}_dur[s,n] and txE[t])..		qD[t+1,s,n]	=E= (qD[t,s,n]*(1-rDepr[t,s,n])+sum(nn$({m}_dur2inv[s,n,nn]), qD[t,s,nn]))/(1+g_LR);
	E_{name}_pk[t,s,n]$({m}_dur[s,n] and tx02E[t])..	pD[t,s,n]	=E= sqrt(sqr(sum(nn$({m}_dur2inv[s,n,nn]), Rrate[t]*pD[t-1,s,nn]*(1+adjCostPar[s,n]*(qD[t-1,s,nn]/qD[t-1,s,n]-(rDepr[t-1,s,n]+g_LR)))/(1+infl_LR)+pD[t,s,nn]*(adjCostPar[s,n]*0.5*(sqr(rDepr[t,s,n]+g_LR)-sqr(qD[t,s,nn]/qD[t,s,n]))-(1-rDepr[t,s,n])*(1+adjCostPar[s,n]*(qD[t,s,nn]/qD[t,s,n]-(rDepr[t,s,n]+g_LR)))))));
	E_{name}_pkT[t,s,n]$({m}_dur[s,n] and t2E[t])..		pD[t,s,n]	=E= sum(nn$({m}_dur2inv[s,n,nn]), Rrate[t]*pD[t-1,s,nn] * (1+adjCostPar[s,n]*(qD[t-1,s,nn]/qD[t-1,s,n]-(rDepr[t-1,s,n]+g_LR)))/(1+infl_LR) + (rDepr[t,s,n]-1)*pD[t,s,nn]);
	E_{name}_K_tvc[t,s,n]$({m}_dur[s,n] and tE[t])..	qD[t,s,n]	=E= (1+K_tvc[s,n])*qD[t-1,s,n];
	E_{name}_adjCost[t,s]$({m}_sm[s] and txE[t])..		adjCost[t,s] 	=E= sum([n,nn]$({m}_dur2inv[s,n,nn]), pD[t,s,nn] * adjCostPar[s,n]*0.5*qD[t,s,n]*sqr(qD[t,s,nn]/qD[t,s,n]-(rDepr[t,s,n]+g_LR)));
$ENDBLOCK
"""

def firmValueWithAdjCosts(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_vA[t,s]$({m}_sm[s] and tx2E[t])..		vA[t,s] =E= (divd[t+1,s]+vA[t+1,s])/(Rrate[t+1]*(1+g_LR)*(1+infl_LR));
	E_{name}_divd[t,s]$({m}_sm[s] and txE[t])..		divd[t,s] =E= sum(n$({m}_output[s,n]), p[t,n] * qS[t,s,n])-sum(n$({m}_input[s,n]), p[t,n] * qD[t,s,n])-adjCost[t,s]-TotalTax[t,s];
	E_{name}_vAT[t,s]$({m}_sm[s] and t2E[t])..		vA[t,s]	  =E= divd[t,s]/(R_LR-1);
$ENDBLOCK
"""

def firmValueWithAdjCostsAndAbateTech(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_vA[t,s]$({m}_sm[s] and tx2E[t])..		vA[t,s] =E= (divd[t+1,s]+vA[t+1,s])/(Rrate[t+1]*(1+g_LR)*(1+infl_LR));
	E_{name}_divd[t,s]$({m}_sm[s] and txE[t])..		divd[t,s] =E= sum(n$({m}_output[s,n]), p[t,n] * qS[t,s,n])-sum(n$({m}_input[s,n]), p[t,n] * qD[t,s,n])-adjCost[t,s]-TotalTax[t,s]-abateCosts[t,s];
	E_{name}_vAT[t,s]$({m}_sm[s] and t2E[t])..		vA[t,s]	  =E= divd[t,s]/(R_LR-1);
$ENDBLOCK
"""

def initFirmValue(m):
	return f"""
	divd.l[t,s]$({m}_sm[s] and txE[t]) = sum(n$({m}_output[s,n]), p.l[t,n] * qS.l[t,s,n])-sum(n$({m}_input[s,n]), p.l[t,n]*qD.l[t,s,n])-TotalTax.l[t,s];
	vA.l[t,s]$({m}_sm[s] and txE[t]) = divd.l[t,s]/(R_LR-1);
"""

# 2. Prices setting and regulation:
# 2.1. Markup, production taxes, input taxes, lump-sum
def priceWedge(name,m):
	return f"""
$BLOCK B_{name}
	E_{name}_pwInp[t,s,n]$({m}_input[s,n] and txE[t])..			pD[t,s,n]		=E= p[t,n]+tauD[t,s,n];
	E_{name}_pwOut[t,s,n]$({m}_output[s,n] and txE[t])..		p[t,n] 			=E= (1+markup[s])*(pS[t,s,n]+tauS[t,s,n]);
	E_{name}_taxRev[t,s]$({m}_sm[s] and txE[t])..				TotalTax[t,s]	=E= tauLump[t,s]+sum(n$({m}_input[s,n]), tauD[t,s,n] * qD[t,s,n])+sum(n$({m}_output[s,n]), tauS[t,s,n]*qS[t,s,n]);
$ENDBLOCK
"""

# 2.2. Perfect competition instead of markups - use simple j-term to get this.
def priceWedgePC(name,m):
	return f"""
$BLOCK B_{name}
	E_{name}_pwInp[t,s,n]$({m}_input[s,n] and txE[t])..			pD[t,s,n]		=E= p[t,n]+tauD[t,s,n];
	E_{name}_pwOut[t,s,n]$({m}_output[s,n] and txE[t])..		p[t,n] 			=E= pS[t,s,n]+tauS[t,s,n]+jTerm[s];
	E_{name}_taxRev[t,s]$({m}_sm[s] and txE[t])..				TotalTax[t,s]	=E= tauLump[t,s]+sum(n$({m}_input[s,n]), tauD[t,s,n] * qD[t,s,n])+sum(n$({m}_output[s,n]), tauS[t,s,n]*qS[t,s,n]);
$ENDBLOCK
"""

# 2.2. Add tax on emissions
def priceWedgeEmissions(name,m):
	return f"""
$BLOCK B_{name}
	E_{name}_pwInp[t,s,n]$({m}_input[s,n] and txE[t])..					pD[t,s,n]		=E= p[t,n]+tauD[t,s,n];
	E_{name}_pwOut[t,s,n]$({m}_output[s,n] and txE[t])..				p[t,n] 			=E= (1+markup[s])*(pS[t,s,n]+(tauEffCO2[t,s,n]*uCO2[t,s,n])$(dqCO2[s,n])+tauS[t,s,n]);
	E_{name}_taxRev[t,s]$({m}_sm[s] and txE[t])..						TotalTax[t,s]	=E= tauLump[t,s]+sum(n$({m}_input[s,n]), tauD[t,s,n] * qD[t,s,n])+sum(n$({m}_output[s,n]), tauS[t,s,n]*qS[t,s,n]+(tauCO2[t,s,n]*qCO2[t,s,n])$(dqCO2[s,n]));
$ENDBLOCK
"""

# 2.3. Replace markup with $j$-term to capture slack relative to observed profits.
def priceWedgeEmissionsPC(name,m):
	return f"""
$BLOCK B_{name}
	E_{name}_pwInp[t,s,n]$({m}_input[s,n] and txE[t])..			pD[t,s,n]		=E= p[t,n]+tauD[t,s,n];
	E_{name}_pwOut[t,s,n]$({m}_output[s,n] and txE[t])..		p[t,n] 			=E= pS[t,s,n]+(tauEffCO2[t,s,n]*uCO2[t,s,n])$(dqCO2[s,n])+tauS[t,s,n]+jTerm[s];
	E_{name}_taxRev[t,s]$({m}_sm[s] and txE[t])..				TotalTax[t,s]	=E= tauLump[t,s]+sum(n$({m}_input[s,n]), tauD[t,s,n] * qD[t,s,n])+sum(n$({m}_output[s,n]), tauS[t,s,n]*qS[t,s,n]+(tauCO2[t,s,n]*qCO2[t,s,n])$(dqCO2[s,n]));
$ENDBLOCK
"""

def taxCalibration(name, m, taxInstr, taxCond):
	""" taxInstr is a gpy symbol, taxCond is a condition"""
	return f"""
$BLOCK B_{name}
	E_{name}_taxCal{Syms.gpyDomains(taxInstr)}{Syms.gpyCondition(taxCond)}..	{Syms.gpy(taxInstr)} =E= {Syms.gpy(taxInstr).replace(taxInstr.name, taxInstr.name+'0')}+taxRevPar[s];
$ENDBLOCK
"""

def taxCalibration_tauS(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_taxCal[t,s,n]$({m}_output[s,n] and txE[t])..	tauS[t,s,n]	=E= tauS0[t,s,n] + taxRevPar[s];
$ENDBLOCK
"""

# 3. Index Fund Equations


# 4: System of value shares
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

# $BLOCK B_ValueShares
# 	E_Out_knot[t,s,n]$(knotOutTree[s,n])..								vD[t,s,n]	=E= sum(nn$(map[s,nn,n] and branchOut[s,nn]), vS[t,s,n])+sum(nn$(map[s,nn,n] and branchNOut[s,nn]), vD[t,s,n]);
# 	E_Out_shares_o[t,s,n,nn]$(mapOut[s,n,nn] and branchOut[s,n])..		mu[t,s,n,nn]=E= vS[t,s,n]/vD[t,s,nn];
# 	E_Out_shares_no[t,s,n,nn]$(mapOut[s,n,nn] and branchNOut[s,n])..	mu[t,s,n,nn]=E= vD[t,s,n]/vD[t,s,nn];
# 	E_Inp_knot_o[t,s,n]$(knotOut[s,n])..								vS[t,s,n]	=E= sum(nn$(map[s,n,nn]), vD[t,s,nn]);
# 	E_Inp_knot_no[t,s,n]$(knotNOut[s,n])..								vD[t,s,n]	=E= sum(nn$(map[s,n,nn]), vD[t,s,nn]);
# 	E_Inp_shares2o[t,s,n,nn]$(mapInp[s,n,nn] and branch2Out[s,nn])..	mu[t,s,n,nn]=E= vD[t,s,nn]/vS[t,s,n];
# 	E_Inp_shares2no[t,s,n,nn]$(mapInp[s,n,nn] and branch2NOut[s,nn])..	mu[t,s,n,nn]=E= vD[t,s,nn]/vD[t,s,n];
# $ENDBLOCK
