from gamsSnippets_noOut import *
# 1: CRRA-GHH Ramsey
def CRRA_GHH_vU(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_qC[t,s]$({m}_sm[s] and txE[t])..	qC[t,s]		=E= sum([n,nn]$({m}_L2C[s,n,nn]), qD[t,s,nn]-frisch[s]*(qS[t,s,n]/Lscale[s])**((1+frisch[s])/frisch[s])/(1+frisch[s]));
	E_{name}_V[t,s]$({m}_sm[s] and txE[t])..	vU[t,s]		=E= qC[t,s]**(1-crra[s])/(1-crra[s])+discF[s]*vU[t+1,s];
	E_{name}_VT[t,s]$({m}_sm[s] and tE[t])..	vU[t,s]		=E= (qC[t-1,s]**(1-crra[s])/(1-crra[s]))/(1-discF[s]);
	E_{name}_L[t,s,n]$({m}_L[s,n] and txE[t])..	qS[t,s,n]	=E= Lscale[s] * sum(nn$({m}_L2C[s,n,nn]), pS[t,s,n]/pD[t,s,nn])**(frisch[s]);
$ENDBLOCK
"""

def CRRA_Euler(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_vA[t,s]$({m}_sm[s] and txE[t])..		vA[t+1,s]	=E= (vA[t,s]*Rrate[t]+sp[t,s]+jTerm[s])/(1+g_LR);
	E_{name}_vAT[t,s]$({m}_sm[s] and tE[t])..		vA[t,s]		=E= (1+h_tvc[s])*vA[t-1,s];
	E_{name}_euler[t,s]$({m}_sm[s] and tx0E[t])..	qC[t,s]		=E= qC[t-1,s]*(discF[s]*Rrate[t]*sum(n$({m}_output[s,n]), pD[t-1,s,n]/pD[t,s,n]))**(1/crra[s]);	
$ENDBLOCK
"""

def indexFundInvest(name, m):
	return f"""
$BLOCK B_{name}_Calib
	E_{name}_Calib_vAt0[t,s]$({m}_sm[s] and t0[t])..	uIdxFund[s]*vIdxFund[t] =E= uA_Dom[s] * vA[t,s];
$ENDBLOCK
$BLOCK B_{name}
	E_{name}_vAt0[t,s]$({m}_sm[s] and t0[t])..	vA[t,s]	=E= uIdxFund[s] * vIdxFund[t]+vA_F[s];
$ENDBLOCK
"""

def priceWedge(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_labTax[t,s,n]$({m}_L[s,n] and txE[t])..		pS[t,s,n]		=E= p[t,n]*(1-tauS[t,s,n]);
	E_{name}_inpTax[t,s,n]$({m}_input[s,n] and txE[t])..	pD[t,s,n]		=E= p[t,n]*(1+tauD[t,s,n]);
	E_{name}_taxRev[t,s]$({m}_sm[s] and txE[t])..			TotalTax[t,s]	=E= tauLump[t,s]+sum(n$({m}_input[s,n]), tauD[t,s,n]*p[t,n]*qD[t,s,n])+sum(n$({m}_L[s,n]), tauS[t,s,n]*p[t,n]*qS[t,s,n]);
	E_{name}_sp[t,s]$({m}_sm[s] and txE[t])..				sp[t,s]			=E= sum(n$({m}_L[s,n]), p[t,n]*qS[t,s,n])-sum(n$({m}_input[s,n]), p[t,n]*qD[t,s,n])-TotalTax[t,s];
$ENDBLOCK
"""

# Text blocks used to initialize variables:
def init_CRRA_GHH_ss(m):
	""" Initialize variables for CRRA-GHH model as in steady state"""
	return f"""
Lscale.l[s]$({m}_sm[s])	= sum([t,n,nn]$(t0[t] and {m}_L2C[s,n,nn]), qS.l[t,s,n] * (pD.l[t,s,nn]/pS.l[t,s,n])**(frisch.l[s]));
qC.l[t,s]$({m}_sm[s] and txE[t]) = sum([n,nn]$({m}_L2C[s,n,nn]), qD.l[t,s,nn]-frisch.l[s]*(qS.l[t,s,n]/Lscale.l[s])**((1+frisch.l[s])/frisch.l[s])/(1+frisch.l[s]));
sp.l[t,s]$({m}_sm[s] and txE[t]) = sum(n$({m}_L[s,n]), pS.l[t,s,n]*qS.l[t,s,n]) - sum(n$({m}_input[s,n]), pD.l[t,s,n]*qD.l[t,s,n])-tauLump.l[t,s];
jTerm.l[s]$({m}_sm[s])	= sum(t$(t0[t]), (vA.l[t, s]*((1+g_LR)-(1+Rrate.l[t]))-sp.l[t,s])/(1+Rrate.l[t]));
"""


# 2 Static model:
def isoFrisch(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_labor[t,s,n]$({m}_L[s,n] and txE[t])..	qS[t,s,n]	=E=	Lscale[s] * sum(nn$({m}_L2C[s,n,nn]), pS[t,s,n]/pD[t,s,nn])**(frisch[s]);
$ENDBLOCK
"""

def priceWedgeStatic(name,m):
	return f"""
$BLOCK B_{name}
	E_{name}_pwOut[t,s,n]$({m}_L[s,n] and txE[t])..	pS[t,s,n] 		=E= p[t,n]-tauS[t,s,n];
	E_{name}_pwInp[t,s,n]$({m}_input[s,n] and txE[t])..	pD[t,s,n]		=E= p[t,n]+tauD[t,s,n];
	E_{name}_TaxRev[t,s]$({m}_sm[s] and txE[t])..		TotalTax[t,s]	=E= tauLump[t,s]+sum(n$({m}_input[s,n]), tauD[t,s,n] * qD[t,s,n])+sum(n$({m}_L[s,n]), tauS[t,s,n]*qS[t,s,n]);
	E_{name}_sp[t,s]$({m}_sm[s] and txE[t])..			jTerm[s]		=E= sum(n$({m}_L[s,n]), pS[t,s,n]*qS[t,s,n]) - sum(n$({m}_input[s,n]), pD[t,s,n]*qD[t,s,n])-tauLump[t,s];
$ENDBLOCK
"""

# 3: System of value shares
def valueShares():
	return f"""
$BLOCK B_ValueShares
	E_Out_knot[t,s,n]$(knotOutTree[s,n])..								vD[t,s,n]	=E= sum(nn$(map[s,nn,n] and branchOut[s,nn]), vD[t,s,n])+sum(nn$(map[s,nn,n] and branchNOut[s,nn]), vD[t,s,n]);
	E_Out_shares_o[t,s,n,nn]$(mapOut[s,n,nn] and branchOut[s,n])..		mu[t,s,n,nn]=E= vD[t,s,n]/vD[t,s,nn];
	E_Out_shares_no[t,s,n,nn]$(mapOut[s,n,nn] and branchNOut[s,n])..	mu[t,s,n,nn]=E= vD[t,s,n]/vD[t,s,nn];
	E_Inp_knot_o[t,s,n]$(knotOut[s,n])..								vD[t,s,n]	=E= sum(nn$(map[s,n,nn]), vD[t,s,nn]);
	E_Inp_knot_no[t,s,n]$(knotNOut[s,n])..								vD[t,s,n]	=E= sum(nn$(map[s,n,nn]), vD[t,s,nn]);
	E_Inp_shares2o[t,s,n,nn]$(mapInp[s,n,nn] and branch2Out[s,nn])..	mu[t,s,n,nn]=E= vD[t,s,nn]/vD[t,s,n];
	E_Inp_shares2no[t,s,n,nn]$(mapInp[s,n,nn] and branch2NOut[s,nn])..	mu[t,s,n,nn]=E= vD[t,s,nn]/vD[t,s,n];
$ENDBLOCK
"""
