from gamsSnippets import *

# 1. Price/tax blocks: 
def priceBlock(name, m, addMarginal = '', addTax = '', addMargCostInp = ''):
	return f"""
$BLOCK B_{name}
	E_{name}_pD[t,s,n]$({m}_input[s,n] and txE[t])..			pD[t,s,n]		=E= p[t,n]*(1+tauD[t,s,n]){addMargCostInp};
	E_{name}_pS[t,s,n]$({m}_output[s,n] and txE[t])..			p[t,n] 			=E= (1+markup[s])*(pS[t,s,n]+p[t,n]*tauS[t,s,n]{addMarginal});
	E_{name}_TotalTax[t,s]$({m}_sm[s] and txE[t])..				TotalTax[t,s]	=E= tauLump[t,s]+sum(n$({m}_input[s,n]), tauD[t,s,n] * p[t,n] * qD[t,s,n])+sum(n$({m}_output[s,n]), tauS[t,s,n]*p[t,n]*qS[t,s,n]){addTax};
$ENDBLOCK
"""

# 2. Block for calibration of taxes using permannet adjustments. Can accept different tax instruments.
def taxCalibBlock(name, m, taxInstr, taxCond):
	""" taxInstr is a gpy symbol, taxCond is a condition"""
	return f"""
$BLOCK B_{name}
	E_{name}_taxRevPar{Syms.gpyDomains(taxInstr)}{Syms.gpyCondition(taxCond)}..	{Syms.gpy(taxInstr)} =E= {Syms.gpy(taxInstr).replace(taxInstr.name, taxInstr.name+'0')}+taxRevPar[s];
$ENDBLOCK
"""

# 3. Value of the firm
def firmValueBlock(name, m, addCosts = ''):
	return f"""
$BLOCK B_{name}
	E_{name}_vA[t,s]$({m}_sm[s] and tx0[t])..		vA[t,s]	=E= (vA[t-1,s]*Rrate[t-1]-divd[t-1,s])/((1+g_LR)*(1+infl_LR));
	E_{name}_divd[t,s]$({m}_sm[s] and txE[t])..		divd[t,s] =E= sum(n$({m}_output[s,n]), p[t,n] * qS[t,s,n])-sum(n$({m}_input[s,n]), p[t,n] * qD[t,s,n])-TotalTax[t,s]{addCosts};
	E_{name}_vAT[t,s]$({m}_sm[s] and tE[t])..		vA[t,s]	  =E= (1+vA_tvc[s])*vA[t-1,s]/((1+g_LR)*(1+infl_LR));
$ENDBLOCK
"""

def initFirmValueBlock(m, addCosts = ''):
	return f"""
	divd.l[t,s]$({m}_sm[s] and txE[t]) = sum(n$({m}_output[s,n]), p.l[t,n] * qS.l[t,s,n])-sum(n$({m}_input[s,n]), p.l[t,n]*qD.l[t,s,n])-TotalTax.l[t,s]{addCosts};
	vA.l[t,s]$({m}_sm[s] and txE[t]) = divd.l[t,s]/(R_LR-1);
	vA.l[t,s]$({m}_sm[s] and tE[t])	= divd.l[t-1,s]/(R_LR-1);
"""


# 4. Dynamic equations for capital accumulation:
def capitalAccumulation(name, m, adjCosts = False):
	return capitalAccumulationSimple(name,m) if not adjCosts else capitalAccumulationSqrAdjCosts(name,m)

