# 1. Technology Functions
EOPTechFunctions = """
$MACRO stdNormPdf(x) exp(-sqr(x)/2)/(2*sqrt(Pi))
$MACRO EOP_Logit(p, c, e) (1/(1+exp((c-p)/e)))
$MACRO EOP_Normal(p, c, e) errorf((p-c)/e)
$MACRO EOP_NormalMult(p, c, e) errorf((p/c-1)/e)

$MACRO EOP_NormalCost(p, c, e) EOP_Normal(p, c, e)*c-e*stdNormPdf((p-c)/e)
$MACRO EOP_NormalMultCost(p, c, e) c*(EOP_NormalMult(p, c, e)-e*stdNormPdf((p/c-1)/e))

$FUNCTION EOP_Tech({p}, {c}, {e}):
	$IF %techType% == 'normal': EOP_Normal( ({p}), ({c}), ({e}) ) $ENDIF
	$IF %techType% == 'logit' : EOP_Logit( ({p}), ({c}), ({e}) ) $ENDIF
	$IF %techType% == 'normalMult': EOP_NormalMult( ({p}), ({c}), ({e}) ) $ENDIF
$ENDFUNCTION

$FUNCTION EOP_Cost({p}, {c}, {e}):
	$IF %techType% == 'normal': EOP_NormalCost( ({p}), ({c}), ({e}) ) $ENDIF
	$IF %techType% == 'normalMult': EOP_NormalMultCost( ({p}), ({c}), ({e}) ) $ENDIF
$ENDFUNCTION
"""


# 2. EOP abatement:
def EOP_Simple(name, cost = 'techCost[tech,t]'):
	return f"""
$BLOCK B_{name}
	E_uAbate[t,s,n]$(dqCO2[s,n] and txE[t])..		uAbate[t,s,n]		=E= sum(tech, techPot[tech,t] * @EOP_Tech(tauCO2[t,s,n], {cost}, techSmooth[tech,t]));
	E_tauCO2Eff[t,s,n]$(dtauCO2[s,n] and txE[t])..	tauEffCO2[t,s,n]	=E= tauCO2[t,s,n]*(1-uAbate[t,s,n])+sum(tech, techPot[tech,t] * @EOP_Cost(tauCO2[t,s,n], {cost}, techSmooth[tech,t]));
	E_tauCO2[t,s,n]$(dtauCO2[s,n] and txE[t])..		tauCO2[t,s,n]		=E= tauCO2agg[t] * tauDist[t,s,n];
	E_qCO2[t,s,n]$(dqCO2[s,n] and txE[t])..			qCO2[t,s,n]			=E= uCO2[t,s,n] * (1-uAbate[t,s,n]) * qS[t,s,n];
	E_qCO2agg[t]$(txE[t])..							qCO2agg[t]			=E= sum([s,n]$(dqCO2[s,n]), qCO2[t,s,n])-qCO2Base * @EOP_Tech(tauCO2agg[t], DACCost[t], DACSmooth[t]);
$ENDBLOCK

$BLOCK B_{name}_calib
	E_qCO2calib[t,s,n]$(dqCO2[s,n] and txE[t])..	uCO2[t,s,n]	=E= uCO20[t,s,n] * (1+uCO2calib[s,n]);
$ENDBLOCK
"""

def EOP_EconWideCapital(name):
	cost = "techCost[tech,t]*pK_EOP[t]/[R_LR-1+rDepr_EOP]"
	return f"""
{EOP_Simple(name, cost = cost)}

$BLOCK B_{name}_adjCost
	E_{name}_lom[t]$(txE[t])..		qK_EOP[t+1]	  =E= (qK_EOP[t]*(1-rDepr_EOP)+qI_EOP[t])/(1+g_LR);
	E_{name}_pk[t]$(tx02E[t])..		pK_EOP[t]	  =E= sqrt(sqr(Rrate[t]*(1+adjCostPar_EOP*(qI_EOP[t-1]/qK_EOP[t-1]-(rDepr_EOP+g_LR)))/(1+infl_LR)+adjCostPar_EOP*0.5*(sqr(rDepr_EOP+g_LR)-sqr(qI_EOP[t]/qK_EOP[t]))-(1-rDepr_EOP)*(1+adjCostPar_EOP*(qI_EOP[t]/qK_EOP[t]-(rDepr_EOP+g_LR)))));
	E_{name}_pKT[t]$(t2E[t])..		pK_EOP[t]	  =E= Rrate[t]*(1+adjCostPar_EOP*(qI_EOP[t-1]/qK_EOP[t-1]-(rDepr_EOP+g_LR)))/(1+infl_LR)+(rDepr_EOP-1);
	E_{name}_Ktvc[t]$(tE[t])..		qK_EOP[t]	  =E= (1+Ktvc_EOP)*qK_EOP[t-1];
	E_{name}_adjCost[t]$(txE[t])..	adjCostEOP[t] =E= adjCostPar_EOP*0.5*qK_EOP[t]*sqr(qI_EOP[t]/qK_EOP[t]-(rDepr_EOP+g_LR));
$ENDBLOCK

$BLOCK B_{name}_Equi
	E_{name}_equi[t]$(txE[t]).. qK_EOP[t]	=E= 1e6*sum([s,n]$(dqCO2[s,n]), uCO2[t,s,n]*qS[t,s,n]*sum(tech, techPot[tech,t]*@EOP_Cost(tauCO2[t,s,n], {cost}, techSmooth[tech,t])/pK_EOP[t]));
$ENDBLOCK

$BLOCK B_{name}_calibK0
	# E_qK_EOPt0[t]$(t0[t])..	pK_EOP[t]	=E= Rrate[t]+g_LR;
	E_qK_EOPt0[t]$(t0[t])..	pK_EOP[t]	=E= sqrt(sqr(Rrate[t]+adjCostPar_EOP*0.5*(sqr(rDepr_EOP+g_LR)-sqr(qI_EOP[t]/qK_EOP[t]))-(1-rDepr_EOP)*(1+adjCostPar_EOP*(qI_EOP[t]/qK_EOP[t]-(rDepr_EOP+g_LR)))));
$ENDBLOCK
"""

