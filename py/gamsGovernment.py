from gamsSnippets import *

# 1: Simple dynamics
def simpleDynamics(name, m):
	return f"""
$BLOCK B_{name}
	E_lom_{name}[t,s]$(s_{m}[s] and txE[t])..				vAssets[t+1,s,'total']	=E= (vAssets[t,s,'total']*iRate[t]+sp[t,s])/((1+g_LR)*(1+infl_LR));
	E_pwInp_{name}[t,s,n]$(input_{m}[s,n] and txE[t])..				pD[t,s,n]		=E= p[t,n]+tauD[t,s,n];
	E_TaxRev_{name}[t,s]$(s_{m}[s] and txE[t])..					TotalTax[t,s]	=E= sum(n$(input_{m}[s,n]), tauD[t,s,n] * qD[t,s,n]);
	E_sp_{name}[t,s]$(s_{m}[s] and txE[t])..						sp[t,s]			=E= sum(ss$(d_TotalTax[ss]), TotalTax[t,ss])- sum(n$(input_{m}[s,n]), pD[t,s,n]*qD[t,s,n])+jG_budget;
$ENDBLOCK
"""

# 2: Calibration block
def calibrationFlat(name, m):
	return f"""
$BLOCK B_{name}
	E_flatCalib_{name}[t,s,n]$(input_{m}[s,n] and txE[t])..		tauD[t,s,n]	=E= tauD0[t,s,n]*tauG_calib;
$ENDBLOCK
"""

# 3: Balanced budget
def balancedBudget(name, m):
	return f"""
$BLOCK B_{name}
	E_bb_{name}[t,s]$(s_{m}[s] and tx0E[t]).. sp[t,s] =E= 0;
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
