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
;

alias(n,nn,nnn);
alias(s,ss);

sets
	alias_[alias_set,alias_map2]
	P_map[s,n,nn]
	P_map_spinp[s,n,nn]
	P_map_spout[s,n,nn]
	P_knout[s,n]
	P_kninp[s,n]
	P_spout[s,n]
	P_spinp[s,n]
	P_input[s,n]
	P_output[s,n]
	P_int[s,n]
	W_map[s,n,nn]
	W_knot[s,n]
	W_branch[s,n]
	W_knot_o[s,n]
	W_knot_no[s,n]
	W_branch2o[s,n]
	W_branch2no[s,n]
	O_map[s,n,nn]
	O_knot[s,n]
	O_branch[s,n]
	O_knot_o[s,n]
	O_knot_no[s,n]
	O_branch2o[s,n]
	O_branch2no[s,n]
	P_sm[s]
	P_output_n[n]
	P_input_n[n]
	P_endoMu[s,n,nn]
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
	dtauCO2[t,s,n]
	dqCO2[t,s,n]
	nestInvestment[s,n,nn]
	nestHH[s,n,nn]
	L2C[s,n,nn]
	nestG[s,n,nn]
	d_TotalTax[t,s]
	P_dur[s,n]
	P_dur2inv[s,n,nn]
	P_inv[s,n]
;

parameters
	R_LR
	infl_LR
	g_LR
;

variables
	vTax[t,s,taxTypes]
	TotalTax[t,s]
	vD[t,s,n]
	vD_dur[t,s,n]
	vD_depr[t,s,n]
	vD_inv[t,s,n]
	qCO2[t,s,n]
	rDepr[t,s,n]
	vS[t,s,n]
	p[t,n]
	qD[t,s,n]
	pD_dur[t,s,n]
	qS[t,s,n]
	sigma[s,n]
	tauCO2[t,s,n]
	tauS[t,s,n]
	tauD[t,s,n]
	tauLump[t,s]
	tauNonEnv[t,s,n]
	tauNonEnv0[t,s,n]
	pD[t,s,n]
	Rrate[t]
	mu[s,n,nn]
	pS[t,s,n]
	adjCostPar[s,n]
	K_tvc[s,n]
	adjCost[t,s]
	markup[s]
	taxRevPar[s]
;
$GDXIN P
$onMulti
$load alias_set
$load alias_map2
$load n
$load s
$load t
$load taxTypes
$load alias_
$load P_map
$load P_map_spinp
$load P_map_spout
$load P_knout
$load P_kninp
$load P_spout
$load P_spinp
$load P_input
$load P_output
$load P_int
$load W_map
$load W_knot
$load W_branch
$load W_knot_o
$load W_knot_no
$load W_branch2o
$load W_branch2no
$load O_map
$load O_knot
$load O_branch
$load O_knot_o
$load O_knot_no
$load O_branch2o
$load O_branch2no
$load P_sm
$load P_output_n
$load P_input_n
$load P_endoMu
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
$load P_dur
$load P_dur2inv
$load P_inv
$GDXIN
$offMulti;
$GDXIN P
$onMulti
$load R_LR
$load infl_LR
$load g_LR
$GDXIN
$offMulti;
$GDXIN P
$onMulti
$load vTax
$load TotalTax
$load vD
$load vD_dur
$load vD_depr
$load vD_inv
$load qCO2
$load rDepr
$load vS
$load p
$load qD
$load pD_dur
$load qS
$load sigma
$load tauCO2
$load tauS
$load tauD
$load tauLump
$load tauNonEnv
$load tauNonEnv0
$load pD
$load Rrate
$load mu
$load pS
$load adjCostPar
$load K_tvc
$load adjCost
$load markup
$load taxRevPar
$GDXIN
$offMulti;





