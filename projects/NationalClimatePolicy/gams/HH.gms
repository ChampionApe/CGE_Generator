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
	taxTypes
	t
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
	t1[t]
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
	frisch[s]
	crra[s]
	discF[s]
	pS[t,s,n]
	vAssets[t,s]
	DACCost[t]
	techPot[tech,t]
	techCost[tech,t]
	uCO2[t,s,n]
	tauCO2agg[t]
	tauDist[t,s,n]
	qCO2agg[t]
	Rrate[t]
	iRate[t]
	mu[s,n,nn]
	sp[t,s]
	qC[t,s]
	discUtil[t,s]
	h_tvc[s]
	Lscale[s]
	jTerm[s]
;
$GDXIN HH
$onMulti
$load alias_set
$load alias_map2
$load n
$load s
$load taxTypes
$load t
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
$load t1
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
$load crra
$load discF
$load pS
$load vAssets
$load DACCost
$load techPot
$load techCost
$load uCO2
$load tauCO2agg
$load tauDist
$load qCO2agg
$load Rrate
$load iRate
$load mu
$load sp
$load qC
$load discUtil
$load h_tvc
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



# --------------------------------------------B_HH_CRRA_GHH-------------------------------------------
#  Initialize B_HH_CRRA_GHH equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_HH_CRRA_GHH_qC[t,s];
E_HH_CRRA_GHH_qC[t,s]$(hh_sm[s] and txe[t]).. 	qC[t,s]			 =E=  sum([n,nn]$(HH_L2C[s,n,nn]), qD[t,s,nn]-frisch[s]*(qS[t,s,n]/Lscale[s])**((1+frisch[s])/frisch[s])/(1+frisch[s]));
EQUATION E_HH_CRRA_GHH_V[t,s];
E_HH_CRRA_GHH_V[t,s]$(hh_sm[s] and txe[t]).. 	discUtil[t,s]	 =E=  qC[t,s]**(1-crra[s])/(1-crra[s])+discF[s]*discUtil[t+1,s];
EQUATION E_HH_CRRA_GHH_VT[t,s];
E_HH_CRRA_GHH_VT[t,s]$(hh_sm[s] and te[t]).. 	discUtil[t,s]	 =E=  (qC[t-1,s]**(1-crra[s])/(1-crra[s]))/(1-discF[s]);
EQUATION E_HH_CRRA_GHH_L[t,s,n];
E_HH_CRRA_GHH_L[t,s,n]$(hh_l[s,n] and txe[t]).. 	qS[t,s,n]		 =E=  Lscale[s] * sum(nn$(HH_L2C[s,n,nn]), pS[t,s,n]/pD[t,s,nn])**(frisch[s]);

# ----------------------------------------------------------------------------------------------------
#  Define B_HH_CRRA_GHH model
# ----------------------------------------------------------------------------------------------------
Model B_HH_CRRA_GHH /
E_HH_CRRA_GHH_qC, E_HH_CRRA_GHH_V, E_HH_CRRA_GHH_VT, E_HH_CRRA_GHH_L
/;



# ---------------------------------------------B_HH_pWedge--------------------------------------------
#  Initialize B_HH_pWedge equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_HH_pWedge_pwOut[t,s,n];
E_HH_pWedge_pwOut[t,s,n]$(hh_l[s,n] and txe[t]).. 	pS[t,s,n] 		 =E=  p[t,n]-tauS[t,s,n];
EQUATION E_HH_pWedge_pwInp[t,s,n];
E_HH_pWedge_pwInp[t,s,n]$(hh_input[s,n] and txe[t]).. 	pD[t,s,n]		 =E=  p[t,n]+tauD[t,s,n];
EQUATION E_HH_pWedge_TaxRev[t,s];
E_HH_pWedge_TaxRev[t,s]$(hh_sm[s] and txe[t]).. 		TotalTax[t,s]	 =E=  tauLump[t,s]+sum(n$(HH_input[s,n]), tauD[t,s,n] * qD[t,s,n])+sum(n$(HH_L[s,n]), tauS[t,s,n]*qS[t,s,n]);
EQUATION E_HH_pWedge_sp[t,s];
E_HH_pWedge_sp[t,s]$(hh_sm[s] and txe[t]).. 			sp[t,s]			 =E=  sum(n$(HH_L[s,n]), pS[t,s,n]*qS[t,s,n]) - sum(n$(HH_input[s,n]), pD[t,s,n]*qD[t,s,n])-tauLump[t,s];

# ----------------------------------------------------------------------------------------------------
#  Define B_HH_pWedge model
# ----------------------------------------------------------------------------------------------------
Model B_HH_pWedge /
E_HH_pWedge_pwOut, E_HH_pWedge_pwInp, E_HH_pWedge_TaxRev, E_HH_pWedge_sp
/;



# ---------------------------------------------B_HH_euler---------------------------------------------
#  Initialize B_HH_euler equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_HH_euler_lom[t,s];
E_HH_euler_lom[t,s]$(hh_sm[s] and txe[t]).. 				vAssets[t+1,s]	 =E=  ((vAssets[t,s]+jTerm[s])*iRate[t]+sp[t,s])/((1+g_LR)*(1+infl_LR));
EQUATION E_HH_euler_euler[t,s];
E_HH_euler_euler[t,s]$(hh_sm[s] and tx0e[t]).. 			qC[t,s]			 =E=  qC[t-1,s]*(discF[s]*Rrate[t]*sum(n$(HH_output[s,n]), pD[t-1,s,n]/pD[t,s,n]))**(1/crra[s]);
EQUATION E_HH_euler_tvc[t,s];
E_HH_euler_tvc[t,s]$(hh_sm[s] and te[t]).. 				vAssets[t,s]	 =E=  (1+h_tvc[s])*vAssets[t-1,s];

