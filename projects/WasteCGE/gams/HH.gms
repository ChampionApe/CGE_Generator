$ONEOLCOM
$EOLCOM #



;
OPTION SYSOUT=OFF, SOLPRINT=OFF, LIMROW=0, LIMCOL=0, DECIMALS=6;


# User defined functions:

# ----------------------------------------------------------------------------------------------------
#  Define function: SolveEmptyNLP
# ----------------------------------------------------------------------------------------------------


sets
	alias_set
	alias_map2
	n
	s
	t
	taxTypes
	tech
;

alias(n,nn,nnn);
alias(s,ss);

sets
	alias_[alias_set,alias_map2]
	HH_map[s,n,nn]
	HH_map_spinp[s,n,nn]
	HH_map_spout[s,n,nn]
	HH_knout[s,n]
	HH_kninp[s,n]
	HH_spout[s,n]
	HH_spinp[s,n]
	HH_input[s,n]
	HH_output[s,n]
	HH_int[s,n]
	HH_knot[s,n]
	HH_branch[s,n]
	HH_knot_o[s,n]
	HH_knot_no[s,n]
	HH_branch2o[s,n]
	HH_branch2no[s,n]
	HH_endoMu[s,n,nn]
	HH_L2C[s,n,nn]
	HH_L[s,n]
	HH_output_n[n]
	HH_input_n[n]
	HH_sm[s]
	s_p[s]
	n_p[n]
	n_F[n]
	s_HH[s]
	s_G[s]
	s_i[s]
	s_f[s]
	dur_p[n]
	inv_p[n]
	dur2inv[n,nn]
	nEqui[n]
	d_qS[s,n]
	d_qD[s,n]
	d_qSEqui[s,n]
	d_pEqui[n]
	dom2for[n,nn]
	dExport[s,n]
	dImport[s,n,nn]
	dImport_dom[s,n]
	dImport_for[s,n]
	t0[t]
	tx0[t]
	tE[t]
	t2E[t]
	txE[t]
	tx2E[t]
	tx0E[t]
	tx02E[t]
	nestProduction[s,n,nn]
	dtauCO2[s,n]
	dqCO2[s,n]
	nestInvestment[s,n,nn]
	nestHH[s,n,nn]
	L2C[s,n,nn]
	nestG[s,n,nn]
	d_TotalTax[s]
;

parameters
	R_LR
	infl_LR
	g_LR
;

variables
	TotalTax[t,s]
	qCO2[t,s,n]
	M1990
	rDepr[t,s,n]
	p[t,n]
	qD[t,s,n]
	qS[t,s,n]
	sigma[s,n]
	tauCO2[t,s,n]
	tauS[t,s,n]
	tauD[t,s,n]
	tauLump[t,s]
	tauNonEnv[t,s,n]
	tauNonEnv0[t,s,n]
	pD[t,s,n]
	frisch[s,n]
	techCost[tech,t]
	DACCost[t]
	techPot[tech,t]
	uCO2[t,s,n]
	tauCO2agg[t]
	tauDist[t,s,n]
	qCO2agg[t]
	Rrate[t]
	mu[s,n,nn]
	pS[t,s,n]
	crra[s,n]
	Lscale[s,n]
	jTerm[s]
