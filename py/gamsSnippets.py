### Useful snippets of GAMS code. 

# 0.1: Auxiliary functions used for scale-preserving nests:
def _CES(px,py,mu,sigma,norm=None):
	return f"{mu} * ({py}/{px})**({sigma})" if norm is None else f"{mu} * ({py}/({px}*(1+{norm})))**({sigma})"
def _exp(px,py,mu,sigma,norm=None):
	return f"{mu} * exp(({py}-{px})*{sigma})" if norm is None else f"{mu} * exp(({py}-{px})*{sigma}-{norm})"

def _Fnorm_input_demand(ftype,name):
	f = globals()['_'+ftype]
	return f"""E_q_out_{name}[t,s,n]$(branch2o_{name}[s,n] and txE[t])..	qD[t,s,n] =E= sum(nn$(map_{name}[s,nn,n]), qS[t,s,nn]*{f("pD[t,s,n]","pS[t,s,nn]","mu[s,nn,n]","sigma[s,nn]")} / sum(nnn$(map_{name}[s,nn,nnn]), {f("pD[t,s,nnn]","pS[t,s,nn]","mu[s,nn,nnn]","sigma[s,nn]")}));
	E_q_nout_{name}[t,s,n]$(branch2no_{name}[s,n] and txE[t])..		qD[t,s,n] =E= sum(nn$(map_{name}[s,nn,n]), qD[t,s,nn]*{f("pD[t,s,n]","pD[t,s,nn]","mu[s,nn,n]","sigma[s,nn]")} / sum(nnn$(map_{name}[s,nn,nnn]), {f("pD[t,s,nnn]","pD[t,s,nn]","mu[s,nn,nnn]","sigma[s,nn]")}));"""

def _Fnorm_output_demand(ftype,name):
	f = globals()['_'+ftype]
	return f"""E_q_out_{name}[t,s,n]$(branch_o_{name}[s,n] and txE[t])..	qS[t,s,n] =E= sum(nn$(map_{name}[s,n,nn]), qD[t,s,nn]*{f("pD[t,s,nn]","pS[t,s,n]","mu[s,n,nn]","eta[s,nn]")} / (sum(nnn$(map_{name}[s,nnn,nn] and branch_o_{name}[s,nnn]), {f("pS[t,s,nnn]","pD[t,s,nn]","mu[s,nnn,nn]","eta[s,nn]")})+sum(nnn$(map_{name}[s,nnn,nn] and branch_no_{name}[s,nnn]), {f("pD[t,s,nnn]","pD[t,s,nn]","mu[s,nnn,nn]","eta[s,nn]")})));
	E_q_nout_{name}[t,s,n]$(branch_no_{name}[s,n] and txE[t])..		qD[t,s,n] =E= sum(nn$(map_{name}[s,n,nn]), qD[t,s,nn]*{f("pD[t,s,nn]","pD[t,s,n]","mu[s,n,nn]","eta[s,nn]")} / (sum(nnn$(map_{name}[s,nnn,nn] and branch_o_{name}[s,nnn]), {f("pS[t,s,nnn]","pD[t,s,nn]","mu[s,nnn,nn]","eta[s,nn]")})+sum(nnn$(map_{name}[s,nnn,nn] and branch_no_{name}[s,nnn]), {f("pD[t,s,nnn]","pD[t,s,nn]","mu[s,nnn,nn]","eta[s,nn]")})));"""

def _Fnorm_input_with_InclusiveValue(ftype,name):
	f = globals()['_'+ftype]
	return f"""E_q_out_{name}[t,s,n]$(branch2o_{name}[s,n] and txE[t])..	qD[t,s,n] =E= sum(nn$(map_{name}[s,nn,n]), qS[t,s,nn]*{f("pD[t,s,n]","pS[t,s,nn]","mu[s,nn,n]","sigma[s,nn]",norm='qnorm[t,s,nn]')} / qiv_inp[t,s,nn]);
	E_q_nout_{name}[t,s,n]$(branch2no_{name}[s,n] and txE[t])..		qD[t,s,n] =E= sum(nn$(map_{name}[s,nn,n]), qD[t,s,nn]*{f("pD[t,s,n]","pD[t,s,nn]","mu[s,nn,n]","sigma[s,nn]",norm='qnorm[t,s,nn]')} / qiv_inp[t,s,nn]);
	E_inclVal_out_{name}[t,s,n]$(knot_o_{name}[s,n] and txE[t])..	qiv_inp[t,s,n] =E= sum(nn$(map_{name}[s,n,nn]), {f("pD[t,s,nn]","pS[t,s,n]","mu[s,n,nn]","sigma[s,n]",norm='qnorm[t,s,n]')});
	E_inclVal_nout_{name}[t,s,n]$(knot_no_{name}[s,n] and txE[t])..	qiv_inp[t,s,n] =E= sum(nn$(map_{name}[s,n,nn]), {f("pD[t,s,nn]","pD[t,s,n]","mu[s,n,nn]","sigma[s,n]",norm='qnorm[t,s,n]')});"""

