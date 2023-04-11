$ONEOLCOM
$EOLCOM #
;
OPTION SYSOUT=OFF, SOLPRINT=OFF, LIMROW=0, LIMCOL=0, DECIMALS=6;


# ----------------------------------------------------------------------------------------------------
#  Define function: SolveEmptyNLP
# ----------------------------------------------------------------------------------------------------

sets
	alias_set
	alias_map2
	t
	n
	s
	taxTypes
;

alias(n,nn,nnn);
alias(s,ss);

sets
	alias_[alias_set,alias_map2]
	t0[t]
	tE[t]
	t2E[t]
	tx0[t]
	txE[t]
	tx2E[t]
	tx0E[t]
	tx02E[t]
	map_m_G[s,n,nn]
	map_spinp_m_G[s,n,nn]
	map_spout_m_G[s,n,nn]
	knout_m_G[s,n]
	kninp_m_G[s,n]
	spout_m_G[s,n]
	spinp_m_G[s,n]
	input_m_G[s,n]
	output_m_G[s,n]
	int_m_G[s,n]
	map_m_G_ces[s,n,nn]
	knot_m_G_ces[s,n]
	branch_m_G_ces[s,n]
	knot_o_m_G_ces[s,n]
	knot_no_m_G_ces[s,n]
	branch2o_m_G_ces[s,n]
	branch2no_m_G_ces[s,n]
	endo_mu_m_G[s,n,nn]
	input_n_m_G[n]
	s_m_G[s]
	labor[s,n]
	d_TotalTax[s]
	map_m_HH[s,n,nn]
	map_spinp_m_HH[s,n,nn]
	map_spout_m_HH[s,n,nn]
	knout_m_HH[s,n]
	kninp_m_HH[s,n]
	spout_m_HH[s,n]
	spinp_m_HH[s,n]
	input_m_HH[s,n]
	output_m_HH[s,n]
	int_m_HH[s,n]
	map_m_HH_ces[s,n,nn]
	knot_m_HH_ces[s,n]
	branch_m_HH_ces[s,n]
	knot_o_m_HH_ces[s,n]
	knot_no_m_HH_ces[s,n]
	branch2o_m_HH_ces[s,n]
	branch2no_m_HH_ces[s,n]
	endo_mu_m_HH[s,n,nn]
	L2C_m_HH[s,n,nn]
	labor_m_HH[s,n]
	output_n_m_HH[n]
	input_n_m_HH[n]
	s_m_HH[s]
	s_p[s]
	n_p[n]
	n_F[n]
	s_HH[s]
	s_G[s]
	s_i[s]
	s_f[s]
	dur2inv[s,n,nn]
	dur_p[s,n]
	inv_p[s,n]
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
	nestProduction[s,n,nn]
	nestInvestment[s,n,nn]
	nestHH[s,n,nn]
	L2C[s,n,nn]
	nestG[s,n,nn]
	s_itory[s]
	d_itory[s,n]
	map_m_I[s,n,nn]
	map_spinp_m_I[s,n,nn]
	map_spout_m_I[s,n,nn]
	knout_m_I[s,n]
	kninp_m_I[s,n]
	spout_m_I[s,n]
	spinp_m_I[s,n]
	input_m_I[s,n]
	output_m_I[s,n]
	int_m_I[s,n]
	map_m_I_ces[s,n,nn]
	knot_m_I_ces[s,n]
	branch_m_I_ces[s,n]
	knot_o_m_I_ces[s,n]
	knot_no_m_I_ces[s,n]
	branch2o_m_I_ces[s,n]
	branch2no_m_I_ces[s,n]
	exomu_m_I[s,n,nn]
	endo_qD_m_I[s,n]
	endo_qS_m_I[s,n]
	endo_pS_m_I[s,n]
	dur_m_I[s,n]
	inv_m_I[s,n]
	input_n[n]
	output_n_m_I[n]
	input_n_m_I[n]
	s_m_I[s]
	map_m_P[s,n,nn]
	map_spinp_m_P[s,n,nn]
	map_spout_m_P[s,n,nn]
	knout_m_P[s,n]
	kninp_m_P[s,n]
	spout_m_P[s,n]
	spinp_m_P[s,n]
	input_m_P[s,n]
	output_m_P[s,n]
	int_m_P[s,n]
	map_m_P_ces[s,n,nn]
	knot_m_P_ces[s,n]
	branch_m_P_ces[s,n]
	knot_o_m_P_ces[s,n]
	knot_no_m_P_ces[s,n]
	branch2o_m_P_ces[s,n]
	branch2no_m_P_ces[s,n]
	endo_mu_m_P[s,n,nn]
	endo_qD_m_P[s,n]
	dur_m_P[s,n]
	inv_m_P[s,n]
	output_n_m_P[n]
	input_n_m_P[n]
	s_m_P[s]
	dExport_m_Trade[s,n]
	nOut_m_Trade[n]
	s_m_Trade[s]
