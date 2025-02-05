# 1. Technology Functions
EOPTechFunctions = """
$MACRO stdNormPdf(x) exp(-sqr(x)/2)/(sqrt(2*Pi))
$MACRO EOP_Logit(p, c, e) (1/(1+exp((c-p)/e)))
$MACRO EOP_Normal(p, c, e) errorf((p-c)/e)
$MACRO EOP_NormalMult(p, c, e) errorf((p/c-1)/e)
$MACRO EOP_LogNorm(p, c, e) errorf(log(p/c)/e+e/2)
$MACRO EOP_LogNormCost(p, c, e) c * errorf(log(p/c)/e-e/2)

$MACRO EOP_NormalCost(p, c, e) EOP_Normal(p, c, e)*c-e*stdNormPdf((p-c)/e)
$MACRO EOP_NormalMultCost(p, c, e) c*(EOP_NormalMult(p, c, e)-e*stdNormPdf((p/c-1)/e))
$MACRO EOP_NormalUniCost(p, c, e, s, u) (1-s)*EOP_NormalCost(p, c, e)+s * sqr(p)/(2*u)

$FUNCTION EOP_Tech({p}, {c}, {e}):
	$IF %techType% == 'normal': EOP_Normal( ({p}), ({c}), ({e}) ) $ENDIF
	$IF %techType% == 'logit' : EOP_Logit( ({p}), ({c}), ({e}) ) $ENDIF
	$IF %techType% == 'normalMult': EOP_NormalMult( ({p}), ({c}), ({e}) ) $ENDIF
	$IF %techType% == 'logNorm': EOP_LogNorm( ({p}), ({c}), ({e}) ) $ENDIF
$ENDFUNCTION

$FUNCTION EOP_Cost({p}, {c}, {e}):
	$IF %techType% == 'normal': EOP_NormalCost( ({p}), ({c}), ({e}) ) $ENDIF
	$IF %techType% == 'normalMult': EOP_NormalMultCost( ({p}), ({c}), ({e}) ) $ENDIF
	$IF %techType% == 'logNorm': EOP_LogNormCost( ({p}), ({c}), ({e})) $ENDIF
$ENDFUNCTION
"""

# 2. Simple abatement module
def EOP_Simple(name, cost = 'techCost[t,s,tech]', addCosts = ''):
	return f"""
$BLOCK B_{name}
	E_{name}_uAbate[t,s,n]$(dqCO2[s,n] and txE[t])..				uAbate[t,s,n]		=E= sum(tech$(dtech[s,tech]), techPot[t, s, tech] * @EOP_Tech(tauCO2[t,s,n], {cost}, techSmooth[t,s,tech]));
	E_{name}_uAbateC[t,s,n,tech]$(dTechTau[s,n,tech] and txE[t])..	uAbateC[t,s,n,tech] =E= techPot[t,s,tech] * @EOP_Cost(tauCO2[t,s,n], {cost}, techSmooth[t,s,tech]);
	E_{name}_avgAbateCost[t,s,n]$(dtauCO2[s,n] and txE[t]).. 		avgAbateCosts[t,s,n]=E= sum(tech$(dtech[s,tech]), uAbateC[t,s,n,tech]);
	E_{name}_abateCosts[t,s,n]$(dtauCO2[s,n] and txE[t]).. 		abateCosts[t,s,n]	=E= avgAbateCosts[t,s,n]*uCO2[t,s,n]*qS[t,s,n]{addCosts};
	E_{name}_tauCO2Eff[t,s,n]$(dtauCO2[s,n] and txE[t])..			tauEffCO2[t,s,n]	=E= tauCO2[t,s,n]*(1-uAbate[t,s,n])+avgAbateCosts[t,s,n];
	E_{name}_tauCO2[t,s,n]$(dtauCO2[s,n] and txE[t])..				tauCO2[t,s,n]		=E= tauCO2agg[t] * tauDist[t,s,n];
	E_{name}_qCO2[t,s,n]$(dqCO2[s,n] and txE[t])..					qCO2[t,s,n]			=E= uCO2[t,s,n] * (1-uAbate[t,s,n]) * qS[t,s,n];
	E_{name}_qCO2agg[t]$(txE[t])..									qCO2agg[t]			=E= sum([s,n]$(dqCO2[s,n]), qCO2[t,s,n])-qCO2Base * @EOP_Tech(tauCO2agg[t], DACCost[t], DACSmooth[t]);
$ENDBLOCK

$BLOCK B_{name}_calib
	E_{name}_qCO2calib[t,s,n]$(dqCO2[s,n] and txE[t])..	uCO2[t,s,n]	=E= uCO20[t,s,n] * (1+uCO2calib[s,n]);
$ENDBLOCK
"""

