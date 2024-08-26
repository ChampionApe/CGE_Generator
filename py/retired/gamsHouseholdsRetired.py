from gamsSnippets_noOut import *

# 1: Labor supply function
def isoFrisch(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_labor[t,s,n]$({m}_L[s,n] and txE[t])..	qS[t,s,n]	=E=	Lscale[s,n] * ( sum(nn$({m}_L2C[s,n,nn]), pS[t,s,n]/(pD[t,s,nn]*(qD[t,s,nn]**(crra[s,nn]))))**(frisch[s,n]));
$ENDBLOCK
"""

# 2: Ramsey:
def simpleDynamic(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_lom[t,s]$({m}_sm[s] and txE[t])..				vAssets[t+1,s,'total']	=E= (vAssets[t,s,'total']*iRate[t]+sp[t,s])/((1+g_LR)*(1+infl_LR));
	E_{name}_euler[t,s,n]$(output_{m}[s,n] and tx0E[t])..	qD[t,s,n]				=E= qD[t-1,s,n]*(disc[s]*Rrate[t]*pD[t-1,s,n]/pD[t,s,n])**(1/crra[s,n]);
	E_{name}_tvc[t,s]$({m}_sm[s] and tE[t])..				vAssets[t,s,'total']	=E= (1+h_tvc[s])*vAssets[t-1,s,'total'];
$ENDBLOCK
"""

# 3.1
def priceWedge(name,m):
	return f"""
$BLOCK B_{name}
	E_{name}_pwOut[t,s,n]$({m}_L[s,n] and txE[t])..	pS[t,s,n] 		=E= p[t,n]-tauS[t,s,n];
	E_{name}_pwInp[t,s,n]$({m}_input[s,n] and txE[t])..	pD[t,s,n]		=E= p[t,n]+tauD[t,s,n];
	E_{name}_TaxRev[t,s]$({m}_sm[s] and txE[t])..		TotalTax[t,s]	=E= tauLump[t,s]+sum(n$({m}_input[s,n]), tauD[t,s,n] * qD[t,s,n])+sum(n$({m}_L[s,n]), tauS[t,s,n]*qS[t,s,n]);
	E_{name}_sp[t,s]$({m}_sm[s] and txE[t])..			sp[t,s]			=E= sum(n$({m}_L[s,n]), pS[t,s,n]*qS[t,s,n]) - sum(n$({m}_input[s,n]), pD[t,s,n]*qD[t,s,n])-tauLump[t,s];
$ENDBLOCK
"""

# 3.2
def priceWedgeStatic(name,m):
	return f"""
$BLOCK B_{name}
	E_{name}_pwOut[t,s,n]$({m}_L[s,n] and txE[t])..	pS[t,s,n] 		=E= p[t,n]-tauS[t,s,n];
	E_{name}_pwInp[t,s,n]$({m}_input[s,n] and txE[t])..	pD[t,s,n]		=E= p[t,n]+tauD[t,s,n];
	E_{name}_TaxRev[t,s]$({m}_sm[s] and txE[t])..		TotalTax[t,s]	=E= tauLump[t,s]+sum(n$({m}_input[s,n]), tauD[t,s,n] * qD[t,s,n])+sum(n$({m}_L[s,n]), tauS[t,s,n]*qS[t,s,n]);
	E_{name}_sp[t,s]$({m}_sm[s] and txE[t])..			jTerm[s]		=E= sum(n$({m}_L[s,n]), pS[t,s,n]*qS[t,s,n]) - sum(n$({m}_input[s,n]), pD[t,s,n]*qD[t,s,n])-tauLump[t,s];
$ENDBLOCK
"""

# 4: System of value shares
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