;
$GDXIN %rname%
$onMulti
$load alias_set
$load alias_map2
$load t
$load n
$load s
$load taxTypes
$load alias_
$load t0
$load tE
$load t2E
$load tx0
$load txE
$load tx2E
$load tx0E
$load tx02E
$load map_m_G
$load map_spinp_m_G
$load map_spout_m_G
$load knout_m_G
$load kninp_m_G
$load spout_m_G
$load spinp_m_G
$load input_m_G
$load output_m_G
$load int_m_G
$load map_m_G_ces
$load knot_m_G_ces
$load branch_m_G_ces
$load knot_o_m_G_ces
$load knot_no_m_G_ces
$load branch2o_m_G_ces
$load branch2no_m_G_ces
$load endo_mu_m_G
$load input_n_m_G
$load s_m_G
$load labor
$load d_TotalTax
$load map_m_HH
$load map_spinp_m_HH
$load map_spout_m_HH
$load knout_m_HH
$load kninp_m_HH
$load spout_m_HH
$load spinp_m_HH
$load input_m_HH
$load output_m_HH
$load int_m_HH
$load map_m_HH_ces
$load knot_m_HH_ces
$load branch_m_HH_ces
$load knot_o_m_HH_ces
$load knot_no_m_HH_ces
$load branch2o_m_HH_ces
$load branch2no_m_HH_ces
$load endo_mu_m_HH
$load L2C_m_HH
$load labor_m_HH
$load output_n_m_HH
$load input_n_m_HH
$load s_m_HH
$load s_p
$load n_p
$load n_F
$load s_HH
$load s_G
$load s_i
$load s_f
$load dur2inv
$load dur_p
$load inv_p
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
$load nestProduction
$load nestInvestment
$load nestHH
$load L2C
$load nestG
$load s_itory
$load d_itory
$load map_m_I
$load map_spinp_m_I
$load map_spout_m_I
$load knout_m_I
$load kninp_m_I
$load spout_m_I
$load spinp_m_I
$load input_m_I
$load output_m_I
$load int_m_I
$load map_m_I_ces
$load knot_m_I_ces
$load branch_m_I_ces
$load knot_o_m_I_ces
$load knot_no_m_I_ces
$load branch2o_m_I_ces
$load branch2no_m_I_ces
$load exomu_m_I
$load endo_qD_m_I
$load endo_qS_m_I
$load endo_pS_m_I
$load dur_m_I
$load inv_m_I
$load input_n
$load output_n_m_I
$load input_n_m_I
$load s_m_I
$load map_m_P
$load map_spinp_m_P
$load map_spout_m_P
$load knout_m_P
$load kninp_m_P
$load spout_m_P
$load spinp_m_P
$load input_m_P
$load output_m_P
$load int_m_P
$load map_m_P_ces
$load knot_m_P_ces
$load branch_m_P_ces
$load knot_o_m_P_ces
$load knot_no_m_P_ces
$load branch2o_m_P_ces
$load branch2no_m_P_ces
$load endo_mu_m_P
$load endo_qD_m_P
$load dur_m_P
$load inv_m_P
$load output_n_m_P
$load input_n_m_P
$load s_m_P
$load dExport_m_Trade
$load nOut_m_Trade
$load s_m_Trade
$GDXIN
$offMulti;

parameters
	R_LR
	g_LR
	infl_LR
	qnorm_inp[t,s,n]
	qnorm_out[t,s,n]
	inventoryAR[s,n]
;
$GDXIN %rname%
$onMulti
$load R_LR
$load g_LR
$load infl_LR
$load qnorm_inp
$load qnorm_out
$load inventoryAR
$GDXIN
$offMulti;

variables
	pD[t,s,n]
	qD[t,s,n]
	qiv_inp[t,s,n]
	TotalTax[t,s]
	tauS[t,s,n]
	sigma[s,n]
	mu[s,n,nn]
	tauD0[t,s,n]
	p[t,n]
	tauG_calib
	tauD[t,s,n]
	jTerm[s]
	qS[t,s,n]
	qiv_out[t,s,n]
	pS[t,s,n]
	eta[s,n]
	frisch[s,n]
	crra[s,n]
	tauLump[t,s]
	Lscale[s,n]
	vTax[t,s,taxTypes]
	vD[t,s,n]
	vD_dur[t,s,n]
	vD_inv[t,s,n]
	vD_depr[t,s,n]
	rDepr[t,s,n]
	vS[t,s,n]
	pD_dur[t,s,n]
	outShare[t,s,n]
	ic[t,s]
	markup[s]
	Rrate[t]
	icpar[s,n]
	K_tvc[s,n]
	Fscale[s,n]
;
$GDXIN %rname%
$onMulti
$load pD
$load qD
$load qiv_inp
$load TotalTax
$load tauS
$load sigma
$load mu
$load tauD0
$load p
$load tauG_calib
$load tauD
$load jTerm
$load qS
$load qiv_out
$load pS
$load eta
$load frisch
$load crra
$load tauLump
$load Lscale
$load vTax
$load vD
$load vD_dur
$load vD_inv
$load vD_depr
$load rDepr
$load vS
$load pD_dur
$load outShare
$load ic
$load markup
$load Rrate
$load icpar
$load K_tvc
$load Fscale
$GDXIN
$offMulti;