# 3. Abatement with square adjustment costs: This block of equations is added to the EOP_Simple:
def EOP_SqrAdjCosts(name):
	return f""" 
$BLOCK B_{name}_adjCost
	E_{name}_qKd[t,s,tech]$(dtech[s,tech] and txE[t])..		pKEOP[t,s,tech]*qKEOP[t,s,tech]	=E= sum(n$(dTechTau[s,n,tech]), uCO2[t,s,n]*qS[t,s,n]*uAbateC[t,s,n,tech]); # demand for abatement capital
	E_{name}_techCost[t,s,tech]$(dtech[s,tech] and txE[t])..	techCost[t,s,tech]			=E= uKEOP[t,s,tech]*pKEOP[t,s,tech]; # technology cost index
	E_{name}_LOM[t,s,tech]$(dtech[s,tech] and txE[t])..			qKEOP[t+1,s,tech]			=E= (qKEOP[t,s,tech]*(1-rDeprEOP[s,tech])+qIEOP[t,s,tech])/(1+g_LR); # Law of motion for abatement capital
	E_{name}_pK[t,s,tech]$(dtech[s,tech] and tx02E[t])..		pKEOP[t,s,tech]				=E= sqrt(sqr(Rrate[t]*(1+adjCostParEOP[s,tech]*( (qIEOP[t-1,s,tech]+qKmin[t-1,s,tech]*(rDeprEOP[s,tech]+g_LR))/(qKEOP[t-1,s,tech]+qKmin[t-1,s,tech])-(rDeprEOP[s,tech]+g_LR)))/(1+infl_LR)+adjCostParEOP[s,tech]*0.5*(sqr(rDeprEOP[s,tech]+g_LR)-sqr((qIEOP[t,s,tech]+qKmin[t,s,tech]*(rDeprEOP[s,tech]+g_LR))/(qKEOP[t,s,tech]+qKmin[t,s,tech])))-(1-rDeprEOP[s,tech])*(1+adjCostParEOP[s,tech]*((qIEOP[t,s,tech]+qKmin[t,s,tech]*(rDeprEOP[s,tech]+g_LR))/(qKEOP[t,s,tech]+qKmin[t,s,tech])-(rDeprEOP[s,tech]+g_LR))))); # Tobin's Q for abatement capital
	E_{name}_pKT[t,s,tech]$(dtech[s,tech] and t2E[t])..			pKEOP[t,s,tech]				=E= sqrt(sqr(Rrate[t]*(1+adjCostParEOP[s,tech]*( (qIEOP[t-1,s,tech]+qKmin[t-1,s,tech]*(rDeprEOP[s,tech]+g_LR))/(qKEOP[t-1,s,tech]+qKmin[t-1,s,tech])-(rDeprEOP[s,tech]+g_LR)))/(1+infl_LR)+rDeprEOP[s,tech]-1)); # steady state approximation of Tobin's Q
	E_{name}_Ktvc[t,s,tech]$(dtech[s,tech] and tE[t])..			qKEOP[t,s,tech]	 			=E= (1+KtvcEOP[s,tech])*qKEOP[t-1,s,tech]/(1+g_LR); # TVC condition for abatement capital
	E_{name}_divd[t,s,tech]$(dtech[s,tech] and txE[t])..		divdEOP[t,s,tech]			=E= pKEOP[t,s,tech]*qKEOP[t,s,tech]-qIEOP[t,s,tech]-(qKEOP[t,s,tech]+qKmin[t,s,tech])*adjCostParEOP[s,tech]*0.5*sqr((qIEOP[t,s,tech]+qKmin[t,s,tech]*(rDeprEOP[s,tech]+g_LR))/(qKEOP[t,s,tech]+qKmin[t,s,tech])-(rDeprEOP[s,tech]+g_LR));
$ENDBLOCK

$BLOCK B_{name}_calibK0
	E_{name}_qKEOPt0[t,s,tech]$(dtech[s,tech] and t0[t])..	pKEOP[t,s,tech]	=E= Rrate[t]+adjCostParEOP[s,tech]*0.5*(sqr(rDeprEOP[s,tech]+g_LR)-sqr((qIEOP[t,s,tech]+qKmin[t,s,tech]*(rDeprEOP[s,tech]+g_LR))/(qKEOP[t,s,tech]+qKmin[t,s,tech])))-(1-rDeprEOP[s,tech])*(1+adjCostParEOP[s,tech]*((qIEOP[t,s,tech]+qKmin[t,s,tech]*(rDeprEOP[s,tech]+g_LR))/(qKEOP[t,s,tech]+qKmin[t,s,tech])-(rDeprEOP[s,tech]+g_LR))); # Tobin's Q for abatement capital, t0
$ENDBLOCK
"""

