$ONEOLCOM
$EOLCOM #



;
OPTION SYSOUT=OFF, SOLPRINT=OFF, LIMROW=0, LIMCOL=0, DECIMALS=6;


# User defined functions:

# ----------------------------------------------------------------------------------------------------
#  Define function: SolveEmptyNLP
# ----------------------------------------------------------------------------------------------------


# DEFINE LOCAL FUNCTIONS/MACROS:
$MACRO stdNormPdf(x) exp(-sqr(x)/2)/(2*sqrt(Pi))
$MACRO EOP_Logit(p, c, e) (1/(1+exp((c-p)/e)))
$MACRO EOP_Normal(p, c, e) errorf((p-c)/e)
$MACRO EOP_NormalMult(p, c, e) errorf((p/c-1)/e)
$MACRO EOP_NormalCost(p, c, e) EOP_Normal(p, c, e)*c-e*stdNormPdf((p-c)/e)
$MACRO EOP_NormalMultCost(p, c, e) c*(EOP_NormalMult(p, c, e)-e*stdNormPdf((p/c-1)/e))


# ----------------------------------------------------------------------------------------------------
#  Define function: EOP_Tech
# ----------------------------------------------------------------------------------------------------



# ----------------------------------------------------------------------------------------------------
#  Define function: EOP_Cost
# ----------------------------------------------------------------------------------------------------




# DECLARE SYMBOLS FROM DATABASE:
sets
	alias_set
	alias_map2
	t
	s
	taxTypes
	n
	tech
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
	nestProduction[s,n,nn]
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
	I_output_n[n]
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
	G_L[s,n]
	G_input_n[n]
	G_sm[s]
	s_itory[s]
	d_itory[s,n]
	T_dExport[s,n]
	T_nF[n]
	T_nD[n]
	T_sm[s]
;

parameters
	R_LR
	infl_LR
	g_LR
	itoryAR[s,n]
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
	DACCost[t]
	techPot[tech,t]
	techCost[tech,t]
	uCO2[t,s,n]
	tauCO2agg[t]
	tauDist[t,s,n]
	qCO2agg[t]
	tauEffCO2[t,s,n]
	Rrate[t]
	mu[s,n,nn]
	pS[t,s,n]
	adjCostPar[s,n]
	K_tvc[s,n]
	adjCost[t,s]
	markup[s]
	vA[t,s]
	divd[t,s]
	taxRevPar[s]
	tauLump0[t,s]
	crra[s]
	Lscale[s]
	jTerm[s]
	tauD0[t,s,n]
	Fscale[s,n]
	uCO20[t,s,n]
	uAbate[t,s,n]
	uCO2Calib[s,n]
	DACSmooth[t]
	techSmooth[tech,t]
	qCO2Base
	tauCO2Base
	softConstr
	obj
;


# LOAD SYMBOLS FROM DATABASE:
$GDXIN vA_2019_solDB
$onMulti
$load alias_set
$load alias_map2
$load t
$load s
$load taxTypes
$load n
$load tech
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
$load nestProduction
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
$load I_output_n
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
$load G_L
$load G_input_n
$load G_sm
$load s_itory
$load d_itory
$load T_dExport
$load T_nF
$load T_nD
$load T_sm
$GDXIN
$offMulti;
$GDXIN vA_2019_solDB
$onMulti
$load R_LR
$load infl_LR
$load g_LR
$load itoryAR
$GDXIN
$offMulti;
$GDXIN vA_2019_solDB
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
$load DACCost
$load techPot
$load techCost
$load uCO2
$load tauCO2agg
$load tauDist
$load qCO2agg
$load tauEffCO2
$load Rrate
$load mu
$load pS
$load adjCostPar
$load K_tvc
$load adjCost
$load markup
$load vA
$load divd
$load taxRevPar
$load tauLump0
$load crra
$load Lscale
$load jTerm
$load tauD0
$load Fscale
$load uCO20
$load uAbate
$load uCO2Calib
$load DACSmooth
$load techSmooth
$load qCO2Base
$load tauCO2Base
$load softConstr
$load obj
$GDXIN
$offMulti;


# WRITE INIT STATEMENTS FROM MODULES:









# WRITE BLOCKS OF EQUATIONS:


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
E_P_pWedge_pwInp[t,s,n]$(p_input[s,n] and txe[t]).. 					pD[t,s,n]		 =E=  p[t,n]+tauD[t,s,n];
EQUATION E_P_pWedge_pwOut[t,s,n];
E_P_pWedge_pwOut[t,s,n]$(p_output[s,n] and txe[t]).. 				p[t,n] 			 =E=  (1+markup[s])*(pS[t,s,n]+(tauEffCO2[t,s,n]*uCO2[t,s,n])$(dqCO2[s,n])+tauS[t,s,n]);
EQUATION E_P_pWedge_taxRev[t,s];
E_P_pWedge_taxRev[t,s]$(p_sm[s] and txe[t]).. 						TotalTax[t,s]	 =E=  tauLump[t,s]+sum(n$(P_input[s,n]), tauD[t,s,n] * qD[t,s,n])+sum(n$(P_output[s,n]), tauS[t,s,n]*qS[t,s,n]+(tauCO2[t,s,n]*qCO2[t,s,n])$(dqCO2[s,n]));

# ----------------------------------------------------------------------------------------------------
#  Define B_P_pWedge model
# ----------------------------------------------------------------------------------------------------
Model B_P_pWedge /
E_P_pWedge_pwInp, E_P_pWedge_pwOut, E_P_pWedge_taxRev
/;



# --------------------------------------------B_P_firmValue-------------------------------------------
#  Initialize B_P_firmValue equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_P_firmValue_vA[t,s];
E_P_firmValue_vA[t,s]$(p_sm[s] and tx2e[t]).. 		vA[t,s]  =E=  (divd[t+1,s]+vA[t+1,s])/(Rrate[t+1]*(1+g_LR)*(1+infl_LR));
EQUATION E_P_firmValue_divd[t,s];
E_P_firmValue_divd[t,s]$(p_sm[s] and txe[t]).. 		divd[t,s]  =E=  sum(n$(P_output[s,n]), p[t,n] * qS[t,s,n])-sum(n$(P_input[s,n]), p[t,n] * qD[t,s,n])-adjCost[t,s]-TotalTax[t,s];
EQUATION E_P_firmValue_vAT[t,s];
E_P_firmValue_vAT[t,s]$(p_sm[s] and t2e[t]).. 		vA[t,s]	   =E=  divd[t,s]/(R_LR-1);

# ----------------------------------------------------------------------------------------------------
#  Define B_P_firmValue model
# ----------------------------------------------------------------------------------------------------
Model B_P_firmValue /
E_P_firmValue_vA, E_P_firmValue_divd, E_P_firmValue_vAT
/;



# --------------------------------------------B_P_taxCalib--------------------------------------------
#  Initialize B_P_taxCalib equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_P_taxCalib_taxCal[t,s];
E_P_taxCalib_taxCal[t,s]$(p_sm[s]).. 	tauLump[t,s]  =E=  tauLump0[t,s]+taxRevPar[s];

# ----------------------------------------------------------------------------------------------------
#  Define B_P_taxCalib model
# ----------------------------------------------------------------------------------------------------
Model B_P_taxCalib /
E_P_taxCalib_taxCal
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



# ---------------------------------------------B_I_pWedge---------------------------------------------
#  Initialize B_I_pWedge equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_I_pWedge_pwInp[t,s,n];
E_I_pWedge_pwInp[t,s,n]$(i_input[s,n] and txe[t]).. 			pD[t,s,n]		 =E=  p[t,n]+tauD[t,s,n];
EQUATION E_I_pWedge_pwOut[t,s,n];
E_I_pWedge_pwOut[t,s,n]$(i_output[s,n] and txe[t]).. 		p[t,n] 			 =E=  (1+markup[s])*(pS[t,s,n]+tauS[t,s,n]);
EQUATION E_I_pWedge_taxRev[t,s];
E_I_pWedge_taxRev[t,s]$(i_sm[s] and txe[t]).. 				TotalTax[t,s]	 =E=  tauLump[t,s]+sum(n$(I_input[s,n]), tauD[t,s,n] * qD[t,s,n])+sum(n$(I_output[s,n]), tauS[t,s,n]*qS[t,s,n]);

# ----------------------------------------------------------------------------------------------------
#  Define B_I_pWedge model
# ----------------------------------------------------------------------------------------------------
Model B_I_pWedge /
E_I_pWedge_pwInp, E_I_pWedge_pwOut, E_I_pWedge_taxRev
/;



# --------------------------------------------B_I_taxCalib--------------------------------------------
#  Initialize B_I_taxCalib equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_I_taxCalib_taxCal[t,s];
E_I_taxCalib_taxCal[t,s]$(i_sm[s]).. 	tauLump[t,s]  =E=  tauLump0[t,s]+taxRevPar[s];

# ----------------------------------------------------------------------------------------------------
#  Define B_I_taxCalib model
# ----------------------------------------------------------------------------------------------------
Model B_I_taxCalib /
E_I_taxCalib_taxCal
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