# -------------------------------------------------B_W------------------------------------------------
#  Initialize B_W equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_W_zpOut[t,s,n];
E_W_zpOut[t,s,n]$(w_knot_o[s,n] and txe[t]).. 	pS[t,s,n]*qS[t,s,n]  =E=  sum(nn$(W_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_W_zpNOut[t,s,n];
E_W_zpNOut[t,s,n]$(w_knot_no[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(W_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_W_qOut[t,s,n];
E_W_qOut[t,s,n]$(w_branch2o[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(W_map[s,nn,n]), mu[s,nn,n] * (pS[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qS[t,s,nn]);
EQUATION E_W_qNOut[t,s,n];
E_W_qNOut[t,s,n]$(w_branch2no[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(W_map[s,nn,n]), mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qD[t,s,nn]);

# ----------------------------------------------------------------------------------------------------
#  Define B_W model
# ----------------------------------------------------------------------------------------------------
Model B_W /
E_W_zpOut, E_W_zpNOut, E_W_qOut, E_W_qNOut
/;



# -------------------------------------------------B_O------------------------------------------------
#  Initialize B_O equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_O_zpOut[t,s,n];
E_O_zpOut[t,s,n]$(o_knot_o[s,n] and txe[t]).. 	pS[t,s,n]*qS[t,s,n]  =E=  sum(nn$(O_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_O_zpNOut[t,s,n];
E_O_zpNOut[t,s,n]$(o_knot_no[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(O_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_O_qOut[t,s,n];
E_O_qOut[t,s,n]$(o_branch2o[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(O_map[s,nn,n]), mu[s,nn,n] * (pS[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qS[t,s,nn]);
EQUATION E_O_qNOut[t,s,n];
E_O_qNOut[t,s,n]$(o_branch2no[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(O_map[s,nn,n]), mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qD[t,s,nn]);

# ----------------------------------------------------------------------------------------------------
#  Define B_O model
# ----------------------------------------------------------------------------------------------------
Model B_O /
E_O_zpOut, E_O_zpNOut, E_O_qOut, E_O_qNOut
/;



# ---------------------------------------------B_P_adjCost--------------------------------------------
#  Initialize B_P_adjCost equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_P_adjCost_lom[t,s,n];
E_P_adjCost_lom[t,s,n]$(p_dur[s,n] and txe[t]).. 		qD[t+1,s,n]	 =E=  (qD[t,s,n]*(1-rDepr[t,s,n])+sum(nn$(P_dur2inv[s,n,nn]), qD[t,s,nn]))/(1+g_LR);
EQUATION E_P_adjCost_pk[t,s,n];
E_P_adjCost_pk[t,s,n]$(p_dur[s,n] and tx02e[t]).. 	pD[t,s,n]	 =E=  sqrt(sqr(sum(nn$(P_dur2inv[s,n,nn]), Rrate[t]*pD[t-1,s,nn]*(1+adjCostPar[s,n]*(qD[t-1,s,nn]/qD[t-1,s,n]-(rDepr[t-1,s,n]+g_LR)))/(1+infl_LR)+pD[t,s,nn]*(adjCostPar[s,n]*0.5*(sqr(rDepr[t,s,n]+g_LR)-sqr(qD[t,s,nn]/qD[t,s,n]))-(1-rDepr[t,s,n])*(1+adjCostPar[s,n]*(qD[t,s,nn]/qD[t,s,n]-(rDepr[t,s,n]+g_LR)))))));
EQUATION E_P_adjCost_pkT[t,s,n];
E_P_adjCost_pkT[t,s,n]$(p_dur[s,n] and t2e[t]).. 		pD[t,s,n]	 =E=  sum(nn$(P_dur2inv[s,n,nn]), Rrate[t]*pD[t-1,s,nn] * (1+adjCostPar[s,n]*(qD[t-1,s,nn]/qD[t-1,s,n]-(rDepr[t-1,s,n]+g_LR)))/(1+infl_LR) + (rDepr[t,s,n]-1)*pD[t,s,nn]);
EQUATION E_P_adjCost_K_tvc[t,s,n];
E_P_adjCost_K_tvc[t,s,n]$(p_dur[s,n] and te[t]).. 	qD[t,s,n]	 =E=  (1+K_tvc[s,n])*qD[t-1,s,n];
EQUATION E_P_adjCost_adjCost[t,s];
E_P_adjCost_adjCost[t,s]$(p_sm[s] and txe[t]).. 		adjCost[t,s] 	 =E=  sum([n,nn]$(P_dur2inv[s,n,nn]), pD[t,s,nn] * adjCostPar[s,n]*0.5*qD[t,s,n]*sqr(qD[t,s,nn]/qD[t,s,n]-(rDepr[t,s,n]+g_LR)));

# ----------------------------------------------------------------------------------------------------
#  Define B_P_adjCost model
# ----------------------------------------------------------------------------------------------------
Model B_P_adjCost /
E_P_adjCost_lom, E_P_adjCost_pk, E_P_adjCost_pkT, E_P_adjCost_K_tvc, E_P_adjCost_adjCost
/;



# ---------------------------------------------B_P_pWedge---------------------------------------------
#  Initialize B_P_pWedge equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_P_pWedge_pwInp[t,s,n];
E_P_pWedge_pwInp[t,s,n]$(p_input[s,n] and txe[t]).. 			pD[t,s,n]		 =E=  p[t,n]+tauD[t,s,n];
EQUATION E_P_pWedge_pwOut[t,s,n];
E_P_pWedge_pwOut[t,s,n]$(p_output[s,n] and txe[t]).. 		p[t,n] 			 =E=  (1+markup[s])*(pS[t,s,n]+tauS[t,s,n]+(adjCost[t,s]+tauLump[t,s])/qS[t,s,n]);
EQUATION E_P_pWedge_taxRev[t,s];
E_P_pWedge_taxRev[t,s]$(s_p[s] and txe[t]).. 				TotalTax[t,s]	 =E=  tauLump[t,s]+sum(n$(P_input[s,n]), tauD[t,s,n] * qD[t,s,n])+sum(n$(P_output[s,n]), tauS[t,s,n]*qS[t,s,n]);
EQUATION E_P_pWedge_tauS[t,s,n];
E_P_pWedge_tauS[t,s,n]$(p_output[s,n] and txe[t]).. 			tauS[t,s,n]		 =E=  tauCO2[t,s,n] * qCO2[t,s,n]/qS[t,s,n]+tauNonEnv[t,s,n];

# ----------------------------------------------------------------------------------------------------
#  Define B_P_pWedge model
# ----------------------------------------------------------------------------------------------------
Model B_P_pWedge /
E_P_pWedge_pwInp, E_P_pWedge_pwOut, E_P_pWedge_taxRev, E_P_pWedge_tauS
/;



# --------------------------------------------B_P_taxCalib--------------------------------------------
#  Initialize B_P_taxCalib equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_P_taxCalib_taxCal[t,s,n];
E_P_taxCalib_taxCal[t,s,n]$(p_output[s,n] and txe[t]).. 	tauNonEnv[t,s,n]	 =E=  tauNonEnv0[t,s,n] * (1+taxRevPar[s]);

# ----------------------------------------------------------------------------------------------------
#  Define B_P_taxCalib model
# ----------------------------------------------------------------------------------------------------
Model B_P_taxCalib /
E_P_taxCalib_taxCal
/;



# ----------------------------------------------------------------------------------------------------
#  Define P_B model
# ----------------------------------------------------------------------------------------------------
Model P_B /
E_W_zpOut, E_W_zpNOut, E_W_qOut, E_W_qNOut, E_O_zpOut, E_O_zpNOut, E_O_qOut, E_O_qNOut, E_P_adjCost_lom, E_P_adjCost_pk, E_P_adjCost_pkT, E_P_adjCost_K_tvc, E_P_adjCost_adjCost, E_P_pWedge_pwInp, E_P_pWedge_pwOut, E_P_pWedge_taxRev, E_P_pWedge_tauS
/;


# ----------------------------------------------------------------------------------------------------
#  Define P_C model
# ----------------------------------------------------------------------------------------------------
Model P_C /
E_W_zpOut, E_W_zpNOut, E_W_qOut, E_W_qNOut, E_O_zpOut, E_O_zpNOut, E_O_qOut, E_O_qNOut, E_P_adjCost_lom, E_P_adjCost_pk, E_P_adjCost_pkT, E_P_adjCost_K_tvc, E_P_adjCost_adjCost, E_P_pWedge_pwInp, E_P_pWedge_pwOut, E_P_pWedge_taxRev, E_P_pWedge_tauS, E_P_taxCalib_taxCal
/;

variables
	j_W_zpOut[t,s,n]
	j_W_zpNOut[t,s,n]
	j_W_qOut[t,s,n]
	j_W_qNOut[t,s,n]
	j_O_zpOut[t,s,n]
	j_O_zpNOut[t,s,n]
	j_O_qOut[t,s,n]
	j_O_qNOut[t,s,n]
	j_P_adjCost_lom[t,s,n]
	j_P_adjCost_pk[t,s,n]
	j_P_adjCost_pkT[t,s,n]
	j_P_adjCost_K_tvc[t,s,n]
	j_P_adjCost_adjCost[t,s]
	j_P_pWedge_pwInp[t,s,n]
	j_P_pWedge_pwOut[t,s,n]
	j_P_pWedge_taxRev[t,s]
	j_P_pWedge_tauS[t,s,n]
	j_P_taxCalib_taxCal[t,s,n]
;


# ------------------------------------------------j_P_C-----------------------------------------------
#  Initialize j_P_C equation block
# ----------------------------------------------------------------------------------------------------
EQUATION j_E_W_zpOut[t,s,n];
j_E_W_zpOut[t,s,n]$(w_knot_o[s,n] and txe[t]).. 	pS[t,s,n]*qS[t,s,n]  =E=  sum(nn$(W_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn])+j_W_zpOut[t,s,n];
EQUATION j_E_W_zpNOut[t,s,n];
j_E_W_zpNOut[t,s,n]$(w_knot_no[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(W_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn])+j_W_zpNOut[t,s,n];
EQUATION j_E_W_qOut[t,s,n];
j_E_W_qOut[t,s,n]$(w_branch2o[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(W_map[s,nn,n]), mu[s,nn,n] * (pS[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qS[t,s,nn])+j_W_qOut[t,s,n];
EQUATION j_E_W_qNOut[t,s,n];
j_E_W_qNOut[t,s,n]$(w_branch2no[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(W_map[s,nn,n]), mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qD[t,s,nn])+j_W_qNOut[t,s,n];
EQUATION j_E_O_zpOut[t,s,n];
j_E_O_zpOut[t,s,n]$(o_knot_o[s,n] and txe[t]).. 	pS[t,s,n]*qS[t,s,n]  =E=  sum(nn$(O_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn])+j_O_zpOut[t,s,n];
EQUATION j_E_O_zpNOut[t,s,n];
j_E_O_zpNOut[t,s,n]$(o_knot_no[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(O_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn])+j_O_zpNOut[t,s,n];
EQUATION j_E_O_qOut[t,s,n];
j_E_O_qOut[t,s,n]$(o_branch2o[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(O_map[s,nn,n]), mu[s,nn,n] * (pS[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qS[t,s,nn])+j_O_qOut[t,s,n];
EQUATION j_E_O_qNOut[t,s,n];
j_E_O_qNOut[t,s,n]$(o_branch2no[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(O_map[s,nn,n]), mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qD[t,s,nn])+j_O_qNOut[t,s,n];
EQUATION j_E_P_adjCost_lom[t,s,n];
j_E_P_adjCost_lom[t,s,n]$(p_dur[s,n] and txe[t]).. 		qD[t+1,s,n]	 =E=  (qD[t,s,n]*(1-rDepr[t,s,n])+sum(nn$(P_dur2inv[s,n,nn]), qD[t,s,nn]))/(1+g_LR)+j_P_adjCost_lom[t,s,n];
EQUATION j_E_P_adjCost_pk[t,s,n];
j_E_P_adjCost_pk[t,s,n]$(p_dur[s,n] and tx02e[t]).. 	pD[t,s,n]	 =E=  sqrt(sqr(sum(nn$(P_dur2inv[s,n,nn]), Rrate[t]*pD[t-1,s,nn]*(1+adjCostPar[s,n]*(qD[t-1,s,nn]/qD[t-1,s,n]-(rDepr[t-1,s,n]+g_LR)))/(1+infl_LR)+pD[t,s,nn]*(adjCostPar[s,n]*0.5*(sqr(rDepr[t,s,n]+g_LR)-sqr(qD[t,s,nn]/qD[t,s,n]))-(1-rDepr[t,s,n])*(1+adjCostPar[s,n]*(qD[t,s,nn]/qD[t,s,n]-(rDepr[t,s,n]+g_LR)))))))+j_P_adjCost_pk[t,s,n];
EQUATION j_E_P_adjCost_pkT[t,s,n];
j_E_P_adjCost_pkT[t,s,n]$(p_dur[s,n] and t2e[t]).. 		pD[t,s,n]	 =E=  sum(nn$(P_dur2inv[s,n,nn]), Rrate[t]*pD[t-1,s,nn] * (1+adjCostPar[s,n]*(qD[t-1,s,nn]/qD[t-1,s,n]-(rDepr[t-1,s,n]+g_LR)))/(1+infl_LR) + (rDepr[t,s,n]-1)*pD[t,s,nn])+j_P_adjCost_pkT[t,s,n];
EQUATION j_E_P_adjCost_K_tvc[t,s,n];
j_E_P_adjCost_K_tvc[t,s,n]$(p_dur[s,n] and te[t]).. 	qD[t,s,n]	 =E=  (1+K_tvc[s,n])*qD[t-1,s,n]+j_P_adjCost_K_tvc[t,s,n];
EQUATION j_E_P_adjCost_adjCost[t,s];
j_E_P_adjCost_adjCost[t,s]$(p_sm[s] and txe[t]).. 		adjCost[t,s] 	 =E=  sum([n,nn]$(P_dur2inv[s,n,nn]), pD[t,s,nn] * adjCostPar[s,n]*0.5*qD[t,s,n]*sqr(qD[t,s,nn]/qD[t,s,n]-(rDepr[t,s,n]+g_LR)))+j_P_adjCost_adjCost[t,s];
EQUATION j_E_P_pWedge_pwInp[t,s,n];
j_E_P_pWedge_pwInp[t,s,n]$(p_input[s,n] and txe[t]).. 			pD[t,s,n]		 =E=  p[t,n]+tauD[t,s,n]+j_P_pWedge_pwInp[t,s,n];
EQUATION j_E_P_pWedge_pwOut[t,s,n];
j_E_P_pWedge_pwOut[t,s,n]$(p_output[s,n] and txe[t]).. 		p[t,n] 			 =E=  (1+markup[s])*(pS[t,s,n]+tauS[t,s,n]+(adjCost[t,s]+tauLump[t,s])/qS[t,s,n])+j_P_pWedge_pwOut[t,s,n];
EQUATION j_E_P_pWedge_taxRev[t,s];
j_E_P_pWedge_taxRev[t,s]$(s_p[s] and txe[t]).. 				TotalTax[t,s]	 =E=  tauLump[t,s]+sum(n$(P_input[s,n]), tauD[t,s,n] * qD[t,s,n])+sum(n$(P_output[s,n]), tauS[t,s,n]*qS[t,s,n])+j_P_pWedge_taxRev[t,s];
EQUATION j_E_P_pWedge_tauS[t,s,n];
j_E_P_pWedge_tauS[t,s,n]$(p_output[s,n] and txe[t]).. 			tauS[t,s,n]		 =E=  tauCO2[t,s,n] * qCO2[t,s,n]/qS[t,s,n]+tauNonEnv[t,s,n]+j_P_pWedge_tauS[t,s,n];
EQUATION j_E_P_taxCalib_taxCal[t,s,n];
j_E_P_taxCalib_taxCal[t,s,n]$(p_output[s,n] and txe[t]).. 	tauNonEnv[t,s,n]	 =E=  tauNonEnv0[t,s,n] * (1+taxRevPar[s])+j_P_taxCalib_taxCal[t,s,n];

# ----------------------------------------------------------------------------------------------------
#  Define j_P_C model
# ----------------------------------------------------------------------------------------------------
Model j_P_C /
j_E_W_zpOut, j_E_W_zpNOut, j_E_W_qOut, j_E_W_qNOut, j_E_O_zpOut, j_E_O_zpNOut, j_E_O_qOut, j_E_O_qNOut, j_E_P_adjCost_lom, j_E_P_adjCost_pk, j_E_P_adjCost_pkT, j_E_P_adjCost_K_tvc, j_E_P_adjCost_adjCost, j_E_P_pWedge_pwInp, j_E_P_pWedge_pwOut, j_E_P_pWedge_taxRev, j_E_P_pWedge_tauS, j_E_P_taxCalib_taxCal
/;


qS.fx[t,s,n]$(P_output[s,n]) = qS.l[t,s,n]$(P_output[s,n]);
sigma.fx[s,n]$(P_kninp[s,n]) = sigma.l[s,n]$(P_kninp[s,n]);
mu.fx[s,n,nn]$((P_map[s,n,nn] and ( not (P_endoMu[s,n,nn])))) = mu.l[s,n,nn]$((P_map[s,n,nn] and ( not (P_endoMu[s,n,nn]))));
tauNonEnv0.fx[t,s,n]$(P_output[s,n]) = tauNonEnv0.l[t,s,n]$(P_output[s,n]);
tauD.fx[t,s,n]$(P_input[s,n]) = tauD.l[t,s,n]$(P_input[s,n]);
tauLump.fx[t,s]$(P_sm[s]) = tauLump.l[t,s]$(P_sm[s]);
p.fx[t,n]$((P_input_n[n] and ( not (P_output_n[n])))) = p.l[t,n]$((P_input_n[n] and ( not (P_output_n[n]))));
qCO2.fx[t,s,n]$(P_output[s,n]) = qCO2.l[t,s,n]$(P_output[s,n]);
tauCO2.fx[t,s,n]$(P_output[s,n]) = tauCO2.l[t,s,n]$(P_output[s,n]);
Rrate.fx[t] = Rrate.l[t];
rDepr.fx[t,s,n]$(P_dur[s,n]) = rDepr.l[t,s,n]$(P_dur[s,n]);
adjCostPar.fx[s,n]$(P_dur[s,n]) = adjCostPar.l[s,n]$(P_dur[s,n]);
K_tvc.fx[s,n]$(P_dur[s,n]) = K_tvc.l[s,n]$(P_dur[s,n]);
qD.fx[t,s,n]$((P_dur[s,n] and t0[t])) = qD.l[t,s,n]$((P_dur[s,n] and t0[t]));pD.fx[t,s,n]$((P_int[s,n] or P_input[s,n] or (P_dur[s,n] and txE[t]))) = pD.l[t,s,n]$((P_int[s,n] or P_input[s,n] or (P_dur[s,n] and txE[t])));
pS.fx[t,s,n]$(P_output[s,n]) = pS.l[t,s,n]$(P_output[s,n]);
p.fx[t,n]$((P_output_n[n] and tx0[t])) = p.l[t,n]$((P_output_n[n] and tx0[t]));
qD.fx[t,s,n]$((P_int[s,n] or (P_input[s,n] and tx0[t]) or (P_dur[s,n] and tx0[t]))) = qD.l[t,s,n]$((P_int[s,n] or (P_input[s,n] and tx0[t]) or (P_dur[s,n] and tx0[t])));
adjCost.fx[t,s]$((P_sm[s] and txE[t])) = adjCost.l[t,s]$((P_sm[s] and txE[t]));
tauS.fx[t,s,n]$(P_output[s,n]) = tauS.l[t,s,n]$(P_output[s,n]);
TotalTax.fx[t,s]$((P_sm[s] and tx0E[t])) = TotalTax.l[t,s]$((P_sm[s] and tx0E[t]));qD.fx[t,s,n]$((P_input[s,n] and t0[t])) = qD.l[t,s,n]$((P_input[s,n] and t0[t]));
p.fx[t,n]$((P_output_n[n] and t0[t])) = p.l[t,n]$((P_output_n[n] and t0[t]));
TotalTax.fx[t,s]$((P_sm[s] and t0[t])) = TotalTax.l[t,s]$((P_sm[s] and t0[t]));mu.fx[s,n,nn]$(P_endoMu[s,n,nn]) = mu.l[s,n,nn]$(P_endoMu[s,n,nn]);
tauNonEnv.fx[t,s,n]$(P_output[s,n]) = tauNonEnv.l[t,s,n]$(P_output[s,n]);
taxRevPar.fx[s]$(P_sm[s]) = taxRevPar.l[s]$(P_sm[s]);
markup.fx[s]$(P_sm[s]) = markup.l[s]$(P_sm[s]);pD.fx[t,s,n]$((P_int[s,n] or P_input[s,n] or (P_dur[s,n] and txE[t]))) = pD.l[t,s,n]$((P_int[s,n] or P_input[s,n] or (P_dur[s,n] and txE[t])));
pS.fx[t,s,n]$(P_output[s,n]) = pS.l[t,s,n]$(P_output[s,n]);
p.fx[t,n]$(((P_output_n[n] and tx0[t]) or (P_output_n[n] and t0[t]))) = p.l[t,n]$(((P_output_n[n] and tx0[t]) or (P_output_n[n] and t0[t])));
qD.fx[t,s,n]$(((P_int[s,n] or (P_input[s,n] and tx0[t]) or (P_dur[s,n] and tx0[t])) or (P_input[s,n] and t0[t]))) = qD.l[t,s,n]$(((P_int[s,n] or (P_input[s,n] and tx0[t]) or (P_dur[s,n] and tx0[t])) or (P_input[s,n] and t0[t])));
adjCost.fx[t,s]$((P_sm[s] and txE[t])) = adjCost.l[t,s]$((P_sm[s] and txE[t]));
tauS.fx[t,s,n]$(P_output[s,n]) = tauS.l[t,s,n]$(P_output[s,n]);
TotalTax.fx[t,s]$(((P_sm[s] and tx0E[t]) or (P_sm[s] and t0[t]))) = TotalTax.l[t,s]$(((P_sm[s] and tx0E[t]) or (P_sm[s] and t0[t])));pD.fx[t,s,n]$((P_int[s,n] or P_input[s,n] or (P_dur[s,n] and txE[t]))) = pD.l[t,s,n]$((P_int[s,n] or P_input[s,n] or (P_dur[s,n] and txE[t])));
pS.fx[t,s,n]$(P_output[s,n]) = pS.l[t,s,n]$(P_output[s,n]);
p.fx[t,n]$((P_output_n[n] and tx0[t])) = p.l[t,n]$((P_output_n[n] and tx0[t]));
qD.fx[t,s,n]$((P_int[s,n] or (P_input[s,n] and tx0[t]) or (P_dur[s,n] and tx0[t]))) = qD.l[t,s,n]$((P_int[s,n] or (P_input[s,n] and tx0[t]) or (P_dur[s,n] and tx0[t])));
adjCost.fx[t,s]$((P_sm[s] and txE[t])) = adjCost.l[t,s]$((P_sm[s] and txE[t]));
tauS.fx[t,s,n]$(P_output[s,n]) = tauS.l[t,s,n]$(P_output[s,n]);
TotalTax.fx[t,s]$((P_sm[s] and tx0E[t])) = TotalTax.l[t,s]$((P_sm[s] and tx0E[t]));
mu.fx[s,n,nn]$(P_endoMu[s,n,nn]) = mu.l[s,n,nn]$(P_endoMu[s,n,nn]);
tauNonEnv.fx[t,s,n]$(P_output[s,n]) = tauNonEnv.l[t,s,n]$(P_output[s,n]);
taxRevPar.fx[s]$(P_sm[s]) = taxRevPar.l[s]$(P_sm[s]);
markup.fx[s]$(P_sm[s]) = markup.l[s]$(P_sm[s]);qS.fx[t,s,n]$(P_output[s,n]) = qS.l[t,s,n]$(P_output[s,n]);
sigma.fx[s,n]$(P_kninp[s,n]) = sigma.l[s,n]$(P_kninp[s,n]);
mu.fx[s,n,nn]$(((P_map[s,n,nn] and ( not (P_endoMu[s,n,nn]))) or P_endoMu[s,n,nn])) = mu.l[s,n,nn]$(((P_map[s,n,nn] and ( not (P_endoMu[s,n,nn]))) or P_endoMu[s,n,nn]));
tauNonEnv0.fx[t,s,n]$(P_output[s,n]) = tauNonEnv0.l[t,s,n]$(P_output[s,n]);
tauD.fx[t,s,n]$(P_input[s,n]) = tauD.l[t,s,n]$(P_input[s,n]);
tauLump.fx[t,s]$(P_sm[s]) = tauLump.l[t,s]$(P_sm[s]);
p.fx[t,n]$((P_input_n[n] and ( not (P_output_n[n])))) = p.l[t,n]$((P_input_n[n] and ( not (P_output_n[n]))));
qCO2.fx[t,s,n]$(P_output[s,n]) = qCO2.l[t,s,n]$(P_output[s,n]);
tauCO2.fx[t,s,n]$(P_output[s,n]) = tauCO2.l[t,s,n]$(P_output[s,n]);
Rrate.fx[t] = Rrate.l[t];
rDepr.fx[t,s,n]$(P_dur[s,n]) = rDepr.l[t,s,n]$(P_dur[s,n]);
adjCostPar.fx[s,n]$(P_dur[s,n]) = adjCostPar.l[s,n]$(P_dur[s,n]);
K_tvc.fx[s,n]$(P_dur[s,n]) = K_tvc.l[s,n]$(P_dur[s,n]);
qD.fx[t,s,n]$((P_dur[s,n] and t0[t])) = qD.l[t,s,n]$((P_dur[s,n] and t0[t]));
tauNonEnv.fx[t,s,n]$(P_output[s,n]) = tauNonEnv.l[t,s,n]$(P_output[s,n]);
taxRevPar.fx[s]$(P_sm[s]) = taxRevPar.l[s]$(P_sm[s]);
markup.fx[s]$(P_sm[s]) = markup.l[s]$(P_sm[s]);qS.fx[t,s,n]$(P_output[s,n]) = qS.l[t,s,n]$(P_output[s,n]);
sigma.fx[s,n]$(P_kninp[s,n]) = sigma.l[s,n]$(P_kninp[s,n]);
mu.fx[s,n,nn]$((P_map[s,n,nn] and ( not (P_endoMu[s,n,nn])))) = mu.l[s,n,nn]$((P_map[s,n,nn] and ( not (P_endoMu[s,n,nn]))));
tauNonEnv0.fx[t,s,n]$(P_output[s,n]) = tauNonEnv0.l[t,s,n]$(P_output[s,n]);
tauD.fx[t,s,n]$(P_input[s,n]) = tauD.l[t,s,n]$(P_input[s,n]);
tauLump.fx[t,s]$(P_sm[s]) = tauLump.l[t,s]$(P_sm[s]);
p.fx[t,n]$(((P_input_n[n] and ( not (P_output_n[n]))) or (P_output_n[n] and t0[t]))) = p.l[t,n]$(((P_input_n[n] and ( not (P_output_n[n]))) or (P_output_n[n] and t0[t])));
qCO2.fx[t,s,n]$(P_output[s,n]) = qCO2.l[t,s,n]$(P_output[s,n]);
tauCO2.fx[t,s,n]$(P_output[s,n]) = tauCO2.l[t,s,n]$(P_output[s,n]);
Rrate.fx[t] = Rrate.l[t];
rDepr.fx[t,s,n]$(P_dur[s,n]) = rDepr.l[t,s,n]$(P_dur[s,n]);
adjCostPar.fx[s,n]$(P_dur[s,n]) = adjCostPar.l[s,n]$(P_dur[s,n]);
K_tvc.fx[s,n]$(P_dur[s,n]) = K_tvc.l[s,n]$(P_dur[s,n]);
qD.fx[t,s,n]$(((P_dur[s,n] and t0[t]) or (P_input[s,n] and t0[t]))) = qD.l[t,s,n]$(((P_dur[s,n] and t0[t]) or (P_input[s,n] and t0[t])));
TotalTax.fx[t,s]$((P_sm[s] and t0[t])) = TotalTax.l[t,s]$((P_sm[s] and t0[t]));
solve j_P_C using CNS;j_W_zpOut.fx[t,s,n]$(w_knot_o[s,n] and txe[t]) = j_W_zpOut.l[t,s,n]$(w_knot_o[s,n] and txe[t]);
j_W_zpNOut.fx[t,s,n]$(w_knot_no[s,n] and txe[t]) = j_W_zpNOut.l[t,s,n]$(w_knot_no[s,n] and txe[t]);
j_W_qOut.fx[t,s,n]$(w_branch2o[s,n] and txe[t]) = j_W_qOut.l[t,s,n]$(w_branch2o[s,n] and txe[t]);
j_W_qNOut.fx[t,s,n]$(w_branch2no[s,n] and txe[t]) = j_W_qNOut.l[t,s,n]$(w_branch2no[s,n] and txe[t]);
j_O_zpOut.fx[t,s,n]$(o_knot_o[s,n] and txe[t]) = j_O_zpOut.l[t,s,n]$(o_knot_o[s,n] and txe[t]);
j_O_zpNOut.fx[t,s,n]$(o_knot_no[s,n] and txe[t]) = j_O_zpNOut.l[t,s,n]$(o_knot_no[s,n] and txe[t]);
j_O_qOut.fx[t,s,n]$(o_branch2o[s,n] and txe[t]) = j_O_qOut.l[t,s,n]$(o_branch2o[s,n] and txe[t]);
j_O_qNOut.fx[t,s,n]$(o_branch2no[s,n] and txe[t]) = j_O_qNOut.l[t,s,n]$(o_branch2no[s,n] and txe[t]);
j_P_adjCost_lom.fx[t,s,n]$(p_dur[s,n] and txe[t]) = j_P_adjCost_lom.l[t,s,n]$(p_dur[s,n] and txe[t]);
j_P_adjCost_pk.fx[t,s,n]$(p_dur[s,n] and tx02e[t]) = j_P_adjCost_pk.l[t,s,n]$(p_dur[s,n] and tx02e[t]);
j_P_adjCost_pkT.fx[t,s,n]$(p_dur[s,n] and t2e[t]) = j_P_adjCost_pkT.l[t,s,n]$(p_dur[s,n] and t2e[t]);
j_P_adjCost_K_tvc.fx[t,s,n]$(p_dur[s,n] and te[t]) = j_P_adjCost_K_tvc.l[t,s,n]$(p_dur[s,n] and te[t]);
j_P_adjCost_adjCost.fx[t,s]$(p_sm[s] and txe[t]) = j_P_adjCost_adjCost.l[t,s]$(p_sm[s] and txe[t]);
j_P_pWedge_pwInp.fx[t,s,n]$(p_input[s,n] and txe[t]) = j_P_pWedge_pwInp.l[t,s,n]$(p_input[s,n] and txe[t]);
j_P_pWedge_pwOut.fx[t,s,n]$(p_output[s,n] and txe[t]) = j_P_pWedge_pwOut.l[t,s,n]$(p_output[s,n] and txe[t]);
j_P_pWedge_taxRev.fx[t,s]$(s_p[s] and txe[t]) = j_P_pWedge_taxRev.l[t,s]$(s_p[s] and txe[t]);
j_P_pWedge_tauS.fx[t,s,n]$(p_output[s,n] and txe[t]) = j_P_pWedge_tauS.l[t,s,n]$(p_output[s,n] and txe[t]);
j_P_taxCalib_taxCal.fx[t,s,n]$(p_output[s,n] and txe[t]) = j_P_taxCalib_taxCal.l[t,s,n]$(p_output[s,n] and txe[t]);pD.lo[t,s,n]$((P_int[s,n] or P_input[s,n] or (P_dur[s,n] and txE[t]))) = -inf;
pD.up[t,s,n]$((P_int[s,n] or P_input[s,n] or (P_dur[s,n] and txE[t]))) = inf;
pS.lo[t,s,n]$(P_output[s,n]) = -inf;
pS.up[t,s,n]$(P_output[s,n]) = inf;
p.lo[t,n]$((P_output_n[n] and tx0[t])) = -inf;
p.up[t,n]$((P_output_n[n] and tx0[t])) = inf;
qD.lo[t,s,n]$((P_int[s,n] or (P_input[s,n] and tx0[t]) or (P_dur[s,n] and tx0[t]))) = -inf;
qD.up[t,s,n]$((P_int[s,n] or (P_input[s,n] and tx0[t]) or (P_dur[s,n] and tx0[t]))) = inf;
adjCost.lo[t,s]$((P_sm[s] and txE[t])) = -inf;
adjCost.up[t,s]$((P_sm[s] and txE[t])) = inf;
tauS.lo[t,s,n]$(P_output[s,n]) = -inf;
tauS.up[t,s,n]$(P_output[s,n]) = inf;
TotalTax.lo[t,s]$((P_sm[s] and tx0E[t])) = -inf;
TotalTax.up[t,s]$((P_sm[s] and tx0E[t])) = inf;
mu.lo[s,n,nn]$(P_endoMu[s,n,nn]) = -inf;
mu.up[s,n,nn]$(P_endoMu[s,n,nn]) = inf;
tauNonEnv.lo[t,s,n]$(P_output[s,n]) = -inf;
tauNonEnv.up[t,s,n]$(P_output[s,n]) = inf;
taxRevPar.lo[s]$(P_sm[s]) = -inf;
taxRevPar.up[s]$(P_sm[s]) = inf;
markup.lo[s]$(P_sm[s]) = -inf;
markup.up[s]$(P_sm[s]) = inf;solve j_P_C using CNS;parameters
	par_j_W_zpOut[t,s,n]
	par_j_W_zpNOut[t,s,n]
	par_j_W_qOut[t,s,n]
	par_j_W_qNOut[t,s,n]
	par_j_O_zpOut[t,s,n]
	par_j_O_zpNOut[t,s,n]
	par_j_O_qOut[t,s,n]
	par_j_O_qNOut[t,s,n]
	par_j_P_adjCost_lom[t,s,n]
	par_j_P_adjCost_pk[t,s,n]
	par_j_P_adjCost_pkT[t,s,n]
	par_j_P_adjCost_K_tvc[t,s,n]
	par_j_P_adjCost_adjCost[t,s]
	par_j_P_pWedge_pwInp[t,s,n]
	par_j_P_pWedge_pwOut[t,s,n]
	par_j_P_pWedge_taxRev[t,s]
	par_j_P_pWedge_tauS[t,s,n]
	par_j_P_taxCalib_taxCal[t,s,n]
;

# Initialize parameter group:
	par_j_W_zpOut[t,s,n]$(w_knot_o[s,n] and txe[t])=j_W_zpOut.l[t,s,n];
	par_j_W_zpNOut[t,s,n]$(w_knot_no[s,n] and txe[t])=j_W_zpNOut.l[t,s,n];
	par_j_W_qOut[t,s,n]$(w_branch2o[s,n] and txe[t])=j_W_qOut.l[t,s,n];
	par_j_W_qNOut[t,s,n]$(w_branch2no[s,n] and txe[t])=j_W_qNOut.l[t,s,n];
	par_j_O_zpOut[t,s,n]$(o_knot_o[s,n] and txe[t])=j_O_zpOut.l[t,s,n];
	par_j_O_zpNOut[t,s,n]$(o_knot_no[s,n] and txe[t])=j_O_zpNOut.l[t,s,n];
	par_j_O_qOut[t,s,n]$(o_branch2o[s,n] and txe[t])=j_O_qOut.l[t,s,n];
	par_j_O_qNOut[t,s,n]$(o_branch2no[s,n] and txe[t])=j_O_qNOut.l[t,s,n];
	par_j_P_adjCost_lom[t,s,n]$(p_dur[s,n] and txe[t])=j_P_adjCost_lom.l[t,s,n];
	par_j_P_adjCost_pk[t,s,n]$(p_dur[s,n] and tx02e[t])=j_P_adjCost_pk.l[t,s,n];
	par_j_P_adjCost_pkT[t,s,n]$(p_dur[s,n] and t2e[t])=j_P_adjCost_pkT.l[t,s,n];
	par_j_P_adjCost_K_tvc[t,s,n]$(p_dur[s,n] and te[t])=j_P_adjCost_K_tvc.l[t,s,n];
	par_j_P_adjCost_adjCost[t,s]$(p_sm[s] and txe[t])=j_P_adjCost_adjCost.l[t,s];
	par_j_P_pWedge_pwInp[t,s,n]$(p_input[s,n] and txe[t])=j_P_pWedge_pwInp.l[t,s,n];
	par_j_P_pWedge_pwOut[t,s,n]$(p_output[s,n] and txe[t])=j_P_pWedge_pwOut.l[t,s,n];
	par_j_P_pWedge_taxRev[t,s]$(s_p[s] and txe[t])=j_P_pWedge_taxRev.l[t,s];
	par_j_P_pWedge_tauS[t,s,n]$(p_output[s,n] and txe[t])=j_P_pWedge_tauS.l[t,s,n];
	par_j_P_taxCalib_taxCal[t,s,n]$(p_output[s,n] and txe[t])=j_P_taxCalib_taxCal.l[t,s,n];


Scalar i;
for (i = 1 to 10,
	j_W_zpOut.fx[t,s,n]$(w_knot_o[s,n] and txe[t]) = (1-(i/10)**(0.1))*par_j_W_zpOut[t,s,n];
	j_W_zpNOut.fx[t,s,n]$(w_knot_no[s,n] and txe[t]) = (1-(i/10)**(0.1))*par_j_W_zpNOut[t,s,n];
	j_W_qOut.fx[t,s,n]$(w_branch2o[s,n] and txe[t]) = (1-(i/10)**(0.1))*par_j_W_qOut[t,s,n];
	j_W_qNOut.fx[t,s,n]$(w_branch2no[s,n] and txe[t]) = (1-(i/10)**(0.1))*par_j_W_qNOut[t,s,n];
	j_O_zpOut.fx[t,s,n]$(o_knot_o[s,n] and txe[t]) = (1-(i/10)**(0.1))*par_j_O_zpOut[t,s,n];
	j_O_zpNOut.fx[t,s,n]$(o_knot_no[s,n] and txe[t]) = (1-(i/10)**(0.1))*par_j_O_zpNOut[t,s,n];
	j_O_qOut.fx[t,s,n]$(o_branch2o[s,n] and txe[t]) = (1-(i/10)**(0.1))*par_j_O_qOut[t,s,n];
	j_O_qNOut.fx[t,s,n]$(o_branch2no[s,n] and txe[t]) = (1-(i/10)**(0.1))*par_j_O_qNOut[t,s,n];
	j_P_adjCost_lom.fx[t,s,n]$(p_dur[s,n] and txe[t]) = (1-(i/10)**(0.1))*par_j_P_adjCost_lom[t,s,n];
	j_P_adjCost_pk.fx[t,s,n]$(p_dur[s,n] and tx02e[t]) = (1-(i/10)**(0.1))*par_j_P_adjCost_pk[t,s,n];
	j_P_adjCost_pkT.fx[t,s,n]$(p_dur[s,n] and t2e[t]) = (1-(i/10)**(0.1))*par_j_P_adjCost_pkT[t,s,n];
	j_P_adjCost_K_tvc.fx[t,s,n]$(p_dur[s,n] and te[t]) = (1-(i/10)**(0.1))*par_j_P_adjCost_K_tvc[t,s,n];
	j_P_adjCost_adjCost.fx[t,s]$(p_sm[s] and txe[t]) = (1-(i/10)**(0.1))*par_j_P_adjCost_adjCost[t,s];
	j_P_pWedge_pwInp.fx[t,s,n]$(p_input[s,n] and txe[t]) = (1-(i/10)**(0.1))*par_j_P_pWedge_pwInp[t,s,n];
	j_P_pWedge_pwOut.fx[t,s,n]$(p_output[s,n] and txe[t]) = (1-(i/10)**(0.1))*par_j_P_pWedge_pwOut[t,s,n];
	j_P_pWedge_taxRev.fx[t,s]$(s_p[s] and txe[t]) = (1-(i/10)**(0.1))*par_j_P_pWedge_taxRev[t,s];
	j_P_pWedge_tauS.fx[t,s,n]$(p_output[s,n] and txe[t]) = (1-(i/10)**(0.1))*par_j_P_pWedge_tauS[t,s,n];
	j_P_taxCalib_taxCal.fx[t,s,n]$(p_output[s,n] and txe[t]) = (1-(i/10)**(0.1))*par_j_P_taxCalib_taxCal[t,s,n];
solve j_P_C using CNS;);