EOPIte_CapitalCalib = f"""
techCost.l[t,s,tech]$(dtech[s,tech] and txE[t]) = uKEOP.l[t,s,tech]*pKEOP.l[t,s,tech];
uAbateC.l[t,s,n,tech]$(dTechTau[s,n,tech] and txE[t]) = techPot.l[t,s,tech] * @EOP_Cost(tauCO2.l[t,s,n], techCost.l[t,s,tech], techSmooth.l[t,s,tech]);
qKEOP.l[t,s,tech]$(dtech[s,tech] and txE[t]) = sum(n$(dTechTau[s,n,tech]), uCO2.l[t,s,n]*qS.l[t,s,n]*uAbateC.l[t,s,n,tech])/pKEOP.l[t,s,tech];
qKEOP.l[t,s,tech]$(dtech[s,tech] and tE[t])	 = (1+KtvcEOP.l[s,tech])*qKEOP.l[t-1,s,tech]/(1+g_LR);
qIEOP.l[t,s,tech]$(dtech[s,tech] and txE[t]) = (1+g_LR)*qKEOP.l[t+1,s,tech]+(rDeprEOP.l[s,tech]-1)*qKEOP.l[t,s,tech];
"""

EOPIte_PriceCalib = f"""
pKEOP.l[t,s,tech]$(dtech[s,tech] and t2E[t])	= Rrate.l[t]*(1+adjCostParEOP.l[s,tech]*( (qIEOP.l[t-1,s,tech]+qKmin.l[t-1,s,tech]*(rDeprEOP.l[s,tech]+g_LR))/(qKEOP.l[t-1,s,tech]+qKmin.l[t-1,s,tech])-(rDeprEOP.l[s,tech]+g_LR)))/(1+infl_LR)+rDeprEOP.l[s,tech]-1;
pKEOP.l[t,s,tech]$(dtech[s,tech] and tx02E[t])	= Rrate.l[t]*(1+adjCostParEOP.l[s,tech]*( (qIEOP.l[t-1,s,tech]+qKmin.l[t-1,s,tech]*(rDeprEOP.l[s,tech]+g_LR))/(qKEOP.l[t-1,s,tech]+qKmin.l[t-1,s,tech])-(rDeprEOP.l[s,tech]+g_LR)))/(1+infl_LR)+adjCostParEOP.l[s,tech]*0.5*(sqr(rDeprEOP.l[s,tech]+g_LR)-sqr((qIEOP.l[t,s,tech]+qKmin.l[t,s,tech]*(rDeprEOP.l[s,tech]+g_LR))/(qKEOP.l[t,s,tech]+qKmin.l[t,s,tech])))-(1-rDeprEOP.l[s,tech])*(1+adjCostParEOP.l[s,tech]*((qIEOP.l[t,s,tech]+qKmin.l[t,s,tech]*(rDeprEOP.l[s,tech]+g_LR))/(qKEOP.l[t,s,tech]+qKmin.l[t,s,tech])-(rDeprEOP.l[s,tech]+g_LR)));
pKEOP.l[t,s,tech]$(dtech[s,tech] and t0[t])		= Rrate.l[t]+adjCostParEOP.l[s,tech]*0.5*(sqr(rDeprEOP.l[s,tech]+g_LR)-sqr((qIEOP.l[t,s,tech]+qKmin.l[t,s,tech]*(rDeprEOP.l[s,tech]+g_LR))/(qKEOP.l[t,s,tech]+qKmin.l[t,s,tech])))-(1-rDeprEOP.l[s,tech])*(1+adjCostParEOP.l[s,tech]*((qIEOP.l[t,s,tech]+qKmin.l[t,s,tech]*(rDeprEOP.l[s,tech]+g_LR))/(qKEOP.l[t,s,tech]+qKmin.l[t,s,tech])-(rDeprEOP.l[s,tech]+g_LR)));
"""