# -------------------------------------------B_HH_isoFrisch-------------------------------------------
#  Initialize B_HH_isoFrisch equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_HH_isoFrisch_labor[t,s,n];
E_HH_isoFrisch_labor[t,s,n]$(hh_l[s,n] and txe[t]).. 	qS[t,s,n]	 =E= 	Lscale[s] * sum(nn$(HH_L2C[s,n,nn]), pS[t,s,n]/pD[t,s,nn])**(frisch[s]);

# ----------------------------------------------------------------------------------------------------
#  Define B_HH_isoFrisch model
# ----------------------------------------------------------------------------------------------------
Model B_HH_isoFrisch /
E_HH_isoFrisch_labor
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
E_HH_pWedge_sp[t,s]$(hh_sm[s] and txe[t]).. 			jTerm[s]		 =E=  sum(n$(HH_L[s,n]), pS[t,s,n]*qS[t,s,n]) - sum(n$(HH_input[s,n]), pD[t,s,n]*qD[t,s,n])-tauLump[t,s];

# ----------------------------------------------------------------------------------------------------
#  Define B_HH_pWedge model
# ----------------------------------------------------------------------------------------------------
Model B_HH_pWedge /
E_HH_pWedge_pwOut, E_HH_pWedge_pwInp, E_HH_pWedge_TaxRev, E_HH_pWedge_sp
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



# -----------------------------------------------B_G_bb-----------------------------------------------
#  Initialize B_G_bb equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_G_bb_pw[t,s,n];
E_G_bb_pw[t,s,n]$(g_input[s,n] and txe[t]).. 	pD[t,s,n]	 =E=  p[t,n]+tauD[t,s,n];
EQUATION E_G_bb_taxRev[t,s];
E_G_bb_taxRev[t,s]$(g_sm[s] and txe[t]).. 	TotalTax[t,s]	 =E=  sum(n$(G_input[s,n]), tauD[t,s,n] * qD[t,s,n]);
EQUATION E_G_bb_bb[t,s];
E_G_bb_bb[t,s]$(g_sm[s] and txe[t]).. 			jTerm[s]	 =E=  sum(ss$(d_TotalTax[ss]), TotalTax[t,ss])-sum(n$(G_input[s,n]), pD[t,s,n]*qD[t,s,n]);

# ----------------------------------------------------------------------------------------------------
#  Define B_G_bb model
# ----------------------------------------------------------------------------------------------------
Model B_G_bb /
E_G_bb_pw, E_G_bb_taxRev, E_G_bb_bb
/;



# --------------------------------------------B_G_taxCalib--------------------------------------------
#  Initialize B_G_taxCalib equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_G_taxCalib_taxCal[t,s,n];
E_G_taxCalib_taxCal[t,s,n]$(g_input[s,n] and txe[t]).. 	tauD[t,s,n]	 =E=  tauD0[t,s,n]*(1+taxRevPar[s]);

# ----------------------------------------------------------------------------------------------------
#  Define B_G_taxCalib model
# ----------------------------------------------------------------------------------------------------
Model B_G_taxCalib /
E_G_taxCalib_taxCal
/;




# -----------------------------------------------B_Itory----------------------------------------------
#  Initialize B_Itory equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_Itory[t,s,n];
E_Itory[t,s,n]$(d_itory[s,n] and tx0e[t]).. 	qD[t,s,n]  =E=  itoryAR[s,n] * qD[t-1,s,n];

# ----------------------------------------------------------------------------------------------------
#  Define B_Itory model
# ----------------------------------------------------------------------------------------------------
Model B_Itory /
E_Itory
/;




# -------------------------------------------------B_T------------------------------------------------
#  Initialize B_T equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_T_armington[t,s,n];
E_T_armington[t,s,n]$(t_dexport[s,n] and txe[t]).. 	qD[t,s,n]		 =E=  sum(nn$(dom2for[n,nn]), Fscale[s,n] * (p[t,nn]/pD[t,s,n])**(sigma[s,n]));
EQUATION E_T_pwInp[t,s,n];
E_T_pwInp[t,s,n]$(t_dexport[s,n] and txe[t]).. 		pD[t,s,n]		 =E=  p[t,n] + tauD[t,s,n];
EQUATION E_T_TaxRev[t,s];
E_T_TaxRev[t,s]$(t_sm[s] and txe[t]).. 				TotalTax[t,s]	 =E=  tauLump[t,s]+sum(n$(T_dExport[s,n]), tauD[t,s,n]*qD[t,s,n]);

