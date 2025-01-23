def addPrefixIf(k, prefix = None):
	return k if prefix is None else prefixt+'_'+k

# 1. Simple Accounting and targeting
def AccountSimple(name, m = None):
	return f"""
$BLOCK B_{name}
	E_{name}_tauCO2[t,s,n]$({addPrefixIf('dtauCO2[s,n]',m)} and txE[t]).. 		tauCO2[t,s,n]	=E= tauCO2agg[t] * tauDist[t,s,n];
	E_{name}_tauCO2Eff[t,s,n]$({addPrefixIf('dtauCO2[s,n]',m)} and txE[t])..	tauEffCO2[t,s,n]=E= tauCO2[t,s,n];
	E_{name}_qCO2[t,s,n]$({addPrefixIf('dqCO2[s,n]',m)} and txE[t])..			qCO2[t,s,n]	    =E= uCO2[t,s,n] * qS[t,s,n];
	E_{name}_qCO2agg[t]$(txE[t])..								{addPrefixIf('qCO2agg[t]',m)}	=E= sum([s,n]$({addPrefixIf('dqCO2[s,n]',m)}), qCO2[t,s,n]);
$ENDBLOCK

$BLOCK B_{name}_calib
	E_{name}_qCO2calib[t,s,n]$({addPrefixIf('dqCO2[s,n]',m)} and txE[t])..	uCO2[t,s,n]	=E= uCO20[t,s,n] * (1+uCO2calib[s,n]);
$ENDBLOCK
"""


# 2. Emission targets
# 2.1. Single year targets. 
def SYT(name, targetVariable = "0"):
	""" Single Year Targets"""
	return f"""
$BLOCK B_{name}_SYT_EXO_Calib
	E_SYT_qCO2agg[t]$(t_SYT[t] and tx0E[t]).. 	qCO2agg[t]		=E= qCO2_SYT[t];
	E_SYT_tauCO2agg[t]$(t_SYT_NB[t])..			tauCO2agg[t]	=E= tauCO2agg0[t];
$ENDBLOCK
$BLOCK B_{name}_SYT_t0
	E_SYT_t0[t]$(t_SYT[t] and t0[t])..	qCO2agg[t]	=E= qCO2_SYT[t];
$ENDBLOCK
$MODEL B_{name}_SYT_EXO
	B_{name}_SYT_EXO_Calib
	B_{name}_SYT_t0
;

$BLOCK B_{name}_SYT_HR_Calib
	E_SYT_HR_qCO2agg[t]$(t_SYT[t] and tx0E[t])..	 	qCO2agg[t]		=E= qCO2_SYT[t];
	E_SYT_HR_tauCO2agg[t]$(t_SYT_NB[t])..				tauCO2agg[t+1]	=E= tauCO2agg[t]*Rrate[t]/(1+infl_LR);
$ENDBLOCK
$MODEL B_{name}_SYT_HR
	B_{name}_SYT_HR_Calib
	B_{name}_SYT_t0
;

$BLOCK B_{name}_SYT_OPT_Calib
	E_SYT_OPT_qCO2agg[t]$(t_SYT[t] and tx0E[t]).. 	qCO2agg[t]		=E= qCO2_SYT[t];
	E_SYT_OPT_obj.. obj =E= {targetVariable};
$ENDBLOCK

$MODEL B_{name}_SYT_OPT
	B_{name}_SYT_OPT_Calib
	B_{name}_SYT_t0
;
"""


# 2.2. Linear reduction paths.
def LRP(name, **kwargs):
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

def EB(name, targetVariable = "0"):
	""" Emission Budget (cumulative)"""
	return f"""
$BLOCK B_{name}_EB_HR_Calib
	E_EB_HR_qCO2agg[t]$(t_EB[t] and tx0E[t]).. 		qCO2_EB[t]		=E= sum(tt$(t2tt_EB[t, tt]), qCO2agg[tt]*(1+g_LR)**(tt.val-t.val));
	E_EB_HR_SYT_qCO2agg[t]$(t_EB_SYT[t])..			qCO2agg[t]		=E= qCO2_EB_SYT[t];
	E_EB_HR_tauCO2agg[t]$(t_EB_NB[t])..				tauCO2agg[t+1]	=E= tauCO2agg[t]*Rrate[t]/(1+infl_LR);
$ENDBLOCK
$BLOCK B_{name}_EB_t0
	E_EB_t0[t]$(t_EB[t] and t0[t])..	qCO2_EB[t]		=E= sum(tt$(t2tt_EB[t, tt]), qCO2agg[tt]);
$ENDBLOCK
$MODEL B_{name}_EB_HR
	B_{name}_EB_HR_Calib
	B_{name}_EB_t0
;	

$BLOCK B_{name}_EB_OPT_Calib
	E_EB_OPT_qCO2agg[t]$(t_EB[t] and tx0E[t]).. 	qCO2_EB[t]	=E= sum(tt$(t2tt_EB[t, tt]), qCO2agg[tt]*(1+g_LR)**(tt.val-t.val));
	E_EB_OPT_SYT_qCO2agg[t]$(t_EB_SYT[t])..			qCO2agg[t]	=E= qCO2_EB_SYT[t];
	E_EB_OPT_obj.. obj =E= {targetVariable};
$ENDBLOCK
$MODEL B_{name}_EB_OPT
	B_{name}_EB_OPT_Calib
	B_{name}_EB_t0
;

"""

