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
	I_map[s,n,nn]
	I_map_spinp[s,n,nn]
	I_map_spout[s,n,nn]
	I_knout[s,n]
	I_kninp[s,n]
	I_spout[s,n]
	I_spinp[s,n]
	I_input[s,n]
	I_output[s,n]
	I_int[s,n]
	I_knot[s,n]
	I_branch[s,n]
	I_knot_o[s,n]
	I_knot_no[s,n]
	I_branch2o[s,n]
	I_branch2no[s,n]
	I_sm[s]
	I_output_n[n]
	I_input_n[n]
	I_endoMu[s,n,nn]
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
	nestInvestment[s,n,nn]
	dtauCO2[s,n]
	dqCO2[s,n]
	nestHH[s,n,nn]
	L2C[s,n,nn]
	nestG[s,n,nn]
	d_TotalTax[s]
	I_dur[s,n]
	I_dur2inv[s,n,nn]
	I_inv[s,n]
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
	techPot[tech,t]
	techCost[tech,t]
	DACCost[t]
	uCO2[t,s,n]
	tauCO2agg[t]
	tauDist[t,s,n]
	qCO2agg[t]
	Rrate[t]
	mu[s,n,nn]
	pS[t,s,n]
	adjCostPar[s,n]
	K_tvc[s,n]
	adjCost[t,s]
	markup[s]
	taxRevPar[s]
;
$GDXIN I
$onMulti
$load alias_set
$load alias_map2
$load n
$load s
$load t
$load taxTypes
$load tech
$load alias_
$load I_map
$load I_map_spinp
$load I_map_spout
$load I_knout
$load I_kninp
$load I_spout
$load I_spinp
$load I_input
$load I_output
$load I_int
$load I_knot
$load I_branch
$load I_knot_o
$load I_knot_no
$load I_branch2o
$load I_branch2no
$load I_sm
$load I_output_n
$load I_input_n
$load I_endoMu
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
$load nestInvestment
$load dtauCO2
$load dqCO2
$load nestHH
$load L2C
$load nestG
$load d_TotalTax
$load I_dur
$load I_dur2inv
$load I_inv
$GDXIN
$offMulti;
$GDXIN I
$onMulti
$load R_LR
$load infl_LR
$load g_LR
$GDXIN
$offMulti;
$GDXIN I
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
$load techPot
$load techCost
$load DACCost
$load uCO2
$load tauCO2agg
$load tauDist
$load qCO2agg
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