;
$GDXIN HH
$onMulti
$load alias_set
$load alias_map2
$load n
$load s
$load t
$load taxTypes
$load tech
$load alias_
$load HH_map
$load HH_map_spinp
$load HH_map_spout
$load HH_knout
$load HH_kninp
$load HH_spout
$load HH_spinp
$load HH_input
$load HH_output
$load HH_int
$load HH_knot
$load HH_branch
$load HH_knot_o
$load HH_knot_no
$load HH_branch2o
$load HH_branch2no
$load HH_endoMu
$load HH_L2C
$load HH_L
$load HH_output_n
$load HH_input_n
$load HH_sm
$load s_p
$load n_p
$load n_F
$load s_HH
$load s_G
$load s_i
$load s_f
$load dur_p
$load inv_p
$load dur2inv
$load nEqui
$load d_qS
$load d_qD
$load d_qSEqui
$load d_pEqui
$load dom2for
$load dExport
$load dImport
$load dImport_dom
$load dImport_for
$load t0
$load tx0
$load tE
$load t2E
$load txE
$load tx2E
$load tx0E
$load tx02E
$load nestProduction
$load dtauCO2
$load dqCO2
$load nestInvestment
$load nestHH
$load L2C
$load nestG
$load d_TotalTax
$GDXIN
$offMulti;
$GDXIN HH
$onMulti
$load R_LR
$load infl_LR
$load g_LR
$GDXIN
$offMulti;
$GDXIN HH
$onMulti
$load TotalTax
$load qCO2
$load M1990
$load rDepr
$load p
$load qD
$load qS
$load sigma
$load tauCO2
$load tauS
$load tauD
$load tauLump
$load tauNonEnv
$load tauNonEnv0
$load pD
$load frisch
$load techCost
$load DACCost
$load techPot
$load uCO2
$load tauCO2agg
$load tauDist
$load qCO2agg
$load Rrate
$load mu
$load pS
$load crra
$load Lscale
$load jTerm
$GDXIN
$offMulti;