# ----------------------------------------------------------------------------------------------------
#  Define B_HH_euler model
# ----------------------------------------------------------------------------------------------------
Model B_HH_euler /
E_HH_euler_lom, E_HH_euler_euler, E_HH_euler_tvc
/;



# ----------------------------------------------------------------------------------------------------
#  Define M_HH model
# ----------------------------------------------------------------------------------------------------
Model M_HH /
E_HH_zp, E_HH_q, E_HH_CRRA_GHH_qC, E_HH_CRRA_GHH_V, E_HH_CRRA_GHH_VT, E_HH_CRRA_GHH_L, E_HH_pWedge_pwOut, E_HH_pWedge_pwInp, E_HH_pWedge_TaxRev, E_HH_pWedge_sp, E_HH_euler_lom, E_HH_euler_euler, E_HH_euler_tvc
/;


# Fix exogenous variables in state B:
sigma.fx[s,n]$(HH_kninp[s,n]) = sigma.l[s,n]$(HH_kninp[s,n]);
mu.fx[s,n,nn]$(((HH_map[s,n,nn] and ( not (HH_endoMu[s,n,nn]))) or HH_endoMu[s,n,nn])) = mu.l[s,n,nn]$(((HH_map[s,n,nn] and ( not (HH_endoMu[s,n,nn]))) or HH_endoMu[s,n,nn]));
discF.fx[s]$(HH_sm[s]) = discF.l[s]$(HH_sm[s]);
frisch.fx[s]$(HH_sm[s]) = frisch.l[s]$(HH_sm[s]);
crra.fx[s]$(HH_sm[s]) = crra.l[s]$(HH_sm[s]);
Rrate.fx[t] = Rrate.l[t];
iRate.fx[t] = iRate.l[t];
h_tvc.fx[s]$(HH_sm[s]) = h_tvc.l[s]$(HH_sm[s]);
vAssets.fx[t,s]$((HH_sm[s] and t0[t])) = vAssets.l[t,s]$((HH_sm[s] and t0[t]));
tauD.fx[t,s,n]$(HH_input[s,n]) = tauD.l[t,s,n]$(HH_input[s,n]);
tauS.fx[t,s,n]$(HH_L[s,n]) = tauS.l[t,s,n]$(HH_L[s,n]);
tauLump.fx[t,s]$(((HH_sm[s] and tx0E[t]) or (HH_sm[s] and t0[t]))) = tauLump.l[t,s]$(((HH_sm[s] and tx0E[t]) or (HH_sm[s] and t0[t])));
p.fx[t,n]$((HH_output_n[n] or HH_input_n[n])) = p.l[t,n]$((HH_output_n[n] or HH_input_n[n]));
Lscale.fx[s]$(HH_sm[s]) = Lscale.l[s]$(HH_sm[s]);
jTerm.fx[s]$(HH_sm[s]) = jTerm.l[s]$(HH_sm[s]);

# Unfix endogenous variables in state B:
pD.lo[t,s,n]$((((HH_int[s,n] or HH_input[s,n]) or (HH_output[s,n] and tx0E[t])) or (HH_output[s,n] and t0[t]))) = -inf;
pD.up[t,s,n]$((((HH_int[s,n] or HH_input[s,n]) or (HH_output[s,n] and tx0E[t])) or (HH_output[s,n] and t0[t]))) = inf;
qS.lo[t,s,n]$(((HH_L[s,n] and tx0E[t]) or (HH_L[s,n] and t0[t]))) = -inf;
qS.up[t,s,n]$(((HH_L[s,n] and tx0E[t]) or (HH_L[s,n] and t0[t]))) = inf;
qD.lo[t,s,n]$((((HH_input[s,n] and tx0E[t]) or (HH_int[s,n] or HH_output[s,n])) or (HH_input[s,n] and t0[t]))) = -inf;
qD.up[t,s,n]$((((HH_input[s,n] and tx0E[t]) or (HH_int[s,n] or HH_output[s,n])) or (HH_input[s,n] and t0[t]))) = inf;
pS.lo[t,s,n]$((HH_L[s,n] and txE[t])) = -inf;
pS.up[t,s,n]$((HH_L[s,n] and txE[t])) = inf;
sp.lo[t,s]$((HH_sm[s] and txE[t])) = -inf;
sp.up[t,s]$((HH_sm[s] and txE[t])) = inf;
vAssets.lo[t,s]$(((HH_sm[s] and tx0[t]) or (HH_sm[s] and t1[t]))) = -inf;
vAssets.up[t,s]$(((HH_sm[s] and tx0[t]) or (HH_sm[s] and t1[t]))) = inf;
qC.lo[t,s]$((HH_sm[s] and txE[t])) = -inf;
qC.up[t,s]$((HH_sm[s] and txE[t])) = inf;
discUtil.lo[t,s]$(HH_sm[s]) = -inf;
discUtil.up[t,s]$(HH_sm[s]) = inf;
TotalTax.lo[t,s]$(((HH_sm[s] and tx0E[t]) or (HH_sm[s] and t0[t]))) = -inf;
TotalTax.up[t,s]$(((HH_sm[s] and tx0E[t]) or (HH_sm[s] and t0[t]))) = inf;

solve M_HH using CNS;
