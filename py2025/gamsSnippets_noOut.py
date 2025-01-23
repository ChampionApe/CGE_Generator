from gmsPython.gmsWrite import Syms

# 0.1: Auxiliary functions used for scale-preserving nests:
def _CES(px,py,mu,sigma,norm=None):
	return f"{mu} * ({py}/{px})**({sigma})" if norm is None else f"{mu} * ({py}/({px}*(1+{norm})))**({sigma})"
def _exp(px,py,mu,sigma,norm=None):
	return f"{mu} * exp(({py}-{px})*{sigma})" if norm is None else f"{mu} * exp(({py}-{px})*{sigma}-{norm})"

# 0.2: Normalized demand
def _Fnorm_input_demand(ftype, name):
	f = globals()['_'+ftype]
	return f"""E_{name}_q[t,s,n]$({name}_branch[s,n] and txE[t])..		qD[t,s,n] =E= sum(nn$({name}_map[s,nn,n]), qS[t,s,nn]*{f("pD[t,s,n]","pD[t,s,nn]","mu[s,nn,n]","sigma[s,nn]")} / sum(nnn$({name}_map[s,nn,nnn]), {f("pD[t,s,nnn]","pD[t,s,nn]","mu[s,nn,nnn]","sigma[s,nn]")}));"""

def _Fnorm_output_demand(ftype, name):
	f = globals()['_'+ftype]
	return f"""E_{name}_q[t,s,n]$({name}_branch[s,n] and txE[t])..		qD[t,s,n] =E= sum(nn$({name}_map[s,n,nn]), qD[t,s,nn]*{f("pD[t,s,nn]","pD[t,s,n]","mu[s,n,nn]","eta[s,nn]")} / sum(nnn$({name}_map[s,nnn,nn]), {f("pD[t,s,nnn]","pD[t,s,nn]","mu[s,nnn,nn]","eta[s,nn]")}));"""

# 0.2: Zero profit equations:
def zp_input(name):
	return f"""E_{name}_zp[t,s,n]$({name}_knot[s,n] and txE[t])..	pD[t,s,n]*qD[t,s,n] =E= sum(nn$({name}_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);"""
def zp_output(name):
	return f"""E_{name}_zp[t,s,n]$({name}_knot[s,n] and txE[t])..	pD[t,s,n]*qD[t,s,n] =E= sum(nn$({name}_map[s,nn,n]), qD[t,s,nn]*pD[t,s,nn]);"""

# 1: Input type nests:
# 1.1: CES nest:
def CES(name,**kwargs):
	return f"""
$BLOCK B_{name}
	{zp_input(name)}
	E_{name}_q[t,s,n]$({name}_branch[s,n] and txE[t])..	qD[t,s,n] =E= sum(nn$({name}_map[s,nn,n]), mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qD[t,s,nn]);
$ENDBLOCK
"""

# 1.2: Scale-preserving nests:
def Fnorm_input(ftype,name):
	return f"""
$BLOCK B_{name}
	{zp_input(name)}
	{_Fnorm_input_demand(ftype,name)}
$ENDBLOCK
"""
def CES_norm(name):
	return Fnorm_input('CES',name)
def MNL(name):
	return Fnorm_input('exp',name)

# 2: Output type nests:
# 2.1: CET function:
def CET(name,**kwargs):
	return f"""
$BLOCK B_{name}
	{zp_output(name)}
	E_{name}_demand[t,s,n]$({name}_branch[s,n] and txE[t])..	qD[t,s,n] =E= sum(nn$({name}_map[s,n,nn]), mu[s,n,nn] * (pD[t,s,n]/pD[t,s,nn])**(eta[s,nn]) * qD[t,s,nn]);
$ENDBLOCK
"""

# 2.2: scale-preserving nests: 
def Fnorm_output(ftype,name):
	return f"""
$BLOCK B_{name}
	{zp_output(name)}
	{_Fnorm_output_demand(ftype,name)}
$ENDBLOCK
"""

def CET_norm(name,m):
	return Fnorm_output('CES',name)
def MNL_out(name,m):
	return Fnorm_output('exp',name)



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