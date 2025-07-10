$ONEOLCOM
$EOLCOM #



;
OPTION SYSOUT=OFF, SOLPRINT=OFF, LIMROW=0, LIMCOL=0, DECIMALS=6;


# User defined functions:

# ----------------------------------------------------------------------------------------------------
#  Define function: SolveEmptyNLP
# ----------------------------------------------------------------------------------------------------


# DEFINE LOCAL FUNCTIONS/MACROS:
$MACRO IntApprox(l,u,s,x) (l+sqrt(sqr(x-l)+s)+u-sqrt(sqr(x-u)+s))/2
$MACRO RC_Power_ua(l, u, e, r) (l+(u-l)*(1-r**(e)/(1+e)))
$MACRO RC_Power_ur(l, u, e, p, s) ((u-IntApprox(l,u,s,p))/(u-l))**(1/e)


# ----------------------------------------------------------------------------------------------------
#  Define function: RC_ua
# ----------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------
#  Define function: RC_ur
# ----------------------------------------------------------------------------------------------------










# DECLARE SYMBOLS FROM DATABASE:
sets
	alias_set
	alias_map2
	s
	n
	t
	m
	k
	o
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
	sWaste[s]
	sEnergy[s]
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
	t0[t]
	t1[t]
	tx0[t]
	tE[t]
	t2E[t]
	txE[t]
	tx2E[t]
	tx0E[t]
	tx02E[t]
	n_waste[n]
	n_wasteE[n]
	nm[n]
	nm_F[n]
	nm_D[n]
	ns_F[n]
	n2m2k2o[n,m,k,o]
	mw_D[m]
	nw_D[n]
	nw_F[n]
	nw[n]
	n2m_D[n,m]
	n2m_F[n,m]
	n2m[n,m]
	nr2m_D[n,m]
	dWS[s,m]
	dWTn[s,n]
	dWS_int[s,m]
	dqSR[s,n]
	dWSn[s,n]
	dWSnm[s,n,m]
	dWTy[s,n]
	dWTyF[s,n]
	endo_qS[s,n]
	nestProdInp[s,n,nn]
	nestProdOut[s,n,nn]
	dtauCO2[s,n]
	dqCO2[s,n]
	nestWasteInp[s,n,nn]
	nestWasteOut[s,n,nn]
	n_ZW[n]
	nestInvest[s,n,nn]
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
	PInp_map[s,n,nn]
	PInp_knot[s,n]
	PInp_branch[s,n]
	PInp_knot_o[s,n]
	PInp_knot_no[s,n]
	PInp_branch2o[s,n]
	PInp_branch2no[s,n]
	POut_map[s,n,nn]
	POut_knot[s,n]
	POut_branch[s,n]
	POut_branch_o[s,n]
	POut_branch_no[s,n]
	P_sm[s]
	P_endoP[n]
	P_input_n[n]
	P_exoQS[s,n]
	P_exoP[n]
	P_endoMu[s,n,nn]
	P_dur[s,n]
	P_dur2inv[s,n,nn]
	P_inv[s,n]
	W_map[s,n,nn]
	W_map_spinp[s,n,nn]
	W_map_spout[s,n,nn]
	W_knout[s,n]
	W_kninp[s,n]
	W_spout[s,n]
	W_spinp[s,n]
	W_input[s,n]
	W_output[s,n]
	W_int[s,n]
	WInp_map[s,n,nn]
	WInp_knot[s,n]
	WInp_branch[s,n]
	WInp_knot_o[s,n]
	WInp_knot_no[s,n]
	WInp_branch2o[s,n]
	WInp_branch2no[s,n]
	WOut_map[s,n,nn]
	WOut_knot[s,n]
	WOut_branch[s,n]
	WOut_branch_o[s,n]
	WOut_branch_no[s,n]
	W_sm[s]
	W_endoP[n]
	W_input_n[n]
	W_exoQS[s,n]
	W_exoP[n]
	W_endoMu[s,n,nn]
	W_dur[s,n]
	W_dur2inv[s,n,nn]
	W_inv[s,n]
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
	C_map[s,n,nn]
	C_map_spinp[s,n,nn]
	C_map_spout[s,n,nn]
	C_knout[s,n]
	C_kninp[s,n]
	C_spout[s,n]
	C_spinp[s,n]
	C_input[s,n]
	C_output[s,n]
	C_int[s,n]
	C_knot[s,n]
	C_branch[s,n]
	C_knot_o[s,n]
	C_knot_no[s,n]
	C_branch2o[s,n]
	C_branch2no[s,n]
	C_endoMu[s,n,nn]
	C_L2C[s,n,nn]
	C_L[s,n]
	C_C[s,n]
	C_output_n[n]
	C_input_n[n]
	C_sm[s]
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
	qNorm[s,n,nn]
	uWS_D0[t,s,m]
	uWS_int0[t,s,m]
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
	qWS[t,s,m]
	uWS_D[t,s,m]
	intRcEff[t,s,m]
	uWS_int[t,s,m]
	qWSP[t,s,m]
	uWS[t,s,n,m]
	uWTy[s,n]
	uWTyF[s,n]
	WTD_W[t,m]
	WTD_d[t,m]
	WTD_dmin[t,m]
	WTD_r[t,m]
	WTD_a[t,m]
	WTD_e[t,m]
	WTD_gwe[m]
	WTD_alphal[t,m]
	WTD_alphau[t,m]
	WTD_beta[t,m]
	WTD_smooth[m]
	WTD_gd[t,m]
	WTD_ge[t,m]
	WTD_gr[t,m]
	WTD_zetaE[t,m]
	sigma[s,n]
	eta[s,n]
	tauCO2[t,s,n]
	tauLump[t,s]
	tauS[t,s,n]
	tauD[t,s,n]
	pWext[t,s,m]
	pW[t,s,n]
	pD[t,s,n]
	frisch[s]
	crra[s]
	discF[s]
	uCO2[t,s,n]
	tauCO2agg[t]
	tauDist[t,s,n]
	qCO2agg[t]
	tauEffCO2[t,s,n]
	Rrate[t]
	pS[t,s,n]
	mu[s,n,nn]
	markup[s]
	vA[t,s]
	vA_tvc[s]
	divd[t,s]
	taxRevPar[s]
	tauLump0[t,s]
	K_tvc[s,n]
	adjCostPar[s,n]
	adjCost[t,s]
	WTDpar[s,n]
	WTFpar[s,n]
	qSRpar[s,n]
	alphauCal[m]
	gammarCal[m]
	WTD_qSnwCal[n]
	WTD_qSnmCal[n]
	WTD_pSnwCal[m]
	WTD_qSWECal[n]
	WTD_alphau0[t,m]
	WTD_gr0[t,m]
	WTD_ge0[t,m]
	WTD_gd0[t,m]
	tauD0[t,s,n]
	vU[t,s]
	jTerm[s]
	gadj[s]
	vU_tvc[s]
	tauS0[t,s,n]
	Lscale[s]
	qC[t,s]
	Fscale[s,n]
	Fscale_WI[s,m]
	uCO20[t,s,n]
	uCO2Calib[s,n]
;


# LOAD SYMBOLS FROM DATABASE:
$GDXIN vGRSIntRC2019CGE_db
$onMulti
$load alias_set
$load alias_map2
$load s
$load n
$load t
$load m
$load k
$load o
$load alias_
$load s_p
$load n_p
$load n_F
$load s_HH
$load s_G
$load s_i
$load s_f
$load sWaste
$load sEnergy
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
$load t0
$load t1
$load tx0
$load tE
$load t2E
$load txE
$load tx2E
$load tx0E
$load tx02E
$load n_waste
$load n_wasteE
$load nm
$load nm_F
$load nm_D
$load ns_F
$load n2m2k2o
$load mw_D
$load nw_D
$load nw_F
$load nw
$load n2m_D
$load n2m_F
$load n2m
$load nr2m_D
$load dWS
$load dWTn
$load dWS_int
$load dqSR
$load dWSn
$load dWSnm
$load dWTy
$load dWTyF
$load endo_qS
$load nestProdInp
$load nestProdOut
$load dtauCO2
$load dqCO2
$load nestWasteInp
$load nestWasteOut
$load n_ZW
$load nestInvest
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
$load PInp_map
$load PInp_knot
$load PInp_branch
$load PInp_knot_o
$load PInp_knot_no
$load PInp_branch2o
$load PInp_branch2no
$load POut_map
$load POut_knot
$load POut_branch
$load POut_branch_o
$load POut_branch_no
$load P_sm
$load P_endoP
$load P_input_n
$load P_exoQS
$load P_exoP
$load P_endoMu
$load P_dur
$load P_dur2inv
$load P_inv
$load W_map
$load W_map_spinp
$load W_map_spout
$load W_knout
$load W_kninp
$load W_spout
$load W_spinp
$load W_input
$load W_output
$load W_int
$load WInp_map
$load WInp_knot
$load WInp_branch
$load WInp_knot_o
$load WInp_knot_no
$load WInp_branch2o
$load WInp_branch2no
$load WOut_map
$load WOut_knot
$load WOut_branch
$load WOut_branch_o
$load WOut_branch_no
$load W_sm
$load W_endoP
$load W_input_n
$load W_exoQS
$load W_exoP
$load W_endoMu
$load W_dur
$load W_dur2inv
$load W_inv
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
$load C_map
$load C_map_spinp
$load C_map_spout
$load C_knout
$load C_kninp
$load C_spout
$load C_spinp
$load C_input
$load C_output
$load C_int
$load C_knot
$load C_branch
$load C_knot_o
$load C_knot_no
$load C_branch2o
$load C_branch2no
$load C_endoMu
$load C_L2C
$load C_L
$load C_C
$load C_output_n
$load C_input_n
$load C_sm
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
$GDXIN vGRSIntRC2019CGE_db
$onMulti
$load R_LR
$load infl_LR
$load g_LR
$load qNorm
$load uWS_D0
$load uWS_int0
$load inventoryAR
$GDXIN
$offMulti;
$GDXIN vGRSIntRC2019CGE_db
$onMulti
$load TotalTax
$load qCO2
$load M1990
$load rDepr
$load p
$load qD
$load qS
$load qWS
$load uWS_D
$load intRcEff
$load uWS_int
$load qWSP
$load uWS
$load uWTy
$load uWTyF
$load WTD_W
$load WTD_d
$load WTD_dmin
$load WTD_r
$load WTD_a
$load WTD_e
$load WTD_gwe
$load WTD_alphal
$load WTD_alphau
$load WTD_beta
$load WTD_smooth
$load WTD_gd
$load WTD_ge
$load WTD_gr
$load WTD_zetaE
$load sigma
$load eta
$load tauCO2
$load tauLump
$load tauS
$load tauD
$load pWext
$load pW
$load pD
$load frisch
$load crra
$load discF
$load uCO2
$load tauCO2agg
$load tauDist
$load qCO2agg
$load tauEffCO2
$load Rrate
$load pS
$load mu
$load markup
$load vA
$load vA_tvc
$load divd
$load taxRevPar
$load tauLump0
$load K_tvc
$load adjCostPar
$load adjCost
$load WTDpar
$load WTFpar
$load qSRpar
$load alphauCal
$load gammarCal
$load WTD_qSnwCal
$load WTD_qSnmCal
$load WTD_pSnwCal
$load WTD_qSWECal
$load WTD_alphau0
$load WTD_gr0
$load WTD_ge0
$load WTD_gd0
$load tauD0
$load vU
$load jTerm
$load gadj
$load vU_tvc
$load tauS0
$load Lscale
$load qC
$load Fscale
$load Fscale_WI
$load uCO20
$load uCO2Calib
$GDXIN
$offMulti;


