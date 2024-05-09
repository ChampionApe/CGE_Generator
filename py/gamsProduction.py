from gamsSnippets import *

# 1: Adjustment costs / installation cost equations:
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

# 2.1: Introduce price wedge with mark-up, unit-tax, and installation costs
def priceWedge(name,m):
	return f"""
$BLOCK B_{name}
	E_{name}_pwInp[t,s,n]$({m}_input[s,n] and txE[t])..			pD[t,s,n]		=E= p[t,n]+tauD[t,s,n];
	E_{name}_pwOut[t,s,n]$({m}_output[s,n] and txE[t])..		p[t,n] 			=E= (1+markup[s])*(pS[t,s,n]+tauS[t,s,n]+(adjCost[t,s]+tauLump[t,s])/qS[t,s,n]);
	E_{name}_taxRev[t,s]$({m}_sm[s] and txE[t])..				TotalTax[t,s]	=E= tauLump[t,s]+sum(n$({m}_input[s,n]), tauD[t,s,n] * qD[t,s,n])+sum(n$({m}_output[s,n]), tauS[t,s,n]*qS[t,s,n]);
$ENDBLOCK
"""

# 2.2: Add taxes on emissions
def priceWedgeEmissions(name,m):
	return f"""
$BLOCK B_{name}
	E_{name}_pwInp[t,s,n]$({m}_input[s,n] and txE[t])..			pD[t,s,n]		=E= p[t,n]+tauD[t,s,n];
	E_{name}_pwOut[t,s,n]$({m}_output[s,n] and txE[t])..		p[t,n] 			=E= (1+markup[s])*(pS[t,s,n]+tauS[t,s,n]+(adjCost[t,s]+tauLump[t,s])/qS[t,s,n]);
	E_{name}_taxRev[t,s]$(s_{m}[s] and txE[t])..				TotalTax[t,s]	=E= tauLump[t,s]+sum(n$({m}_input[s,n]), tauD[t,s,n] * qD[t,s,n])+sum(n$({m}_output[s,n]), tauS[t,s,n]*qS[t,s,n]);
	E_{name}_tauS[t,s,n]$({m}_output[s,n] and txE[t])..			tauS[t,s,n]		=E= tauCO2[t,s,n] * qCO2[t,s,n]/qS[t,s,n]+tauNonEnv[t,s,n];
$ENDBLOCK
"""

# Calibration 
def taxCalibration(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_taxCal[t,s,n]$({m}_output[s,n] and txE[t])..	tauNonEnv[t,s,n]	=E= tauNonEnv0[t,s,n] * (1+taxRevPar[s]);
$ENDBLOCK
"""

# 3: System of value shares
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