init_EconWideCapital = """
qK_EOP.l[t] = 1e6*(sum([s,n]$(dqCO2[s,n]), uCO2.l[t,s,n]*qS.l[t,s,n]*sum(tech, techPot.l[tech,t]*@EOP_Cost(tauCO2.l[t,s,n], techCost.l[tech,t]*pK_EOP.l[t]/[R_LR-1+rDepr_EOP.l], techSmooth.l[tech,t])/pK_EOP.l[t])));
qI_EOP.l[t]	= (rDepr_EOP.l+g_LR)*qK_EOP.l[t];
"""

# 3. Emission regulation:
def SYT(name):
	""" Single Year Targets"""
	return f"""
$BLOCK B_{name}_SYT_Calib
	E_SYT_qCO2agg[t]$(t_SYT[t] and tx0E[t]).. 	qCO2agg[t]		=E= qCO2_SYT[t];
	E_SYT_tauCO2agg[t]$(t_SYT_NB[t])..			tauCO2agg[t]	=E= 0;
$ENDBLOCK
$BLOCK B_{name}_SYT_t0
	E_SYT_t0[t]$(t_SYT[t] and t0[t])..	qCO2agg[t]	=E= qCO2_SYT[t];
$ENDBLOCK
$MODEL B_{name}_SYT
	B_{name}_SYT_Calib
	B_{name}_SYT_t0
;

$BLOCK B_{name}_SYT_HR_Calib
	E_SYT_HR_qCO2agg[t]$(t_SYT[t] and tx0E[t])..	 	qCO2agg[t]		=E= qCO2_SYT[t];
	E_SYT_HR_tauCO2agg[t]$(t_SYT_NB[t])..				tauCO2agg[t]	=E= tauCO2agg[t+1]/Rrate[t];
$ENDBLOCK
$MODEL B_{name}_SYT_HR
	B_{name}_SYT_HR_Calib
	B_{name}_SYT_t0
;

$BLOCK B_{name}_SYT_OPT_Calib
	E_SYT_OPT_qCO2agg[t]$(t_SYT[t] and tx0E[t]).. 	qCO2agg[t]		=E= qCO2_SYT[t];
	# E_SYT_OPT_obj..								obj =E= 1;
	E_SYT_OPT_obj..									obj =E= sum([t,s]$(t0[t] and s_HH[s]), vU[t,s]);
$ENDBLOCK
$MODEL B_{name}_SYT_OPT
	B_{name}_SYT_OPT_Calib
	B_{name}_SYT_t0
;
"""

def LRP(name):
	""" Linear Reduction Paths """
	return f"""
$BLOCK B_{name}_LRP_Calib
	E_LRP_qCO2agg[t]$(t_LRP[t] and tx0E[t]).. 		qCO2agg[t]		=E= qCO2_LRP[t];
$ENDBLOCK
$BLOCK B_{name}_LRP_t0
	E_LRP_t0[t]$(t_LRP[t] and t0[t])..	qCO2agg[t]	=E= qCO2_LRP[t];
$ENDBLOCK
$MODEL B_{name}_LRP
	B_{name}_LRP_Calib
	B_{name}_LRP_t0
;
"""

def EB(name):
	""" Emission Budget (cumulative)"""
	return f"""
$BLOCK B_{name}_EB_HR_Calib
	E_EB_HR_qCO2agg[t]$(t_EB[t] and tx0E[t]).. 		qCO2_EB[t]		=E= sum(tt$(t2tt_EB[t, tt]), qCO2agg[tt]);
	E_EB_HR_SYT_qCO2agg[t]$(t_EB_SYT[t])..			qCO2agg[t]		=E= qCO2_EB_SYT[t];
	E_EB_HR_tauCO2agg[t]$(t_EB_NB[t])..				tauCO2agg[t]	=E= tauCO2agg[t+1]/Rrate[t];
$ENDBLOCK
$BLOCK B_{name}_EB_t0
	E_EB_t0[t]$(t_EB[t] and t0[t])..	qCO2_EB[t]		=E= sum(tt$(t2tt_EB[t, tt]), qCO2agg[tt]);
$ENDBLOCK
$MODEL B_{name}_EB_HR
	B_{name}_EB_HR_Calib
	B_{name}_EB_t0
;	

$BLOCK B_{name}_EB_OPT_Calib
	E_EB_OPT_qCO2agg[t]$(t_EB[t] and tx0E[t]).. 	qCO2_EB[t]	=E= sum(tt$(t2tt_EB[t, tt]), qCO2agg[tt]);
	E_EB_OPT_SYT_qCO2agg[t]$(t_EB_SYT[t])..			qCO2agg[t]	=E= qCO2_EB_SYT[t];
	E_EB_OPT_obj..									obj =E= sum([t,s]$(t0[t] and s_HH[s]), vU[t,s]);
$ENDBLOCK
$MODEL B_{name}_EB_OPT
	B_{name}_EB_OPT_Calib
	B_{name}_EB_t0
;

"""