# WRITE INIT STATEMENTS FROM MODULES:










# WRITE BLOCKS OF EQUATIONS:


# -----------------------------------------------B_PInp-----------------------------------------------
#  Initialize B_PInp equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_PInp_zpOut[t,s,n];
E_PInp_zpOut[t,s,n]$(pinp_knot_o[s,n] and txe[t]).. 	pS[t,s,n]*qS[t,s,n]  =E=  sum(nn$(PInp_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_PInp_zpNOut[t,s,n];
E_PInp_zpNOut[t,s,n]$(pinp_knot_no[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(PInp_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_PInp_qOut[t,s,n];
E_PInp_qOut[t,s,n]$(pinp_branch2o[s,n] and txe[t]).. 	qD[t,s,n] * sum(nn$(PInp_map[s,nn,n]), qNorm[s,nn,n])  =E=  sum(nn$(PInp_map[s,nn,n]), qNorm[s,nn,n] * mu[s,nn,n] * (pS[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qS[t,s,nn]);
EQUATION E_PInp_qNOut[t,s,n];
E_PInp_qNOut[t,s,n]$(pinp_branch2no[s,n] and txe[t]).. 	qD[t,s,n] * sum(nn$(PInp_map[s,nn,n]), qNorm[s,nn,n])  =E=  sum(nn$(PInp_map[s,nn,n]), qNorm[s,nn,n] * mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qD[t,s,nn]);

# ----------------------------------------------------------------------------------------------------
#  Define B_PInp model
# ----------------------------------------------------------------------------------------------------
Model B_PInp /
E_PInp_zpOut, E_PInp_zpNOut, E_PInp_qOut, E_PInp_qNOut
/;



# -----------------------------------------------B_POut-----------------------------------------------
#  Initialize B_POut equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_POut_zp[t,s,n];
E_POut_zp[t,s,n]$(pout_knot[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(POut_map[s,nn,n] and POut_branch_o[s,nn]), qS[t,s,nn]*pS[t,s,nn])+sum(nn$(POut_map[s,nn,n] and POut_branch_no[s,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_POut_demand_out[t,s,n];
E_POut_demand_out[t,s,n]$(pout_branch_o[s,n] and txe[t]).. 		qS[t,s,n] * sum(nn$(POut_map[s,n,nn]), qNorm[s,n,nn])  =E=  sum(nn$(POut_map[s,n,nn]), qNorm[s,n,nn] * mu[s,n,nn] * (pS[t,s,n]/pD[t,s,nn])**(eta[s,nn]) * qD[t,s,nn]);
EQUATION E_POut_demand_nout[t,s,n];
E_POut_demand_nout[t,s,n]$(pout_branch_no[s,n] and txe[t]).. 	qD[t,s,n] * sum(nn$(POut_map[s,n,nn]), qNorm[s,n,nn])  =E=  sum(nn$(POut_map[s,n,nn]), qNorm[s,n,nn] * mu[s,n,nn] * (pD[t,s,n]/pD[t,s,nn])**(eta[s,nn]) * qD[t,s,nn]);

# ----------------------------------------------------------------------------------------------------
#  Define B_POut model
# ----------------------------------------------------------------------------------------------------
Model B_POut /
E_POut_zp, E_POut_demand_out, E_POut_demand_nout
/;



# ----------------------------------------------B_P_price---------------------------------------------
#  Initialize B_P_price equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_P_price_pD[t,s,n];
E_P_price_pD[t,s,n]$(p_input[s,n] and txe[t]).. 			pD[t,s,n]		 =E=  p[t,n]*(1+tauD[t,s,n])+pW[t,s,n]$(dWSn[s,n]);
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



# -----------------------------------------------B_P_WS-----------------------------------------------
#  Initialize B_P_WS equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_P_WS_pWext[t,s,m];
E_P_WS_pWext[t,s,m]$(p_sm[s] and dws[s,m] and txe[t]).. 		pWext[t,s,m]	 =E=  (uWS_D[t,s,m] * (sum(n$(n2m_D[n,m]), pD[t,s,n])+sum(n$(dWTy[s,n]), uWTy[s,n] * pD[t,s,n])) + (1-uWS_D[t,s,m])* (sum(n$(n2m_F[n,m]), pD[t,s,n])+sum(n$(dWTyF[s,n]), uWTyF[s,n]*pD[t,s,n])));
EQUATION E_P_WS_pW[t,s,n];
E_P_WS_pW[t,s,n]$(p_sm[s] and dwsn[s,n] and txe[t]).. 		pW[t,s,n]		 =E=  sum(m$(dWSnm[s,n,m]), uWS[t,s,n,m] * (((1-(uWS_int[t,s,m]*intRcEff[t,s,m])$(dWS_int[s,m])) * pWext[t,s,m])-(uWS_int[t,s,m]*intRcEff[t,s,m])$(dWS_int[s,m])*sum(nn$(nr2m_D[nn,m]), p[t,n])));
EQUATION E_P_WS_qSR[t,s,n];
E_P_WS_qSR[t,s,n]$(p_sm[s] and dqsr[s,n] and txe[t]).. 		qS[t,s,n]		 =E=  sum(m$(nr2m_D[n,m]), uWS_int[t,s,m]*intRcEff[t,s,m] * qWS[t,s,m] / (1-uWS_int[t,s,m]*intRcEff[t,s,m]));
EQUATION E_P_WS_qWS[t,s,m];
E_P_WS_qWS[t,s,m]$(p_sm[s] and dws[s,m] and txe[t]).. 						qWS[t,s,m]	 =E=  sum(n$(dWSnm[s,n,m]), uWS[t,s,n,m] * qD[t,s,n]);
EQUATION E_P_WS_qDWTD[t,s,n];
E_P_WS_qDWTD[t,s,n]$(p_sm[s] and dwtn[s,n] and nw_d[n] and txe[t]).. 		qD[t,s,n]	 =E=  sum(m$(n2m[n,m]), uWS_D[t,s,m] * qWS[t,s,m]);
EQUATION E_P_WS_qDWTyD[t,s,n];
E_P_WS_qDWTyD[t,s,n]$(p_sm[s] and dwty[s,n] and txe[t]).. 					qD[t,s,n]	 =E=  uWTy[s,n] * sum(m$(dWS[s,m]), uWS_D[t,s,m]*qWS[t,s,m]);
EQUATION E_P_WS_qDWTF[t,s,n];
E_P_WS_qDWTF[t,s,n]$(p_sm[s] and dwtn[s,n] and nw_f[n] and txe[t]).. 		qD[t,s,n]	 =E=  sum(m$(n2m[n,m]), (1-uWS_D[t,s,m]) * qWS[t,s,m])+WTFpar[s,n];
EQUATION E_P_WS_qDWTyF[t,s,n];
E_P_WS_qDWTyF[t,s,n]$(p_sm[s] and dwtyf[s,n] and txe[t]).. 					qD[t,s,n]	 =E=  uWTyF[s,n] * sum(m$(dWS[s,m]), (1-uWS_D[t,s,m])*qWS[t,s,m]);

# ----------------------------------------------------------------------------------------------------
#  Define B_P_WS model
# ----------------------------------------------------------------------------------------------------
Model B_P_WS /
E_P_WS_pWext, E_P_WS_pW, E_P_WS_qSR, E_P_WS_qWS, E_P_WS_qDWTD, E_P_WS_qDWTyD, E_P_WS_qDWTF, E_P_WS_qDWTyF
/;



# ----------------------------------------------B_P_WSCal---------------------------------------------
#  Initialize B_P_WSCal equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_P_WSCal_qSR[t,s,n];
E_P_WSCal_qSR[t,s,n]$(p_sm[s] and dqsr[s,n] and txe[t]).. 					qSRpar[s,n]	 =E=  sum(m$(nr2m_D[n,m]), uWS_int[t,s,m]-uWS_int0[t,s,m]);
EQUATION E_P_WSCal_qDWTD[t,s,n];
E_P_WSCal_qDWTD[t,s,n]$(p_sm[s] and dwtn[s,n] and nw_d[n] and txe[t]).. 	WTDpar[s,n]  =E=  sum(m$(n2m[n,m]), uWS_D[t,s,m]-uWS_D0[t,s,m]);

# ----------------------------------------------------------------------------------------------------
#  Define B_P_WSCal model
# ----------------------------------------------------------------------------------------------------
Model B_P_WSCal /
E_P_WSCal_qSR, E_P_WSCal_qDWTD
/;




# -----------------------------------------------B_WInp-----------------------------------------------
#  Initialize B_WInp equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_WInp_zpOut[t,s,n];
E_WInp_zpOut[t,s,n]$(winp_knot_o[s,n] and txe[t]).. 	pS[t,s,n]*qS[t,s,n]  =E=  sum(nn$(WInp_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_WInp_zpNOut[t,s,n];
E_WInp_zpNOut[t,s,n]$(winp_knot_no[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(WInp_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_WInp_qOut[t,s,n];
E_WInp_qOut[t,s,n]$(winp_branch2o[s,n] and txe[t]).. 	qD[t,s,n] * sum(nn$(WInp_map[s,nn,n]), qNorm[s,nn,n])  =E=  sum(nn$(WInp_map[s,nn,n]), qNorm[s,nn,n] * mu[s,nn,n] * (pS[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qS[t,s,nn]);
EQUATION E_WInp_qNOut[t,s,n];
E_WInp_qNOut[t,s,n]$(winp_branch2no[s,n] and txe[t]).. 	qD[t,s,n] * sum(nn$(WInp_map[s,nn,n]), qNorm[s,nn,n])  =E=  sum(nn$(WInp_map[s,nn,n]), qNorm[s,nn,n] * mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qD[t,s,nn]);

# ----------------------------------------------------------------------------------------------------
#  Define B_WInp model
# ----------------------------------------------------------------------------------------------------
Model B_WInp /
E_WInp_zpOut, E_WInp_zpNOut, E_WInp_qOut, E_WInp_qNOut
/;



# -----------------------------------------------B_WOut-----------------------------------------------
#  Initialize B_WOut equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_WOut_zp[t,s,n];
E_WOut_zp[t,s,n]$(wout_knot[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(WOut_map[s,nn,n] and WOut_branch_o[s,nn]), qS[t,s,nn]*pS[t,s,nn])+sum(nn$(WOut_map[s,nn,n] and WOut_branch_no[s,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_WOut_demand_out[t,s,n];
E_WOut_demand_out[t,s,n]$(wout_branch_o[s,n] and txe[t]).. 		qS[t,s,n] * sum(nn$(WOut_map[s,n,nn]), qNorm[s,n,nn])  =E=  sum(nn$(WOut_map[s,n,nn]), qNorm[s,n,nn] * mu[s,n,nn] * (pS[t,s,n]/pD[t,s,nn])**(eta[s,nn]) * qD[t,s,nn]);
EQUATION E_WOut_demand_nout[t,s,n];
E_WOut_demand_nout[t,s,n]$(wout_branch_no[s,n] and txe[t]).. 	qD[t,s,n] * sum(nn$(WOut_map[s,n,nn]), qNorm[s,n,nn])  =E=  sum(nn$(WOut_map[s,n,nn]), qNorm[s,n,nn] * mu[s,n,nn] * (pD[t,s,n]/pD[t,s,nn])**(eta[s,nn]) * qD[t,s,nn]);

# ----------------------------------------------------------------------------------------------------
#  Define B_WOut model
# ----------------------------------------------------------------------------------------------------
Model B_WOut /
E_WOut_zp, E_WOut_demand_out, E_WOut_demand_nout
/;



# ----------------------------------------------B_W_price---------------------------------------------
#  Initialize B_W_price equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_W_price_pD[t,s,n];
E_W_price_pD[t,s,n]$(w_input[s,n] and txe[t]).. 			pD[t,s,n]		 =E=  p[t,n]*(1+tauD[t,s,n])+pW[t,s,n]$(dWSn[s,n]);
EQUATION E_W_price_pS[t,s,n];
E_W_price_pS[t,s,n]$(w_output[s,n] and txe[t]).. 			p[t,n] 			 =E=  (1+markup[s])*(pS[t,s,n]+p[t,n]*tauS[t,s,n]+(tauEffCO2[t,s,n]*uCO2[t,s,n])$(dqCO2[s,n]));
EQUATION E_W_price_TotalTax[t,s];
E_W_price_TotalTax[t,s]$(w_sm[s] and txe[t]).. 				TotalTax[t,s]	 =E=  tauLump[t,s]+sum(n$(W_input[s,n]), tauD[t,s,n] * p[t,n] * qD[t,s,n])+sum(n$(W_output[s,n]), tauS[t,s,n]*p[t,n]*qS[t,s,n])+sum(n$(W_output[s,n] and dqCO2[s,n]), tauCO2[t,s,n]*qCO2[t,s,n]);

# ----------------------------------------------------------------------------------------------------
#  Define B_W_price model
# ----------------------------------------------------------------------------------------------------
Model B_W_price /
E_W_price_pD, E_W_price_pS, E_W_price_TotalTax
/;



# --------------------------------------------B_W_firmValue-------------------------------------------
#  Initialize B_W_firmValue equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_W_firmValue_vA[t,s];
E_W_firmValue_vA[t,s]$(w_sm[s] and tx0[t]).. 		vA[t,s]	 =E=  (vA[t-1,s]*Rrate[t-1]-divd[t-1,s])/((1+g_LR)*(1+infl_LR));
EQUATION E_W_firmValue_divd[t,s];
E_W_firmValue_divd[t,s]$(w_sm[s] and txe[t]).. 		divd[t,s]  =E=  sum(n$(W_output[s,n]), p[t,n] * qS[t,s,n])-sum(n$(W_input[s,n]), p[t,n] * qD[t,s,n])-TotalTax[t,s]-adjCost[t,s];
EQUATION E_W_firmValue_vAT[t,s];
E_W_firmValue_vAT[t,s]$(w_sm[s] and te[t]).. 		vA[t,s]	   =E=  (1+vA_tvc[s])*vA[t-1,s]/((1+g_LR)*(1+infl_LR));

# ----------------------------------------------------------------------------------------------------
#  Define B_W_firmValue model
# ----------------------------------------------------------------------------------------------------
Model B_W_firmValue /
E_W_firmValue_vA, E_W_firmValue_divd, E_W_firmValue_vAT
/;



# --------------------------------------------B_W_taxCalib--------------------------------------------
#  Initialize B_W_taxCalib equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_W_taxCalib_taxRevPar[t,s];
E_W_taxCalib_taxRevPar[t,s]$(w_sm[s]).. 	tauLump[t,s]  =E=  tauLump0[t,s]+taxRevPar[s];

# ----------------------------------------------------------------------------------------------------
#  Define B_W_taxCalib model
# ----------------------------------------------------------------------------------------------------
Model B_W_taxCalib /
E_W_taxCalib_taxRevPar
/;



# ---------------------------------------------B_W_adjCost--------------------------------------------
#  Initialize B_W_adjCost equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_W_adjCost_lom[t,s,n];
E_W_adjCost_lom[t,s,n]$(w_dur[s,n] and txe[t]).. 		qD[t+1,s,n]	 =E=  (qD[t,s,n]*(1-rDepr[t,s,n])+sum(nn$(W_dur2inv[s,n,nn]), qD[t,s,nn]))/(1+g_LR);
EQUATION E_W_adjCost_pk[t,s,n];
E_W_adjCost_pk[t,s,n]$(w_dur[s,n] and tx02e[t]).. 	pD[t,s,n]	 =E=  sum(nn$(W_dur2inv[s,n,nn]), Rrate[t]*(pD[t-1,s,nn]+adjCostPar[s,n]*(qD[t-1,s,nn]/qD[t-1,s,n]-(rDepr[t-1,s,n]+g_LR)))/(1+infl_LR)+(adjCostPar[s,n]*0.5*(sqr(rDepr[t,s,n]+g_LR)-sqr(qD[t,s,nn]/qD[t,s,n]))-(1-rDepr[t,s,n])*(pD[t,s,nn]+adjCostPar[s,n]*(qD[t,s,nn]/qD[t,s,n]-(rDepr[t,s,n]+g_LR)))));
EQUATION E_W_adjCost_pkT[t,s,n];
E_W_adjCost_pkT[t,s,n]$(w_dur[s,n] and t2e[t]).. 		pD[t,s,n]	 =E=  sum(nn$(W_dur2inv[s,n,nn]), Rrate[t]*(pD[t-1,s,nn]+adjCostPar[s,n]*(qD[t-1,s,nn]/qD[t-1,s,n]-(rDepr[t-1,s,n]+g_LR)))/(1+infl_LR)+(rDepr[t,s,n]-1)*pD[t,s,nn]);
EQUATION E_W_adjCost_K_tvc[t,s,n];
E_W_adjCost_K_tvc[t,s,n]$(w_dur[s,n] and te[t]).. 	qD[t,s,n]	 =E=  (1+K_tvc[s,n])*qD[t-1,s,n]/(1+g_LR);
EQUATION E_W_adjCost_adjCost[t,s];
E_W_adjCost_adjCost[t,s]$(w_sm[s] and txe[t]).. 		adjCost[t,s] 	 =E=  sum([n,nn]$(W_dur2inv[s,n,nn]), adjCostPar[s,n]*0.5*qD[t,s,n]*sqr(qD[t,s,nn]/qD[t,s,n]-(rDepr[t,s,n]+g_LR)));

# ----------------------------------------------------------------------------------------------------
#  Define B_W_adjCost model
# ----------------------------------------------------------------------------------------------------
Model B_W_adjCost /
E_W_adjCost_lom, E_W_adjCost_pk, E_W_adjCost_pkT, E_W_adjCost_K_tvc, E_W_adjCost_adjCost
/;



# -----------------------------------------------B_W_WS-----------------------------------------------
#  Initialize B_W_WS equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_W_WS_pW[t,s,n];
E_W_WS_pW[t,s,n]$(w_sm[s] and dwsn[s,n] and txe[t]).. 						pW[t,s,n]	 =E=  sum(m$(dWSnm[s,n,m]), uWS[t,s,n,m] * (uWS_D[t,s,m] * (sum(nn$(n2m_D[nn,m]), pD[t,s,nn])+sum(nn$(dWTy[s,nn]), uWTy[s,nn] * pD[t,s,nn])) + (1-uWS_D[t,s,m])* (sum(nn$(n2m_F[nn,m]), pD[t,s,nn])+sum(nn$(dWTyF[s,nn]), uWTyF[s,nn]*pD[t,s,nn]))));
EQUATION E_W_WS_qWS[t,s,m];
E_W_WS_qWS[t,s,m]$(w_sm[s] and dws[s,m] and txe[t]).. 						qWS[t,s,m]	 =E=  sum(n$(dWSnm[s,n,m]), uWS[t,s,n,m] * qD[t,s,n]);
EQUATION E_W_WS_qDWTD[t,s,n];
E_W_WS_qDWTD[t,s,n]$(w_sm[s] and dwtn[s,n] and nw_d[n] and txe[t]).. 		qD[t,s,n]	 =E=  sum(m$(n2m[n,m]), uWS_D[t,s,m] * qWS[t,s,m]);
EQUATION E_W_WS_qDWTyD[t,s,n];
E_W_WS_qDWTyD[t,s,n]$(w_sm[s] and dwty[s,n] and txe[t]).. 					qD[t,s,n]	 =E=  uWTy[s,n] * sum(m$(dWS[s,m]), uWS_D[t,s,m]*qWS[t,s,m]);
EQUATION E_W_WS_qDWTF[t,s,n];
E_W_WS_qDWTF[t,s,n]$(w_sm[s] and dwtn[s,n] and nw_f[n] and txe[t]).. 		qD[t,s,n]	 =E=  sum(m$(n2m[n,m]), (1-uWS_D[t,s,m]) * qWS[t,s,m])+WTFpar[s,n];
EQUATION E_W_WS_qDWTyF[t,s,n];
E_W_WS_qDWTyF[t,s,n]$(w_sm[s] and dwtyf[s,n] and txe[t]).. 					qD[t,s,n]	 =E=  uWTyF[s,n] * sum(m$(dWS[s,m]), (1-uWS_D[t,s,m])*qWS[t,s,m]);

# ----------------------------------------------------------------------------------------------------
#  Define B_W_WS model
# ----------------------------------------------------------------------------------------------------
Model B_W_WS /
E_W_WS_pW, E_W_WS_qWS, E_W_WS_qDWTD, E_W_WS_qDWTyD, E_W_WS_qDWTF, E_W_WS_qDWTyF
/;



# ----------------------------------------------B_W_WSCal---------------------------------------------
#  Initialize B_W_WSCal equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_W_WSCal_qDWTD[t,s,n];
E_W_WSCal_qDWTD[t,s,n]$(w_sm[s] and dwtn[s,n] and nw_d[n] and txe[t]).. 	WTDpar[s,n]  =E=  sum(m$(n2m[n,m]), uWS_D[t,s,m]-uWS_D0[t,s,m]);

# ----------------------------------------------------------------------------------------------------
#  Define B_W_WSCal model
# ----------------------------------------------------------------------------------------------------
Model B_W_WSCal /
E_W_WSCal_qDWTD
/;



# ----------------------------------------------B_W_Treat---------------------------------------------
#  Initialize B_W_Treat equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_W_Treat_W[t,s,m];
E_W_Treat_W[t,s,m]$(w_sm[s] and mw_d[m] and txe[t]).. 	WTD_W[t,m]	 =E=  sum(ss$(dWS[ss,m]), qWS[t,ss,m] * uWS_D[t,ss,m]);
EQUATION E_W_Treat_d[t,s,m];
E_W_Treat_d[t,s,m]$(w_sm[s] and mw_d[m] and txe[t]).. 	WTD_d[t,m]	 =E=  WTD_dmin[t,m];
EQUATION E_W_Treat_zeta[t,s,m];
E_W_Treat_zeta[t,s,m]$(w_sm[s] and mw_d[m] and txe[t]).. 	WTD_zetaE[t,m]	 =E=  [sum(n$(n_ZW[n]), pD[t,s,n]) * (WTD_gr[t,m]-WTD_ge[t,m])+WTD_gwe[m]*sum(n$(n_wasteE[n]), pS[t,s,n])]/sum(n$(nr2m_D[n,m]), pS[t,s,n]);
EQUATION E_W_Treat_r[t,s,m];
E_W_Treat_r[t,s,m]$(w_sm[s] and mw_d[m] and txe[t]).. 	WTD_r[t,m]	 =E=  



 RC_Power_ur( (WTD_alphal[t,m]), (WTD_alphau[t,m]), (WTD_beta[t,m]), (WTD_zetaE[t,m]), (WTD_smooth[m]) ) 




;
EQUATION E_W_Treat_a[t,s,m];
E_W_Treat_a[t,s,m]$(w_sm[s] and mw_d[m] and txe[t]).. 	WTD_a[t,m]	 =E=  



 RC_Power_ua( (WTD_alphal[t,m]), (WTD_alphau[t,m]), (WTD_beta[t,m]), (WTD_r[t,m]) ) 




;
EQUATION E_W_Treat_e[t,s,m];
E_W_Treat_e[t,s,m]$(w_sm[s] and mw_d[m] and txe[t]).. 	WTD_e[t,m]	 =E=  1-WTD_d[t,m]-WTD_r[t,m]*(1-WTD_dmin[t,m]);
EQUATION E_W_Treat_pWTD[t,s,n];
E_W_Treat_pWTD[t,s,n]$(w_sm[s] and nw_d[n] and txe[t])..  pS[t,s,n]  =E=  sum(m$(n2m_D[n,m]), sum(nn$(n_ZW[nn]), pD[t,s,nn]) * (WTD_gd[t,m]*WTD_d[t,m]+WTD_ge[t,m]*WTD_e[t,m]+WTD_gr[t,m]*WTD_r[t,m]*(1-WTD_dmin[t,m]))-WTD_r[t,m]*WTD_a[t,m]*(1-WTD_dmin[t,m])*sum(nn$(nr2m_D[nn,m]), pS[t,s,nn])-WTD_e[t,m]*WTD_gwe[m]*sum(nn$(n_wasteE[nn]),pS[t,s,nn]));

# ----------------------------------------------------------------------------------------------------
#  Define B_W_Treat model
# ----------------------------------------------------------------------------------------------------
Model B_W_Treat /
E_W_Treat_W, E_W_Treat_d, E_W_Treat_zeta, E_W_Treat_r, E_W_Treat_a, E_W_Treat_e, E_W_Treat_pWTD
/;



# ----------------------------------------------B_W_Prod----------------------------------------------
#  Initialize B_W_Prod equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_W_Prod_ZW[t,s,n];
E_W_Prod_ZW[t,s,n]$(w_sm[s] and n_zw[n] and txe[t]).. 				qD[t,s,n]	 =E=  sum(m$(mw_D[m]), WTD_W[t,m]* (WTD_gd[t,m] * WTD_d[t,m]+WTD_ge[t,m] *WTD_e[t,m]+WTD_gr[t,m]*WTD_r[t,m]*(1-WTD_dmin[t,m])));
EQUATION E_W_Prod_qSnm[t,s,n];
E_W_Prod_qSnm[t,s,n]$(w_output[s,n] and nm_d[n] and txe[t]).. 		qS[t,s,n]	 =E=  WTD_qSnmCal[n]+sum(m$(nr2m_D[n,m]), WTD_a[t,m] * WTD_r[t,m] * (1-WTD_dmin[t,m])*WTD_W[t,m]);
EQUATION E_W_Prod_qSnw[t,s,n];
E_W_Prod_qSnw[t,s,n]$(w_output[s,n] and nw_d[n] and txe[t]).. 		qS[t,s,n]	 =E=  WTD_qSnwCal[n]+sum(m$(mw_D[m] and n2m_D[n,m]), WTD_W[t,m]);
EQUATION E_W_Prod_qSWE[t,s,n];
E_W_Prod_qSWE[t,s,n]$(w_output[s,n] and n_wastee[n] and txe[t]).. 	qS[t,s,n]	 =E=  WTD_qSWECal[n]+sum(m$(mw_D[m]), WTD_gwe[m] * WTD_e[t,m] * WTD_W[t,m]);

# ----------------------------------------------------------------------------------------------------
#  Define B_W_Prod model
# ----------------------------------------------------------------------------------------------------
Model B_W_Prod /
E_W_Prod_ZW, E_W_Prod_qSnm, E_W_Prod_qSnw, E_W_Prod_qSWE
/;



# ----------------------------------------------B_W_Calib---------------------------------------------
#  Initialize B_W_Calib equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_W_Calib_alphau[t,m];
E_W_Calib_alphau[t,m]$(mw_d[m] and txe[t])..  	WTD_alphau[t,m]	 =E=  WTD_alphau0[t,m] + alphauCal[m];
EQUATION E_W_Calib_gammar[t,m];
E_W_Calib_gammar[t,m]$(mw_d[m] and txe[t])..  	WTD_gr[t,m]		 =E=  WTD_gr0[t,m] + gammarCal[m];
EQUATION E_W_Calib_gammae[t,m];
E_W_Calib_gammae[t,m]$(mw_d[m] and txe[t]).. 		WTD_ge[t,m]		 =E=  WTD_ge0[t,m] + WTD_pSnwCal[m];
EQUATION E_W_Calib_gammad[t,m];
E_W_Calib_gammad[t,m]$(mw_d[m] and txe[t]).. 		WTD_gd[t,m]		 =E=  WTD_gd0[t,m] + WTD_pSnwCal[m];

# ----------------------------------------------------------------------------------------------------
#  Define B_W_Calib model
# ----------------------------------------------------------------------------------------------------
Model B_W_Calib /
E_W_Calib_alphau, E_W_Calib_gammar, E_W_Calib_gammae, E_W_Calib_gammad
/;




# -------------------------------------------------B_I------------------------------------------------
#  Initialize B_I equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_I_zpOut[t,s,n];
E_I_zpOut[t,s,n]$(i_knot_o[s,n] and txe[t]).. 	pS[t,s,n]*qS[t,s,n]  =E=  sum(nn$(I_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_I_zpNOut[t,s,n];
E_I_zpNOut[t,s,n]$(i_knot_no[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(I_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_I_qOut[t,s,n];
E_I_qOut[t,s,n]$(i_branch2o[s,n] and txe[t]).. 	qD[t,s,n] * sum(nn$(I_map[s,nn,n]), qNorm[s,nn,n])  =E=  sum(nn$(I_map[s,nn,n]), qNorm[s,nn,n] * mu[s,nn,n] * (pS[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qS[t,s,nn]);
EQUATION E_I_qNOut[t,s,n];
E_I_qNOut[t,s,n]$(i_branch2no[s,n] and txe[t]).. 	qD[t,s,n] * sum(nn$(I_map[s,nn,n]), qNorm[s,nn,n])  =E=  sum(nn$(I_map[s,nn,n]), qNorm[s,nn,n] * mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qD[t,s,nn]);

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




# -------------------------------------------------B_C------------------------------------------------
#  Initialize B_C equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_C_zp[t,s,n];
E_C_zp[t,s,n]$(c_knot[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(C_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_C_q[t,s,n];
E_C_q[t,s,n]$(c_branch[s,n] and txe[t]).. 	qD[t,s,n] * sum(nn$(C_map[s,nn,n]), qNorm[s,nn,n])  =E=  sum(nn$(C_map[s,nn,n]), qNorm[s,nn,n] * mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qD[t,s,nn]);

# ----------------------------------------------------------------------------------------------------
#  Define B_C model
# ----------------------------------------------------------------------------------------------------
Model B_C /
E_C_zp, E_C_q
/;



# ----------------------------------------------B_C_price---------------------------------------------
#  Initialize B_C_price equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_C_price_pD[t,s,n];
E_C_price_pD[t,s,n]$(c_input[s,n] and txe[t]).. 	pD[t,s,n]		 =E=  p[t,n]*(1+tauD[t,s,n])+pW[t,s,n]$(dWSn[s,n]);
EQUATION E_C_price_w[t,s,n];
E_C_price_w[t,s,n]$(c_l[s,n] and txe[t]).. 			pS[t,s,n]		 =E=  p[t,n]*(1-tauS[t,s,n]);
EQUATION E_C_price_TotalTax[t,s];
E_C_price_TotalTax[t,s]$(c_sm[s] and txe[t]).. 		TotalTax[t,s]	 =E=  tauLump[t,s]+sum(n$(C_input[s,n]), tauD[t,s,n] * p[t,n] * qD[t,s,n])+sum(n$(C_L[s,n]), tauS[t,s,n]*p[t,n]*qS[t,s,n]);
EQUATION E_C_price_vA0[t,s];
E_C_price_vA0[t,s]$(c_sm[s] and t0[t]).. 			vA[t+1,s]		 =E=  (vA[t,s] * Rrate[t] + sum(n$(C_L[s,n]), p[t,n]*qS[t,s,n])-sum(n$(C_input[s,n]), p[t,n]*qD[t,s,n])-TotalTax[t,s]+jTerm[s])/(1+g_LR);
EQUATION E_C_price_vA[t,s];
E_C_price_vA[t,s]$(c_sm[s] and tx0e[t]).. 			vA[t+1,s]		 =E=  (vA[t,s] * Rrate[t] + sum(n$(C_L[s,n]), p[t,n]*qS[t,s,n])-sum(n$(C_input[s,n]), p[t,n]*qD[t,s,n])-TotalTax[t,s]+jTerm[s])/(1+g_LR);

# ----------------------------------------------------------------------------------------------------
#  Define B_C_price model
# ----------------------------------------------------------------------------------------------------
Model B_C_price /
E_C_price_pD, E_C_price_w, E_C_price_TotalTax, E_C_price_vA0, E_C_price_vA
/;



# -----------------------------------------------B_C_vU-----------------------------------------------
#  Initialize B_C_vU equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_C_vU_qC[t,s];
E_C_vU_qC[t,s]$(c_sm[s] and txe[t]).. 	qC[t,s]		 =E=  sum([n,nn]$(C_L2C[s,n,nn]), qD[t,s,nn]-frisch[s]*Lscale[s]*(qS[t,s,n]/Lscale[s])**((1+frisch[s])/frisch[s])/(1+frisch[s]));
EQUATION E_C_vU_vU[t,s];
E_C_vU_vU[t,s]$(c_sm[s] and txe[t]).. 	vU[t,s]		 =E=  (qC[t,s]**(1-crra[s]))/(1-crra[s])+(1+gadj[s])*discF[s]*vU[t+1,s];
EQUATION E_C_vU_vUT[t,s];
E_C_vU_vUT[t,s]$(c_sm[s] and te[t]).. 	vU[t,s]		 =E=  vU[t-1,s]*(1+vU_tvc[s])/(1+gadj[s]);
EQUATION E_C_vU_qL[t,s,n];
E_C_vU_qL[t,s,n]$(c_l[s,n] and txe[t])..  qS[t,s,n]	 =E=  Lscale[s] * sum(nn$(C_L2C[s,n,nn]), pS[t,s,n]/pD[t,s,nn])**(frisch[s]);

# ----------------------------------------------------------------------------------------------------
#  Define B_C_vU model
# ----------------------------------------------------------------------------------------------------
Model B_C_vU /
E_C_vU_qC, E_C_vU_vU, E_C_vU_vUT, E_C_vU_qL
/;



# --------------------------------------------B_C_taxCalib--------------------------------------------
#  Initialize B_C_taxCalib equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_C_taxCalib_taxRevPar[t,s,n];
E_C_taxCalib_taxRevPar[t,s,n]$((c_l[s,n] and txe[t])).. 	tauS[t,s,n]  =E=  tauS0[t,s,n]+taxRevPar[s];

# ----------------------------------------------------------------------------------------------------
#  Define B_C_taxCalib model
# ----------------------------------------------------------------------------------------------------
Model B_C_taxCalib /
E_C_taxCalib_taxRevPar
/;



# ----------------------------------------------B_C_Euler---------------------------------------------
#  Initialize B_C_Euler equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_C_Euler_Euler[t,s,n];
E_C_Euler_Euler[t,s,n]$(c_c[s,n] and tx0e[t]).. 	qD[t,s,n]	 =E=  qD[t-1,s,n]*(discF[s]*Rrate[t]*(pD[t-1,s,n]/pD[t,s,n]))**(1/crra[s])/(1+g_LR);
EQUATION E_C_Euler_TVC[t,s];
E_C_Euler_TVC[t,s]$(c_sm[s] and te[t]).. 			vA[t,s]		 =E=  vA[t-1,s]*(1+vA_tvc[s])/(1+g_LR);

# ----------------------------------------------------------------------------------------------------
#  Define B_C_Euler model
# ----------------------------------------------------------------------------------------------------
Model B_C_Euler /
E_C_Euler_Euler, E_C_Euler_TVC
/;



# -----------------------------------------------B_C_WS-----------------------------------------------
#  Initialize B_C_WS equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_C_WS_pW[t,s,n];
E_C_WS_pW[t,s,n]$(c_sm[s] and dwsn[s,n] and txe[t]).. 						pW[t,s,n]	 =E=  sum(m$(dWSnm[s,n,m]), uWS[t,s,n,m] * (uWS_D[t,s,m] * (sum(nn$(n2m_D[nn,m]), pD[t,s,nn])+sum(nn$(dWTy[s,nn]), uWTy[s,nn] * pD[t,s,nn])) + (1-uWS_D[t,s,m])* (sum(nn$(n2m_F[nn,m]), pD[t,s,nn])+sum(nn$(dWTyF[s,nn]), uWTyF[s,nn]*pD[t,s,nn]))));
EQUATION E_C_WS_qWS[t,s,m];
E_C_WS_qWS[t,s,m]$(c_sm[s] and dws[s,m] and txe[t]).. 						qWS[t,s,m]	 =E=  sum(n$(dWSnm[s,n,m]), uWS[t,s,n,m] * qD[t,s,n]);
EQUATION E_C_WS_qDWTD[t,s,n];
E_C_WS_qDWTD[t,s,n]$(c_sm[s] and dwtn[s,n] and nw_d[n] and txe[t]).. 		qD[t,s,n]	 =E=  sum(m$(n2m[n,m]), uWS_D[t,s,m] * qWS[t,s,m]);
EQUATION E_C_WS_qDWTyD[t,s,n];
E_C_WS_qDWTyD[t,s,n]$(c_sm[s] and dwty[s,n] and txe[t]).. 					qD[t,s,n]	 =E=  uWTy[s,n] * sum(m$(dWS[s,m]), uWS_D[t,s,m]*qWS[t,s,m]);
EQUATION E_C_WS_qDWTF[t,s,n];
E_C_WS_qDWTF[t,s,n]$(c_sm[s] and dwtn[s,n] and nw_f[n] and txe[t]).. 		qD[t,s,n]	 =E=  sum(m$(n2m[n,m]), (1-uWS_D[t,s,m]) * qWS[t,s,m])+WTFpar[s,n];
EQUATION E_C_WS_qDWTyF[t,s,n];
E_C_WS_qDWTyF[t,s,n]$(c_sm[s] and dwtyf[s,n] and txe[t]).. 					qD[t,s,n]	 =E=  uWTyF[s,n] * sum(m$(dWS[s,m]), (1-uWS_D[t,s,m])*qWS[t,s,m]);

# ----------------------------------------------------------------------------------------------------
#  Define B_C_WS model
# ----------------------------------------------------------------------------------------------------
Model B_C_WS /
E_C_WS_pW, E_C_WS_qWS, E_C_WS_qDWTD, E_C_WS_qDWTyD, E_C_WS_qDWTF, E_C_WS_qDWTyF
/;



# ----------------------------------------------B_C_WSCal---------------------------------------------
#  Initialize B_C_WSCal equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_C_WSCal_qDWTD[t,s,n];
E_C_WSCal_qDWTD[t,s,n]$(c_sm[s] and dwtn[s,n] and nw_d[n] and txe[t]).. 	WTDpar[s,n]  =E=  sum(m$(n2m[n,m]), uWS_D[t,s,m]-uWS_D0[t,s,m]);

# ----------------------------------------------------------------------------------------------------
#  Define B_C_WSCal model
# ----------------------------------------------------------------------------------------------------
Model B_C_WSCal /
E_C_WSCal_qDWTD
/;




# -------------------------------------------------B_G------------------------------------------------
#  Initialize B_G equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_G_zp[t,s,n];
E_G_zp[t,s,n]$(g_knot[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(G_map[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_G_q[t,s,n];
E_G_q[t,s,n]$(g_branch[s,n] and txe[t]).. 	qD[t,s,n] * sum(nn$(G_map[s,nn,n]), qNorm[s,nn,n])  =E=  sum(nn$(G_map[s,nn,n]), qNorm[s,nn,n] * mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qD[t,s,nn]);

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
E_G_price_vA0[t,s]$(g_sm[s] and t0[t]).. 			vA[t+1,s]		 =E=  (vA[t,s] * Rrate[t]+sum(ss$(d_TotalTax[ss]), TotalTax[t,ss])-sum(n$(G_input[s,n]), p[t,n]*qD[t,s,n])-TotalTax[t,s]+jTerm[s])/(1+g_LR);
EQUATION E_G_price_vA[t,s];
E_G_price_vA[t,s]$(g_sm[s] and tx0e[t]).. 			vA[t+1,s]		 =E=  (vA[t,s] * Rrate[t]+sum(ss$(d_TotalTax[ss]), TotalTax[t,ss])-sum(n$(G_input[s,n]), p[t,n]*qD[t,s,n])-TotalTax[t,s]+jTerm[s])/(1+g_LR);

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



# -----------------------------------------------B_T_WI-----------------------------------------------
#  Initialize B_T_WI equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_T_WI_qWS[t,s,m];
E_T_WI_qWS[t,s,m]$(t_sm[s] and dws[s,m] and txe[t]).. 	qWS[t,s,m]	 =E=  Fscale_WI[s,m] * sum([n,nn]$(n2m_D[n,m] and dom2for[n,nn]), (p[t,nn]/pD[t,s,n])**(sigma[s,n]));

# ----------------------------------------------------------------------------------------------------
#  Define B_T_WI model
# ----------------------------------------------------------------------------------------------------
Model B_T_WI /
E_T_WI_qWS
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
#  Define M_vGRSIntRC2019CGE_B model
# ----------------------------------------------------------------------------------------------------
Model M_vGRSIntRC2019CGE_B /
E_PInp_zpOut, E_PInp_zpNOut, E_PInp_qOut, E_PInp_qNOut, E_POut_zp, E_POut_demand_out, E_POut_demand_nout, E_P_price_pD, E_P_price_pS, E_P_price_TotalTax, E_P_firmValue_vA, E_P_firmValue_divd, E_P_firmValue_vAT, E_P_adjCost_lom, E_P_adjCost_pk, E_P_adjCost_pkT, E_P_adjCost_K_tvc, E_P_adjCost_adjCost, E_P_WS_pWext, E_P_WS_pW, E_P_WS_qSR, E_P_WS_qWS, E_P_WS_qDWTD, E_P_WS_qDWTyD, E_P_WS_qDWTF, E_P_WS_qDWTyF, E_WInp_zpOut, E_WInp_zpNOut, E_WInp_qOut, E_WInp_qNOut, E_WOut_zp, E_WOut_demand_out, E_WOut_demand_nout, E_W_price_pD, E_W_price_pS, E_W_price_TotalTax, E_W_firmValue_vA, E_W_firmValue_divd, E_W_firmValue_vAT, E_W_adjCost_lom, E_W_adjCost_pk, E_W_adjCost_pkT, E_W_adjCost_K_tvc, E_W_adjCost_adjCost, E_W_WS_pW, E_W_WS_qWS, E_W_WS_qDWTD, E_W_WS_qDWTyD, E_W_WS_qDWTF, E_W_WS_qDWTyF, E_W_Treat_W, E_W_Treat_d, E_W_Treat_zeta, E_W_Treat_r, E_W_Treat_a, E_W_Treat_e, E_W_Treat_pWTD, E_W_Prod_ZW, E_W_Prod_qSnm, E_W_Prod_qSnw, E_W_Prod_qSWE, E_I_zpOut, E_I_zpNOut, E_I_qOut, E_I_qNOut, E_I_price_pD, E_I_price_pS, E_I_price_TotalTax, E_I_firmValue_vA, E_I_firmValue_divd, E_I_firmValue_vAT, E_C_zp, E_C_q, E_C_price_pD, E_C_price_w, E_C_price_TotalTax, E_C_price_vA0, E_C_price_vA, E_C_vU_qC, E_C_vU_vU, E_C_vU_vUT, E_C_vU_qL, E_C_Euler_Euler, E_C_Euler_TVC, E_C_WS_pW, E_C_WS_qWS, E_C_WS_qDWTD, E_C_WS_qDWTyD, E_C_WS_qDWTF, E_C_WS_qDWTyF, E_G_zp, E_G_q, E_G_price_pD, E_G_price_TotalTax, E_G_price_vA0, E_G_price_vA, E_T_qD, E_T_pD, E_T_TotalTax, E_T_WI_qWS, E_IVT, E_M_tauCO2, E_M_tauCO2Eff, E_M_qCO2, E_M_qCO2agg, E_Equi_equi
/;


# ----------------------------------------------------------------------------------------------------
#  Define M_vGRSIntRC2019CGE_C model
# ----------------------------------------------------------------------------------------------------
Model M_vGRSIntRC2019CGE_C /
E_PInp_zpOut, E_PInp_zpNOut, E_PInp_qOut, E_PInp_qNOut, E_POut_zp, E_POut_demand_out, E_POut_demand_nout, E_P_price_pD, E_P_price_pS, E_P_price_TotalTax, E_P_firmValue_vA, E_P_firmValue_divd, E_P_firmValue_vAT, E_P_adjCost_lom, E_P_adjCost_pk, E_P_adjCost_pkT, E_P_adjCost_K_tvc, E_P_adjCost_adjCost, E_P_WS_pWext, E_P_WS_pW, E_P_WS_qSR, E_P_WS_qWS, E_P_WS_qDWTD, E_P_WS_qDWTyD, E_P_WS_qDWTF, E_P_WS_qDWTyF, E_P_taxCalib_taxRevPar, E_P_WSCal_qSR, E_P_WSCal_qDWTD, E_WInp_zpOut, E_WInp_zpNOut, E_WInp_qOut, E_WInp_qNOut, E_WOut_zp, E_WOut_demand_out, E_WOut_demand_nout, E_W_price_pD, E_W_price_pS, E_W_price_TotalTax, E_W_firmValue_vA, E_W_firmValue_divd, E_W_firmValue_vAT, E_W_adjCost_lom, E_W_adjCost_pk, E_W_adjCost_pkT, E_W_adjCost_K_tvc, E_W_adjCost_adjCost, E_W_WS_pW, E_W_WS_qWS, E_W_WS_qDWTD, E_W_WS_qDWTyD, E_W_WS_qDWTF, E_W_WS_qDWTyF, E_W_Treat_W, E_W_Treat_d, E_W_Treat_zeta, E_W_Treat_r, E_W_Treat_a, E_W_Treat_e, E_W_Treat_pWTD, E_W_Prod_ZW, E_W_Prod_qSnm, E_W_Prod_qSnw, E_W_Prod_qSWE, E_W_taxCalib_taxRevPar, E_W_WSCal_qDWTD, E_W_Calib_alphau, E_W_Calib_gammar, E_W_Calib_gammae, E_W_Calib_gammad, E_I_zpOut, E_I_zpNOut, E_I_qOut, E_I_qNOut, E_I_price_pD, E_I_price_pS, E_I_price_TotalTax, E_I_firmValue_vA, E_I_firmValue_divd, E_I_firmValue_vAT, E_I_taxCalib_taxRevPar, E_C_zp, E_C_q, E_C_price_pD, E_C_price_w, E_C_price_TotalTax, E_C_price_vA0, E_C_price_vA, E_C_vU_qC, E_C_vU_vU, E_C_vU_vUT, E_C_vU_qL, E_C_Euler_Euler, E_C_Euler_TVC, E_C_WS_pW, E_C_WS_qWS, E_C_WS_qDWTD, E_C_WS_qDWTyD, E_C_WS_qDWTF, E_C_WS_qDWTyF, E_C_taxCalib_taxRevPar, E_C_WSCal_qDWTD, E_G_zp, E_G_q, E_G_price_pD, E_G_price_TotalTax, E_G_price_vA0, E_G_price_vA, E_G_taxCalib_taxRevPar, E_T_qD, E_T_pD, E_T_TotalTax, E_T_WI_qWS, E_IVT, E_M_tauCO2, E_M_tauCO2Eff, E_M_qCO2, E_M_qCO2agg, E_M_qCO2calib, E_Equi_equi_tx0E
/;
;

# Fix exogenous variables in state:
sigma.fx[s,n]$(P_kninp[s,n]) = sigma.l[s,n]$(P_kninp[s,n]);
mu.fx[s,n,nn]$(((P_map[s,n,nn] and ( not (P_endoMu[s,n,nn]))) or P_endoMu[s,n,nn])) = mu.l[s,n,nn]$(((P_map[s,n,nn] and ( not (P_endoMu[s,n,nn]))) or P_endoMu[s,n,nn]));
vA_tvc.fx[s]$(P_sm[s]) = vA_tvc.l[s]$(P_sm[s]);
tauD.fx[t,s,n]$(P_input[s,n]) = tauD.l[t,s,n]$(P_input[s,n]);
tauS.fx[t,s,n]$(P_output[s,n]) = tauS.l[t,s,n]$(P_output[s,n]);
tauLump0.fx[t,s]$(P_sm[s]) = tauLump0.l[t,s]$(P_sm[s]);
qS.fx[t,s,n]$((P_output[s,n] and P_exoQS[s,n])) = qS.l[t,s,n]$((P_output[s,n] and P_exoQS[s,n]));
p.fx[t,n]$(((P_input_n[n] or P_exoP[n]) and ( not (P_endoP[n])))) = p.l[t,n]$(((P_input_n[n] or P_exoP[n]) and ( not (P_endoP[n]))));
Rrate.fx[t] = Rrate.l[t];
tauCO2.fx[t,s,n]$((P_output[s,n] and dqCO2[s,n])) = tauCO2.l[t,s,n]$((P_output[s,n] and dqCO2[s,n]));
qCO2.fx[t,s,n]$((P_output[s,n] and dqCO2[s,n])) = qCO2.l[t,s,n]$((P_output[s,n] and dqCO2[s,n]));
uCO2.fx[t,s,n]$((P_output[s,n] and dqCO2[s,n])) = uCO2.l[t,s,n]$((P_output[s,n] and dqCO2[s,n]));
tauEffCO2.fx[t,s,n]$((P_output[s,n] and dqCO2[s,n])) = tauEffCO2.l[t,s,n]$((P_output[s,n] and dqCO2[s,n]));
rDepr.fx[t,s,n]$(P_dur[s,n]) = rDepr.l[t,s,n]$(P_dur[s,n]);
K_tvc.fx[s,n]$(P_dur[s,n]) = K_tvc.l[s,n]$(P_dur[s,n]);
qD.fx[t,s,n]$((P_dur[s,n] and t0[t])) = qD.l[t,s,n]$((P_dur[s,n] and t0[t]));
adjCostPar.fx[s,n]$(P_dur[s,n]) = adjCostPar.l[s,n]$(P_dur[s,n]);
eta.fx[s,n]$(P_knout[s,n]) = eta.l[s,n]$(P_knout[s,n]);
uWS.fx[t,s,n,m]$((dWSnm[s,n,m] and P_sm[s])) = uWS.l[t,s,n,m]$((dWSnm[s,n,m] and P_sm[s]));
intRcEff.fx[t,s,m]$((P_sm[s] and dWS_int[s,m])) = intRcEff.l[t,s,m]$((P_sm[s] and dWS_int[s,m]));
markup.fx[s]$(P_sm[s]) = markup.l[s]$(P_sm[s]);
taxRevPar.fx[s]$(P_sm[s]) = taxRevPar.l[s]$(P_sm[s]);
tauLump.fx[t,s]$(P_sm[s]) = tauLump.l[t,s]$(P_sm[s]);
uWS_D.fx[t,s,m]$((dWS[s,m] and P_sm[s])) = uWS_D.l[t,s,m]$((dWS[s,m] and P_sm[s]));
uWTy.fx[s,n]$((dWTy[s,n] and P_sm[s])) = uWTy.l[s,n]$((dWTy[s,n] and P_sm[s]));
uWTyF.fx[s,n]$((dWTyF[s,n] and P_sm[s])) = uWTyF.l[s,n]$((dWTyF[s,n] and P_sm[s]));
WTFpar.fx[s,n]$((dWTn[s,n] and nw_F[n] and P_sm[s])) = WTFpar.l[s,n]$((dWTn[s,n] and nw_F[n] and P_sm[s]));
WTDpar.fx[s,n]$((dWTn[s,n] and nw_D[n] and P_sm[s])) = WTDpar.l[s,n]$((dWTn[s,n] and nw_D[n] and P_sm[s]));
uWS_int.fx[t,s,m]$((dWS_int[s,m] and P_sm[s])) = uWS_int.l[t,s,m]$((dWS_int[s,m] and P_sm[s]));
qSRpar.fx[s,n]$((dqSR[s,n] and P_sm[s])) = qSRpar.l[s,n]$((dqSR[s,n] and P_sm[s]));
sigma.fx[s,n]$(W_kninp[s,n]) = sigma.l[s,n]$(W_kninp[s,n]);
mu.fx[s,n,nn]$(((W_map[s,n,nn] and ( not (W_endoMu[s,n,nn]))) or W_endoMu[s,n,nn])) = mu.l[s,n,nn]$(((W_map[s,n,nn] and ( not (W_endoMu[s,n,nn]))) or W_endoMu[s,n,nn]));
vA_tvc.fx[s]$(W_sm[s]) = vA_tvc.l[s]$(W_sm[s]);
tauD.fx[t,s,n]$(W_input[s,n]) = tauD.l[t,s,n]$(W_input[s,n]);
tauS.fx[t,s,n]$(W_output[s,n]) = tauS.l[t,s,n]$(W_output[s,n]);
tauLump0.fx[t,s]$(W_sm[s]) = tauLump0.l[t,s]$(W_sm[s]);
qS.fx[t,s,n]$((W_output[s,n] and W_exoQS[s,n])) = qS.l[t,s,n]$((W_output[s,n] and W_exoQS[s,n]));
p.fx[t,n]$(((W_input_n[n] or W_exoP[n]) and ( not (W_endoP[n])))) = p.l[t,n]$(((W_input_n[n] or W_exoP[n]) and ( not (W_endoP[n]))));
Rrate.fx[t] = Rrate.l[t];
tauCO2.fx[t,s,n]$((W_output[s,n] and dqCO2[s,n])) = tauCO2.l[t,s,n]$((W_output[s,n] and dqCO2[s,n]));
qCO2.fx[t,s,n]$((W_output[s,n] and dqCO2[s,n])) = qCO2.l[t,s,n]$((W_output[s,n] and dqCO2[s,n]));
uCO2.fx[t,s,n]$((W_output[s,n] and dqCO2[s,n])) = uCO2.l[t,s,n]$((W_output[s,n] and dqCO2[s,n]));
tauEffCO2.fx[t,s,n]$((W_output[s,n] and dqCO2[s,n])) = tauEffCO2.l[t,s,n]$((W_output[s,n] and dqCO2[s,n]));
rDepr.fx[t,s,n]$(W_dur[s,n]) = rDepr.l[t,s,n]$(W_dur[s,n]);
K_tvc.fx[s,n]$(W_dur[s,n]) = K_tvc.l[s,n]$(W_dur[s,n]);
qD.fx[t,s,n]$((W_dur[s,n] and t0[t])) = qD.l[t,s,n]$((W_dur[s,n] and t0[t]));
adjCostPar.fx[s,n]$(W_dur[s,n]) = adjCostPar.l[s,n]$(W_dur[s,n]);
eta.fx[s,n]$(W_knout[s,n]) = eta.l[s,n]$(W_knout[s,n]);
uWS.fx[t,s,n,m]$((dWSnm[s,n,m] and W_sm[s])) = uWS.l[t,s,n,m]$((dWSnm[s,n,m] and W_sm[s]));
WTD_dmin.fx[t,m]$((mw_D[m] and txE[t])) = WTD_dmin.l[t,m]$((mw_D[m] and txE[t]));
WTD_alphal.fx[t,m]$((mw_D[m] and txE[t])) = WTD_alphal.l[t,m]$((mw_D[m] and txE[t]));
WTD_beta.fx[t,m]$(mw_D[m]) = WTD_beta.l[t,m]$(mw_D[m]);
WTD_smooth.fx[m]$(mw_D[m]) = WTD_smooth.l[m]$(mw_D[m]);
WTD_gwe.fx[m]$(mw_D[m]) = WTD_gwe.l[m]$(mw_D[m]);
WTD_alphau0.fx[t,m]$((mw_D[m] and txE[t])) = WTD_alphau0.l[t,m]$((mw_D[m] and txE[t]));
WTD_gr0.fx[t,m]$((mw_D[m] and txE[t])) = WTD_gr0.l[t,m]$((mw_D[m] and txE[t]));
WTD_ge0.fx[t,m]$((mw_D[m] and txE[t])) = WTD_ge0.l[t,m]$((mw_D[m] and txE[t]));
WTD_gd0.fx[t,m]$((mw_D[m] and txE[t])) = WTD_gd0.l[t,m]$((mw_D[m] and txE[t]));
qWS.fx[t,s,m]$((dWS[s,m] and ( not (W_sm[s])))) = qWS.l[t,s,m]$((dWS[s,m] and ( not (W_sm[s]))));
uWS_D.fx[t,s,m]$(((dWS[s,m] and ( not (W_sm[s])) and txE[t]) or (dWS[s,m] and W_sm[s]))) = uWS_D.l[t,s,m]$(((dWS[s,m] and ( not (W_sm[s])) and txE[t]) or (dWS[s,m] and W_sm[s])));
markup.fx[s]$(W_sm[s]) = markup.l[s]$(W_sm[s]);
taxRevPar.fx[s]$(W_sm[s]) = taxRevPar.l[s]$(W_sm[s]);
tauLump.fx[t,s]$(W_sm[s]) = tauLump.l[t,s]$(W_sm[s]);
uWTy.fx[s,n]$((dWTy[s,n] and W_sm[s])) = uWTy.l[s,n]$((dWTy[s,n] and W_sm[s]));
uWTyF.fx[s,n]$((dWTyF[s,n] and W_sm[s])) = uWTyF.l[s,n]$((dWTyF[s,n] and W_sm[s]));
WTFpar.fx[s,n]$((dWTn[s,n] and nw_F[n] and W_sm[s])) = WTFpar.l[s,n]$((dWTn[s,n] and nw_F[n] and W_sm[s]));
WTDpar.fx[s,n]$((dWTn[s,n] and nw_D[n] and W_sm[s])) = WTDpar.l[s,n]$((dWTn[s,n] and nw_D[n] and W_sm[s]));
WTD_alphau.fx[t,m]$((mw_D[m] and txE[t])) = WTD_alphau.l[t,m]$((mw_D[m] and txE[t]));
alphauCal.fx[m]$(mw_D[m]) = alphauCal.l[m]$(mw_D[m]);
gammarCal.fx[m]$(mw_D[m]) = gammarCal.l[m]$(mw_D[m]);
WTD_gr.fx[t,m]$((mw_D[m] and txE[t])) = WTD_gr.l[t,m]$((mw_D[m] and txE[t]));
WTD_ge.fx[t,m]$((mw_D[m] and txE[t])) = WTD_ge.l[t,m]$((mw_D[m] and txE[t]));
WTD_gd.fx[t,m]$((mw_D[m] and txE[t])) = WTD_gd.l[t,m]$((mw_D[m] and txE[t]));
WTD_qSnwCal.fx[n]$(nw_D[n]) = WTD_qSnwCal.l[n]$(nw_D[n]);
WTD_qSnmCal.fx[n]$(nm_D[n]) = WTD_qSnmCal.l[n]$(nm_D[n]);
WTD_qSWECal.fx[n]$(n_wasteE[n]) = WTD_qSWECal.l[n]$(n_wasteE[n]);
WTD_pSnwCal.fx[m]$(mw_D[m]) = WTD_pSnwCal.l[m]$(mw_D[m]);
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
sigma.fx[s,n]$(C_kninp[s,n]) = sigma.l[s,n]$(C_kninp[s,n]);
mu.fx[s,n,nn]$(((C_map[s,n,nn] and ( not (C_endoMu[s,n,nn]))) or C_endoMu[s,n,nn])) = mu.l[s,n,nn]$(((C_map[s,n,nn] and ( not (C_endoMu[s,n,nn]))) or C_endoMu[s,n,nn]));
crra.fx[s]$(C_sm[s]) = crra.l[s]$(C_sm[s]);
discF.fx[s]$(C_sm[s]) = discF.l[s]$(C_sm[s]);
vU_tvc.fx[s]$(C_sm[s]) = vU_tvc.l[s]$(C_sm[s]);
gadj.fx[s]$(C_sm[s]) = gadj.l[s]$(C_sm[s]);
tauD.fx[t,s,n]$(C_input[s,n]) = tauD.l[t,s,n]$(C_input[s,n]);
tauS.fx[t,s,n]$(((C_L[s,n] and ( not ((C_L[s,n] and txE[t])))) or (C_L[s,n] and txE[t]))) = tauS.l[t,s,n]$(((C_L[s,n] and ( not ((C_L[s,n] and txE[t])))) or (C_L[s,n] and txE[t])));
tauLump.fx[t,s]$(C_sm[s]) = tauLump.l[t,s]$(C_sm[s]);
tauS0.fx[t,s,n]$((C_L[s,n] and txE[t])) = tauS0.l[t,s,n]$((C_L[s,n] and txE[t]));
p.fx[t,n]$((C_output_n[n] or C_input_n[n])) = p.l[t,n]$((C_output_n[n] or C_input_n[n]));
Rrate.fx[t] = Rrate.l[t];
vA.fx[t,s]$((C_sm[s] and t0[t])) = vA.l[t,s]$((C_sm[s] and t0[t]));
vA_tvc.fx[s]$(C_sm[s]) = vA_tvc.l[s]$(C_sm[s]);
frisch.fx[s]$(C_sm[s]) = frisch.l[s]$(C_sm[s]);
uWS.fx[t,s,n,m]$((dWSnm[s,n,m] and C_sm[s])) = uWS.l[t,s,n,m]$((dWSnm[s,n,m] and C_sm[s]));
taxRevPar.fx[s]$(C_sm[s]) = taxRevPar.l[s]$(C_sm[s]);
jTerm.fx[s]$(C_sm[s]) = jTerm.l[s]$(C_sm[s]);
Lscale.fx[s]$(C_sm[s]) = Lscale.l[s]$(C_sm[s]);
uWS_D.fx[t,s,m]$((dWS[s,m] and C_sm[s])) = uWS_D.l[t,s,m]$((dWS[s,m] and C_sm[s]));
uWTy.fx[s,n]$((dWTy[s,n] and C_sm[s])) = uWTy.l[s,n]$((dWTy[s,n] and C_sm[s]));
uWTyF.fx[s,n]$((dWTyF[s,n] and C_sm[s])) = uWTyF.l[s,n]$((dWTyF[s,n] and C_sm[s]));
WTFpar.fx[s,n]$((dWTn[s,n] and nw_F[n] and C_sm[s])) = WTFpar.l[s,n]$((dWTn[s,n] and nw_F[n] and C_sm[s]));
WTDpar.fx[s,n]$((dWTn[s,n] and nw_D[n] and C_sm[s])) = WTDpar.l[s,n]$((dWTn[s,n] and nw_D[n] and C_sm[s]));
sigma.fx[s,n]$(G_kninp[s,n]) = sigma.l[s,n]$(G_kninp[s,n]);
mu.fx[s,n,nn]$(((G_map[s,n,nn] and ( not (G_endoMu[s,n,nn]))) or G_endoMu[s,n,nn])) = mu.l[s,n,nn]$(((G_map[s,n,nn] and ( not (G_endoMu[s,n,nn]))) or G_endoMu[s,n,nn]));
tauD.fx[t,s,n]$(G_input[s,n]) = tauD.l[t,s,n]$(G_input[s,n]);
tauLump.fx[t,s]$(((G_sm[s] and ( not ((G_sm[s] and txE[t])))) or (G_sm[s] and txE[t]))) = tauLump.l[t,s]$(((G_sm[s] and ( not ((G_sm[s] and txE[t])))) or (G_sm[s] and txE[t])));
tauLump0.fx[t,s]$((G_sm[s] and txE[t])) = tauLump0.l[t,s]$((G_sm[s] and txE[t]));
vA.fx[t,s]$(G_sm[s]) = vA.l[t,s]$(G_sm[s]);
p.fx[t,n]$(G_input_n[n]) = p.l[t,n]$(G_input_n[n]);
Rrate.fx[t] = Rrate.l[t];
qD.fx[t,s,n]$(((G_output[s,n] and tx0E[t]) or (G_output[s,n] and t0[t]))) = qD.l[t,s,n]$(((G_output[s,n] and tx0E[t]) or (G_output[s,n] and t0[t])));
taxRevPar.fx[s]$(G_sm[s]) = taxRevPar.l[s]$(G_sm[s]);
jTerm.fx[s]$(G_sm[s]) = jTerm.l[s]$(G_sm[s]);
p.fx[t,n]$((T_nF[n] or T_nD[n])) = p.l[t,n]$((T_nF[n] or T_nD[n]));
sigma.fx[s,n]$(T_dExport[s,n]) = sigma.l[s,n]$(T_dExport[s,n]);
tauD.fx[t,s,n]$(T_dExport[s,n]) = tauD.l[t,s,n]$(T_dExport[s,n]);
tauLump.fx[t,s]$(((T_sm[s] and tx0E[t]) or (T_sm[s] and t0[t]))) = tauLump.l[t,s]$(((T_sm[s] and tx0E[t]) or (T_sm[s] and t0[t])));
Fscale.fx[s,n]$(T_dExport[s,n]) = Fscale.l[s,n]$(T_dExport[s,n]);
Fscale_WI.fx[s,m]$((dWS[s,m] and T_sm[s])) = Fscale_WI.l[s,m]$((dWS[s,m] and T_sm[s]));
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
qS.lo[t,s,n]$(((P_output[s,n] and ( not (P_exoQS[s,n])) and tx0[t]) or (P_output[s,n] and ( not (P_exoQS[s,n])) and t0[t]))) = -inf;
qS.up[t,s,n]$(((P_output[s,n] and ( not (P_exoQS[s,n])) and tx0[t]) or (P_output[s,n] and ( not (P_exoQS[s,n])) and t0[t]))) = inf;
pW.lo[t,s,n]$((dWSn[s,n] and P_sm[s])) = -inf;
pW.up[t,s,n]$((dWSn[s,n] and P_sm[s])) = inf;
qWS.lo[t,s,m]$((dWS[s,m] and P_sm[s])) = -inf;
qWS.up[t,s,m]$((dWS[s,m] and P_sm[s])) = inf;
pWext.lo[t,s,m]$((dWS[s,m] and P_sm[s])) = -inf;
pWext.up[t,s,m]$((dWS[s,m] and P_sm[s])) = inf;
pD.lo[t,s,n]$((((W_int[s,n] or W_input[s,n]) or (W_dur[s,n] and txE[t]) or (W_sm[s] and n_ZW[n] and tx0E[t])) or (W_sm[s] and n_ZW[n] and t0[t]))) = -inf;
pD.up[t,s,n]$((((W_int[s,n] or W_input[s,n]) or (W_dur[s,n] and txE[t]) or (W_sm[s] and n_ZW[n] and tx0E[t])) or (W_sm[s] and n_ZW[n] and t0[t]))) = inf;
pS.lo[t,s,n]$(W_output[s,n]) = -inf;
pS.up[t,s,n]$(W_output[s,n]) = inf;
p.lo[t,n]$(((W_endoP[n] and tx0[t]) or (W_endoP[n] and t0[t]))) = -inf;
p.up[t,n]$(((W_endoP[n] and tx0[t]) or (W_endoP[n] and t0[t]))) = inf;
qD.lo[t,s,n]$(((W_int[s,n] or (W_input[s,n] and tx0[t]) or (W_dur[s,n] and tx0[t]) or (W_sm[s] and n_ZW[n] and txE[t])) or (W_input[s,n] and t0[t]))) = -inf;
qD.up[t,s,n]$(((W_int[s,n] or (W_input[s,n] and tx0[t]) or (W_dur[s,n] and tx0[t]) or (W_sm[s] and n_ZW[n] and txE[t])) or (W_input[s,n] and t0[t]))) = inf;
TotalTax.lo[t,s]$(((W_sm[s] and tx0E[t]) or (W_sm[s] and t0[t]))) = -inf;
TotalTax.up[t,s]$(((W_sm[s] and tx0E[t]) or (W_sm[s] and t0[t]))) = inf;
vA.lo[t,s]$(W_sm[s]) = -inf;
vA.up[t,s]$(W_sm[s]) = inf;
divd.lo[t,s]$(W_sm[s]) = -inf;
divd.up[t,s]$(W_sm[s]) = inf;
adjCost.lo[t,s]$((W_sm[s] and txE[t])) = -inf;
adjCost.up[t,s]$((W_sm[s] and txE[t])) = inf;
qS.lo[t,s,n]$(((W_output[s,n] and ( not (W_exoQS[s,n])) and tx0[t]) or (W_output[s,n] and ( not (W_exoQS[s,n])) and t0[t]))) = -inf;
qS.up[t,s,n]$(((W_output[s,n] and ( not (W_exoQS[s,n])) and tx0[t]) or (W_output[s,n] and ( not (W_exoQS[s,n])) and t0[t]))) = inf;
pW.lo[t,s,n]$((dWSn[s,n] and W_sm[s])) = -inf;
pW.up[t,s,n]$((dWSn[s,n] and W_sm[s])) = inf;
qWS.lo[t,s,m]$((dWS[s,m] and W_sm[s])) = -inf;
qWS.up[t,s,m]$((dWS[s,m] and W_sm[s])) = inf;
WTD_W.lo[t,m]$((mw_D[m] and txE[t])) = -inf;
WTD_W.up[t,m]$((mw_D[m] and txE[t])) = inf;
WTD_d.lo[t,m]$((mw_D[m] and txE[t])) = -inf;
WTD_d.up[t,m]$((mw_D[m] and txE[t])) = inf;
WTD_zetaE.lo[t,m]$((mw_D[m] and txE[t])) = -inf;
WTD_zetaE.up[t,m]$((mw_D[m] and txE[t])) = inf;
WTD_r.lo[t,m]$(((mw_D[m] and tx0E[t]) or (mw_D[m] and t0[t]))) = -inf;
WTD_r.up[t,m]$(((mw_D[m] and tx0E[t]) or (mw_D[m] and t0[t]))) = inf;
WTD_a.lo[t,m]$(((mw_D[m] and tx0E[t]) or (mw_D[m] and t0[t]))) = -inf;
WTD_a.up[t,m]$(((mw_D[m] and tx0E[t]) or (mw_D[m] and t0[t]))) = inf;
WTD_e.lo[t,m]$((mw_D[m] and txE[t])) = -inf;
WTD_e.up[t,m]$((mw_D[m] and txE[t])) = inf;
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
pD.lo[t,s,n]$((((C_int[s,n] or C_input[s,n]) or (C_C[s,n] and tx0E[t])) or (C_C[s,n] and t0[t]))) = -inf;
pD.up[t,s,n]$((((C_int[s,n] or C_input[s,n]) or (C_C[s,n] and tx0E[t])) or (C_C[s,n] and t0[t]))) = inf;
qD.lo[t,s,n]$((((C_input[s,n] and tx0E[t]) or (C_int[s,n] or C_output[s,n])) or (C_input[s,n] and t0[t]))) = -inf;
qD.up[t,s,n]$((((C_input[s,n] and tx0E[t]) or (C_int[s,n] or C_output[s,n])) or (C_input[s,n] and t0[t]))) = inf;
pS.lo[t,s,n]$((C_L[s,n] and txE[t])) = -inf;
pS.up[t,s,n]$((C_L[s,n] and txE[t])) = inf;
vU.lo[t,s]$(C_sm[s]) = -inf;
vU.up[t,s]$(C_sm[s]) = inf;
TotalTax.lo[t,s]$(((C_sm[s] and tx0E[t]) or (C_sm[s] and t0[t]))) = -inf;
TotalTax.up[t,s]$(((C_sm[s] and tx0E[t]) or (C_sm[s] and t0[t]))) = inf;
vA.lo[t,s]$((C_sm[s] and tx0[t])) = -inf;
vA.up[t,s]$((C_sm[s] and tx0[t])) = inf;
qS.lo[t,s,n]$(((C_L[s,n] and tx0E[t]) or (C_L[s,n] and t0[t]))) = -inf;
qS.up[t,s,n]$(((C_L[s,n] and tx0E[t]) or (C_L[s,n] and t0[t]))) = inf;
qC.lo[t,s]$((C_sm[s] and txE[t])) = -inf;
qC.up[t,s]$((C_sm[s] and txE[t])) = inf;
pW.lo[t,s,n]$((dWSn[s,n] and C_sm[s])) = -inf;
pW.up[t,s,n]$((dWSn[s,n] and C_sm[s])) = inf;
qWS.lo[t,s,m]$((dWS[s,m] and C_sm[s])) = -inf;
qWS.up[t,s,m]$((dWS[s,m] and C_sm[s])) = inf;
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
qWS.lo[t,s,m]$(((T_sm[s] and dWS[s,m] and tx0E[t]) or (T_sm[s] and dWS[s,m] and t0[t]))) = -inf;
qWS.up[t,s,m]$(((T_sm[s] and dWS[s,m] and tx0E[t]) or (T_sm[s] and dWS[s,m] and t0[t]))) = inf;
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
 solve M_vGRSIntRC2019CGE_B using CNS;