init_SqrAdjCosts = f"""
uAbateC.l[t,s,n,tech]$(dTechTau[s,n,tech]) = techPot.l[t,s,tech] * @EOP_Cost(tauCO2.l[t,s,n], techCost.l[t,s,tech], techSmooth.l[t,s,tech]);
pKEOP.l[t,s,tech]$(dtech[s,tech]) = Rrate.l[t]+rDeprEOP.l[s,tech]-1;
qKEOP.l[t,s,tech]$(dtech[s,tech]) = sum(n$(dTechTau[s,n,tech]), uCO2.l[t,s,n]*qS.l[t,s,n]*uAbateC.l[t,s,n,tech])/pKEOP.l[t,s,tech];
qIEOP.l[t,s,tech]$(dtech[s,tech] and txE[t]) = (1+g_LR)*qKEOP.l[t+1,s,tech]+(rDeprEOP.l[s,tech]-1)*qKEOP.l[t,s,tech];
qKmin.l[t,s,tech]$(dtech[s,tech]) = qKminRate*techPot.l[t,s,tech] * techCost.l[t,s,tech] * sum(n$(dTechTau[s,n,tech]), uCO2.l[t,s,n] * qS.l[t,s,n]) / pKEOP.l[t,s,tech];
{EOPIte_PriceCalib}
"""


