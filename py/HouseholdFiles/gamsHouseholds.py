from gamsSnippets_noOut import *

############################################################
################	1. StaticConsumer		################
############################################################
# 1.1. Simple CRRA value:
def CRRA_vU(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_vU[t,s]$({m}_sm[s] and txE[t])..	vU[t,s]		=E= sum(n$({m}_C[s,n]), qD[t,s,n])**(1-crra[s])/(1-crra[s])+(1+gadj[s])*discF[s]*vU[t+1,s];
	E_{name}_vUT[t,s]$({m}_sm[s] and tE[t])..	vU[t,s]		=E= vU[t-1,s]*(1+vU_tvc[s])/(1+gadj[s]);
$ENDBLOCK
"""

# 1.2. Price/tax blocks: 
def priceBlock(name, m, addInc_tx0 = '', addInc_t0 = ''):
	return f"""
$BLOCK B_{name}
	E_{name}_pD[t,s,n]$({m}_input[s,n] and txE[t])..	pD[t,s,n]		=E= p[t,n]*(1+tauD[t,s,n]); # effective input prices
	E_{name}_w[t,s,n]$({m}_L[s,n] and txE[t])..			pS[t,s,n]		=E= p[t,n]*(1-tauS[t,s,n]); # effective wage rate after taxes
	E_{name}_TotalTax[t,s]$({m}_sm[s] and txE[t])..		TotalTax[t,s]	=E= tauLump[t,s]+sum(n$({m}_input[s,n]), tauD[t,s,n] * p[t,n] * qD[t,s,n])+sum(n$({m}_L[s,n]), tauS[t,s,n]*p[t,n]*qS[t,s,n]); # total tax transfers
	E_{name}_vA0[t,s]$({m}_sm[s] and t0[t])..			vA[t+1,s]		=E= (vA[t,s] * Rrate[t] + sum(n$({m}_L[s,n]), p[t,n]*qS[t,s,n])-sum(n$({m}_input[s,n]), p[t,n]*qD[t,s,n])-TotalTax[t,s]{addInc_t0})/(1+g_LR); # law of motion for household assets, initial year
	E_{name}_vA[t,s]$({m}_sm[s] and tx0E[t])..			vA[t+1,s]		=E= (vA[t,s] * Rrate[t] + sum(n$({m}_L[s,n]), p[t,n]*qS[t,s,n])-sum(n$({m}_input[s,n]), p[t,n]*qD[t,s,n])-TotalTax[t,s]{addInc_tx0})/(1+g_LR); # law of motion for household assets
$ENDBLOCK
"""

# 1.3. Block for calibration of taxes using permannet adjustments. Can accept different tax instruments.
def taxCalibBlock(name, m, taxInstr, taxCond):
	""" taxInstr is a gpy symbol, taxCond is a condition"""
	return f"""
$BLOCK B_{name}
	E_{name}_taxRevPar{Syms.gpyDomains(taxInstr)}{Syms.gpyCondition(taxCond)}..	{Syms.gpy(taxInstr)} =E= {Syms.gpy(taxInstr).replace(taxInstr.name, taxInstr.name+'0')}+taxRevPar[s];
$ENDBLOCK
"""

# 1.4 Init method:
def init_vU(m):
	""" Initialize variables for CRRA-GHH model as in steady state"""
	return f"""
vU.l[t,s]$({m}_sm[s] and txE[t]) = (sum(n$({m}_C[s,n]), qD.l[t,s,n])**(1-crra.l[s])/(1-crra.l[s]))/(1-discF.l[s]*(1+gadj.l[s]));
vU.l[t,s]$({m}_sm[s] and tE[t])  = vU.l[t-1,s];
"""


# 1.5. With GHH preferences
def CRRA_GHH_vU(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_qC[t,s]$({m}_sm[s] and txE[t])..	qC[t,s]		=E= sum([n,nn]$({m}_L2C[s,n,nn]), qD[t,s,nn]-frisch[s]*Lscale[s]*(qS[t,s,n]/Lscale[s])**((1+frisch[s])/frisch[s])/(1+frisch[s]));	
	E_{name}_vU[t,s]$({m}_sm[s] and txE[t])..	vU[t,s]		=E= (qC[t,s]**(1-crra[s]))/(1-crra[s])+(1+gadj[s])*discF[s]*vU[t+1,s];
	E_{name}_vUT[t,s]$({m}_sm[s] and tE[t])..	vU[t,s]		=E= vU[t-1,s]*(1+vU_tvc[s])/(1+gadj[s]);
	E_{name}_qL[t,s,n]$({m}_L[s,n] and txE[t]).. qS[t,s,n]	=E= Lscale[s] * sum(nn$({m}_L2C[s,n,nn]), pS[t,s,n]/pD[t,s,nn])**(frisch[s]);
$ENDBLOCK
"""

def init_GHH_vU(m):
	""" Initialize variables for CRRA-GHH model as in steady state"""
	return f"""
Lscale.l[s]$({m}_sm[s])	= sum([t,n,nn]$(t0[t] and {m}_L2C[s,n,nn]), qS.l[t,s,n] * (pD.l[t,s,nn]/pS.l[t,s,n])**(1/frisch.l[s]));
qC.l[t,s]$({m}_sm[s] and txE[t]) = sum([n,nn]$({m}_L2C[s,n,nn]), qD.l[t,s,nn]-frisch.l[s]*Lscale.l[s]*(qS.l[t,s,n]/Lscale.l[s])**((1+frisch.l[s])/frisch.l[s])/(1+frisch.l[s]));
vU.l[t,s]$({m}_sm[s] and txE[t]) = (qC.l[t,s]**(1-crra.l[s])/(1-crra.l[s]))/(1-discF.l[s]);
vU.l[t,s]$({m}_sm[s] and tE[t])  = vU.l[t-1,s];
"""

############################################################
################		2. Ramsey			################
############################################################

def CRRA_Euler(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_Euler[t,s,n]$({m}_C[s,n] and tx0E[t])..	qD[t,s,n]	=E= qD[t-1,s,n]*(discF[s]*Rrate[t]*(pD[t-1,s,n]/pD[t,s,n]))**(1/crra[s])/(1+g_LR);
	E_{name}_TVC[t,s]$({m}_sm[s] and tE[t])..			vA[t,s]		=E= vA[t-1,s]*(1+vA_tvc[s])/(1+g_LR);
$ENDBLOCK
"""

############################################################
################		3. IdxFund			################
############################################################

def idxFund(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_vAt0[t,s]$({m}_sm[s] and t0[t])..	vA[t,s]	=E= uIdxFund[s] * vIdxFund[t]+vA_F[s];
$ENDBLOCK
"""


############################################################
################		4. EV measures		################
############################################################


### EVIInc defines auxiliary variables used for definition of EV measures.
def EVIncEq_StaticNCES(name, m, GHH = False):
	qC = 'qC[t,s]' if GHH else """sum(n$({m}_C[s,n]), qD[t,s,n])"""
	text = f"""E_{name}_yInc[t,s]$({m}_sm[s] and txE[t])..		yInc[t,s] =E= vA[t+1,s]*(1+g_LR)-vA[t,s]*Rrate[t]+{qC};
	E_{name}_HIncT[t,s]$({m}_sm[s] and tE[t])..		HInc[t,s] =E= yInc[t-1,s]/(1-(1+g_LR)/R_LR);
	E_{name}_HInc[t,s]$({m}_sm[s] and tx0E[t])..	HInc[t,s] =E= (HInc[t-1,s]-yInc[t-1,s])*Rrate[t-1]/(1+g_LR);
	E_{name}_WIncT[t,s]$({m}_sm[s] and tE[t])..		WInc[t,s] =E= sum(n$({m}_L[s,n]), pS[t-1,s,n]*qS[t-1,s,n])/(1-(1+g_LR)/R_LR);
	E_{name}_WInc[t,s]$({m}_sm[s] and tx0E[t])..	WInc[t,s] =E= (WInc[t-1,s]-sum(n$({m}_L[s,n]), pS[t-1,s,n]*qS[t-1,s,n]))*Rrate[t-1]/(1+g_LR);
	E_{name}_TIncT[t,s]$({m}_sm[s] and tE[t])..		TInc[t,s] =E= tauLump[t-1,s]/(1-(1+g_LR)/R_LR);
	E_{name}_TInc[t,s]$({m}_sm[s] and tx0E[t])..	TInc[t,s] =E= (TInc[t-1,s]-tauLump[t-1,s])/(1-(1+g_LR)/R_LR);"""
	zInc = """
	E_{name}_ZInc[t,s]$({m}_sm[s])..				ZInc[t,s] =E= frisch[s]*WInc[t,s]/(1+frisch[s]);"""
	return text+zInc if GHH else text

def EVIncEq_Ramsey(name, m, GHH = False):
	pVeq = f"""
	E_{name}_pVT[t,s]$({m}_sm[s] and tE[t])..		pV[t,s]	  =E= sum(n$({m}_C[s,n]), pD[t,s,n])/( (1-discF[s]**(1/crra[s])/(R_LR**((crra[s]-1)/crra[s])))**(crra[s]/(crra[s]-1)) );
	E_{name}_pV[t,s]$({m}_sm[s] and tx0E[t])..		pV[t,s]	  =E= Rrate[t-1]*[(pV[t-1,s]**((crra[s]-1)/crra[s])-sum(n$({m}_C[s,n]), pD[t-1,s,n])**((crra[s]-1)/crra[s]))/(discF[s]**(1/crra[s]))]**((crra[s]/(crra[s]-1)));"""
	return EVIncEq_StaticNCES(name, m, GHH = GHH) + pVeq

def EVInc_StaticNCES(name, m, GHH = False):
	return f"""
$BLOCK B_{name}
	{EVIncEq_StaticNCES(name,m,GHH = GHH)}
$ENDBLOCK
"""
def EVInc_Ramsey(name, m, GHH = False):
	return f"""
$BLOCK B_{name}
	{EVIncEq_Ramsey(name,m,GHH = GHH)}
$ENDBLOCK
"""

def initRamsey(states, GHH = False):
	return f"""
Set state /{', '.join(states)}/;
alias(state, stateAls);

Variables 
yInc[t,s,state], HInc[t,s,state], WInc[t,s,state], ZInc[t,s,state], TInc[t,s,state], vAInc[t,s,state], pV[t,s,state]
EV_pV[t,s,state], EV_vA[t,s,state], EV_HInc[t,s,state], EV_WInc[t,s,state], EV_ZInc[t,s,state], EV_TInc[t,s,state], EV[t,s,state];
"""

### Solve EVInc without adding equation blocks etc.:
def init_EVIncStaticNCES(m, state, GHH = False):
	qC = 'qC.l[t,s]' if GHH else """sum(n$({m}_C[s,n]), qD.l[t,s,n])"""
	text = f"""
	yInc.l[t,s,state]$({m}_sm[s] and txE[t] and sameAs(state, '{state}')) = vA.l[t+1,s]*(1+g_LR)-vA.l[t,s]*Rrate.l[t]+{qC};
	HInc.l[t,s,state]$({m}_sm[s] and tE[t] and sameAs(state, '{state}'))  = yInc.l[t-1,s,state]/(1-(1+g_LR)/R_LR);
	WInc.l[t,s,state]$({m}_sm[s] and tE[t] and sameAs(state, '{state}'))  = sum(n$({m}_L[s,n]), pS.l[t-1,s,n]*qS.l[t-1,s,n])/(1-(1+g_LR)/R_LR);
	TInc.l[t,s,state]$({m}_sm[s] and tE[t] and sameAs(state, '{state}'))  = tauLump.l[t-1,s]/(1-(1+g_LR)/R_LR);
	vAInc.l[t,s,state]$({m}_sm[s] and sameAs(state, '{state}')) = vA.l[t,s];
	pV.l[t,s,state]$({m}_sm[s] and txE[t] and sameAs(state, '{state}')) = sum(n$({m}_C[s,n]), pD.l[t,s,n]);
	pV.l[t,s,state]$({m}_sm[s] and tE[t] and sameAs(state, '{state}')) = sum(n$({m}_C[s,n]), pD.l[t-1,s,n]);

Scalar tscl_{m};

tscl_{m} = card(t)-1;
While(tscl_{m} >= 1,
	Hinc.l[t,s,state]$({m}_sm[s] and (ord(t) = tscl_{m}) and sameAs(state, '{state}')) = HInc.l[t+1,s,state]*(1+g_LR)/Rrate.l[t]+yInc.l[t,s,state];
	WInc.l[t,s,state]$({m}_sm[s] and (ord(t) = tscl_{m}) and sameAs(state, '{state}')) = WInc.l[t+1,s,state]*(1+g_LR)/Rrate.l[t]+sum(n$({m}_L[s,n]), pS.l[t,s,n]*qS.l[t,s,n]);
	TInc.l[t,s,state]$({m}_sm[s] and (ord(t) = tscl_{m}) and sameAs(state, '{state}')) = TInc.l[t+1,s,state]*(1+g_LR)/Rrate.l[t]+tauLump.l[t,s];
	tscl_{m} = tscl_{m}-1;
);
"""

	if GHH:
		text += f"""ZInc.l[t,s,state]$({m}_sm[s] and sameAs(state, '{state}')) = frisch.l[s]*WInc.l[t,s,state]/(1+frisch.l[s]);"""
	return text

def init_EVIncRamsey(m, state, GHH = False):
	text = init_EVIncStaticNCES(m, state, GHH = GHH) # note that pV is defiend simply as the consumer price index in the staticNCES run already.

	pC = f"""sum(n$({m}_C[s,n]), pD.l[t,s,n])"""
	pCm = f"""sum(n$({m}_C[s,n]), pD.l[t-1,s,n])"""
	return text + f"""
	pV.l[t,s,state]$({m}_sm[s] and tE[t] and sameAs(state, '{state}')) = pV.l[t,s,state]/( (1-discF.l[s]**(1/crra.l[s])/(R_LR**((crra.l[s]-1)/crra.l[s])))**(crra.l[s]/(crra.l[s]-1)) );

tscl_{m} = card(t)-1;
While(tscl_{m} >= 1,
	pV.l[t,s,state]$({m}_sm[s] and (ord(t) = tscl_{m}) and sameAs(state, '{state}')) = (pV.l[t,s,state]**((crra.l[s]-1)/crra.l[s])+discF.l[s]**(1/crra.l[s])*(pV.l[t+1,s,state]/Rrate.l[t])**((crra.l[s]-1)/crra.l[s]))**(crra.l[s]/(crra.l[s]-1));
	tscl_{m} = tscl_{m}-1;
);
"""

### EV measures:
def init_EVStaticNCES(m, state, base = 'base', GHH = False):
	""" Get EV measures """
	relPrices = f"""((sum(stateAls$(sameAs(stateAls, {base})), pV.l[t,s,stateAls])-pV.l[t,s,state])/pV.l[t,s,state])"""
	text = f"""
	{init_EVIncStaticNCES(m, state, GHH = GHH)}

	EV_pV.l[t,s,state]$({m}_sm[s] and tE[t] and sameAs(state, '{state}')) = {relPrices}*yInc.l[t-1,s,state]/(1-(1+g_LR)/R_LR);

tscl_{m} = card(t)-1;
While(tscl_{m} >= 1,
	EV_pV.l[t,s,state]$({m}_sm[s] and (ord(t) = tscl_{m}) and sameAs(state, '{state}')) = EV_pV.l[t+1,s,state]*(1+g_LR)/Rrate.l[t]+{relPrices}*yInc.l[t,s];
	tscl_{m} = tscl_{m}-1;
);

	EV_vA.l[t,s,state]$({m}_sm[s] and sameAs(state, '{state}')) = vAInc.l[t,s,state]-sum(stateAls$(sameAs(stateAls, {base})), vAInc.l[t,s,stateAls]);
	EV_HInc.l[t,s,state]$({m}_sm[s] and sameAs(state, '{state}')) = HInc.l[t,s,state]-sum(stateAls$(sameAs(stateAls, {base})), HInc.l[t,s,stateAls]);
	EV_WInc.l[t,s,state]$({m}_sm[s] and sameAs(state, '{state}')) = WInc.l[t,s,state]-sum(stateAls$(sameAs(stateAls, {base})), WInc.l[t,s,stateAls]);
	EV_TInc.l[t,s,state]$({m}_sm[s] and sameAs(state, '{state}')) = -TInc.l[t,s,state]+sum(stateAls$(sameAs(stateAls, {base})), TInc.l[t,s,stateAls]);
	EV.l[t,s,state]$({m}_sm[s] and sameAs(state, '{state}')) = EV_pV.l[t,s,state]+EV_vA.l[t,s,state]+EV_HInc.l[t,s,state];
"""
	if GHH:
		text += f""" EV_ZInc.l[t,s,state]$({m}_sm[s] and sameAs(state, '{state}')) = sum(stateAls$(sameAs(stateAls, {base})), ZInc.l[t,s,stateAls])-ZInc.l[t,s,state];"""
	return text

def init_EVRamsey(m, state, base = 'base', GHH = False):
	""" Get EV measures """
	text = f"""
	{init_EVIncRamsey(m, state, GHH = GHH)}

	EV_pV.l[t,s,state]$({m}_sm[s] and sameAs(state, '{state}')) = (sum(stateAls$(sameAs(stateAls, {base})), pV.l[t,s,stateAls])-pV.l[t,s,state])*(vAInc.l[t,s,state]+HInc.l[t,s,state])/pV.l[t,s,state];	
	EV_vA.l[t,s,state]$({m}_sm[s] and sameAs(state, '{state}')) = vAInc.l[t,s,state]-sum(stateAls$(sameAs(stateAls, {base})), vAInc.l[t,s,stateAls]);
	EV_HInc.l[t,s,state]$({m}_sm[s] and sameAs(state, '{state}')) = HInc.l[t,s,state]-sum(stateAls$(sameAs(stateAls, {base})), HInc.l[t,s,stateAls]);
	EV_WInc.l[t,s,state]$({m}_sm[s] and sameAs(state, '{state}')) = WInc.l[t,s,state]-sum(stateAls$(sameAs(stateAls, {base})), WInc.l[t,s,stateAls]);
	EV_TInc.l[t,s,state]$({m}_sm[s] and sameAs(state, '{state}')) = sum(stateAls$(sameAs(stateAls, {base})), TInc.l[t,s,stateAls])-TInc.l[t,s,state];
	EV.l[t,s,state]$({m}_sm[s] and sameAs(state, '{state}')) = EV_pV.l[t,s,state]+EV_vA.l[t,s,state]+EV_HInc.l[t,s,state];
"""
	if GHH:
		text += f""" EV_ZInc.l[t,s,state]$({m}_sm[s] and sameAs(state, '{state}')) = sum(stateAls$(sameAs(stateAls, {base})), ZInc.l[t,s,stateAls])-ZInc.l[t,s,state];"""
	return text