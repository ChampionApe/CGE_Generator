# 0.1: Auxiliary functions used for scale-preserving nests:
def _CES(px,py,mu,sigma,norm=None):
	return f"{mu} * ({py}/{px})**({sigma})" if norm is None else f"{mu} * ({py}/({px}*(1+{norm})))**({sigma})"
def _exp(px,py,mu,sigma,norm=None):
	return f"{mu} * exp(({py}-{px})*{sigma})" if norm is None else f"{mu} * exp(({py}-{px})*{sigma}-{norm})"

# 0.2: Normalized demand
def _Fnorm_input_demand(ftype, name):
	f = globals()['_'+ftype]
	return f"""E_q_{name}[t,s,n]$(branch_{name}[s,n] and txE[t])..		qD[t,s,n] =E= sum(nn$(map_{name}[s,nn,n]), qS[t,s,nn]*{f("pD[t,s,n]","pD[t,s,nn]","mu[s,nn,n]","sigma[s,nn]")} / sum(nnn$(map_{name}[s,nn,nnn]), {f("pD[t,s,nnn]","pD[t,s,nn]","mu[s,nn,nnn]","sigma[s,nn]")}));"""

def _Fnorm_output_demand(ftype, name):
	f = globals()['_'+ftype]
	return f"""E_q_{name}[t,s,n]$(branch_{name}[s,n] and txE[t])..		qD[t,s,n] =E= sum(nn$(map_{name}[s,n,nn]), qD[t,s,nn]*{f("pD[t,s,nn]","pD[t,s,n]","mu[s,n,nn]","eta[s,nn]")} / sum(nnn$(map_{name}[s,nnn,nn]), {f("pD[t,s,nnn]","pD[t,s,nn]","mu[s,nnn,nn]","eta[s,nn]")}));"""

# 0.2: Zero profit equations:
def zp_input(name):
	return f"""E_zp_{name}[t,s,n]$(knot_{name}[s,n] and txE[t])..	pD[t,s,n]*qD[t,s,n] =E= sum(nn$(map_{name}[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);"""
def zp_output(name):
	return f"""E_zp_{name}[t,s,n]$(knot_{name}[s,n] and txE[t])..	pD[t,s,n]*qD[t,s,n] =E= sum(nn$(map_{name}[s,nn,n]), qD[t,s,nn]*pD[t,s,nn]);"""

# 1: Input type nests:
# 1.1: CES nest:
def CES(name,m,**kwargs):
	return f"""
$BLOCK B_{name}
	{zp_input(name)}
	E_q_{name}[t,s,n]$(branch_{name}[s,n] and txE[t])..	qD[t,s,n] =E= sum(nn$(map_{name}[s,nn,n]), mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qD[t,s,nn]);
$ENDBLOCK
"""

# 1.2: Scale-preserving nests:
def Fnorm_input(ftype,name,m):
	return f"""
$BLOCK B_{name}
	{zp_input(name)}
	{_Fnorm_input_demand(ftype,name)}
$ENDBLOCK
"""
def CES_norm(name,m):
	return Fnorm_input('CES',name,m)
def MNL(name,m):
	return Fnorm_input('exp',name,m)

# 2: Output type nests:
# 2.1: CET function:
def CET(name,m,**kwargs):
	return f"""
$BLOCK B_{name}
	{zp_output(name)}
	E_demand_{name}[t,s,n]$(branch_{name}[s,n] and txE[t])..	qD[t,s,n] =E= sum(nn$(map_{name}[s,n,nn]), mu[s,n,nn] * (pD[t,s,n]/pD[t,s,nn])**(eta[s,nn]) * qD[t,s,nn]);
$ENDBLOCK
"""

# 2.2: scale-preserving nests: 
def Fnorm_output(ftype,name,m):
	return f"""
$BLOCK B_{name}
	{zp_output(name)}
	{_Fnorm_output_demand(ftype,name)}
$ENDBLOCK
"""

def CET_norm(name,m):
	return Fnorm_output('CES',name,m)
def MNL_out(name,m):
	return Fnorm_output('exp',name,m)