# -------------------------------------------------B_I------------------------------------------------
#  Initialize B_I equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_I_zpOut[t,s,n];
E_I_zpOut[t,s,n]$(i_knot_o[s,n] and txe[t]).. 	pS[t,s,n]*qS[t,s,n]  =E=  sum(nn$(I_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_I_zpNOut[t,s,n];
E_I_zpNOut[t,s,n]$(i_knot_no[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(I_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_I_qOut[t,s,n];
E_I_qOut[t,s,n]$(i_branch2o[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(I_map[s,nn,n]), mu[s,nn,n] * (pS[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qS[t,s,nn]);
EQUATION E_I_qNOut[t,s,n];
E_I_qNOut[t,s,n]$(i_branch2no[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(I_map[s,nn,n]), mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qD[t,s,nn]);

# ----------------------------------------------------------------------------------------------------
#  Define B_I model
# ----------------------------------------------------------------------------------------------------
Model B_I /
E_I_zpOut, E_I_zpNOut, E_I_qOut, E_I_qNOut
/;



# ---------------------------------------------B_I_adjCost--------------------------------------------
#  Initialize B_I_adjCost equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_I_adjCost_lom[t,s,n];
E_I_adjCost_lom[t,s,n]$(i_dur[s,n] and txe[t]).. 		qD[t+1,s,n]	 =E=  (qD[t,s,n]*(1-rDepr[t,s,n])+sum(nn$(I_dur2inv[s,n,nn]), qD[t,s,nn]))/(1+g_LR);
EQUATION E_I_adjCost_pk[t,s,n];
E_I_adjCost_pk[t,s,n]$(i_dur[s,n] and tx02e[t]).. 	pD[t,s,n]	 =E=  sqrt(sqr(sum(nn$(I_dur2inv[s,n,nn]), Rrate[t]*pD[t-1,s,nn]*(1+adjCostPar[s,n]*(qD[t-1,s,nn]/qD[t-1,s,n]-(rDepr[t-1,s,n]+g_LR)))/(1+infl_LR)+pD[t,s,nn]*(adjCostPar[s,n]*0.5*(sqr(rDepr[t,s,n]+g_LR)-sqr(qD[t,s,nn]/qD[t,s,n]))-(1-rDepr[t,s,n])*(1+adjCostPar[s,n]*(qD[t,s,nn]/qD[t,s,n]-(rDepr[t,s,n]+g_LR)))))));
EQUATION E_I_adjCost_pkT[t,s,n];
E_I_adjCost_pkT[t,s,n]$(i_dur[s,n] and t2e[t]).. 		pD[t,s,n]	 =E=  sum(nn$(I_dur2inv[s,n,nn]), Rrate[t]*pD[t-1,s,nn] * (1+adjCostPar[s,n]*(qD[t-1,s,nn]/qD[t-1,s,n]-(rDepr[t-1,s,n]+g_LR)))/(1+infl_LR) + (rDepr[t,s,n]-1)*pD[t,s,nn]);
EQUATION E_I_adjCost_K_tvc[t,s,n];
E_I_adjCost_K_tvc[t,s,n]$(i_dur[s,n] and te[t]).. 	qD[t,s,n]	 =E=  (1+K_tvc[s,n])*qD[t-1,s,n];
EQUATION E_I_adjCost_adjCost[t,s];
E_I_adjCost_adjCost[t,s]$(i_sm[s] and txe[t]).. 		adjCost[t,s] 	 =E=  sum([n,nn]$(I_dur2inv[s,n,nn]), pD[t,s,nn] * adjCostPar[s,n]*0.5*qD[t,s,n]*sqr(qD[t,s,nn]/qD[t,s,n]-(rDepr[t,s,n]+g_LR)));

# ----------------------------------------------------------------------------------------------------
#  Define B_I_adjCost model
# ----------------------------------------------------------------------------------------------------
Model B_I_adjCost /
E_I_adjCost_lom, E_I_adjCost_pk, E_I_adjCost_pkT, E_I_adjCost_K_tvc, E_I_adjCost_adjCost
/;



# ---------------------------------------------B_I_pWedge---------------------------------------------
#  Initialize B_I_pWedge equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_I_pWedge_pwInp[t,s,n];
E_I_pWedge_pwInp[t,s,n]$(i_input[s,n] and txe[t]).. 			pD[t,s,n]		 =E=  p[t,n]+tauD[t,s,n];
EQUATION E_I_pWedge_pwOut[t,s,n];
E_I_pWedge_pwOut[t,s,n]$(i_output[s,n] and txe[t]).. 		p[t,n] 			 =E=  (1+markup[s])*(pS[t,s,n]+tauS[t,s,n]+(adjCost[t,s]+tauLump[t,s])/qS[t,s,n]);
EQUATION E_I_pWedge_taxRev[t,s];
E_I_pWedge_taxRev[t,s]$(i_sm[s] and txe[t]).. 				TotalTax[t,s]	 =E=  tauLump[t,s]+sum(n$(I_input[s,n]), tauD[t,s,n] * qD[t,s,n])+sum(n$(I_output[s,n]), tauS[t,s,n]*qS[t,s,n]);
EQUATION E_I_pWedge_tauS[t,s,n];
E_I_pWedge_tauS[t,s,n]$(i_output[s,n] and txe[t]).. 			tauS[t,s,n]		 =E=  tauCO2[t,s,n] * qCO2[t,s,n]/qS[t,s,n]+tauNonEnv[t,s,n];

# ----------------------------------------------------------------------------------------------------
#  Define B_I_pWedge model
# ----------------------------------------------------------------------------------------------------
Model B_I_pWedge /
E_I_pWedge_pwInp, E_I_pWedge_pwOut, E_I_pWedge_taxRev, E_I_pWedge_tauS
/;



# --------------------------------------------B_I_taxCalib--------------------------------------------
#  Initialize B_I_taxCalib equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_I_taxCalib_taxCal[t,s,n];
E_I_taxCalib_taxCal[t,s,n]$(i_output[s,n] and txe[t]).. 	tauNonEnv[t,s,n]	 =E=  tauNonEnv0[t,s,n] * (1+taxRevPar[s]);

# ----------------------------------------------------------------------------------------------------
#  Define B_I_taxCalib model
# ----------------------------------------------------------------------------------------------------
Model B_I_taxCalib /
E_I_taxCalib_taxCal
/;



# ----------------------------------------------------------------------------------------------------
#  Define I_B model
# ----------------------------------------------------------------------------------------------------
Model I_B /
E_I_zpOut, E_I_zpNOut, E_I_qOut, E_I_qNOut, E_I_adjCost_lom, E_I_adjCost_pk, E_I_adjCost_pkT, E_I_adjCost_K_tvc, E_I_adjCost_adjCost, E_I_pWedge_pwInp, E_I_pWedge_pwOut, E_I_pWedge_taxRev, E_I_pWedge_tauS
/;


# ----------------------------------------------------------------------------------------------------
#  Define I_C model
# ----------------------------------------------------------------------------------------------------
Model I_C /
E_I_zpOut, E_I_zpNOut, E_I_qOut, E_I_qNOut, E_I_adjCost_lom, E_I_adjCost_pk, E_I_adjCost_pkT, E_I_adjCost_K_tvc, E_I_adjCost_adjCost, E_I_pWedge_pwInp, E_I_pWedge_pwOut, E_I_pWedge_taxRev, E_I_pWedge_tauS, E_I_taxCalib_taxCal
/;


# Fix exogenous variables in state B:
sigma.fx[s,n]$(I_kninp[s,n]) = sigma.l[s,n]$(I_kninp[s,n]);
mu.fx[s,n,nn]$(((I_map[s,n,nn] and ( not (I_endoMu[s,n,nn]))) or I_endoMu[s,n,nn])) = mu.l[s,n,nn]$(((I_map[s,n,nn] and ( not (I_endoMu[s,n,nn]))) or I_endoMu[s,n,nn]));
tauNonEnv0.fx[t,s,n]$(I_output[s,n]) = tauNonEnv0.l[t,s,n]$(I_output[s,n]);
tauD.fx[t,s,n]$(I_input[s,n]) = tauD.l[t,s,n]$(I_input[s,n]);
tauLump.fx[t,s]$(I_sm[s]) = tauLump.l[t,s]$(I_sm[s]);
tauCO2.fx[t,s,n]$(I_output[s,n]) = tauCO2.l[t,s,n]$(I_output[s,n]);
rDepr.fx[t,s,n]$(I_dur[s,n]) = rDepr.l[t,s,n]$(I_dur[s,n]);
adjCostPar.fx[s,n]$(I_dur[s,n]) = adjCostPar.l[s,n]$(I_dur[s,n]);
K_tvc.fx[s,n]$(I_dur[s,n]) = K_tvc.l[s,n]$(I_dur[s,n]);
qD.fx[t,s,n]$((I_dur[s,n] and t0[t])) = qD.l[t,s,n]$((I_dur[s,n] and t0[t]));
qS.fx[t,s,n]$(I_output[s,n]) = qS.l[t,s,n]$(I_output[s,n]);
p.fx[t,n]$((I_input_n[n] and ( not (I_output_n[n])))) = p.l[t,n]$((I_input_n[n] and ( not (I_output_n[n]))));
qCO2.fx[t,s,n]$(I_output[s,n]) = qCO2.l[t,s,n]$(I_output[s,n]);
Rrate.fx[t] = Rrate.l[t];
tauNonEnv.fx[t,s,n]$(I_output[s,n]) = tauNonEnv.l[t,s,n]$(I_output[s,n]);
taxRevPar.fx[s]$(I_sm[s]) = taxRevPar.l[s]$(I_sm[s]);
markup.fx[s]$(I_sm[s]) = markup.l[s]$(I_sm[s]);

# Unfix endogenous variables in state B:
pD.lo[t,s,n]$(((I_int[s,n] or I_input[s,n]) or (I_dur[s,n] and txE[t]))) = -inf;
pD.up[t,s,n]$(((I_int[s,n] or I_input[s,n]) or (I_dur[s,n] and txE[t]))) = inf;
pS.lo[t,s,n]$(I_output[s,n]) = -inf;
pS.up[t,s,n]$(I_output[s,n]) = inf;
p.lo[t,n]$(((I_output_n[n] and tx0[t]) or (I_output_n[n] and t0[t]))) = -inf;
p.up[t,n]$(((I_output_n[n] and tx0[t]) or (I_output_n[n] and t0[t]))) = inf;
qD.lo[t,s,n]$(((I_int[s,n] or (I_input[s,n] and tx0[t]) or (I_dur[s,n] and tx0[t])) or (I_input[s,n] and t0[t]))) = -inf;
qD.up[t,s,n]$(((I_int[s,n] or (I_input[s,n] and tx0[t]) or (I_dur[s,n] and tx0[t])) or (I_input[s,n] and t0[t]))) = inf;
adjCost.lo[t,s]$((I_sm[s] and txE[t])) = -inf;
adjCost.up[t,s]$((I_sm[s] and txE[t])) = inf;
tauS.lo[t,s,n]$(I_output[s,n]) = -inf;
tauS.up[t,s,n]$(I_output[s,n]) = inf;
TotalTax.lo[t,s]$(((I_sm[s] and tx0E[t]) or (I_sm[s] and t0[t]))) = -inf;
TotalTax.up[t,s]$(((I_sm[s] and tx0E[t]) or (I_sm[s] and t0[t]))) = inf;

solve I_B using CNS;
