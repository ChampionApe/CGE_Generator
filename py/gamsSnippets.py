from gmsPython.gmsWrite import Syms

# 0.1: Auxiliary functions used for scale-preserving nests:
def _CES(px,py,mu,sigma,norm=None):
	return f"{mu} * ({py}/{px})**({sigma})" if norm is None else f"{mu} * ({py}/({px}*(1+{norm})))**({sigma})"
def _exp(px,py,mu,sigma,norm=None):
	return f"{mu} * exp(({py}-{px})*{sigma})" if norm is None else f"{mu} * exp(({py}-{px})*{sigma}-{norm})"

def _Fnorm_input_demand(ftype,name):
	f = globals()['_'+ftype]
	return f"""E_{name}_qOut[t,s,n]$({name}_branch2o[s,n] and txE[t])..	qD[t,s,n] =E= sum(nn$({name}_map[s,nn,n]), qS[t,s,nn]*{f("pD[t,s,n]","pS[t,s,nn]","mu[s,nn,n]","sigma[s,nn]")} / sum(nnn$({name}_map[s,nn,nnn]), {f("pD[t,s,nnn]","pS[t,s,nn]","mu[s,nn,nnn]","sigma[s,nn]")}));
	E_{name}_qNOut[t,s,n]$({name}_branch2no[s,n] and txE[t])..		qD[t,s,n] =E= sum(nn$({name}_map[s,nn,n]), qD[t,s,nn]*{f("pD[t,s,n]","pD[t,s,nn]","mu[s,nn,n]","sigma[s,nn]")} / sum(nnn$({name}_map[s,nn,nnn]), {f("pD[t,s,nnn]","pD[t,s,nn]","mu[s,nn,nnn]","sigma[s,nn]")}));"""

def _Fnorm_output_demand(ftype,name):
	f = globals()['_'+ftype]
	return f"""E_{name}_qOut[t,s,n]$({name}_branch_o[s,n] and txE[t])..	qS[t,s,n] =E= sum(nn$({name}_map[s,n,nn]), qD[t,s,nn]*{f("pD[t,s,nn]","pS[t,s,n]","mu[s,n,nn]","eta[s,nn]")} / (sum(nnn$({name}_map[s,nnn,nn] and {name}_branch_o[s,nnn]), {f("pS[t,s,nnn]","pD[t,s,nn]","mu[s,nnn,nn]","eta[s,nn]")})+sum(nnn$({name}_map[s,nnn,nn] and {name}_branch_no[s,nnn]), {f("pD[t,s,nnn]","pD[t,s,nn]","mu[s,nnn,nn]","eta[s,nn]")})));
	E_{name}_qNOut[t,s,n]$({name}_branch_no[s,n] and txE[t])..		qD[t,s,n] =E= sum(nn$({name}_map[s,n,nn]), qD[t,s,nn]*{f("pD[t,s,nn]","pD[t,s,n]","mu[s,n,nn]","eta[s,nn]")} / (sum(nnn$({name}_map[s,nnn,nn] and {name}_branch_o[s,nnn]), {f("pS[t,s,nnn]","pD[t,s,nn]","mu[s,nnn,nn]","eta[s,nn]")})+sum(nnn$({name}_map[s,nnn,nn] and {name}_branch_no[s,nnn]), {f("pD[t,s,nnn]","pD[t,s,nn]","mu[s,nnn,nn]","eta[s,nn]")})));"""

def _Fnorm_input_with_InclusiveValue(ftype,name):
	f = globals()['_'+ftype]
	return f"""E_{name}_qOut[t,s,n]$({name}_branch2o[s,n] and txE[t])..	qD[t,s,n] =E= sum(nn$({name}_map[s,nn,n]), qS[t,s,nn]*{f("pD[t,s,n]","pS[t,s,nn]","mu[s,nn,n]","sigma[s,nn]",norm='qnorm[t,s,nn]')} / qiv_inp[t,s,nn]);
	E_{name}_qNOut[t,s,n]$({name}_branch2no[s,n] and txE[t])..		qD[t,s,n] =E= sum(nn$({name}_map[s,nn,n]), qD[t,s,nn]*{f("pD[t,s,n]","pD[t,s,nn]","mu[s,nn,n]","sigma[s,nn]",norm='qnorm[t,s,nn]')} / qiv_inp[t,s,nn]);
	E_{name}_inclVal_out[t,s,n]$({name}_knot_o[s,n] and txE[t])..	qiv_inp[t,s,n] =E= sum(nn$({name}_map[s,n,nn]), {f("pD[t,s,nn]","pS[t,s,n]","mu[s,n,nn]","sigma[s,n]",norm='qnorm[t,s,n]')});
	E_{name}_inclVal_nout[t,s,n]$({name}_knot_no[s,n] and txE[t])..	qiv_inp[t,s,n] =E= sum(nn$({name}_map[s,n,nn]), {f("pD[t,s,nn]","pD[t,s,n]","mu[s,n,nn]","sigma[s,n]",norm='qnorm[t,s,n]')});"""

