from gamsSnippets_noOut import *

# Block of equations for stand alone, baseline model:
def balancedBudget(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_pw[t,s,n]$({m}_input[s,n] and txE[t])..	pD[t,s,n]	=E= p[t,n]*(1+tauD[t,s,n]);
	E_{name}_taxRev[t,s]$({m}_sm[s] and txE[t])..	TotalTax[t,s]	=E= sum(n$({m}_input[s,n]), tauD[t,s,n] * p[t,n]*qD[t,s,n]);
	E_{name}_bb[t,s]$({m}_sm[s] and txE[t])..			jTerm[s]	=E= sum(ss$(d_TotalTax[ss]), TotalTax[t,ss])-sum(n$({m}_input[s,n]), p[t,n]*qD[t,s,n]);
$ENDBLOCK
"""

def taxCalibration(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_taxCal[t,s,n]$({m}_input[s,n] and txE[t])..	tauD[t,s,n]	=E= tauD0[t,s,n]+taxRevPar[s];
$ENDBLOCK
"""

# 5: System of value shares
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