# ----------------------------------------------------------------------------------------------------
#  Define B_T model
# ----------------------------------------------------------------------------------------------------
Model B_T /
E_T_armington, E_T_pwInp, E_T_TaxRev
/;




# -------------------------------------------------B_M------------------------------------------------
#  Initialize B_M equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_uAbate[t,s,n];
E_uAbate[t,s,n]$(dqco2[s,n] and txe[t]).. 		uAbate[t,s,n]		 =E=  sum(tech, techPot[tech,t] * 



 EOP_Normal( (tauCO2[t,s,n]), (techCost[tech,t]), (techSmooth[tech,t]) ) 




	








	








);
EQUATION E_tauCO2Eff[t,s,n];
E_tauCO2Eff[t,s,n]$(dtauco2[s,n] and txe[t]).. 	tauEffCO2[t,s,n]	 =E=  tauCO2[t,s,n]*(1-uAbate[t,s,n])+sum(tech, techPot[tech,t] * 



 EOP_NormalCost( (tauCO2[t,s,n]), (techCost[tech,t]), (techSmooth[tech,t]) ) 




	








);
EQUATION E_tauCO2[t,s,n];
E_tauCO2[t,s,n]$(dtauco2[s,n] and txe[t]).. 		tauCO2[t,s,n]		 =E=  tauCO2agg[t] * tauDist[t,s,n];
EQUATION E_qCO2[t,s,n];
E_qCO2[t,s,n]$(dqco2[s,n] and txe[t]).. 			qCO2[t,s,n]			 =E=  uCO2[t,s,n] * (1-uAbate[t,s,n]) * qS[t,s,n];
EQUATION E_qCO2agg[t];
E_qCO2agg[t]$(txe[t]).. 							qCO2agg[t]			 =E=  sum([s,n]$(dqCO2[s,n]), qCO2[t,s,n])-qCO2Base * 



 EOP_Normal( (tauCO2agg[t]), (DACCost[t]), (DACSmooth[t]) ) 




	








	








;

# ----------------------------------------------------------------------------------------------------
#  Define B_M model
# ----------------------------------------------------------------------------------------------------
Model B_M /
E_uAbate, E_tauCO2Eff, E_tauCO2, E_qCO2, E_qCO2agg
/;



# ----------------------------------------------B_M_calib---------------------------------------------
#  Initialize B_M_calib equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_qCO2calib[t,s,n];
E_qCO2calib[t,s,n]$(dqco2[s,n] and txe[t]).. 	uCO2[t,s,n]	 =E=  uCO20[t,s,n] * (1+uCO2calib[s,n]);

# ----------------------------------------------------------------------------------------------------
#  Define B_M_calib model
# ----------------------------------------------------------------------------------------------------
Model B_M_calib /
E_qCO2calib
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
#  Define M_vA_2019_CGE_B model
# ----------------------------------------------------------------------------------------------------
Model M_vA_2019_CGE_B /
E_W_zpOut, E_W_zpNOut, E_W_qOut, E_W_qNOut, E_O_zpOut, E_O_zpNOut, E_O_qOut, E_O_qNOut, E_P_adjCost_lom, E_P_adjCost_pk, E_P_adjCost_pkT, E_P_adjCost_K_tvc, E_P_adjCost_adjCost, E_P_pWedge_pwInp, E_P_pWedge_pwOut, E_P_pWedge_taxRev, E_P_firmValue_vA, E_P_firmValue_divd, E_P_firmValue_vAT, E_I_zpOut, E_I_zpNOut, E_I_qOut, E_I_qNOut, E_I_pWedge_pwInp, E_I_pWedge_pwOut, E_I_pWedge_taxRev, E_HH_zp, E_HH_q, E_HH_isoFrisch_labor, E_HH_pWedge_pwOut, E_HH_pWedge_pwInp, E_HH_pWedge_TaxRev, E_HH_pWedge_sp, E_G_zp, E_G_q, E_G_bb_pw, E_G_bb_taxRev, E_G_bb_bb, E_G_taxCalib_taxCal, E_Itory, E_T_armington, E_T_pwInp, E_T_TaxRev, E_uAbate, E_tauCO2Eff, E_tauCO2, E_qCO2, E_qCO2agg, E_Equi_equi
/;