# # 4. Abatement with minimum levels:
# def EOP_SqrAdjCosts_Kwedge(name):
# 	return f""" 
# $BLOCK B_{name}_adjCost
# 	E_{name}_qKd[t,s,tech]$(dtech[s,tech] and txE[t])..		pKEOP[t,s,tech]*(qKEOP[t,s,tech]+qKEOPwedge[t,s,tech])	=E= sum(n$(dTechTau[s,n,tech]), uCO2[t,s,n]*qS[t,s,n]*uAbateC[t,s,n,tech]); # demand for abatement capital
# 	E_{name}_techCost[t,s,tech]$(dtech[s,tech] and txE[t])..	techCost[t,s,tech]			=E= uKEOP[t,s,tech]*pKEOP[t,s,tech]; # technology cost index
# 	E_{name}_LOM[t,s,tech]$(dtech[s,tech] and txE[t])..			qKEOP[t+1,s,tech]			=E= (qKEOP[t,s,tech]*(1-rDeprEOP[s,tech])+qIEOP[t,s,tech])/(1+g_LR); # Law of motion for abatement capital
# 	E_{name}_pK[t,s,tech]$(dtech[s,tech] and tx02E[t])..		pKEOP[t,s,tech]				=E= sqrt(sqr(Rrate[t]*(1+adjCostParEOP[s,tech]*( (qIEOP[t-1,s,tech]+qKmin[t-1,s,tech]*(rDeprEOP[s,tech]+g_LR))/(qKEOP[t-1,s,tech]+qKmin[t-1,s,tech])-(rDeprEOP[s,tech]+g_LR)))/(1+infl_LR)+adjCostParEOP[s,tech]*0.5*(sqr(rDeprEOP[s,tech]+g_LR)-sqr((qIEOP[t,s,tech]+qKmin[t,s,tech]*(rDeprEOP[s,tech]+g_LR))/(qKEOP[t,s,tech]+qKmin[t,s,tech])))-(1-rDeprEOP[s,tech])*(1+adjCostParEOP[s,tech]*((qIEOP[t,s,tech]+qKmin[t,s,tech]*(rDeprEOP[s,tech]+g_LR))/(qKEOP[t,s,tech]+qKmin[t,s,tech])-(rDeprEOP[s,tech]+g_LR))))); # Tobin's Q for abatement capital
# 	E_{name}_pKT[t,s,tech]$(dtech[s,tech] and t2E[t])..			pKEOP[t,s,tech]				=E= sqrt(sqr(Rrate[t]*(1+adjCostParEOP[s,tech]*( (qIEOP[t-1,s,tech]+qKmin[t-1,s,tech]*(rDeprEOP[s,tech]+g_LR))/(qKEOP[t-1,s,tech]+qKmin[t-1,s,tech])-(rDeprEOP[s,tech]+g_LR)))/(1+infl_LR)+rDeprEOP[s,tech]-1)); # steady state approximation of Tobin's Q
# 	E_{name}_Ktvc[t,s,tech]$(dtech[s,tech] and tE[t])..			qKEOP[t,s,tech]	 			=E= (1+KtvcEOP[s,tech])*qKEOP[t-1,s,tech]/(1+g_LR); # TVC condition for abatement capital
# 	E_{name}_divd[t,s,tech]$(dtech[s,tech] and txE[t])..		divdEOP[t,s,tech]			=E= pKEOP[t,s,tech]*qKEOP[t,s,tech]-qIEOP[t,s,tech]-(qKEOP[t,s,tech]+qKmin[t,s,tech])*adjCostParEOP[s,tech]*0.5*sqr((qIEOP[t,s,tech]+qKmin[t,s,tech]*(rDeprEOP[s,tech]+g_LR))/(qKEOP[t,s,tech]+qKmin[t,s,tech])-(rDeprEOP[s,tech]+g_LR));
# $ENDBLOCK

# $BLOCK B_{name}_calibK0
# 	E_{name}_qKEOPt0[t,s,tech]$(dtech[s,tech] and t0[t])..	pKEOP[t,s,tech]	=E= sqrt(sqr(Rrate[t]+adjCostParEOP[s,tech]*0.5*(sqr(rDeprEOP[s,tech]+g_LR)-sqr((qIEOP[t,s,tech]+qKmin[t,s,tech]*(rDeprEOP[s,tech]+g_LR))/(qKEOP[t,s,tech]+qKmin[t,s,tech])))-(1-rDeprEOP[s,tech])*(1+adjCostParEOP[s,tech]*((qIEOP[t,s,tech]+qKmin[t,s,tech]*(rDeprEOP[s,tech]+g_LR))/(qKEOP[t,s,tech]+qKmin[t,s,tech])-(rDeprEOP[s,tech]+g_LR))))); # Tobin's Q for abatement capital, t0
# $ENDBLOCK
# """

