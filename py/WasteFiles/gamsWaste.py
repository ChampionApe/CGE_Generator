# 1. Add recycling technology functions:
recyclTech = """
$MACRO IntApprox(l,u,s,x) (l+sqrt(sqr(x-l)+s)+u-sqrt(sqr(x-u)+s))/2
$MACRO RC_Power_ua(l, u, e, r) (l+(u-l)*(1-r**(e)/(1+e)))
$MACRO RC_Power_ur(l, u, e, p, s) ((u-IntApprox(l,u,s,p))/(u-l))**(1/e)

$FUNCTION RC_ua({l}, {u}, {e}, {r}):
	$IF %RCTech% == 'power': RC_Power_ua( ({l}), ({u}), ({e}), ({r}) ) $ENDIF
$ENDFUNCTION
$FUNCTION RC_ur({l}, {u}, {e}, {p}, {s}):
	$IF %RCTech% == 'power': RC_Power_ur( ({l}), ({u}), ({e}), ({p}), ({s}) ) $ENDIF
$ENDFUNCTION
"""

# 2. Main Waste Management Blocks
def wasteTreatment(name, m, **kwargs):
	return f"""
$BLOCK B_{name}
	E_{name}_W[t,s,m]$({m}_sm[s] and mw_D[m] and txE[t])..	WTD_W[t,m]	=E= sum(ss$(dWS[ss,m]), qWS[t,ss,m] * uWS_D[t,ss,m]); # total waste for domestic treatment
	E_{name}_d[t,s,m]$({m}_sm[s] and mw_D[m] and txE[t])..	WTD_d[t,m]	=E= WTD_dmin[t,m]; # share of waste deposited for landfill
	E_{name}_zeta[t,s,m]$({m}_sm[s] and mw_D[m] and txE[t])..	WTD_zetaE[t,m]	=E= [sum(n$(n_ZW[n]), pD[t,s,n]) * (WTD_gr[t,m]-WTD_ge[t,m])+WTD_gwe[m]*sum(n$(n_wasteE[n]), pS[t,s,n])]/sum(n$(nr2m_D[n,m]), pS[t,s,n]);
	E_{name}_r[t,s,m]$({m}_sm[s] and mw_D[m] and txE[t])..	WTD_r[t,m]	=E= @RC_ur(WTD_alphal[t,m], WTD_alphau[t,m], WTD_beta[t,m], WTD_zetaE[t,m], WTD_smooth[m]); # recycling out of recyclable waste
	E_{name}_a[t,s,m]$({m}_sm[s] and mw_D[m] and txE[t])..	WTD_a[t,m]	=E= @RC_ua(WTD_alphal[t,m], WTD_alphau[t,m], WTD_beta[t,m], WTD_r[t,m]); # output of recycled materials per kton of waste purposed for recycling
	E_{name}_e[t,s,m]$({m}_sm[s] and mw_D[m] and txE[t])..	WTD_e[t,m]	=E= 1-WTD_d[t,m]-WTD_r[t,m]*(1-WTD_dmin[t,m]); # waste for waste incineration
	E_{name}_pWTD[t,s,n]$({m}_sm[s] and nw_D[n] and txE[t]).. pS[t,s,n] =E= sum(m$(n2m_D[n,m]), sum(nn$(n_ZW[nn]), pD[t,s,nn]) * (WTD_gd[t,m]*WTD_d[t,m]+WTD_ge[t,m]*WTD_e[t,m]+WTD_gr[t,m]*WTD_r[t,m]*(1-WTD_dmin[t,m]))-WTD_r[t,m]*WTD_a[t,m]*(1-WTD_dmin[t,m])*sum(nn$(nr2m_D[nn,m]), pS[t,s,nn])-WTD_e[t,m]*WTD_gwe[m]*sum(nn$(n_wasteE[nn]),pS[t,s,nn]));
$ENDBLOCK
"""

def wasteTreatProd(name, m, **kwargs):
	return f"""
$BLOCK B_{name}
	E_{name}_ZW[t,s,n]$({m}_sm[s] and n_ZW[n] and txE[t])..				qD[t,s,n]	=E= sum(m$(mw_D[m]), WTD_W[t,m]* (WTD_gd[t,m] * WTD_d[t,m]+WTD_ge[t,m] *WTD_e[t,m]+WTD_gr[t,m]*WTD_r[t,m]*(1-WTD_dmin[t,m]))); # waste treatment production function
	E_{name}_qSnm[t,s,n]$({m}_output[s,n] and nm_D[n] and txE[t])..		qS[t,s,n]	=E= WTD_qSnmCal[n]+sum(m$(nr2m_D[n,m]), WTD_a[t,m] * WTD_r[t,m] * (1-WTD_dmin[t,m])*WTD_W[t,m]); # supply of recycled materials 
	E_{name}_qSnw[t,s,n]$({m}_output[s,n] and nw_D[n] and txE[t])..		qS[t,s,n]	=E= WTD_qSnwCal[n]+sum(m$(mw_D[m] and n2m_D[n,m]), WTD_W[t,m]); # supply of waste treatment services
	E_{name}_qSWE[t,s,n]$({m}_output[s,n] and n_wasteE[n] and txE[t])..	qS[t,s,n]	=E= WTD_qSWECal[n]+sum(m$(mw_D[m]), WTD_gwe[m] * WTD_e[t,m] * WTD_W[t,m]); # supply of energy from waste incineration
$ENDBLOCK
"""

def wasteTreatCalib(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_alphau[t,m]$(mw_D[m] and txE[t]).. 	WTD_alphau[t,m]	=E= WTD_alphau0[t,m] + alphauCal[m];
	E_{name}_gammar[t,m]$(mw_D[m] and txE[t]).. 	WTD_gr[t,m]		=E= WTD_gr0[t,m] + gammarCal[m];
	E_{name}_gammae[t,m]$(mw_D[m] and txE[t])..		WTD_ge[t,m]		=E= WTD_ge0[t,m] + WTD_pSnwCal[m];
	E_{name}_gammad[t,m]$(mw_D[m] and txE[t])..		WTD_gd[t,m]		=E= WTD_gd0[t,m] + WTD_pSnwCal[m];
$ENDBLOCK
"""