# ----------------------------------------------------------------------------------------------------
#  Define M_vA_2019_CGE_C model
# ----------------------------------------------------------------------------------------------------
Model M_vA_2019_CGE_C /
E_W_zpOut, E_W_zpNOut, E_W_qOut, E_W_qNOut, E_O_zpOut, E_O_zpNOut, E_O_qOut, E_O_qNOut, E_P_adjCost_lom, E_P_adjCost_pk, E_P_adjCost_pkT, E_P_adjCost_K_tvc, E_P_adjCost_adjCost, E_P_pWedge_pwInp, E_P_pWedge_pwOut, E_P_pWedge_taxRev, E_P_firmValue_vA, E_P_firmValue_divd, E_P_firmValue_vAT, E_P_taxCalib_taxCal, E_I_zpOut, E_I_zpNOut, E_I_qOut, E_I_qNOut, E_I_pWedge_pwInp, E_I_pWedge_pwOut, E_I_pWedge_taxRev, E_I_taxCalib_taxCal, E_HH_zp, E_HH_q, E_HH_isoFrisch_labor, E_HH_pWedge_pwOut, E_HH_pWedge_pwInp, E_HH_pWedge_TaxRev, E_HH_pWedge_sp, E_G_zp, E_G_q, E_G_bb_pw, E_G_bb_taxRev, E_G_bb_bb, E_G_taxCalib_taxCal, E_Itory, E_T_armington, E_T_pwInp, E_T_TaxRev, E_uAbate, E_tauCO2Eff, E_tauCO2, E_qCO2, E_qCO2agg, E_qCO2calib, E_Equi_equi_tx0E
/;
;