# init_SqrAdjCosts_Kwedge = f"""
# uAbateC.l[t,s,n,tech]$(dTechTau[s,n,tech]) = techPot.l[t,s,tech] * @EOP_Cost(tauCO2.l[t,s,n], techCost.l[t,s,tech], techSmooth.l[t,s,tech]);
# qKEOPwedge.l[t,s,tech]$(dtech[s,tech]) = techPot.l[t,s,tech] * @EOP_Cost(0, techCost.l[t,s,tech], techSmooth.l[t,s,tech]);
# pKEOP.l[t,s,tech]$(dtech[s,tech]) = Rrate.l[t]+rDeprEOP.l[s,tech]-1;
# qKEOP.l[t,s,tech]$(dtech[s,tech]) = sum(n$(dTechTau[s,n,tech]), uCO2.l[t,s,n]*qS.l[t,s,n]*uAbateC.l[t,s,n,tech])/pKEOP.l[t,s,tech]-qKEOPwedge.l[t,s,tech];
# qIEOP.l[t,s,tech]$(dtech[s,tech] and txE[t]) = (1+g_LR)*qKEOP.l[t+1,s,tech]+(rDeprEOP.l[s,tech]-1)*qKEOP.l[t,s,tech];
# qKmin.l[t,s,tech]$(dtech[s,tech]) = qKminRate*techPot.l[t,s,tech] * techCost.l[t,s,tech] * sum(n$(dTechTau[s,n,tech]), uCO2.l[t,s,n] * qS.l[t,s,n]) / pKEOP.l[t,s,tech];
# {EOPIte_PriceCalib}
# """
#
#
# # Mixing distributions:
# def EOP_MixedDistr(name, cost = 'techCost[t,s,tech]', addCosts = ''):
# 	return f"""
# $BLOCK B_{name}
# 	E_{name}_uAbate[t,s,n]$(dqCO2[s,n] and txE[t])..				uAbate[t,s,n]		=E= sum(tech$(dtech[s,tech]), techPot[t, s, tech] * (uTechUni * tauCO2[t,s,n]/(techCost[t,s,tech]*uniTechMax[t,s,tech]) +(1-uTechUni) * @EOP_Tech(tauCO2[t,s,n], {cost}, techSmooth[t,s,tech])));
# 	E_{name}_uAbateC[t,s,n,tech]$(dTechTau[s,n,tech] and txE[t])..	uAbateC[t,s,n,tech] =E= techPot[t,s,tech] * (uTechUni*sqr(tauCO2[t,s,n]/techCost[t,s,tech])/(2*uniTechMax[t,s,tech]) + (1-uTechUni)*@EOP_Cost(tauCO2[t,s,n], {cost}, techSmooth[t,s,tech]));
# 	E_{name}_avgAbateCost[t,s,n]$(dtauCO2[s,n] and txE[t]).. 		avgAbateCosts[t,s,n]=E= sum(tech$(dtech[s,tech]), uAbateC[t,s,n,tech]);
# 	E_{name}_abateCosts[t,s,n]$(dtauCO2[s,n] and txE[t]).. 		abateCosts[t,s,n]	=E= avgAbateCosts[t,s,n]*uCO2[t,s,n]*qS[t,s,n]{addCosts};
# 	E_{name}_tauCO2Eff[t,s,n]$(dtauCO2[s,n] and txE[t])..			tauEffCO2[t,s,n]	=E= tauCO2[t,s,n]*(1-uAbate[t,s,n])+avgAbateCosts[t,s,n];
# 	E_{name}_tauCO2[t,s,n]$(dtauCO2[s,n] and txE[t])..				tauCO2[t,s,n]		=E= tauCO2agg[t] * tauDist[t,s,n];
# 	E_{name}_qCO2[t,s,n]$(dqCO2[s,n] and txE[t])..					qCO2[t,s,n]			=E= uCO2[t,s,n] * (1-uAbate[t,s,n]) * qS[t,s,n];
# 	E_{name}_qCO2agg[t]$(txE[t])..									qCO2agg[t]			=E= sum([s,n]$(dqCO2[s,n]), qCO2[t,s,n])-qCO2Base * @EOP_Tech(tauCO2agg[t], DACCost[t], DACSmooth[t]);
# $ENDBLOCK

# $BLOCK B_{name}_calib
# 	E_{name}_qCO2calib[t,s,n]$(dqCO2[s,n] and txE[t])..	uCO2[t,s,n]	=E= uCO20[t,s,n] * (1+uCO2calib[s,n]);
# $ENDBLOCK
# """


