$ONEOLCOM
$EOLCOM #



;
OPTION SYSOUT=OFF, SOLPRINT=OFF, LIMROW=0, LIMCOL=0, DECIMALS=6;


# User defined functions:

# ----------------------------------------------------------------------------------------------------
#  Define function: SolveEmptyNLP
# ----------------------------------------------------------------------------------------------------


# DEFINE LOCAL FUNCTIONS/MACROS:









# DECLARE SYMBOLS FROM DATABASE:
sets
	alias_set
	alias_map2
	taxTypes
	s
	t
	n
;

alias(n,nn,nnn);
alias(s,ss);
alias(t,tt);

sets
	alias_[alias_set,alias_map2]
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
	nestProdInp[s,n,nn]
	dtauCO2[s,n]
	dqCO2[s,n]
	nestInvestment[s,n,nn]
	nestHH[s,n,nn]
	L2C[s,n,nn]
	nestG[s,n,nn]
	d_TotalTax[s]
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
	Inp_map[s,n,nn]
	Inp_knot[s,n]
	Inp_branch[s,n]
	Inp_knot_o[s,n]
	Inp_knot_no[s,n]
	Inp_branch2o[s,n]
	Inp_branch2no[s,n]
	P_sm[s]
	P_endoP[n]
	P_input_n[n]
	P_endoMu[s,n,nn]
	P_dur[s,n]
	P_dur2inv[s,n,nn]
	P_inv[s,n]
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
	I_endoP[n]
	I_input_n[n]
	I_endoMu[s,n,nn]
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
	HH_C[s,n]
	HH_output_n[n]
	HH_input_n[n]
	HH_sm[s]
	G_map[s,n,nn]
	G_map_spinp[s,n,nn]
	G_map_spout[s,n,nn]
	G_knout[s,n]
	G_kninp[s,n]
	G_spout[s,n]
	G_spinp[s,n]
	G_input[s,n]
	G_output[s,n]
	G_int[s,n]
	G_knot[s,n]
	G_branch[s,n]
	G_knot_o[s,n]
	G_knot_no[s,n]
	G_branch2o[s,n]
	G_branch2no[s,n]
	G_endoMu[s,n,nn]
	G_input_n[n]
	G_sm[s]
	T_dExport[s,n]
	T_nF[n]
	T_nD[n]
	T_sm[s]
	sInventory[s]
	dInventory[s,n]
;

parameters
	R_LR
	infl_LR
	g_LR
	inventoryAR[s,n]
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
	tauLump[t,s]
	tauS[t,s,n]
	tauD[t,s,n]
	pD[t,s,n]
	frisch[s]
	uCO2[t,s,n]
	tauCO2agg[t]
	tauDist[t,s,n]
	qCO2agg[t]
	tauEffCO2[t,s,n]
	Rrate[t]
	mu[s,n,nn]
	pS[t,s,n]
	markup[s]
	vA[t,s]
	vA_tvc[s]
	divd[t,s]
	taxRevPar[s]
	tauLump0[t,s]
	K_tvc[s,n]
	adjCostPar[s,n]
	adjCost[t,s]
	tauD0[t,s,n]
	crra[s]
	vU[t,s]
	vU_tvc[s]
	discF[s]
	jTerm[s]
	gadj[s]
	tauS0[t,s,n]
	Fscale[s,n]
	uCO20[t,s,n]
	uCO2Calib[s,n]
;


# LOAD SYMBOLS FROM DATABASE:
$GDXIN vSmalldb
$onMulti
$load alias_set
$load alias_map2
$load taxTypes
$load s
$load t
$load n
$load alias_
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
$load nestProdInp
$load dtauCO2
$load dqCO2
$load nestInvestment
$load nestHH
$load L2C
$load nestG
$load d_TotalTax
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
$load Inp_map
$load Inp_knot
$load Inp_branch
$load Inp_knot_o
$load Inp_knot_no
$load Inp_branch2o
$load Inp_branch2no
$load P_sm
$load P_endoP
$load P_input_n
$load P_endoMu
$load P_dur
$load P_dur2inv
$load P_inv
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
$load I_endoP
$load I_input_n
$load I_endoMu
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
$load HH_C
$load HH_output_n
$load HH_input_n
$load HH_sm
$load G_map
$load G_map_spinp
$load G_map_spout
$load G_knout
$load G_kninp
$load G_spout
$load G_spinp
$load G_input
$load G_output
$load G_int
$load G_knot
$load G_branch
$load G_knot_o
$load G_knot_no
$load G_branch2o
$load G_branch2no
$load G_endoMu
$load G_input_n
$load G_sm
$load T_dExport
$load T_nF
$load T_nD
$load T_sm
$load sInventory
$load dInventory
$GDXIN
$offMulti;
$GDXIN vSmalldb
$onMulti
$load R_LR
$load infl_LR
$load g_LR
$load inventoryAR
$GDXIN
$offMulti;
$GDXIN vSmalldb
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
$load tauLump
$load tauS
$load tauD
$load pD
$load frisch
$load uCO2
$load tauCO2agg
$load tauDist
$load qCO2agg
$load tauEffCO2
$load Rrate
$load mu
$load pS
$load markup
$load vA
$load vA_tvc
$load divd
$load taxRevPar
$load tauLump0
$load K_tvc
$load adjCostPar
$load adjCost
$load tauD0
$load crra
$load vU
$load vU_tvc
$load discF
$load jTerm
$load gadj
$load tauS0
$load Fscale
$load uCO20
$load uCO2Calib
$GDXIN
$offMulti;


# WRITE INIT STATEMENTS FROM MODULES:









# WRITE BLOCKS OF EQUATIONS:


# ------------------------------------------------B_Inp-----------------------------------------------
#  Initialize B_Inp equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_Inp_zpOut[t,s,n];
E_Inp_zpOut[t,s,n]$(inp_knot_o[s,n] and txe[t]).. 	pS[t,s,n]*qS[t,s,n]  =E=  sum(nn$(Inp_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_Inp_zpNOut[t,s,n];
E_Inp_zpNOut[t,s,n]$(inp_knot_no[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(Inp_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_Inp_qOut[t,s,n];
E_Inp_qOut[t,s,n]$(inp_branch2o[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(Inp_map[s,nn,n]), mu[s,nn,n] * (pS[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qS[t,s,nn]);
EQUATION E_Inp_qNOut[t,s,n];
E_Inp_qNOut[t,s,n]$(inp_branch2no[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(Inp_map[s,nn,n]), mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qD[t,s,nn]);

# ----------------------------------------------------------------------------------------------------
#  Define B_Inp model
# ----------------------------------------------------------------------------------------------------
Model B_Inp /
E_Inp_zpOut, E_Inp_zpNOut, E_Inp_qOut, E_Inp_qNOut
/;



# ----------------------------------------------B_P_price---------------------------------------------
#  Initialize B_P_price equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_P_price_pD[t,s,n];
E_P_price_pD[t,s,n]$(p_input[s,n] and txe[t]).. 			pD[t,s,n]		 =E=  p[t,n]*(1+tauD[t,s,n]);
EQUATION E_P_price_pS[t,s,n];
E_P_price_pS[t,s,n]$(p_output[s,n] and txe[t]).. 			p[t,n] 			 =E=  (1+markup[s])*(pS[t,s,n]+p[t,n]*tauS[t,s,n]+(tauEffCO2[t,s,n]*uCO2[t,s,n])$(dqCO2[s,n]));
EQUATION E_P_price_TotalTax[t,s];
E_P_price_TotalTax[t,s]$(p_sm[s] and txe[t]).. 				TotalTax[t,s]	 =E=  tauLump[t,s]+sum(n$(P_input[s,n]), tauD[t,s,n] * p[t,n] * qD[t,s,n])+sum(n$(P_output[s,n]), tauS[t,s,n]*p[t,n]*qS[t,s,n])+sum(n$(P_output[s,n] and dqCO2[s,n]), tauCO2[t,s,n]*qCO2[t,s,n]);

# ----------------------------------------------------------------------------------------------------
#  Define B_P_price model
# ----------------------------------------------------------------------------------------------------
Model B_P_price /
E_P_price_pD, E_P_price_pS, E_P_price_TotalTax
/;



# --------------------------------------------B_P_firmValue-------------------------------------------
#  Initialize B_P_firmValue equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_P_firmValue_vA[t,s];
E_P_firmValue_vA[t,s]$(p_sm[s] and tx0[t]).. 		vA[t,s]	 =E=  (vA[t-1,s]*Rrate[t-1]-divd[t-1,s])/((1+g_LR)*(1+infl_LR));
EQUATION E_P_firmValue_divd[t,s];
E_P_firmValue_divd[t,s]$(p_sm[s] and txe[t]).. 		divd[t,s]  =E=  sum(n$(P_output[s,n]), p[t,n] * qS[t,s,n])-sum(n$(P_input[s,n]), p[t,n] * qD[t,s,n])-TotalTax[t,s]-adjCost[t,s];
EQUATION E_P_firmValue_vAT[t,s];
E_P_firmValue_vAT[t,s]$(p_sm[s] and te[t]).. 		vA[t,s]	   =E=  (1+vA_tvc[s])*vA[t-1,s]/((1+g_LR)*(1+infl_LR));

# ----------------------------------------------------------------------------------------------------
#  Define B_P_firmValue model
# ----------------------------------------------------------------------------------------------------
Model B_P_firmValue /
E_P_firmValue_vA, E_P_firmValue_divd, E_P_firmValue_vAT
/;



# --------------------------------------------B_P_taxCalib--------------------------------------------
#  Initialize B_P_taxCalib equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_P_taxCalib_taxRevPar[t,s];
E_P_taxCalib_taxRevPar[t,s]$(p_sm[s]).. 	tauLump[t,s]  =E=  tauLump0[t,s]+taxRevPar[s];

# ----------------------------------------------------------------------------------------------------
#  Define B_P_taxCalib model
# ----------------------------------------------------------------------------------------------------
Model B_P_taxCalib /
E_P_taxCalib_taxRevPar
/;



# ---------------------------------------------B_P_adjCost--------------------------------------------
#  Initialize B_P_adjCost equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_P_adjCost_lom[t,s,n];
E_P_adjCost_lom[t,s,n]$(p_dur[s,n] and txe[t]).. 		qD[t+1,s,n]	 =E=  (qD[t,s,n]*(1-rDepr[t,s,n])+sum(nn$(P_dur2inv[s,n,nn]), qD[t,s,nn]))/(1+g_LR);
EQUATION E_P_adjCost_pk[t,s,n];
E_P_adjCost_pk[t,s,n]$(p_dur[s,n] and tx02e[t]).. 	pD[t,s,n]	 =E=  sum(nn$(P_dur2inv[s,n,nn]), Rrate[t]*(pD[t-1,s,nn]+adjCostPar[s,n]*(qD[t-1,s,nn]/qD[t-1,s,n]-(rDepr[t-1,s,n]+g_LR)))/(1+infl_LR)+(adjCostPar[s,n]*0.5*(sqr(rDepr[t,s,n]+g_LR)-sqr(qD[t,s,nn]/qD[t,s,n]))-(1-rDepr[t,s,n])*(pD[t,s,nn]+adjCostPar[s,n]*(qD[t,s,nn]/qD[t,s,n]-(rDepr[t,s,n]+g_LR)))));
EQUATION E_P_adjCost_pkT[t,s,n];
E_P_adjCost_pkT[t,s,n]$(p_dur[s,n] and t2e[t]).. 		pD[t,s,n]	 =E=  sum(nn$(P_dur2inv[s,n,nn]), Rrate[t]*(pD[t-1,s,nn]+adjCostPar[s,n]*(qD[t-1,s,nn]/qD[t-1,s,n]-(rDepr[t-1,s,n]+g_LR)))/(1+infl_LR)+(rDepr[t,s,n]-1)*pD[t,s,nn]);
EQUATION E_P_adjCost_K_tvc[t,s,n];
E_P_adjCost_K_tvc[t,s,n]$(p_dur[s,n] and te[t]).. 	qD[t,s,n]	 =E=  (1+K_tvc[s,n])*qD[t-1,s,n]/(1+g_LR);
EQUATION E_P_adjCost_adjCost[t,s];
E_P_adjCost_adjCost[t,s]$(p_sm[s] and txe[t]).. 		adjCost[t,s] 	 =E=  sum([n,nn]$(P_dur2inv[s,n,nn]), adjCostPar[s,n]*0.5*qD[t,s,n]*sqr(qD[t,s,nn]/qD[t,s,n]-(rDepr[t,s,n]+g_LR)));

# ----------------------------------------------------------------------------------------------------
#  Define B_P_adjCost model
# ----------------------------------------------------------------------------------------------------
Model B_P_adjCost /
E_P_adjCost_lom, E_P_adjCost_pk, E_P_adjCost_pkT, E_P_adjCost_K_tvc, E_P_adjCost_adjCost
/;




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



# ----------------------------------------------B_I_price---------------------------------------------
#  Initialize B_I_price equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_I_price_pD[t,s,n];
E_I_price_pD[t,s,n]$(i_input[s,n] and txe[t]).. 			pD[t,s,n]		 =E=  p[t,n]*(1+tauD[t,s,n]);
EQUATION E_I_price_pS[t,s,n];
E_I_price_pS[t,s,n]$(i_output[s,n] and txe[t]).. 			p[t,n] 			 =E=  (1+markup[s])*(pS[t,s,n]+p[t,n]*tauS[t,s,n]);
EQUATION E_I_price_TotalTax[t,s];
E_I_price_TotalTax[t,s]$(i_sm[s] and txe[t]).. 				TotalTax[t,s]	 =E=  tauLump[t,s]+sum(n$(I_input[s,n]), tauD[t,s,n] * p[t,n] * qD[t,s,n])+sum(n$(I_output[s,n]), tauS[t,s,n]*p[t,n]*qS[t,s,n]);

# ----------------------------------------------------------------------------------------------------
#  Define B_I_price model
# ----------------------------------------------------------------------------------------------------
Model B_I_price /
E_I_price_pD, E_I_price_pS, E_I_price_TotalTax
/;



# --------------------------------------------B_I_firmValue-------------------------------------------
#  Initialize B_I_firmValue equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_I_firmValue_vA[t,s];
E_I_firmValue_vA[t,s]$(i_sm[s] and tx0[t]).. 		vA[t,s]	 =E=  (vA[t-1,s]*Rrate[t-1]-divd[t-1,s])/((1+g_LR)*(1+infl_LR));
EQUATION E_I_firmValue_divd[t,s];
E_I_firmValue_divd[t,s]$(i_sm[s] and txe[t]).. 		divd[t,s]  =E=  sum(n$(I_output[s,n]), p[t,n] * qS[t,s,n])-sum(n$(I_input[s,n]), p[t,n] * qD[t,s,n])-TotalTax[t,s];
EQUATION E_I_firmValue_vAT[t,s];
E_I_firmValue_vAT[t,s]$(i_sm[s] and te[t]).. 		vA[t,s]	   =E=  (1+vA_tvc[s])*vA[t-1,s]/((1+g_LR)*(1+infl_LR));

# ----------------------------------------------------------------------------------------------------
#  Define B_I_firmValue model
# ----------------------------------------------------------------------------------------------------
Model B_I_firmValue /
E_I_firmValue_vA, E_I_firmValue_divd, E_I_firmValue_vAT
/;



# --------------------------------------------B_I_taxCalib--------------------------------------------
#  Initialize B_I_taxCalib equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_I_taxCalib_taxRevPar[t,s,n];
E_I_taxCalib_taxRevPar[t,s,n]$(i_input[s,n]).. 	tauD[t,s,n]  =E=  tauD0[t,s,n]+taxRevPar[s];

# ----------------------------------------------------------------------------------------------------
#  Define B_I_taxCalib model
# ----------------------------------------------------------------------------------------------------
Model B_I_taxCalib /
E_I_taxCalib_taxRevPar
/;




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



# ---------------------------------------------B_HH_price---------------------------------------------
#  Initialize B_HH_price equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_HH_price_pD[t,s,n];
E_HH_price_pD[t,s,n]$(hh_input[s,n] and txe[t]).. 	pD[t,s,n]		 =E=  p[t,n]*(1+tauD[t,s,n]);
EQUATION E_HH_price_w[t,s,n];
E_HH_price_w[t,s,n]$(hh_l[s,n] and txe[t]).. 			pS[t,s,n]		 =E=  p[t,n]*(1-tauS[t,s,n]);
EQUATION E_HH_price_TotalTax[t,s];
E_HH_price_TotalTax[t,s]$(hh_sm[s] and txe[t]).. 		TotalTax[t,s]	 =E=  tauLump[t,s]+sum(n$(HH_input[s,n]), tauD[t,s,n] * p[t,n] * qD[t,s,n])+sum(n$(HH_L[s,n]), tauS[t,s,n]*p[t,n]*qS[t,s,n]);
EQUATION E_HH_price_vA0[t,s];
E_HH_price_vA0[t,s]$(hh_sm[s] and t0[t]).. 			vA[t+1,s]		 =E=  (vA[t,s] * Rrate[t] + sum(n$(HH_L[s,n]), p[t,n]*qS[t,s,n])-sum(n$(HH_input[s,n]), p[t,n]*qD[t,s,n])-TotalTax[t,s])/(1+g_LR);
EQUATION E_HH_price_vA[t,s];
E_HH_price_vA[t,s]$(hh_sm[s] and tx0e[t]).. 			vA[t+1,s]		 =E=  (vA[t,s] * Rrate[t] + sum(n$(HH_L[s,n]), p[t,n]*qS[t,s,n])-sum(n$(HH_input[s,n]), p[t,n]*qD[t,s,n])-TotalTax[t,s])/(1+g_LR);

# ----------------------------------------------------------------------------------------------------
#  Define B_HH_price model
# ----------------------------------------------------------------------------------------------------
Model B_HH_price /
E_HH_price_pD, E_HH_price_w, E_HH_price_TotalTax, E_HH_price_vA0, E_HH_price_vA
/;



# -----------------------------------------------B_HH_vU----------------------------------------------
#  Initialize B_HH_vU equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_HH_vU_vU[t,s];
E_HH_vU_vU[t,s]$(hh_sm[s] and txe[t]).. 	vU[t,s]		 =E=  sum(n$(HH_C[s,n]), qD[t,s,n])**(1-crra[s])/(1-crra[s])+(1+gadj[s])*discF[s]*vU[t+1,s];
EQUATION E_HH_vU_vUT[t,s];
E_HH_vU_vUT[t,s]$(hh_sm[s] and te[t]).. 	vU[t,s]		 =E=  vU[t-1,s]*(1+vU_tvc[s])/(1+gadj[s]);

# ----------------------------------------------------------------------------------------------------
#  Define B_HH_vU model
# ----------------------------------------------------------------------------------------------------
Model B_HH_vU /
E_HH_vU_vU, E_HH_vU_vUT
/;



# --------------------------------------------B_HH_taxCalib-------------------------------------------
#  Initialize B_HH_taxCalib equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_HH_taxCalib_taxRevPar[t,s,n];
E_HH_taxCalib_taxRevPar[t,s,n]$((hh_l[s,n] and txe[t])).. 	tauS[t,s,n]  =E=  tauS0[t,s,n]+taxRevPar[s];

# ----------------------------------------------------------------------------------------------------
#  Define B_HH_taxCalib model
# ----------------------------------------------------------------------------------------------------
Model B_HH_taxCalib /
E_HH_taxCalib_taxRevPar
/;




# -------------------------------------------------B_G------------------------------------------------
#  Initialize B_G equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_G_zp[t,s,n];
E_G_zp[t,s,n]$(g_knot[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(G_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_G_q[t,s,n];
E_G_q[t,s,n]$(g_branch[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(G_map[s,nn,n]), mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qD[t,s,nn]);

# ----------------------------------------------------------------------------------------------------
#  Define B_G model
# ----------------------------------------------------------------------------------------------------
Model B_G /
E_G_zp, E_G_q
/;



# ----------------------------------------------B_G_price---------------------------------------------
#  Initialize B_G_price equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_G_price_pD[t,s,n];
E_G_price_pD[t,s,n]$(g_input[s,n] and txe[t]).. 	pD[t,s,n]		 =E=  p[t,n]*(1+tauD[t,s,n]);
EQUATION E_G_price_TotalTax[t,s];
E_G_price_TotalTax[t,s]$(g_sm[s] and txe[t]).. 		TotalTax[t,s]	 =E=  tauLump[t,s]+sum(n$(G_input[s,n]), tauD[t,s,n] * p[t,n] * qD[t,s,n]);
EQUATION E_G_price_vA0[t,s];
E_G_price_vA0[t,s]$(g_sm[s] and t0[t]).. 			vA[t+1,s]		 =E=  (vA[t,s] * Rrate[t]+sum(ss$(d_TotalTax[ss]), TotalTax[t,ss])-sum(n$(G_input[s,n]), p[t,n]*qD[t,s,n])-TotalTax[t,s])/(1+g_LR);
EQUATION E_G_price_vA[t,s];
E_G_price_vA[t,s]$(g_sm[s] and tx0e[t]).. 			vA[t+1,s]		 =E=  (vA[t,s] * Rrate[t]+sum(ss$(d_TotalTax[ss]), TotalTax[t,ss])-sum(n$(G_input[s,n]), p[t,n]*qD[t,s,n])-TotalTax[t,s])/(1+g_LR);

# ----------------------------------------------------------------------------------------------------
#  Define B_G_price model
# ----------------------------------------------------------------------------------------------------
Model B_G_price /
E_G_price_pD, E_G_price_TotalTax, E_G_price_vA0, E_G_price_vA
/;



# --------------------------------------------B_G_taxCalib--------------------------------------------
#  Initialize B_G_taxCalib equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_G_taxCalib_taxRevPar[t,s];
E_G_taxCalib_taxRevPar[t,s]$((g_sm[s] and txe[t])).. 	tauLump[t,s]  =E=  tauLump0[t,s]+taxRevPar[s];

# ----------------------------------------------------------------------------------------------------
#  Define B_G_taxCalib model
# ----------------------------------------------------------------------------------------------------
Model B_G_taxCalib /
E_G_taxCalib_taxRevPar
/;




# -------------------------------------------------B_T------------------------------------------------
#  Initialize B_T equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_T_qD[t,s,n];
E_T_qD[t,s,n]$(t_dexport[s,n] and txe[t]).. 	qD[t,s,n]		 =E=  sum(nn$(dom2for[n,nn]), Fscale[s,n] * (p[t,nn]/pD[t,s,n])**(sigma[s,n]));
EQUATION E_T_pD[t,s,n];
E_T_pD[t,s,n]$(t_dexport[s,n] and txe[t]).. 	pD[t,s,n]		 =E=  p[t,n]*(1+ tauD[t,s,n]);
EQUATION E_T_TotalTax[t,s];
E_T_TotalTax[t,s]$(t_sm[s] and txe[t]).. 	TotalTax[t,s]	 =E=  tauLump[t,s]+sum(n$(T_dExport[s,n]), tauD[t,s,n]*qD[t,s,n]);

# ----------------------------------------------------------------------------------------------------
#  Define B_T model
# ----------------------------------------------------------------------------------------------------
Model B_T /
E_T_qD, E_T_pD, E_T_TotalTax
/;




# ------------------------------------------------B_IVT-----------------------------------------------
#  Initialize B_IVT equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_IVT[t,s,n];
E_IVT[t,s,n]$(dinventory[s,n] and tx0e[t]).. 	qD[t,s,n]  =E=  inventoryAR[s,n] * qD[t-1,s,n]/(1+g_LR);

# ----------------------------------------------------------------------------------------------------
#  Define B_IVT model
# ----------------------------------------------------------------------------------------------------
Model B_IVT /
E_IVT
/;




# -------------------------------------------------B_M------------------------------------------------
#  Initialize B_M equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_M_tauCO2[t,s,n];
E_M_tauCO2[t,s,n]$(dtauco2[s,n] and txe[t])..  		tauCO2[t,s,n]	 =E=  tauCO2agg[t] * tauDist[t,s,n];
EQUATION E_M_tauCO2Eff[t,s,n];
E_M_tauCO2Eff[t,s,n]$(dtauco2[s,n] and txe[t]).. 	tauEffCO2[t,s,n] =E=  tauCO2[t,s,n];
EQUATION E_M_qCO2[t,s,n];
E_M_qCO2[t,s,n]$(dqco2[s,n] and txe[t]).. 			qCO2[t,s,n]	     =E=  uCO2[t,s,n] * qS[t,s,n];
EQUATION E_M_qCO2agg[t];
E_M_qCO2agg[t]$(txe[t]).. 								qCO2agg[t]	 =E=  sum([s,n]$(dqCO2[s,n]), qCO2[t,s,n]);

# ----------------------------------------------------------------------------------------------------
#  Define B_M model
# ----------------------------------------------------------------------------------------------------
Model B_M /
E_M_tauCO2, E_M_tauCO2Eff, E_M_qCO2, E_M_qCO2agg
/;



# ----------------------------------------------B_M_calib---------------------------------------------
#  Initialize B_M_calib equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_M_qCO2calib[t,s,n];
E_M_qCO2calib[t,s,n]$(dqco2[s,n] and txe[t]).. 	uCO2[t,s,n]	 =E=  uCO20[t,s,n] * (1+uCO2calib[s,n]);

# ----------------------------------------------------------------------------------------------------
#  Define B_M_calib model
# ----------------------------------------------------------------------------------------------------
Model B_M_calib /
E_M_qCO2calib
/;




# -------------------------------------------B_Equi_baseline------------------------------------------
#  Initialize B_Equi_baseline equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_Equi_equi[t,n];
E_Equi_equi[t,n]$(nequi[n] and txe[t]).. 	 sum(s$(d_qS[s,n]), qS[t,s,n])  =E=  sum(s$(d_qD[s,n]), qD[t,s,n]);

# ----------------------------------------------------------------------------------------------------
#  Define B_Equi_baseline model
# ----------------------------------------------------------------------------------------------------
Model B_Equi_baseline /
E_Equi_equi
/;



# --------------------------------------------B_Equi_calib--------------------------------------------
#  Initialize B_Equi_calib equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_Equi_equi_tx0E[t,n];
E_Equi_equi_tx0E[t,n]$(nequi[n] and tx0e[t]).. 	 sum(s$(d_qS[s,n]), qS[t,s,n])  =E=  sum(s$(d_qD[s,n]), qD[t,s,n]);

# ----------------------------------------------------------------------------------------------------
#  Define B_Equi_calib model
# ----------------------------------------------------------------------------------------------------
Model B_Equi_calib /
E_Equi_equi_tx0E
/;



# DEFINE MODELS:

# ----------------------------------------------------------------------------------------------------
#  Define M_vSmall_B model
# ----------------------------------------------------------------------------------------------------
Model M_vSmall_B /
E_Inp_zpOut, E_Inp_zpNOut, E_Inp_qOut, E_Inp_qNOut, E_P_price_pD, E_P_price_pS, E_P_price_TotalTax, E_P_firmValue_vA, E_P_firmValue_divd, E_P_firmValue_vAT, E_P_adjCost_lom, E_P_adjCost_pk, E_P_adjCost_pkT, E_P_adjCost_K_tvc, E_P_adjCost_adjCost, E_I_zpOut, E_I_zpNOut, E_I_qOut, E_I_qNOut, E_I_price_pD, E_I_price_pS, E_I_price_TotalTax, E_I_firmValue_vA, E_I_firmValue_divd, E_I_firmValue_vAT, E_HH_zp, E_HH_q, E_HH_price_pD, E_HH_price_w, E_HH_price_TotalTax, E_HH_price_vA0, E_HH_price_vA, E_HH_vU_vU, E_HH_vU_vUT, E_G_zp, E_G_q, E_G_price_pD, E_G_price_TotalTax, E_G_price_vA0, E_G_price_vA, E_T_qD, E_T_pD, E_T_TotalTax, E_IVT, E_M_tauCO2, E_M_tauCO2Eff, E_M_qCO2, E_M_qCO2agg, E_Equi_equi
/;


# ----------------------------------------------------------------------------------------------------
#  Define M_vSmall_C model
# ----------------------------------------------------------------------------------------------------
Model M_vSmall_C /
E_Inp_zpOut, E_Inp_zpNOut, E_Inp_qOut, E_Inp_qNOut, E_P_price_pD, E_P_price_pS, E_P_price_TotalTax, E_P_firmValue_vA, E_P_firmValue_divd, E_P_firmValue_vAT, E_P_adjCost_lom, E_P_adjCost_pk, E_P_adjCost_pkT, E_P_adjCost_K_tvc, E_P_adjCost_adjCost, E_P_taxCalib_taxRevPar, E_I_zpOut, E_I_zpNOut, E_I_qOut, E_I_qNOut, E_I_price_pD, E_I_price_pS, E_I_price_TotalTax, E_I_firmValue_vA, E_I_firmValue_divd, E_I_firmValue_vAT, E_I_taxCalib_taxRevPar, E_HH_zp, E_HH_q, E_HH_price_pD, E_HH_price_w, E_HH_price_TotalTax, E_HH_price_vA0, E_HH_price_vA, E_HH_vU_vU, E_HH_vU_vUT, E_HH_taxCalib_taxRevPar, E_G_zp, E_G_q, E_G_price_pD, E_G_price_TotalTax, E_G_price_vA0, E_G_price_vA, E_G_taxCalib_taxRevPar, E_T_qD, E_T_pD, E_T_TotalTax, E_IVT, E_M_tauCO2, E_M_tauCO2Eff, E_M_qCO2, E_M_qCO2agg, E_M_qCO2calib, E_Equi_equi_tx0E
/;
;

# Fix exogenous variables in state:
sigma.fx[s,n]$(P_kninp[s,n]) = sigma.l[s,n]$(P_kninp[s,n]);
mu.fx[s,n,nn]$(((P_map[s,n,nn] and ( not (P_endoMu[s,n,nn]))) or P_endoMu[s,n,nn])) = mu.l[s,n,nn]$(((P_map[s,n,nn] and ( not (P_endoMu[s,n,nn]))) or P_endoMu[s,n,nn]));
vA_tvc.fx[s]$(P_sm[s]) = vA_tvc.l[s]$(P_sm[s]);
tauD.fx[t,s,n]$(P_input[s,n]) = tauD.l[t,s,n]$(P_input[s,n]);
tauS.fx[t,s,n]$(P_output[s,n]) = tauS.l[t,s,n]$(P_output[s,n]);
tauLump0.fx[t,s]$(P_sm[s]) = tauLump0.l[t,s]$(P_sm[s]);
qS.fx[t,s,n]$(P_output[s,n]) = qS.l[t,s,n]$(P_output[s,n]);
p.fx[t,n]$((P_input_n[n] and ( not (P_endoP[n])))) = p.l[t,n]$((P_input_n[n] and ( not (P_endoP[n]))));
Rrate.fx[t] = Rrate.l[t];
tauCO2.fx[t,s,n]$((P_output[s,n] and dqCO2[s,n])) = tauCO2.l[t,s,n]$((P_output[s,n] and dqCO2[s,n]));
qCO2.fx[t,s,n]$((P_output[s,n] and dqCO2[s,n])) = qCO2.l[t,s,n]$((P_output[s,n] and dqCO2[s,n]));
uCO2.fx[t,s,n]$((P_output[s,n] and dqCO2[s,n])) = uCO2.l[t,s,n]$((P_output[s,n] and dqCO2[s,n]));
tauEffCO2.fx[t,s,n]$((P_output[s,n] and dqCO2[s,n])) = tauEffCO2.l[t,s,n]$((P_output[s,n] and dqCO2[s,n]));
rDepr.fx[t,s,n]$(P_dur[s,n]) = rDepr.l[t,s,n]$(P_dur[s,n]);
K_tvc.fx[s,n]$(P_dur[s,n]) = K_tvc.l[s,n]$(P_dur[s,n]);
qD.fx[t,s,n]$((P_dur[s,n] and t0[t])) = qD.l[t,s,n]$((P_dur[s,n] and t0[t]));
adjCostPar.fx[s,n]$(P_dur[s,n]) = adjCostPar.l[s,n]$(P_dur[s,n]);
markup.fx[s]$(P_sm[s]) = markup.l[s]$(P_sm[s]);
taxRevPar.fx[s]$(P_sm[s]) = taxRevPar.l[s]$(P_sm[s]);
tauLump.fx[t,s]$(P_sm[s]) = tauLump.l[t,s]$(P_sm[s]);
sigma.fx[s,n]$(I_kninp[s,n]) = sigma.l[s,n]$(I_kninp[s,n]);
mu.fx[s,n,nn]$(((I_map[s,n,nn] and ( not (I_endoMu[s,n,nn]))) or I_endoMu[s,n,nn])) = mu.l[s,n,nn]$(((I_map[s,n,nn] and ( not (I_endoMu[s,n,nn]))) or I_endoMu[s,n,nn]));
vA_tvc.fx[s]$(I_sm[s]) = vA_tvc.l[s]$(I_sm[s]);
tauS.fx[t,s,n]$(I_output[s,n]) = tauS.l[t,s,n]$(I_output[s,n]);
tauLump.fx[t,s]$(I_sm[s]) = tauLump.l[t,s]$(I_sm[s]);
tauD0.fx[t,s,n]$(I_input[s,n]) = tauD0.l[t,s,n]$(I_input[s,n]);
qS.fx[t,s,n]$(I_output[s,n]) = qS.l[t,s,n]$(I_output[s,n]);
p.fx[t,n]$((I_input_n[n] and ( not (I_endoP[n])))) = p.l[t,n]$((I_input_n[n] and ( not (I_endoP[n]))));
Rrate.fx[t] = Rrate.l[t];
markup.fx[s]$(I_sm[s]) = markup.l[s]$(I_sm[s]);
taxRevPar.fx[s]$(I_sm[s]) = taxRevPar.l[s]$(I_sm[s]);
tauD.fx[t,s,n]$(I_input[s,n]) = tauD.l[t,s,n]$(I_input[s,n]);
sigma.fx[s,n]$(HH_kninp[s,n]) = sigma.l[s,n]$(HH_kninp[s,n]);
mu.fx[s,n,nn]$(((HH_map[s,n,nn] and ( not (HH_endoMu[s,n,nn]))) or HH_endoMu[s,n,nn])) = mu.l[s,n,nn]$(((HH_map[s,n,nn] and ( not (HH_endoMu[s,n,nn]))) or HH_endoMu[s,n,nn]));
crra.fx[s]$(HH_sm[s]) = crra.l[s]$(HH_sm[s]);
discF.fx[s]$(HH_sm[s]) = discF.l[s]$(HH_sm[s]);
vU_tvc.fx[s]$(HH_sm[s]) = vU_tvc.l[s]$(HH_sm[s]);
gadj.fx[s]$(HH_sm[s]) = gadj.l[s]$(HH_sm[s]);
tauD.fx[t,s,n]$(HH_input[s,n]) = tauD.l[t,s,n]$(HH_input[s,n]);
tauS.fx[t,s,n]$(((HH_L[s,n] and ( not ((HH_L[s,n] and txE[t])))) or (HH_L[s,n] and txE[t]))) = tauS.l[t,s,n]$(((HH_L[s,n] and ( not ((HH_L[s,n] and txE[t])))) or (HH_L[s,n] and txE[t])));
tauLump.fx[t,s]$(HH_sm[s]) = tauLump.l[t,s]$(HH_sm[s]);
tauS0.fx[t,s,n]$((HH_L[s,n] and txE[t])) = tauS0.l[t,s,n]$((HH_L[s,n] and txE[t]));
vA.fx[t,s]$((HH_sm[s] or (t0[t] and HH_sm[s]))) = vA.l[t,s]$((HH_sm[s] or (t0[t] and HH_sm[s])));
qS.fx[t,s,n]$((HH_L[s,n] and txE[t])) = qS.l[t,s,n]$((HH_L[s,n] and txE[t]));
p.fx[t,n]$((HH_output_n[n] or HH_input_n[n])) = p.l[t,n]$((HH_output_n[n] or HH_input_n[n]));
Rrate.fx[t] = Rrate.l[t];
taxRevPar.fx[s]$(HH_sm[s]) = taxRevPar.l[s]$(HH_sm[s]);
sigma.fx[s,n]$(G_kninp[s,n]) = sigma.l[s,n]$(G_kninp[s,n]);
mu.fx[s,n,nn]$(((G_map[s,n,nn] and ( not (G_endoMu[s,n,nn]))) or G_endoMu[s,n,nn])) = mu.l[s,n,nn]$(((G_map[s,n,nn] and ( not (G_endoMu[s,n,nn]))) or G_endoMu[s,n,nn]));
tauD.fx[t,s,n]$(G_input[s,n]) = tauD.l[t,s,n]$(G_input[s,n]);
tauLump.fx[t,s]$(((G_sm[s] and ( not ((G_sm[s] and txE[t])))) or (G_sm[s] and txE[t]))) = tauLump.l[t,s]$(((G_sm[s] and ( not ((G_sm[s] and txE[t])))) or (G_sm[s] and txE[t])));
tauLump0.fx[t,s]$((G_sm[s] and txE[t])) = tauLump0.l[t,s]$((G_sm[s] and txE[t]));
vA.fx[t,s]$((G_sm[s] or (t0[t] and G_sm[s]))) = vA.l[t,s]$((G_sm[s] or (t0[t] and G_sm[s])));
p.fx[t,n]$(G_input_n[n]) = p.l[t,n]$(G_input_n[n]);
Rrate.fx[t] = Rrate.l[t];
qD.fx[t,s,n]$(((G_output[s,n] and tx0E[t]) or (G_output[s,n] and t0[t]))) = qD.l[t,s,n]$(((G_output[s,n] and tx0E[t]) or (G_output[s,n] and t0[t])));
taxRevPar.fx[s]$(G_sm[s]) = taxRevPar.l[s]$(G_sm[s]);
p.fx[t,n]$((T_nF[n] or T_nD[n])) = p.l[t,n]$((T_nF[n] or T_nD[n]));
sigma.fx[s,n]$(T_dExport[s,n]) = sigma.l[s,n]$(T_dExport[s,n]);
tauD.fx[t,s,n]$(T_dExport[s,n]) = tauD.l[t,s,n]$(T_dExport[s,n]);
tauLump.fx[t,s]$(((T_sm[s] and tx0E[t]) or (T_sm[s] and t0[t]))) = tauLump.l[t,s]$(((T_sm[s] and tx0E[t]) or (T_sm[s] and t0[t])));
Fscale.fx[s,n]$(T_dExport[s,n]) = Fscale.l[s,n]$(T_dExport[s,n]);
qD.fx[t,s,n]$((dInventory[s,n] and t0[t])) = qD.l[t,s,n]$((dInventory[s,n] and t0[t]));
tauCO2agg.fx[t] = tauCO2agg.l[t];
tauDist.fx[t,s,n]$(dtauCO2[s,n]) = tauDist.l[t,s,n]$(dtauCO2[s,n]);
uCO20.fx[t,s,n]$(dqCO2[s,n]) = uCO20.l[t,s,n]$(dqCO2[s,n]);
uCO2Calib.fx[s,n]$(dqCO2[s,n]) = uCO2Calib.l[s,n]$(dqCO2[s,n]);
uCO2.fx[t,s,n]$(dqCO2[s,n]) = uCO2.l[t,s,n]$(dqCO2[s,n]);
Rrate.fx[t] = Rrate.l[t];

# Unfix endogenous variables in state:
pD.lo[t,s,n]$(((P_int[s,n] or P_input[s,n]) or (P_dur[s,n] and txE[t]))) = -inf;
pD.up[t,s,n]$(((P_int[s,n] or P_input[s,n]) or (P_dur[s,n] and txE[t]))) = inf;
pS.lo[t,s,n]$(P_output[s,n]) = -inf;
pS.up[t,s,n]$(P_output[s,n]) = inf;
p.lo[t,n]$(((P_endoP[n] and tx0[t]) or (P_endoP[n] and t0[t]))) = -inf;
p.up[t,n]$(((P_endoP[n] and tx0[t]) or (P_endoP[n] and t0[t]))) = inf;
qD.lo[t,s,n]$(((P_int[s,n] or (P_input[s,n] and tx0[t]) or (P_dur[s,n] and tx0[t])) or (P_input[s,n] and t0[t]))) = -inf;
qD.up[t,s,n]$(((P_int[s,n] or (P_input[s,n] and tx0[t]) or (P_dur[s,n] and tx0[t])) or (P_input[s,n] and t0[t]))) = inf;
TotalTax.lo[t,s]$(((P_sm[s] and tx0E[t]) or (P_sm[s] and t0[t]))) = -inf;
TotalTax.up[t,s]$(((P_sm[s] and tx0E[t]) or (P_sm[s] and t0[t]))) = inf;
vA.lo[t,s]$(P_sm[s]) = -inf;
vA.up[t,s]$(P_sm[s]) = inf;
divd.lo[t,s]$(P_sm[s]) = -inf;
divd.up[t,s]$(P_sm[s]) = inf;
adjCost.lo[t,s]$((P_sm[s] and txE[t])) = -inf;
adjCost.up[t,s]$((P_sm[s] and txE[t])) = inf;
pD.lo[t,s,n]$((I_int[s,n] or I_input[s,n])) = -inf;
pD.up[t,s,n]$((I_int[s,n] or I_input[s,n])) = inf;
pS.lo[t,s,n]$(I_output[s,n]) = -inf;
pS.up[t,s,n]$(I_output[s,n]) = inf;
p.lo[t,n]$(((I_endoP[n] and tx0[t]) or (I_endoP[n] and t0[t]))) = -inf;
p.up[t,n]$(((I_endoP[n] and tx0[t]) or (I_endoP[n] and t0[t]))) = inf;
qD.lo[t,s,n]$(((I_int[s,n] or (I_input[s,n] and tx0[t])) or (I_input[s,n] and t0[t]))) = -inf;
qD.up[t,s,n]$(((I_int[s,n] or (I_input[s,n] and tx0[t])) or (I_input[s,n] and t0[t]))) = inf;
TotalTax.lo[t,s]$(((I_sm[s] and tx0E[t]) or (I_sm[s] and t0[t]))) = -inf;
TotalTax.up[t,s]$(((I_sm[s] and tx0E[t]) or (I_sm[s] and t0[t]))) = inf;
vA.lo[t,s]$(I_sm[s]) = -inf;
vA.up[t,s]$(I_sm[s]) = inf;
divd.lo[t,s]$(I_sm[s]) = -inf;
divd.up[t,s]$(I_sm[s]) = inf;
pD.lo[t,s,n]$((((HH_int[s,n] or HH_input[s,n]) or (HH_C[s,n] and tx0E[t])) or (HH_C[s,n] and t0[t]))) = -inf;
pD.up[t,s,n]$((((HH_int[s,n] or HH_input[s,n]) or (HH_C[s,n] and tx0E[t])) or (HH_C[s,n] and t0[t]))) = inf;
qD.lo[t,s,n]$((((HH_input[s,n] and tx0E[t]) or (HH_int[s,n] or HH_output[s,n])) or (HH_input[s,n] and t0[t]))) = -inf;
qD.up[t,s,n]$((((HH_input[s,n] and tx0E[t]) or (HH_int[s,n] or HH_output[s,n])) or (HH_input[s,n] and t0[t]))) = inf;
pS.lo[t,s,n]$((HH_L[s,n] and txE[t])) = -inf;
pS.up[t,s,n]$((HH_L[s,n] and txE[t])) = inf;
vU.lo[t,s]$(HH_sm[s]) = -inf;
vU.up[t,s]$(HH_sm[s]) = inf;
TotalTax.lo[t,s]$(((HH_sm[s] and tx0E[t]) or (HH_sm[s] and t0[t]))) = -inf;
TotalTax.up[t,s]$(((HH_sm[s] and tx0E[t]) or (HH_sm[s] and t0[t]))) = inf;
pD.lo[t,s,n]$((((G_int[s,n] or G_input[s,n]) or (G_output[s,n] and tx0E[t])) or (G_output[s,n] and t0[t]))) = -inf;
pD.up[t,s,n]$((((G_int[s,n] or G_input[s,n]) or (G_output[s,n] and tx0E[t])) or (G_output[s,n] and t0[t]))) = inf;
qD.lo[t,s,n]$((((G_input[s,n] and tx0E[t]) or G_int[s,n]) or (G_input[s,n] and t0[t]))) = -inf;
qD.up[t,s,n]$((((G_input[s,n] and tx0E[t]) or G_int[s,n]) or (G_input[s,n] and t0[t]))) = inf;
TotalTax.lo[t,s]$(((G_sm[s] and tx0E[t]) or (G_sm[s] and t0[t]))) = -inf;
TotalTax.up[t,s]$(((G_sm[s] and tx0E[t]) or (G_sm[s] and t0[t]))) = inf;
tauLump.lo[t,s]$(((tx0E[t] and s_HH[s]) or (t0[t] and s_HH[s]))) = -inf;
tauLump.up[t,s]$(((tx0E[t] and s_HH[s]) or (t0[t] and s_HH[s]))) = inf;
qD.lo[t,s,n]$(((T_dExport[s,n] and tx0E[t]) or (T_dExport[s,n] and t0[t]))) = -inf;
qD.up[t,s,n]$(((T_dExport[s,n] and tx0E[t]) or (T_dExport[s,n] and t0[t]))) = inf;
TotalTax.lo[t,s]$(((T_sm[s] and tx0E[t]) or (T_sm[s] and t0[t]))) = -inf;
TotalTax.up[t,s]$(((T_sm[s] and tx0E[t]) or (T_sm[s] and t0[t]))) = inf;
pD.lo[t,s,n]$(T_dExport[s,n]) = -inf;
pD.up[t,s,n]$(T_dExport[s,n]) = inf;
qD.lo[t,s,n]$((dInventory[s,n] and tx0E[t])) = -inf;
qD.up[t,s,n]$((dInventory[s,n] and tx0E[t])) = inf;
qCO2.lo[t,s,n]$(((tx0E[t] and dqCO2[s,n]) or (t0[t] and dqCO2[s,n]))) = -inf;
qCO2.up[t,s,n]$(((tx0E[t] and dqCO2[s,n]) or (t0[t] and dqCO2[s,n]))) = inf;
qCO2agg.lo[t]$(txE[t]) = -inf;
qCO2agg.up[t]$(txE[t]) = inf;
tauCO2.lo[t,s,n]$(dtauCO2[s,n]) = -inf;
tauCO2.up[t,s,n]$(dtauCO2[s,n]) = inf;
tauEffCO2.lo[t,s,n]$(dtauCO2[s,n]) = -inf;
tauEffCO2.up[t,s,n]$(dtauCO2[s,n]) = inf;
qS.lo[t,s,n]$(((tx0E[t] and d_qSEqui[s,n]) or (t0[t] and d_qSEqui[s,n]))) = -inf;
qS.up[t,s,n]$(((tx0E[t] and d_qSEqui[s,n]) or (t0[t] and d_qSEqui[s,n]))) = inf;
p.lo[t,n]$(((tx0E[t] and d_pEqui[n]) or (t0[t] and d_pEqui[n]))) = -inf;
p.up[t,n]$(((tx0E[t] and d_pEqui[n]) or (t0[t] and d_pEqui[n]))) = inf;

# solve:
 solve M_vSmall_B using CNS;