# ----------------------------------------------B_m_G_ces---------------------------------------------
#  Initialize B_m_G_ces equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_zp_m_G_ces[t,s,n];
E_zp_m_G_ces[t,s,n]$(knot_m_g_ces[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(map_m_G_ces[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_q_m_G_ces[t,s,n];
E_q_m_G_ces[t,s,n]$(branch_m_g_ces[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(map_m_G_ces[s,nn,n]), mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qD[t,s,nn]);

# ----------------------------------------------------------------------------------------------------
#  Define B_m_G_ces model
# ----------------------------------------------------------------------------------------------------
Model B_m_G_ces /
E_zp_m_G_ces, E_q_m_G_ces
/;




# ----------------------------------------------B_m_G_BSA---------------------------------------------
#  Initialize B_m_G_BSA equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_pw_m_G_BSA[t,s,n];
E_pw_m_G_BSA[t,s,n]$(input_m_g[s,n] and txe[t]).. 		pD[t,s,n]  =E=  p[t,n]+tauD[t,s,n];
EQUATION E_taxRev_m_G_BSA[t,s];
E_taxRev_m_G_BSA[t,s]$(s_m_g[s] and txe[t]).. 	TotalTax[t,s]  =E=  sum(n$(input_m_G[s,n]), tauD[t,s,n] * qD[t,s,n]);

# ----------------------------------------------------------------------------------------------------
#  Define B_m_G_BSA model
# ----------------------------------------------------------------------------------------------------
Model B_m_G_BSA /
E_pw_m_G_BSA, E_taxRev_m_G_BSA
/;




# ----------------------------------------------B_m_G_CSA---------------------------------------------
#  Initialize B_m_G_CSA equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_ctaxRev_m_G_CSA[t,s,n];
E_ctaxRev_m_G_CSA[t,s,n]$(input_m_g[s,n] and txe[t]).. 	tauD[t,s,n]  =E=  tauD0[t,s,n]*tauG_calib;

# ----------------------------------------------------------------------------------------------------
#  Define B_m_G_CSA model
# ----------------------------------------------------------------------------------------------------
Model B_m_G_CSA /
E_ctaxRev_m_G_CSA
/;




# ----------------------------------------------B_m_G_bb----------------------------------------------
#  Initialize B_m_G_bb equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_bb_m_G_bb[t,s];
E_bb_m_G_bb[t,s]$(s_m_g[s] and txe[t]).. 	jTerm[s]  =E=  sum(ss$(d_TotalTax[ss]), TotalTax[t,ss])-sum(n$(input_m_G[s,n]), pD[t,s,n]*qD[t,s,n]);

# ----------------------------------------------------------------------------------------------------
#  Define B_m_G_bb model
# ----------------------------------------------------------------------------------------------------
Model B_m_G_bb /
E_bb_m_G_bb
/;




# ---------------------------------------------B_m_HH_ces---------------------------------------------
#  Initialize B_m_HH_ces equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_zp_m_HH_ces[t,s,n];
E_zp_m_HH_ces[t,s,n]$(knot_m_hh_ces[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(map_m_HH_ces[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_q_m_HH_ces[t,s,n];
E_q_m_HH_ces[t,s,n]$(branch_m_hh_ces[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(map_m_HH_ces[s,nn,n]), mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qD[t,s,nn]);

# ----------------------------------------------------------------------------------------------------
#  Define B_m_HH_ces model
# ----------------------------------------------------------------------------------------------------
Model B_m_HH_ces /
E_zp_m_HH_ces, E_q_m_HH_ces
/;




# --------------------------------------------B_m_HH_labor--------------------------------------------
#  Initialize B_m_HH_labor equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_labor_m_HH_labor[t,s,n];
E_labor_m_HH_labor[t,s,n]$(labor_m_hh[s,n] and txe[t]).. 	qS[t,s,n]	 =E= 	Lscale[s,n] * ( sum(nn$(L2C_m_HH[s,n,nn]), pS[t,s,n]/(pD[t,s,nn]*(qD[t,s,nn]**(crra[s,nn]))))**(frisch[s,n]));

# ----------------------------------------------------------------------------------------------------
#  Define B_m_HH_labor model
# ----------------------------------------------------------------------------------------------------
Model B_m_HH_labor /
E_labor_m_HH_labor
/;




# ----------------------------------------------B_m_HH_pw---------------------------------------------
#  Initialize B_m_HH_pw equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_pwOut_m_HH_pw[t,s,n];
E_pwOut_m_HH_pw[t,s,n]$(labor_m_hh[s,n] and txe[t]).. 	pS[t,s,n] 		 =E=  p[t,n]-tauS[t,s,n];
EQUATION E_pwInp_m_HH_pw[t,s,n];
E_pwInp_m_HH_pw[t,s,n]$(input_m_hh[s,n] and txe[t]).. 	pD[t,s,n]		 =E=  p[t,n]+tauD[t,s,n];
EQUATION E_TaxRev_m_HH_pw[t,s];
E_TaxRev_m_HH_pw[t,s]$(s_m_hh[s] and txe[t]).. 		TotalTax[t,s]	 =E=  tauLump[t,s]+sum(n$(input_m_HH[s,n]), tauD[t,s,n] * qD[t,s,n])+sum(n$(labor_m_HH[s,n]), tauS[t,s,n]*qS[t,s,n]);
EQUATION E_sp_m_HH_pw[t,s];
E_sp_m_HH_pw[t,s]$(s_m_hh[s] and txe[t]).. 			jTerm[s]		 =E=  sum(n$(labor_m_HH[s,n]), pS[t,s,n]*qS[t,s,n]) - sum(n$(input_m_HH[s,n]), pD[t,s,n]*qD[t,s,n])-tauLump[t,s];

# ----------------------------------------------------------------------------------------------------
#  Define B_m_HH_pw model
# ----------------------------------------------------------------------------------------------------
Model B_m_HH_pw /
E_pwOut_m_HH_pw, E_pwInp_m_HH_pw, E_TaxRev_m_HH_pw, E_sp_m_HH_pw
/;




# ----------------------------------------------B_m_itory---------------------------------------------
#  Initialize B_m_itory equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_m_itory[t,s,n];
E_m_itory[t,s,n]$(d_itory[s,n] and tx0e[t]).. 	qD[t,s,n]  =E=  inventoryAR[s,n] * qD[t-1,s,n];

# ----------------------------------------------------------------------------------------------------
#  Define B_m_itory model
# ----------------------------------------------------------------------------------------------------
Model B_m_itory /
E_m_itory
/;




# ----------------------------------------------B_m_I_ces---------------------------------------------
#  Initialize B_m_I_ces equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_zp_out_m_I_ces[t,s,n];
E_zp_out_m_I_ces[t,s,n]$(knot_o_m_i_ces[s,n] and txe[t]).. 	pS[t,s,n]*qS[t,s,n]  =E=  sum(nn$(map_m_I_ces[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_zp_nout_m_I_ces[t,s,n];
E_zp_nout_m_I_ces[t,s,n]$(knot_no_m_i_ces[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(map_m_I_ces[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_q_out_m_I_ces[t,s,n];
E_q_out_m_I_ces[t,s,n]$(branch2o_m_i_ces[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(map_m_I_ces[s,nn,n]), mu[s,nn,n] * (pS[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qS[t,s,nn]);
EQUATION E_q_nout_m_I_ces[t,s,n];
E_q_nout_m_I_ces[t,s,n]$(branch2no_m_i_ces[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(map_m_I_ces[s,nn,n]), mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qD[t,s,nn]);

# ----------------------------------------------------------------------------------------------------
#  Define B_m_I_ces model
# ----------------------------------------------------------------------------------------------------
Model B_m_I_ces /
E_zp_out_m_I_ces, E_zp_nout_m_I_ces, E_q_out_m_I_ces, E_q_nout_m_I_ces
/;




# ----------------------------------------------B_m_I_IC----------------------------------------------
#  Initialize B_m_I_IC equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_lom_m_I_IC[t,s,n];
E_lom_m_I_IC[t,s,n]$(dur_m_i[s,n] and txe[t]).. 		qD[t+1,s,n]	 =E=  (qD[t,s,n]*(1-rDepr[t,s,n])+sum(nn$(dur2inv[s,n,nn]), qD[t,s,nn]))/(1+g_LR);
EQUATION E_pk_m_I_IC[t,s,n];
E_pk_m_I_IC[t,s,n]$(dur_m_i[s,n] and tx02e[t]).. 	pD[t,s,n]	 =E=  sqrt(sqr(sum(nn$(dur2inv[s,n,nn]), Rrate[t]*pD[t-1,s,nn]*(1+icpar[s,n]*(qD[t-1,s,nn]/qD[t-1,s,n]-(rDepr[t-1,s,n]+g_LR)))/(1+infl_LR)+pD[t,s,nn]*(icpar[s,n]*0.5*(sqr(rDepr[t,s,n]+g_LR)-sqr(qD[t,s,nn]/qD[t,s,n]))-(1-rDepr[t,s,n])*(1+icpar[s,n]*(qD[t,s,nn]/qD[t,s,n]-(rDepr[t,s,n]+g_LR)))))));
EQUATION E_pkT_m_I_IC[t,s,n];
E_pkT_m_I_IC[t,s,n]$(dur_m_i[s,n] and t2e[t]).. 		pD[t,s,n]	 =E=  sum(nn$(dur2inv[s,n,nn]), Rrate[t]*pD[t-1,s,nn] * (1+icpar[s,n]*(qD[t-1,s,nn]/qD[t-1,s,n]-(rDepr[t-1,s,n]+g_LR)))/(1+infl_LR) + (rDepr[t,s,n]-1)*pD[t,s,nn]);
EQUATION E_Ktvc_m_I_IC[t,s,n];
E_Ktvc_m_I_IC[t,s,n]$(dur_m_i[s,n] and te[t]).. 		qD[t,s,n]	 =E=  (1+K_tvc[s,n])*qD[t-1,s,n];
EQUATION E_instcost_m_I_IC[t,s];
E_instcost_m_I_IC[t,s]$(s_m_i[s] and txe[t]).. 		ic[t,s] 	 =E=  sum([n,nn]$(dur2inv[s,n,nn]), pD[t,s,nn] * icpar[s,n]*0.5*qD[t,s,n]*sqr(qD[t,s,nn]/qD[t,s,n]-(rDepr[t,s,n]+g_LR)));

# ----------------------------------------------------------------------------------------------------
#  Define B_m_I_IC model
# ----------------------------------------------------------------------------------------------------
Model B_m_I_IC /
E_lom_m_I_IC, E_pk_m_I_IC, E_pkT_m_I_IC, E_Ktvc_m_I_IC, E_instcost_m_I_IC
/;




# --------------------------------------------B_m_I_pWedge--------------------------------------------
#  Initialize B_m_I_pWedge equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_pwInp_m_I_pWedge[t,s,n];
E_pwInp_m_I_pWedge[t,s,n]$(input_m_i[s,n] and txe[t]).. 			pD[t,s,n]		 =E=  p[t,n]+tauD[t,s,n];
EQUATION E_pwOut_m_I_pWedge[t,s,n];
E_pwOut_m_I_pWedge[t,s,n]$(output_m_i[s,n] and txe[t]).. 		p[t,n] 			 =E=  (1+markup[s])*(pS[t,s,n]+tauS[t,s,n]+(outShare[t,s,n]/qS[t,s,n])*(ic[t,s]+tauLump[t,s]));
EQUATION E_outShare_m_I_pWedge[t,s,n];
E_outShare_m_I_pWedge[t,s,n]$(output_m_i[s,n] and txe[t]).. 		outShare[t,s,n]  =E=  qS[t,s,n]*pS[t,s,n]/(sum(nn$(output_m_I[s,nn]), qS[t,s,nn]*pS[t,s,nn]));
EQUATION E_TaxRev_m_I_pWedge[t,s];
E_TaxRev_m_I_pWedge[t,s]$(s_m_i[s] and txe[t]).. 				TotalTax[t,s]	 =E=  tauLump[t,s]+sum(n$(input_m_I[s,n]), tauD[t,s,n] * qD[t,s,n])+sum(n$(output_m_I[s,n]), tauS[t,s,n]*qS[t,s,n]);

# ----------------------------------------------------------------------------------------------------
#  Define B_m_I_pWedge model
# ----------------------------------------------------------------------------------------------------
Model B_m_I_pWedge /
E_pwInp_m_I_pWedge, E_pwOut_m_I_pWedge, E_outShare_m_I_pWedge, E_TaxRev_m_I_pWedge
/;




# ----------------------------------------------B_m_P_ces---------------------------------------------
#  Initialize B_m_P_ces equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_zp_out_m_P_ces[t,s,n];
E_zp_out_m_P_ces[t,s,n]$(knot_o_m_p_ces[s,n] and txe[t]).. 	pS[t,s,n]*qS[t,s,n]  =E=  sum(nn$(map_m_P_ces[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_zp_nout_m_P_ces[t,s,n];
E_zp_nout_m_P_ces[t,s,n]$(knot_no_m_p_ces[s,n] and txe[t]).. 	pD[t,s,n]*qD[t,s,n]  =E=  sum(nn$(map_m_P_ces[s,n,nn]), qD[t,s,nn]*pD[t,s,nn]);
EQUATION E_q_out_m_P_ces[t,s,n];
E_q_out_m_P_ces[t,s,n]$(branch2o_m_p_ces[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(map_m_P_ces[s,nn,n]), mu[s,nn,n] * (pS[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qS[t,s,nn]);
EQUATION E_q_nout_m_P_ces[t,s,n];
E_q_nout_m_P_ces[t,s,n]$(branch2no_m_p_ces[s,n] and txe[t]).. 	qD[t,s,n]  =E=  sum(nn$(map_m_P_ces[s,nn,n]), mu[s,nn,n] * (pD[t,s,nn]/pD[t,s,n])**(sigma[s,nn]) * qD[t,s,nn]);

# ----------------------------------------------------------------------------------------------------
#  Define B_m_P_ces model
# ----------------------------------------------------------------------------------------------------
Model B_m_P_ces /
E_zp_out_m_P_ces, E_zp_nout_m_P_ces, E_q_out_m_P_ces, E_q_nout_m_P_ces
/;




# ----------------------------------------------B_m_P_IC----------------------------------------------
#  Initialize B_m_P_IC equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_lom_m_P_IC[t,s,n];
E_lom_m_P_IC[t,s,n]$(dur_m_p[s,n] and txe[t]).. 		qD[t+1,s,n]	 =E=  (qD[t,s,n]*(1-rDepr[t,s,n])+sum(nn$(dur2inv[s,n,nn]), qD[t,s,nn]))/(1+g_LR);
EQUATION E_pk_m_P_IC[t,s,n];
E_pk_m_P_IC[t,s,n]$(dur_m_p[s,n] and tx02e[t]).. 	pD[t,s,n]	 =E=  sqrt(sqr(sum(nn$(dur2inv[s,n,nn]), Rrate[t]*pD[t-1,s,nn]*(1+icpar[s,n]*(qD[t-1,s,nn]/qD[t-1,s,n]-(rDepr[t-1,s,n]+g_LR)))/(1+infl_LR)+pD[t,s,nn]*(icpar[s,n]*0.5*(sqr(rDepr[t,s,n]+g_LR)-sqr(qD[t,s,nn]/qD[t,s,n]))-(1-rDepr[t,s,n])*(1+icpar[s,n]*(qD[t,s,nn]/qD[t,s,n]-(rDepr[t,s,n]+g_LR)))))));
EQUATION E_pkT_m_P_IC[t,s,n];
E_pkT_m_P_IC[t,s,n]$(dur_m_p[s,n] and t2e[t]).. 		pD[t,s,n]	 =E=  sum(nn$(dur2inv[s,n,nn]), Rrate[t]*pD[t-1,s,nn] * (1+icpar[s,n]*(qD[t-1,s,nn]/qD[t-1,s,n]-(rDepr[t-1,s,n]+g_LR)))/(1+infl_LR) + (rDepr[t,s,n]-1)*pD[t,s,nn]);
EQUATION E_Ktvc_m_P_IC[t,s,n];
E_Ktvc_m_P_IC[t,s,n]$(dur_m_p[s,n] and te[t]).. 		qD[t,s,n]	 =E=  (1+K_tvc[s,n])*qD[t-1,s,n];
EQUATION E_instcost_m_P_IC[t,s];
E_instcost_m_P_IC[t,s]$(s_m_p[s] and txe[t]).. 		ic[t,s] 	 =E=  sum([n,nn]$(dur2inv[s,n,nn]), pD[t,s,nn] * icpar[s,n]*0.5*qD[t,s,n]*sqr(qD[t,s,nn]/qD[t,s,n]-(rDepr[t,s,n]+g_LR)));

# ----------------------------------------------------------------------------------------------------
#  Define B_m_P_IC model
# ----------------------------------------------------------------------------------------------------
Model B_m_P_IC /
E_lom_m_P_IC, E_pk_m_P_IC, E_pkT_m_P_IC, E_Ktvc_m_P_IC, E_instcost_m_P_IC
/;




# --------------------------------------------B_m_P_pWedge--------------------------------------------
#  Initialize B_m_P_pWedge equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_pwInp_m_P_pWedge[t,s,n];
E_pwInp_m_P_pWedge[t,s,n]$(input_m_p[s,n] and txe[t]).. 			pD[t,s,n]		 =E=  p[t,n]+tauD[t,s,n];
EQUATION E_pwOut_m_P_pWedge[t,s,n];
E_pwOut_m_P_pWedge[t,s,n]$(output_m_p[s,n] and txe[t]).. 		p[t,n] 			 =E=  (1+markup[s])*(pS[t,s,n]+tauS[t,s,n]+(outShare[t,s,n]/qS[t,s,n])*(ic[t,s]+tauLump[t,s]));
EQUATION E_outShare_m_P_pWedge[t,s,n];
E_outShare_m_P_pWedge[t,s,n]$(output_m_p[s,n] and txe[t]).. 		outShare[t,s,n]  =E=  qS[t,s,n]*pS[t,s,n]/(sum(nn$(output_m_P[s,nn]), qS[t,s,nn]*pS[t,s,nn]));
EQUATION E_TaxRev_m_P_pWedge[t,s];
E_TaxRev_m_P_pWedge[t,s]$(s_m_p[s] and txe[t]).. 				TotalTax[t,s]	 =E=  tauLump[t,s]+sum(n$(input_m_P[s,n]), tauD[t,s,n] * qD[t,s,n])+sum(n$(output_m_P[s,n]), tauS[t,s,n]*qS[t,s,n]);

# ----------------------------------------------------------------------------------------------------
#  Define B_m_P_pWedge model
# ----------------------------------------------------------------------------------------------------
Model B_m_P_pWedge /
E_pwInp_m_P_pWedge, E_pwOut_m_P_pWedge, E_outShare_m_P_pWedge, E_TaxRev_m_P_pWedge
/;




# ----------------------------------------------B_m_Trade---------------------------------------------
#  Initialize B_m_Trade equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_armington_m_Trade[t,s,n];
E_armington_m_Trade[t,s,n]$(dexport_m_trade[s,n] and txe[t]).. 	qD[t,s,n]		 =E=  sum(nn$(dom2for[n,nn]), Fscale[s,n] * (p[t,nn]/pD[t,s,n]))**(sigma[s,n]);
EQUATION E_pwInp_m_Trade[t,s,n];
E_pwInp_m_Trade[t,s,n]$(dexport_m_trade[s,n] and txe[t]).. 		pD[t,s,n]		 =E=  p[t,n] + tauD[t,s,n];
EQUATION E_TaxRev_m_Trade[t,s];
E_TaxRev_m_Trade[t,s]$(s_m_trade[s] and txe[t]).. 				TotalTax[t,s]	 =E=  tauLump[t,s]+sum(n$(dExport_m_Trade[s,n]), tauD[t,s,n]*qD[t,s,n]);

# ----------------------------------------------------------------------------------------------------
#  Define B_m_Trade model
# ----------------------------------------------------------------------------------------------------
Model B_m_Trade /
E_armington_m_Trade, E_pwInp_m_Trade, E_TaxRev_m_Trade
/;




# ------------------------------------------B_m_equi_baseline-----------------------------------------
#  Initialize B_m_equi_baseline equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_equi_m_equi[t,n];
E_equi_m_equi[t,n]$(nequi[n] and txe[t]).. 	 sum(s$(d_qS[s,n]), qS[t,s,n])  =E=  sum(s$(d_qD[s,n]), qD[t,s,n]);

# ----------------------------------------------------------------------------------------------------
#  Define B_m_equi_baseline model
# ----------------------------------------------------------------------------------------------------
Model B_m_equi_baseline /
E_equi_m_equi
/;


# ----------------------------------------B_m_equi_calibration----------------------------------------
#  Initialize B_m_equi_calibration equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_equi_m_equi_tx0E[t,n];
E_equi_m_equi_tx0E[t,n]$(nequi[n] and tx0e[t]).. 	 sum(s$(d_qS[s,n]), qS[t,s,n])  =E=  sum(s$(d_qD[s,n]), qD[t,s,n]);

# ----------------------------------------------------------------------------------------------------
#  Define B_m_equi_calibration model
# ----------------------------------------------------------------------------------------------------
Model B_m_equi_calibration /
E_equi_m_equi_tx0E
/;


sigma.fx[s,n]$((kninp_m_G[s,n] or kninp_m_HH[s,n] or kninp_m_I[s,n] or kninp_m_P[s,n] or dExport_m_Trade[s,n])) = sigma.l[s,n];
mu.fx[s,n,nn]$(((map_m_G[s,n,nn] and ( not (endo_mu_m_G[s,n,nn]))) or endo_mu_m_G[s,n,nn] or (map_m_HH[s,n,nn] and ( not (endo_mu_m_HH[s,n,nn]))) or endo_mu_m_HH[s,n,nn] or exomu_m_I[s,n,nn] or (map_m_I[s,n,nn] and ( not (exomu_m_I[s,n,nn]))) or (map_m_P[s,n,nn] and ( not (endo_mu_m_P[s,n,nn]))) or endo_mu_m_P[s,n,nn])) = mu.l[s,n,nn];
tauD0.fx[t,s,n]$(input_m_G[s,n]) = tauD0.l[t,s,n];
TotalTax.fx[t,s]$((d_TotalTax[s] and ( not (s_m_G[s])))) = TotalTax.l[t,s];
qD.fx[t,s,n]$((output_m_G[s,n] or (t0[t] and d_itory[s,n]) or (dur_m_I[s,n] and t0[t]) or (dur_m_P[s,n] and t0[t]))) = qD.l[t,s,n];
p.fx[t,n]$((input_n_m_G[n] or (output_n_m_HH[n] or input_n_m_HH[n]) or (input_n_m_I[n] and ( not (output_n_m_I[n]))) or (input_n_m_P[n] and ( not (output_n_m_P[n]))) or nOut_m_Trade[n])) = p.l[t,n];
tauG_calib.fx = tauG_calib.l;
tauD.fx[t,s,n]$((input_m_G[s,n] or input_m_HH[s,n] or input_m_I[s,n] or input_m_P[s,n] or dExport_m_Trade[s,n])) = tauD.l[t,s,n];
jTerm.fx[s]$((s_m_G[s] or s_m_HH[s])) = jTerm.l[s];
eta.fx[s,n]$((knout_m_HH[s,n] or knout_m_I[s,n] or knout_m_P[s,n])) = eta.l[s,n];
frisch.fx[s,n]$(labor_m_HH[s,n]) = frisch.l[s,n];
crra.fx[s,n]$(output_m_HH[s,n]) = crra.l[s,n];
tauS.fx[t,s,n]$((labor_m_HH[s,n] or output_m_I[s,n] or output_m_P[s,n])) = tauS.l[t,s,n];
tauLump.fx[t,s]$(((s_m_HH[s] and tx0E[t]) or (s_m_HH[s] and t0[t]) or (s_m_I[s] and tx0E[t]) or (s_m_I[s] and t0[t]) or (s_m_P[s] and tx0E[t]) or (s_m_P[s] and t0[t]) or (s_m_Trade[s] and tx0E[t]) or (s_m_Trade[s] and t0[t]))) = tauLump.l[t,s];
Lscale.fx[s,n]$(labor_m_HH[s,n]) = Lscale.l[s,n];
qS.fx[t,s,n]$(((output_m_I[s,n] and ( not ((endo_qS_m_I[s,n] and t0[t])))) or (endo_qS_m_I[s,n] and t0[t]) or output_m_P[s,n])) = qS.l[t,s,n];
markup.fx[s]$((s_m_I[s] or s_m_P[s])) = markup.l[s];
Rrate.fx[t] = Rrate.l[t];
rDepr.fx[t,s,n]$((dur_m_I[s,n] or dur_m_P[s,n])) = rDepr.l[t,s,n];
icpar.fx[s,n]$((dur_m_I[s,n] or dur_m_P[s,n])) = icpar.l[s,n];
K_tvc.fx[s,n]$((dur_m_I[s,n] or dur_m_P[s,n])) = K_tvc.l[s,n];
Fscale.fx[s,n]$(dExport_m_Trade[s,n]) = Fscale.l[s,n];
pD.lo[t,s,n]$(((int_m_G[s,n] or input_m_G[s,n] or output_m_G[s,n]) or ((int_m_HH[s,n] or input_m_HH[s,n]) or (output_m_HH[s,n] and tx0E[t])) or (output_m_HH[s,n] and t0[t]) or (int_m_I[s,n] or input_m_I[s,n]) or (dur_m_I[s,n] and txE[t]) or (int_m_P[s,n] or input_m_P[s,n]) or (dur_m_P[s,n] and txE[t]) or dExport_m_Trade[s,n])) = -inf;
pD.up[t,s,n]$(((int_m_G[s,n] or input_m_G[s,n] or output_m_G[s,n]) or ((int_m_HH[s,n] or input_m_HH[s,n]) or (output_m_HH[s,n] and tx0E[t])) or (output_m_HH[s,n] and t0[t]) or (int_m_I[s,n] or input_m_I[s,n]) or (dur_m_I[s,n] and txE[t]) or (int_m_P[s,n] or input_m_P[s,n]) or (dur_m_P[s,n] and txE[t]) or dExport_m_Trade[s,n])) = inf;
qD.lo[t,s,n]$((((input_m_G[s,n] and tx0E[t]) or int_m_G[s,n]) or (input_m_G[s,n] and t0[t]) or ((input_m_HH[s,n] and tx0E[t]) or (int_m_HH[s,n] or output_m_HH[s,n])) or (input_m_HH[s,n] and t0[t]) or (tx0E[t] and d_itory[s,n]) or (((int_m_I[s,n] or input_m_I[s,n]) and tx0[t]) or (endo_qD_m_I[s,n] and t0[t])) or (((int_m_I[s,n] or input_m_I[s,n]) and t0[t]) and ( not ((endo_qD_m_I[s,n] and t0[t])))) or (dur_m_I[s,n] and tx0[t]) or (int_m_P[s,n] or (input_m_P[s,n] and tx0[t]) or (endo_qD_m_P[s,n] and t0[t])) or ((input_m_P[s,n] and t0[t]) and ( not ((endo_qD_m_P[s,n] and t0[t])))) or (dur_m_P[s,n] and tx0[t]) or (dExport_m_Trade[s,n] and tx0E[t]) or (dExport_m_Trade[s,n] and t0[t]))) = -inf;
qD.up[t,s,n]$((((input_m_G[s,n] and tx0E[t]) or int_m_G[s,n]) or (input_m_G[s,n] and t0[t]) or ((input_m_HH[s,n] and tx0E[t]) or (int_m_HH[s,n] or output_m_HH[s,n])) or (input_m_HH[s,n] and t0[t]) or (tx0E[t] and d_itory[s,n]) or (((int_m_I[s,n] or input_m_I[s,n]) and tx0[t]) or (endo_qD_m_I[s,n] and t0[t])) or (((int_m_I[s,n] or input_m_I[s,n]) and t0[t]) and ( not ((endo_qD_m_I[s,n] and t0[t])))) or (dur_m_I[s,n] and tx0[t]) or (int_m_P[s,n] or (input_m_P[s,n] and tx0[t]) or (endo_qD_m_P[s,n] and t0[t])) or ((input_m_P[s,n] and t0[t]) and ( not ((endo_qD_m_P[s,n] and t0[t])))) or (dur_m_P[s,n] and tx0[t]) or (dExport_m_Trade[s,n] and tx0E[t]) or (dExport_m_Trade[s,n] and t0[t]))) = inf;
qiv_inp.lo[t,s,n]$((spinp_m_G[s,n] or spinp_m_HH[s,n] or spinp_m_I[s,n] or spinp_m_P[s,n])) = -inf;
qiv_inp.up[t,s,n]$((spinp_m_G[s,n] or spinp_m_HH[s,n] or spinp_m_I[s,n] or spinp_m_P[s,n])) = inf;
TotalTax.lo[t,s]$(((s_m_G[s] and tx0E[t]) or (s_m_G[s] and t0[t]) or (s_m_HH[s] and tx0E[t]) or (s_m_HH[s] and t0[t]) or (s_m_I[s] and tx0E[t]) or (s_m_I[s] and t0[t]) or (s_m_P[s] and tx0E[t]) or (s_m_P[s] and t0[t]) or (s_m_Trade[s] and tx0E[t]) or (s_m_Trade[s] and t0[t]))) = -inf;
TotalTax.up[t,s]$(((s_m_G[s] and tx0E[t]) or (s_m_G[s] and t0[t]) or (s_m_HH[s] and tx0E[t]) or (s_m_HH[s] and t0[t]) or (s_m_I[s] and tx0E[t]) or (s_m_I[s] and t0[t]) or (s_m_P[s] and tx0E[t]) or (s_m_P[s] and t0[t]) or (s_m_Trade[s] and tx0E[t]) or (s_m_Trade[s] and t0[t]))) = inf;
tauS.lo[t,s,n]$(((labor[s,n] and tx0E[t]) or (labor[s,n] and t0[t]))) = -inf;
tauS.up[t,s,n]$(((labor[s,n] and tx0E[t]) or (labor[s,n] and t0[t]))) = inf;
qS.lo[t,s,n]$(((labor_m_HH[s,n] and tx0E[t]) or (labor_m_HH[s,n] and t0[t]) or (d_qSEqui[s,n] and tx0E[t]) or (d_qSEqui[s,n] and t0[t]))) = -inf;
qS.up[t,s,n]$(((labor_m_HH[s,n] and tx0E[t]) or (labor_m_HH[s,n] and t0[t]) or (d_qSEqui[s,n] and tx0E[t]) or (d_qSEqui[s,n] and t0[t]))) = inf;
qiv_out.lo[t,s,n]$((spout_m_HH[s,n] or spout_m_I[s,n] or spout_m_P[s,n])) = -inf;
qiv_out.up[t,s,n]$((spout_m_HH[s,n] or spout_m_I[s,n] or spout_m_P[s,n])) = inf;
pS.lo[t,s,n]$((labor_m_HH[s,n] or output_m_I[s,n] or output_m_P[s,n])) = -inf;
pS.up[t,s,n]$((labor_m_HH[s,n] or output_m_I[s,n] or output_m_P[s,n])) = inf;
p.lo[t,n]$(((output_n_m_I[n] and tx0[t]) or (output_n_m_I[n] and t0[t]) or (output_n_m_P[n] and tx0[t]) or (output_n_m_P[n] and t0[t]) or (d_pEqui[n] and tx0E[t]) or (d_pEqui[n] and t0[t]))) = -inf;
p.up[t,n]$(((output_n_m_I[n] and tx0[t]) or (output_n_m_I[n] and t0[t]) or (output_n_m_P[n] and tx0[t]) or (output_n_m_P[n] and t0[t]) or (d_pEqui[n] and tx0E[t]) or (d_pEqui[n] and t0[t]))) = inf;
outShare.lo[t,s,n]$((output_m_I[s,n] or output_m_P[s,n])) = -inf;
outShare.up[t,s,n]$((output_m_I[s,n] or output_m_P[s,n])) = inf;
ic.lo[t,s]$(((s_m_I[s] and txE[t]) or (s_m_P[s] and txE[t]))) = -inf;
ic.up[t,s]$(((s_m_I[s] and txE[t]) or (s_m_P[s] and txE[t]))) = inf;

# ----------------------------------------------------------------------------------------------------
#  Define m_GE_2018_B model
# ----------------------------------------------------------------------------------------------------
Model m_GE_2018_B /
E_zp_m_G_ces, E_q_m_G_ces, E_pw_m_G_BSA, E_taxRev_m_G_BSA, E_bb_m_G_bb, E_zp_m_HH_ces, E_q_m_HH_ces, E_labor_m_HH_labor, E_pwOut_m_HH_pw, E_pwInp_m_HH_pw, E_TaxRev_m_HH_pw, E_sp_m_HH_pw, E_m_itory, E_zp_out_m_I_ces, E_zp_nout_m_I_ces, E_q_out_m_I_ces, E_q_nout_m_I_ces, E_lom_m_I_IC, E_pk_m_I_IC, E_pkT_m_I_IC, E_Ktvc_m_I_IC, E_instcost_m_I_IC, E_pwInp_m_I_pWedge, E_pwOut_m_I_pWedge, E_outShare_m_I_pWedge, E_TaxRev_m_I_pWedge, E_zp_out_m_P_ces, E_zp_nout_m_P_ces, E_q_out_m_P_ces, E_q_nout_m_P_ces, E_lom_m_P_IC, E_pk_m_P_IC, E_pkT_m_P_IC, E_Ktvc_m_P_IC, E_instcost_m_P_IC, E_pwInp_m_P_pWedge, E_pwOut_m_P_pWedge, E_outShare_m_P_pWedge, E_TaxRev_m_P_pWedge, E_armington_m_Trade, E_pwInp_m_Trade, E_TaxRev_m_Trade, E_equi_m_equi
/;


solve m_GE_2018_B using CNS;