# ------------------------------------------------B_HH------------------------------------------------
#  Initialize B_HH equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_HH_zp[t,s,n];
E_HH_zp[t,s,n]$(hh_knot[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(HH_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_HH_q[t,s,n];
E_HH_q[t,s,n]$(hh_branch[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(HH_map[s,nn,n]), mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qD[t,s,nn]);

# ----------------------------------------------------------------------------------------------------
#  Define B_HH model
# ----------------------------------------------------------------------------------------------------
Model B_HH /
E_HH_zp, E_HH_q
/;



# -------------------------------------------B_HH_isoFrisch-------------------------------------------
#  Initialize B_HH_isoFrisch equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_HH_isoFrisch_labor[t,s,n];
E_HH_isoFrisch_labor[t,s,n]$(hh_l[s,n] and txe[t]).. 	qS[t,s,n]	 =E= 	Lscale[s,n] * ( sum(nn$(HH_L2C[s,n,nn]), pS[t,s,n]/(pD[t,s,nn]*(qD[t,s,nn]**(crra[s,nn]))))**(frisch[s,n]));

# ----------------------------------------------------------------------------------------------------
#  Define B_HH_isoFrisch model
# ----------------------------------------------------------------------------------------------------
Model B_HH_isoFrisch /
E_HH_isoFrisch_labor
/;



# ---------------------------------------------B_HH_pWedge--------------------------------------------
#  Initialize B_HH_pWedge equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_pwOut_HH_pWedge[t,s,n];
E_pwOut_HH_pWedge[t,s,n]$(hh_l[s,n] and txe[t]).. 	pS[t,s,n] 		 =E=  p[t,n]-tauS[t,s,n];
EQUATION E_pwInp_HH_pWedge[t,s,n];
E_pwInp_HH_pWedge[t,s,n]$(hh_input[s,n] and txe[t]).. 	pD[t,s,n]		 =E=  p[t,n]+tauD[t,s,n];
EQUATION E_TaxRev_HH_pWedge[t,s];
E_TaxRev_HH_pWedge[t,s]$(hh_sm[s] and txe[t]).. 		TotalTax[t,s]	 =E=  tauLump[t,s]+sum(n$(HH_input[s,n]), tauD[t,s,n] * qD[t,s,n])+sum(n$(HH_L[s,n]), tauS[t,s,n]*qS[t,s,n]);
EQUATION E_sp_HH_pWedge[t,s];
E_sp_HH_pWedge[t,s]$(hh_sm[s] and txe[t]).. 			jTerm[s]		 =E=  sum(n$(HH_L[s,n]), pS[t,s,n]*qS[t,s,n]) - sum(n$(HH_input[s,n]), pD[t,s,n]*qD[t,s,n])-tauLump[t,s];

# ----------------------------------------------------------------------------------------------------
#  Define B_HH_pWedge model
# ----------------------------------------------------------------------------------------------------
Model B_HH_pWedge /
E_pwOut_HH_pWedge, E_pwInp_HH_pWedge, E_TaxRev_HH_pWedge, E_sp_HH_pWedge
/;



# ----------------------------------------------------------------------------------------------------
#  Define HH model
# ----------------------------------------------------------------------------------------------------
Model HH /
E_HH_zp, E_HH_q, E_HH_isoFrisch_labor, E_pwOut_HH_pWedge, E_pwInp_HH_pWedge, E_TaxRev_HH_pWedge, E_sp_HH_pWedge
/;


# Fix exogenous variables in state B:
sigma.fx[s,n]$(HH_kninp[s,n]) = sigma.l[s,n]$(HH_kninp[s,n]);
mu.fx[s,n,nn]$(((HH_map[s,n,nn] and ( not (HH_endoMu[s,n,nn]))) or HH_endoMu[s,n,nn])) = mu.l[s,n,nn]$(((HH_map[s,n,nn] and ( not (HH_endoMu[s,n,nn]))) or HH_endoMu[s,n,nn]));
frisch.fx[s,n]$(HH_L[s,n]) = frisch.l[s,n]$(HH_L[s,n]);
crra.fx[s,n]$(HH_output[s,n]) = crra.l[s,n]$(HH_output[s,n]);
tauD.fx[t,s,n]$(HH_input[s,n]) = tauD.l[t,s,n]$(HH_input[s,n]);
tauS.fx[t,s,n]$(HH_L[s,n]) = tauS.l[t,s,n]$(HH_L[s,n]);
tauLump.fx[t,s]$(((HH_sm[s] and tx0E[t]) or (HH_sm[s] and t0[t]))) = tauLump.l[t,s]$(((HH_sm[s] and tx0E[t]) or (HH_sm[s] and t0[t])));
p.fx[t,n]$((HH_output_n[n] or HH_input_n[n])) = p.l[t,n]$((HH_output_n[n] or HH_input_n[n]));
Lscale.fx[s,n]$(HH_L[s,n]) = Lscale.l[s,n]$(HH_L[s,n]);
jTerm.fx[s]$(HH_sm[s]) = jTerm.l[s]$(HH_sm[s]);

# Unfix endogenous variables in state B:
pD.lo[t,s,n]$((((HH_int[s,n] or HH_input[s,n]) or (HH_output[s,n] and tx0E[t])) or (HH_output[s,n] and t0[t]))) = -inf;
pD.up[t,s,n]$((((HH_int[s,n] or HH_input[s,n]) or (HH_output[s,n] and tx0E[t])) or (HH_output[s,n] and t0[t]))) = inf;
qS.lo[t,s,n]$(((HH_L[s,n] and tx0E[t]) or (HH_L[s,n] and t0[t]))) = -inf;
qS.up[t,s,n]$(((HH_L[s,n] and tx0E[t]) or (HH_L[s,n] and t0[t]))) = inf;
qD.lo[t,s,n]$((((HH_input[s,n] and tx0E[t]) or (HH_int[s,n] or HH_output[s,n])) or (HH_input[s,n] and t0[t]))) = -inf;
qD.up[t,s,n]$((((HH_input[s,n] and tx0E[t]) or (HH_int[s,n] or HH_output[s,n])) or (HH_input[s,n] and t0[t]))) = inf;
pS.lo[t,s,n]$(HH_L[s,n]) = -inf;
pS.up[t,s,n]$(HH_L[s,n]) = inf;
TotalTax.lo[t,s]$(((HH_sm[s] and tx0E[t]) or (HH_sm[s] and t0[t]))) = -inf;
TotalTax.up[t,s]$(((HH_sm[s] and tx0E[t]) or (HH_sm[s] and t0[t]))) = inf;

solve HH using CNS;