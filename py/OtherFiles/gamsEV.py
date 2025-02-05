############################################################
################		1. StaticNECS		################
############################################################


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