# Fix exogenous variables in state:
sigma.fx[s,n]$(P_kninp[s,n]) = sigma.l[s,n]$(P_kninp[s,n]);
mu.fx[s,n,nn]$((P_map[s,n,nn] or P_endoMu[s,n,nn])) = mu.l[s,n,nn]$((P_map[s,n,nn] or P_endoMu[s,n,nn]));
rDepr.fx[t,s,n]$(P_dur[s,n]) = rDepr.l[t,s,n]$(P_dur[s,n]);
adjCostPar.fx[s,n]$(P_dur[s,n]) = adjCostPar.l[s,n]$(P_dur[s,n]);
K_tvc.fx[s,n]$(P_dur[s,n]) = K_tvc.l[s,n]$(P_dur[s,n]);
tauD.fx[t,s,n]$(P_input[s,n]) = tauD.l[t,s,n]$(P_input[s,n]);
tauS.fx[t,s,n]$(P_output[s,n]) = tauS.l[t,s,n]$(P_output[s,n]);
tauCO2.fx[t,s,n]$((P_output[s,n] and dqCO2[s,n])) = tauCO2.l[t,s,n]$((P_output[s,n] and dqCO2[s,n]));
qD.fx[t,s,n]$((P_dur[s,n] and t0[t])) = qD.l[t,s,n]$((P_dur[s,n] and t0[t]));
tauLump0.fx[t,s]$(P_sm[s]) = tauLump0.l[t,s]$(P_sm[s]);
qS.fx[t,s,n]$(P_output[s,n]) = qS.l[t,s,n]$(P_output[s,n]);
p.fx[t,n]$((P_input_n[n] and ( not (P_output_n[n])))) = p.l[t,n]$((P_input_n[n] and ( not (P_output_n[n]))));
qCO2.fx[t,s,n]$((P_output[s,n] and dqCO2[s,n])) = qCO2.l[t,s,n]$((P_output[s,n] and dqCO2[s,n]));
uCO2.fx[t,s,n]$((P_output[s,n] and dqCO2[s,n])) = uCO2.l[t,s,n]$((P_output[s,n] and dqCO2[s,n]));
tauEffCO2.fx[t,s,n]$((P_output[s,n] and dqCO2[s,n])) = tauEffCO2.l[t,s,n]$((P_output[s,n] and dqCO2[s,n]));
Rrate.fx[t] = Rrate.l[t];
markup.fx[s]$(P_sm[s]) = markup.l[s]$(P_sm[s]);
taxRevPar.fx[s]$(P_sm[s]) = taxRevPar.l[s]$(P_sm[s]);
tauLump.fx[t,s]$(P_sm[s]) = tauLump.l[t,s]$(P_sm[s]);
sigma.fx[s,n]$(I_kninp[s,n]) = sigma.l[s,n]$(I_kninp[s,n]);
mu.fx[s,n,nn]$((I_map[s,n,nn] or I_endoMu[s,n,nn])) = mu.l[s,n,nn]$((I_map[s,n,nn] or I_endoMu[s,n,nn]));
tauD.fx[t,s,n]$(I_input[s,n]) = tauD.l[t,s,n]$(I_input[s,n]);
tauS.fx[t,s,n]$(I_output[s,n]) = tauS.l[t,s,n]$(I_output[s,n]);
tauLump0.fx[t,s]$(I_sm[s]) = tauLump0.l[t,s]$(I_sm[s]);
qS.fx[t,s,n]$(I_output[s,n]) = qS.l[t,s,n]$(I_output[s,n]);
p.fx[t,n]$((I_input_n[n] and ( not (I_output_n[n])))) = p.l[t,n]$((I_input_n[n] and ( not (I_output_n[n]))));
Rrate.fx[t] = Rrate.l[t];
markup.fx[s]$(I_sm[s]) = markup.l[s]$(I_sm[s]);
taxRevPar.fx[s]$(I_sm[s]) = taxRevPar.l[s]$(I_sm[s]);
tauLump.fx[t,s]$(I_sm[s]) = tauLump.l[t,s]$(I_sm[s]);
sigma.fx[s,n]$(HH_kninp[s,n]) = sigma.l[s,n]$(HH_kninp[s,n]);
mu.fx[s,n,nn]$(((HH_map[s,n,nn] and ( not (HH_endoMu[s,n,nn]))) or HH_endoMu[s,n,nn])) = mu.l[s,n,nn]$(((HH_map[s,n,nn] and ( not (HH_endoMu[s,n,nn]))) or HH_endoMu[s,n,nn]));
frisch.fx[s]$(HH_sm[s]) = frisch.l[s]$(HH_sm[s]);
crra.fx[s]$(HH_sm[s]) = crra.l[s]$(HH_sm[s]);
tauD.fx[t,s,n]$(HH_input[s,n]) = tauD.l[t,s,n]$(HH_input[s,n]);
tauS.fx[t,s,n]$(HH_L[s,n]) = tauS.l[t,s,n]$(HH_L[s,n]);
tauLump.fx[t,s]$(((HH_sm[s] and tx0E[t]) or (HH_sm[s] and t0[t]))) = tauLump.l[t,s]$(((HH_sm[s] and tx0E[t]) or (HH_sm[s] and t0[t])));
p.fx[t,n]$((HH_output_n[n] or HH_input_n[n])) = p.l[t,n]$((HH_output_n[n] or HH_input_n[n]));
Lscale.fx[s]$(HH_sm[s]) = Lscale.l[s]$(HH_sm[s]);
jTerm.fx[s]$(HH_sm[s]) = jTerm.l[s]$(HH_sm[s]);
sigma.fx[s,n]$(G_kninp[s,n]) = sigma.l[s,n]$(G_kninp[s,n]);
mu.fx[s,n,nn]$(((G_map[s,n,nn] and ( not (G_endoMu[s,n,nn]))) or G_endoMu[s,n,nn])) = mu.l[s,n,nn]$(((G_map[s,n,nn] and ( not (G_endoMu[s,n,nn]))) or G_endoMu[s,n,nn]));
tauD0.fx[t,s,n]$(G_input[s,n]) = tauD0.l[t,s,n]$(G_input[s,n]);
qD.fx[t,s,n]$(G_output[s,n]) = qD.l[t,s,n]$(G_output[s,n]);
taxRevPar.fx[s]$(G_sm[s]) = taxRevPar.l[s]$(G_sm[s]);
jTerm.fx[s]$(G_sm[s]) = jTerm.l[s]$(G_sm[s]);
qD.fx[t,s,n]$((d_itory[s,n] and t0[t])) = qD.l[t,s,n]$((d_itory[s,n] and t0[t]));
p.fx[t,n]$((T_nF[n] or T_nD[n])) = p.l[t,n]$((T_nF[n] or T_nD[n]));
sigma.fx[s,n]$(T_dExport[s,n]) = sigma.l[s,n]$(T_dExport[s,n]);
tauD.fx[t,s,n]$(T_dExport[s,n]) = tauD.l[t,s,n]$(T_dExport[s,n]);
tauLump.fx[t,s]$(((T_sm[s] and tx0E[t]) or (T_sm[s] and t0[t]))) = tauLump.l[t,s]$(((T_sm[s] and tx0E[t]) or (T_sm[s] and t0[t])));
Fscale.fx[s,n]$(T_dExport[s,n]) = Fscale.l[s,n]$(T_dExport[s,n]);
techPot.fx[tech,t] = techPot.l[tech,t];
techCost.fx[tech,t] = techCost.l[tech,t];
techSmooth.fx[tech,t] = techSmooth.l[tech,t];
DACCost.fx[t] = DACCost.l[t];
DACSmooth.fx[t] = DACSmooth.l[t];
tauCO2Base.fx = tauCO2Base.l;
softConstr.fx = softConstr.l;
qCO2Base.fx = qCO2Base.l;
tauCO2agg.fx[t] = tauCO2agg.l[t];
tauDist.fx[t,s,n]$(dtauCO2[s,n]) = tauDist.l[t,s,n]$(dtauCO2[s,n]);
uCO20.fx[t,s,n]$(dqCO2[s,n]) = uCO20.l[t,s,n]$(dqCO2[s,n]);
qS.fx[t,s,n]$(d_qS[s,n]) = qS.l[t,s,n]$(d_qS[s,n]);
uCO2Calib.fx[s,n]$(dqCO2[s,n]) = uCO2Calib.l[s,n]$(dqCO2[s,n]);
uCO2.fx[t,s,n]$(dqCO2[s,n]) = uCO2.l[t,s,n]$(dqCO2[s,n]);
Rrate.fx[t] = Rrate.l[t];