def _Fnorm_output_with_InclusiveValue(ftype,name):
	f = globals()['_'+ftype]
	return f"""E_{name}_qOut[t,s,n]$({name}_branch_o[s,n] and txE[t])..	qS[t,s,n] =E= sum(nn$({name}_map[s,n,nn]), qD[t,s,nn]*{f("pD[t,s,nn]","pS[t,s,n]","mu[s,n,nn]","eta[s,nn]")} / qiv_out[t,s,nn]);
	E_{name}_qNOut[t,s,n]$({name}_branch_no[s,n] and txE[t])..		qD[t,s,n] =E= sum(nn$({name}_map[s,n,nn]), qD[t,s,nn]*{f("pD[t,s,nn]","pD[t,s,n]","mu[s,n,nn]","eta[s,nn]")} / qiv_out[t,s,nn]);
	E_{name}_inclVal_out[t,s,n]$({name}_knot[s,n] and txE[t])..		qiv_out[t,s,n]=E= sum(nn$({name}_map[s,nn,n] and {name}_branch_o[s,nn]), {f("pS[t,s,nn]","pD[t,s,n]","mu[s,nn,n]","eta[s,n]",norm='qnorm[t,s,n]')})+sum(nn$({name}_map[s,nn,n] and {name}_branch_no[s,nn]), {f("pD[t,s,nn]","pD[t,s,n]","mu[s,nn,n]","eta[s,n]",norm='qnorm[t,s,n]')});"""

# 0.2: Zero profit equations:
def zp_input(name):
	return f"""E_{name}_zpOut[t,s,n]$({name}_knot_o[s,n] and txE[t])..	pS[t,s,n]*qS[t,s,n] =E= sum(nn$({name}_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
	E_{name}_zpNOut[t,s,n]$({name}_knot_no[s,n] and txE[t])..	pD[t,s,n]*qD[t,s,n] =E= sum(nn$({name}_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);"""
def zp_output(name):
	return f"""E_{name}_zp[t,s,n]$({name}_knot[s,n] and txE[t])..	pD[t,s,n]*qD[t,s,n] =E= sum(nn$({name}_map[s,nn,n] and {name}_branch_o[s,nn]), qS[t,s,nn]*pS[t,s,nn])+sum(nn$({name}_map[s,nn,n] and {name}_branch_no[s,nn]), qD[t,s,nn]*pD[t,s,nn]);"""

# 1: Input type nests:
# 1.1: CES nest:
def CES(name,**kwargs):
	return f"""
$BLOCK B_{name}
	{zp_input(name)}
	E_{name}_qOut[t,s,n]$({name}_branch2o[s,n] and txE[t])..	qD[t,s,n] =E= sum(nn$({name}_map[s,nn,n]), mu[s,nn,n] * (pS[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qS[t,s,nn]);
	E_{name}_qNOut[t,s,n]$({name}_branch2no[s,n] and txE[t])..	qD[t,s,n] =E= sum(nn$({name}_map[s,nn,n]), mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qD[t,s,nn]);
$ENDBLOCK
"""

# 1.2: Scale-preserving nests:
def Fnorm_input(ftype,name,inclusiveVal = False):
	return f"""
$BLOCK B_{name}
	{zp_input(name)}
	{_Fnorm_input_with_InclusiveValue(ftype,name) if inclusiveVal else _Fnorm_input_demand(ftype,name)}
$ENDBLOCK
"""

def CES_norm(name, inclusiveVal = False):
	return Fnorm_input('CES',name,inclusiveVal=inclusiveVal)

def MNL(name,inclusiveVal = False):
	return Fnorm_input('exp',name,inclusiveVal=inclusiveVal)

# 2: Output type nests:
# 2.1: CET function:
def CET(name,**kwargs):
	return f"""
$BLOCK B_{name}
	{zp_output(name)}
	E_{name}_demand_out[t,s,n]$({name}_branch_o[s,n] and txE[t])..		qS[t,s,n] =E= sum(nn$({name}_map[s,n,nn]), mu[s,n,nn] * (pS[t,s,n]/pD[t,s,nn])**(eta[s,nn]) * qD[t,s,nn]);
	E_{name}_demand_nout[t,s,n]$({name}_branch_no[s,n] and txE[t])..	qD[t,s,n] =E= sum(nn$({name}_map[s,n,nn]), mu[s,n,nn] * (pD[t,s,n]/pD[t,s,nn])**(eta[s,nn]) * qD[t,s,nn]);
$ENDBLOCK
"""
# 2.2: scale-preserving nests: 
def Fnorm_output(ftype, name, inclusiveVal = False):
	return f"""
$BLOCK B_{name}
	{zp_output(name)}
	{_Fnorm_output_with_InclusiveValue(ftype,name) if inclusiveVal else _Fnorm_output_demand(ftype,name)}
$ENDBLOCK
"""

def CET_norm(name, inclusiveVal = False):
	return Fnorm_output('CES', name, inclusiveVal=inclusiveVal)
def MNL_out(name, inclusiveVal = False):
	return Fnorm_output('exp', name, inclusiveVal=inclusiveVal)



# 3: Technology Functions:
techEOP = """
$MACRO stdNormPdf(x) exp(-sqr(x)/2)/(2*sqrt(Pi))
$MACRO EOP_Logit(p, c, e) (1/(1+exp((c-p)/e)))
$MACRO EOP_Normal(p, c, e) errorf((p-c)/e)
$MACRO EOP_NormalMult(p, c, e) errorf((p/c-1)/e)

$MACRO EOP_NormalCost(p, c, e) EOP_Normal(p, c, e)*c-e*stdNormPdf((p-c)/e)
$MACRO EOP_NormalMultCost(p, c, e) c*(EOP_NormalMult(p, c, e)-


$FUNCTION EOP_Tech({p}, {c}, {e}):
	$IF %techType% == 'normal': EOP_Normal( ({p}), ({c}), ({e}) ) $ENDIF
	$IF %techType% == 'logit' : EOP_Logit( ({p}), ({c}), ({e}) ) $ENDIF
$ENDFUNCTION

$FUNCTION EOP_Cost({p}, {c}, {e}):
	$IF %techType% == 'normal': EOP_NormalCost( ({p}), ({c}), ({e}) ) $ENDIF
$ENDFUNCTION
"""


# X: System of value shares
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