def capitalAccumulationSimple(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_lom[t,s,n]$({m}_dur[s,n] and txE[t])..		qD[t+1,s,n]	=E= (qD[t,s,n]*(1-rDepr[t,s,n])+sum(nn$({m}_dur2inv[s,n,nn]), qD[t,s,nn]))/(1+g_LR);
	E_{name}_pk[t,s,n]$({m}_dur[s,n] and tx0E[t])..		pD[t,s,n]	=E= sum(nn$({m}_dur2inv[s,n,nn]), Rrate[t]*pD[t-1,s,nn]+(rDepr[t,s,n]-1)*pD[t,s,nn]);
	E_{name}_K_tvc[t,s,n]$({m}_dur[s,n] and tE[t])..	qD[t,s,n]	=E= (1+K_tvc[s,n])*qD[t-1,s,n]/(1+g_LR);
$ENDBLOCK
"""
# With adjustment costs: 
def capitalAccumulationSqrAdjCosts(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_lom[t,s,n]$({m}_dur[s,n] and txE[t])..		qD[t+1,s,n]	=E= (qD[t,s,n]*(1-rDepr[t,s,n])+sum(nn$({m}_dur2inv[s,n,nn]), qD[t,s,nn]))/(1+g_LR);
	E_{name}_pk[t,s,n]$({m}_dur[s,n] and tx02E[t])..	pD[t,s,n]	=E= sum(nn$({m}_dur2inv[s,n,nn]), Rrate[t]*(pD[t-1,s,nn]+adjCostPar[s,n]*(qD[t-1,s,nn]/qD[t-1,s,n]-(rDepr[t-1,s,n]+g_LR)))/(1+infl_LR)+(adjCostPar[s,n]*0.5*(sqr(rDepr[t,s,n]+g_LR)-sqr(qD[t,s,nn]/qD[t,s,n]))-(1-rDepr[t,s,n])*(pD[t,s,nn]+adjCostPar[s,n]*(qD[t,s,nn]/qD[t,s,n]-(rDepr[t,s,n]+g_LR)))));
	E_{name}_pkT[t,s,n]$({m}_dur[s,n] and t2E[t])..		pD[t,s,n]	=E= sum(nn$({m}_dur2inv[s,n,nn]), Rrate[t]*(pD[t-1,s,nn]+adjCostPar[s,n]*(qD[t-1,s,nn]/qD[t-1,s,n]-(rDepr[t-1,s,n]+g_LR)))/(1+infl_LR)+(rDepr[t,s,n]-1)*pD[t,s,nn]);
	E_{name}_K_tvc[t,s,n]$({m}_dur[s,n] and tE[t])..	qD[t,s,n]	=E= (1+K_tvc[s,n])*qD[t-1,s,n]/(1+g_LR);
	E_{name}_adjCost[t,s]$({m}_sm[s] and txE[t])..		adjCost[t,s] 	=E= sum([n,nn]$({m}_dur2inv[s,n,nn]), adjCostPar[s,n]*0.5*qD[t,s,n]*sqr(qD[t,s,nn]/qD[t,s,n]-(rDepr[t,s,n]+g_LR)));
$ENDBLOCK
"""

# 5. Waste generation blocks:
def wasteGeneration(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_pW[t,s,n]$({m}_sm[s] and dWSn[s,n] and txE[t])..						pW[t,s,n]	=E= sum(m$(dWSnm[s,n,m]), uWS[t,s,n,m] * (uWS_D[t,s,m] * (sum(nn$(n2m_D[nn,m]), pD[t,s,nn])+sum(nn$(dWTy[s,nn]), uWTy[s,nn] * pD[t,s,nn])) + (1-uWS_D[t,s,m])* (sum(nn$(n2m_F[nn,m]), pD[t,s,nn])+sum(nn$(dWTyF[s,nn]), uWTyF[s,nn]*pD[t,s,nn]))));
	E_{name}_qWS[t,s,m]$({m}_sm[s] and dWS[s,m] and txE[t])..						qWS[t,s,m]	=E= sum(n$(dWSnm[s,n,m]), uWS[t,s,n,m] * qD[t,s,n]); # Total waste generation, domestic firms
	E_{name}_qDWTD[t,s,n]$({m}_sm[s] and dWTn[s,n] and nw_D[n] and txE[t])..		qD[t,s,n]	=E= sum(m$(n2m[n,m]), uWS_D[t,s,m] * qWS[t,s,m]); # waste management demand, domestic treatment
	E_{name}_qDWTyD[t,s,n]$({m}_sm[s] and dWTy[s,n] and txE[t])..					qD[t,s,n]	=E= uWTy[s,n] * sum(m$(dWS[s,m]), uWS_D[t,s,m]*qWS[t,s,m]); # demand for domestic residual waste service
	E_{name}_qDWTF[t,s,n]$({m}_sm[s] and dWTn[s,n] and nw_F[n] and txE[t])..		qD[t,s,n]	=E= sum(m$(n2m[n,m]), (1-uWS_D[t,s,m]) * qWS[t,s,m])+WTFpar[s,n]; # waste management demand, foreign treatment
	E_{name}_qDWTyF[t,s,n]$({m}_sm[s] and dWTyF[s,n] and txE[t])..					qD[t,s,n]	=E= uWTyF[s,n] * sum(m$(dWS[s,m]), (1-uWS_D[t,s,m])*qWS[t,s,m]); # demand for foreign residual waste service
$ENDBLOCK
"""

def wasteGenerationCalib(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_qDWTD[t,s,n]$({m}_sm[s] and dWTn[s,n] and nw_D[n] and txE[t])..	WTDpar[s,n] =E= sum(m$(n2m[n,m]), uWS_D[t,s,m]-uWS_D0[t,s,m]);
$ENDBLOCK
"""