def _Fnorm_output_with_InclusiveValue(ftype,name):
	f = globals()['_'+ftype]
	return f"""E_q_out_{name}[t,s,n]$(branch_o_{name}[s,n] and txE[t])..	qS[t,s,n] =E= sum(nn$(map_{name}[s,n,nn]), qD[t,s,nn]*{f("pD[t,s,nn]","pS[t,s,n]","mu[s,n,nn]","eta[s,nn]")} / qiv_out[t,s,nn]);
	E_q_nout_{name}[t,s,n]$(branch_no_{name}[s,n] and txE[t])..		qD[t,s,n] =E= sum(nn$(map_{name}[s,n,nn]), qD[t,s,nn]*{f("pD[t,s,nn]","pD[t,s,n]","mu[s,n,nn]","eta[s,nn]")} / qiv_out[t,s,nn]);
	E_inclVal_out_{name}[t,s,n]$(knot_{name}[s,n] and txE[t])..		qiv_out[t,s,n]=E= sum(nn$(map_{name}[s,nn,n] and branch_o_{name}[s,nn]), {f("pS[t,s,nn]","pD[t,s,n]","mu[s,nn,n]","eta[s,n]",norm='qnorm[t,s,n]')})+sum(nn$(map_{name}[s,nn,n] and branch_no_{name}[s,nn]), {f("pD[t,s,nn]","pD[t,s,n]","mu[s,nn,n]","eta[s,n]",norm='qnorm[t,s,n]')});"""

# 0.2: Zero profit equations:
def zp_input(name):
	return f"""E_zp_out_{name}[t,s,n]$(knot_o_{name}[s,n] and txE[t])..	pS[t,s,n]*qS[t,s,n] =E= sum(nn$(map_{name}[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
	E_zp_nout_{name}[t,s,n]$(knot_no_{name}[s,n] and txE[t])..	pD[t,s,n]*qD[t,s,n] =E= sum(nn$(map_{name}[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);"""
def zp_output(name):
	return f"""E_zp_{name}[t,s,n]$(knot_{name}[s,n] and txE[t])..	pD[t,s,n]*qD[t,s,n] =E= sum(nn$(map_{name}[s,nn,n] and branch_o_{name}[s,nn]), qS[t,s,nn]*pS[t,s,nn])+sum(nn$(map_{name}[s,nn,n] and branch_no_{name}[s,nn]), qD[t,s,nn]*pD[t,s,nn]);"""


# 1: Input type nests:
# 1.1: CES nest:
def CES(name,m,**kwargs):
	return f"""
$BLOCK B_{name}
	{zp_input(name)}
	E_q_out_{name}[t,s,n]$(branch2o_{name}[s,n] and txE[t])..	qD[t,s,n] =E= sum(nn$(map_{name}[s,nn,n]), mu[s,nn,n] * (pS[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qS[t,s,nn]);
	E_q_nout_{name}[t,s,n]$(branch2no_{name}[s,n] and txE[t])..	qD[t,s,n] =E= sum(nn$(map_{name}[s,nn,n]), mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qD[t,s,nn]);
$ENDBLOCK
"""

# 1.2: Scale-preserving nests:
def Fnorm_input(ftype,name,m,inclusiveVal = False):
	return f"""
$BLOCK B_{name}
	{zp_input(name)}
	{_Fnorm_input_with_InclusiveValue(ftype,name) if inclusiveVal else _Fnorm_input_demand(ftype,name)}
$ENDBLOCK
"""
def CES_norm(name,m,inclusiveVal = False):
	return Fnorm_input('CES',name,m,inclusiveVal=inclusiveVal)
def MNL(name,m,inclusiveVal = False):
	return Fnorm_input('exp',name,m,inclusiveVal=inclusiveVal)

# 2: Output type nests:
# 2.1: CET function:
def CET(name,m,**kwargs):
	return f"""
$BLOCK B_{name}
	{zp_output(name)}
	E_demand_out_{name}[t,s,n]$(branch_o_{name}[s,n] and txE[t])..		qS[t,s,n] =E= sum(nn$(map_{name}[s,n,nn]), mu[s,n,nn] * (pS[t,s,n]/pD[t,s,nn])**(eta[s,nn]) * qD[t,s,nn]);
	E_demand_nout_{name}[t,s,n]$(branch_no_{name}[s,n] and txE[t])..	qD[t,s,n] =E= sum(nn$(map_{name}[s,n,nn]), mu[s,n,nn] * (pD[t,s,n]/pD[t,s,nn])**(eta[s,nn]) * qD[t,s,nn]);
$ENDBLOCK
"""
# 2.2: scale-preserving nests: 
def Fnorm_output(ftype,name,m,inclusiveVal = False):
	return f"""
$BLOCK B_{name}
	{zp_output(name)}
	{_Fnorm_output_with_InclusiveValue(ftype,name) if inclusiveVal else _Fnorm_output_demand(ftype,name)}
$ENDBLOCK
"""

def CET_norm(name,m,inclusiveVal = False):
	return Fnorm_output('CES',name,m,inclusiveVal=inclusiveVal)
def MNL_out(name,m,inclusiveVal = False):
	return Fnorm_output('exp',name,m,inclusiveVal=inclusiveVal)