# Unfix endogenous variables in state:
pD.lo[t,s,n]$(((P_int[s,n] or P_input[s,n]) or (P_dur[s,n] and txE[t]))) = -inf;
pD.up[t,s,n]$(((P_int[s,n] or P_input[s,n]) or (P_dur[s,n] and txE[t]))) = inf;
pS.lo[t,s,n]$(P_output[s,n]) = -inf;
pS.up[t,s,n]$(P_output[s,n]) = inf;
p.lo[t,n]$(((P_output_n[n] and tx0[t]) or (P_output_n[n] and t0[t]))) = -inf;
p.up[t,n]$(((P_output_n[n] and tx0[t]) or (P_output_n[n] and t0[t]))) = inf;
qD.lo[t,s,n]$(((P_int[s,n] or (P_input[s,n] and tx0[t]) or (P_dur[s,n] and tx0[t])) or (P_input[s,n] and t0[t]))) = -inf;
qD.up[t,s,n]$(((P_int[s,n] or (P_input[s,n] and tx0[t]) or (P_dur[s,n] and tx0[t])) or (P_input[s,n] and t0[t]))) = inf;
adjCost.lo[t,s]$((P_sm[s] and txE[t])) = -inf;
adjCost.up[t,s]$((P_sm[s] and txE[t])) = inf;
TotalTax.lo[t,s]$(((P_sm[s] and tx0E[t]) or (P_sm[s] and t0[t]))) = -inf;
TotalTax.up[t,s]$(((P_sm[s] and tx0E[t]) or (P_sm[s] and t0[t]))) = inf;
vA.lo[t,s]$(P_sm[s]) = -inf;
vA.up[t,s]$(P_sm[s]) = inf;
divd.lo[t,s]$(P_sm[s]) = -inf;
divd.up[t,s]$(P_sm[s]) = inf;
pD.lo[t,s,n]$((I_int[s,n] or I_input[s,n])) = -inf;
pD.up[t,s,n]$((I_int[s,n] or I_input[s,n])) = inf;
pS.lo[t,s,n]$(I_output[s,n]) = -inf;
pS.up[t,s,n]$(I_output[s,n]) = inf;
p.lo[t,n]$(((I_output_n[n] and tx0[t]) or (I_output_n[n] and t0[t]))) = -inf;
p.up[t,n]$(((I_output_n[n] and tx0[t]) or (I_output_n[n] and t0[t]))) = inf;
qD.lo[t,s,n]$(((I_int[s,n] or (I_input[s,n] and tx0[t])) or (I_input[s,n] and t0[t]))) = -inf;
qD.up[t,s,n]$(((I_int[s,n] or (I_input[s,n] and tx0[t])) or (I_input[s,n] and t0[t]))) = inf;
TotalTax.lo[t,s]$(((I_sm[s] and tx0E[t]) or (I_sm[s] and t0[t]))) = -inf;
TotalTax.up[t,s]$(((I_sm[s] and tx0E[t]) or (I_sm[s] and t0[t]))) = inf;
pD.lo[t,s,n]$((((HH_int[s,n] or HH_input[s,n]) or (HH_output[s,n] and tx0E[t])) or (HH_output[s,n] and t0[t]))) = -inf;
pD.up[t,s,n]$((((HH_int[s,n] or HH_input[s,n]) or (HH_output[s,n] and tx0E[t])) or (HH_output[s,n] and t0[t]))) = inf;
qS.lo[t,s,n]$(((HH_L[s,n] and tx0E[t]) or (HH_L[s,n] and t0[t]))) = -inf;
qS.up[t,s,n]$(((HH_L[s,n] and tx0E[t]) or (HH_L[s,n] and t0[t]))) = inf;
qD.lo[t,s,n]$((((HH_input[s,n] and tx0E[t]) or (HH_int[s,n] or HH_output[s,n])) or (HH_input[s,n] and t0[t]))) = -inf;
qD.up[t,s,n]$((((HH_input[s,n] and tx0E[t]) or (HH_int[s,n] or HH_output[s,n])) or (HH_input[s,n] and t0[t]))) = inf;
pS.lo[t,s,n]$((HH_L[s,n] and txE[t])) = -inf;
pS.up[t,s,n]$((HH_L[s,n] and txE[t])) = inf;
TotalTax.lo[t,s]$(((HH_sm[s] and tx0E[t]) or (HH_sm[s] and t0[t]))) = -inf;
TotalTax.up[t,s]$(((HH_sm[s] and tx0E[t]) or (HH_sm[s] and t0[t]))) = inf;
pD.lo[t,s,n]$((G_int[s,n] or G_input[s,n] or G_output[s,n])) = -inf;
pD.up[t,s,n]$((G_int[s,n] or G_input[s,n] or G_output[s,n])) = inf;
qD.lo[t,s,n]$((((G_input[s,n] and tx0E[t]) or G_int[s,n]) or (G_input[s,n] and t0[t]))) = -inf;
qD.up[t,s,n]$((((G_input[s,n] and tx0E[t]) or G_int[s,n]) or (G_input[s,n] and t0[t]))) = inf;
tauD.lo[t,s,n]$(G_input[s,n]) = -inf;
tauD.up[t,s,n]$(G_input[s,n]) = inf;
TotalTax.lo[t,s]$(((G_sm[s] and tx0E[t]) or (G_sm[s] and t0[t]))) = -inf;
TotalTax.up[t,s]$(((G_sm[s] and tx0E[t]) or (G_sm[s] and t0[t]))) = inf;
tauLump.lo[t,s]$(((s_HH[s] and tx0E[t]) or (s_HH[s] and t0[t]))) = -inf;
tauLump.up[t,s]$(((s_HH[s] and tx0E[t]) or (s_HH[s] and t0[t]))) = inf;
qD.lo[t,s,n]$((d_itory[s,n] and tx0E[t])) = -inf;
qD.up[t,s,n]$((d_itory[s,n] and tx0E[t])) = inf;
qD.lo[t,s,n]$(((T_dExport[s,n] and tx0E[t]) or (T_dExport[s,n] and t0[t]))) = -inf;
qD.up[t,s,n]$(((T_dExport[s,n] and tx0E[t]) or (T_dExport[s,n] and t0[t]))) = inf;
TotalTax.lo[t,s]$(((T_sm[s] and tx0E[t]) or (T_sm[s] and t0[t]))) = -inf;
TotalTax.up[t,s]$(((T_sm[s] and tx0E[t]) or (T_sm[s] and t0[t]))) = inf;
pD.lo[t,s,n]$(T_dExport[s,n]) = -inf;
pD.up[t,s,n]$(T_dExport[s,n]) = inf;
qCO2.lo[t,s,n]$(((tx0E[t] and dqCO2[s,n]) or (t0[t] and dqCO2[s,n]))) = -inf;
qCO2.up[t,s,n]$(((tx0E[t] and dqCO2[s,n]) or (t0[t] and dqCO2[s,n]))) = inf;
qCO2agg.lo[t]$(txE[t]) = -inf;
qCO2agg.up[t]$(txE[t]) = inf;
tauCO2.lo[t,s,n]$(dtauCO2[s,n]) = -inf;
tauCO2.up[t,s,n]$(dtauCO2[s,n]) = inf;
tauEffCO2.lo[t,s,n]$(dtauCO2[s,n]) = -inf;
tauEffCO2.up[t,s,n]$(dtauCO2[s,n]) = inf;
uAbate.lo[t,s,n]$(dqCO2[s,n]) = -inf;
uAbate.up[t,s,n]$(dqCO2[s,n]) = inf;
qS.lo[t,s,n]$(((tx0E[t] and d_qSEqui[s,n]) or (t0[t] and d_qSEqui[s,n]))) = -inf;
qS.up[t,s,n]$(((tx0E[t] and d_qSEqui[s,n]) or (t0[t] and d_qSEqui[s,n]))) = inf;
p.lo[t,n]$(((tx0E[t] and d_pEqui[n]) or (t0[t] and d_pEqui[n]))) = -inf;
p.up[t,n]$(((tx0E[t] and d_pEqui[n]) or (t0[t] and d_pEqui[n]))) = inf;

# solve:
 solve M_vA_2019_CGE_B using CNS;
