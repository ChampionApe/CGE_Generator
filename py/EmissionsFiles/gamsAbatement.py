# 1. Technology Functions
EOPTechFunctions = """
$MACRO stdNormPdf(x) exp(-sqr(x)/2)/(sqrt(2*Pi))
$MACRO EOP_Logit(p, c, e) (1/(1+exp((c-p)/e)))
$MACRO EOP_Normal(p, c, e) errorf((p-c)/e)
$MACRO EOP_NormalMult(p, c, e) errorf((p/c-1)/e)
$MACRO EOP_LogNorm(p, c, e) errorf(log(p/c+1e-6)/e+e/2)
$MACRO EOP_LogNormCost(p, c, e) c * errorf(log(p/c+1e-6)/e-e/2)

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
	E_{name}_uAbate[t,s,n]$(dqCO2[s,n] and txE[t])..				uAbate[t,s,n]		=E= sum(tech$(dTechS[t,s,tech]), techPot[t, s, tech] * @EOP_Tech(tauCO2[t,s,n], {cost}, techSmooth[t,s,tech]));
	E_{name}_uAbateC[t,s,n,tech]$(dTechSN[t,s,n,tech] and txE[t])..	uAbateC[t,s,n,tech] =E= techPot[t,s,tech] * @EOP_Cost(tauCO2[t,s,n], {cost}, techSmooth[t,s,tech]);
	E_{name}_avgAbateCost[t,s,n]$(dtauCO2[s,n] and txE[t]).. 		avgAbateCosts[t,s,n]=E= sum(tech$(dTechS[t,s,tech]), uAbateC[t,s,n,tech]);
	E_{name}_abateCosts[t,s,n]$(dtauCO2[s,n] and txE[t]).. 			abateCosts[t,s,n]	=E= avgAbateCosts[t,s,n]*uCO2[t,s,n]*qS[t,s,n]{addCosts};
	E_{name}_tauCO2Eff[t,s,n]$(dtauCO2[s,n] and txE[t])..			tauEffCO2[t,s,n]	=E= tauCO2[t,s,n]*(1-uAbate[t,s,n])+avgAbateCosts[t,s,n];
	E_{name}_tauCO2[t,s,n]$(dtauCO2[s,n] and txE[t])..				tauCO2[t,s,n]		=E= tauCO2agg[t] * tauDist[t,s,n];
	E_{name}_qCO2[t,s,n]$(dqCO2[s,n] and txE[t])..					qCO2[t,s,n]			=E= uCO2[t,s,n] * (1-uAbate[t,s,n]) * qS[t,s,n];
	E_{name}_qCO2agg[t]$(txE[t])..									qCO2agg[t]			=E= sum([s,n]$(dqCO2[s,n]), qCO2[t,s,n])-qCO2Base * @EOP_Tech(tauCO2agg[t], DACCost[t], DACSmooth[t]);
$ENDBLOCK

$BLOCK B_{name}_calib
	E_{name}_qCO2calib[t,s,n]$(dqCO2[s,n] and txE[t])..	uCO2[t,s,n]	=E= uCO20[t,s,n] * (1+uCO2calib[s,n]);
$ENDBLOCK
"""

# 3. Abatement with square adjustment costs:
# Abated emissions and demand for abatement capital:
def EOP_CapDemand(name, cost = 'techCost[t,s,tech]', addCosts = ''):
	return f"""
$BLOCK B_{name}
	E_{name}_uAbate[t,s,n]$(dqCO2[s,n] and tx0E[t])..					uAbate[t,s,n]		=E= sum(tech$(dTechS[t,s,tech]), techPot[t, s, tech] * @EOP_Tech(tauCO2[t,s,n], {cost}, techSmooth[t,s,tech]));
	E_{name}_uAbateC[t,s,n,tech]$(dTechSN[t,s,n,tech] and tx0E[t])..	uAbateC[t,s,n,tech] =E= techPot[t,s,tech] * @EOP_Cost(tauCO2[t,s,n], {cost}, techSmooth[t,s,tech]);
	E_{name}_avgAbateCost[t,s,n]$(dtauCO2[s,n] and txE[t]).. 			avgAbateCosts[t,s,n]=E= sum(tech$(dTechS[t,s,tech]), uAbateC[t,s,n,tech]);
	E_{name}_abateCosts[t,s,n]$(dtauCO2[s,n] and txE[t]).. 				abateCosts[t,s,n]	=E= avgAbateCosts[t,s,n]*uCO2[t,s,n]*qS[t,s,n]{addCosts};
	E_{name}_tauCO2Eff[t,s,n]$(dtauCO2[s,n] and txE[t])..				tauEffCO2[t,s,n]	=E= tauCO2[t,s,n]*(1-uAbate[t,s,n])+avgAbateCosts[t,s,n];
	E_{name}_tauCO2[t,s,n]$(dtauCO2[s,n] and txE[t])..					tauCO2[t,s,n]		=E= tauCO2agg[t] * tauDist[t,s,n];
	E_{name}_qCO2[t,s,n]$(dqCO2[s,n] and txE[t])..						qCO2[t,s,n]			=E= uCO2[t,s,n] * (1-uAbate[t,s,n]) * qS[t,s,n];
	E_{name}_qCO2agg[t]$(txE[t])..										qCO2agg[t]			=E= sum([s,n]$(dqCO2[s,n]), qCO2[t,s,n])-qCO2Base * @EOP_Tech(tauCO2agg[t], DACCost[t], DACSmooth[t]);
$ENDBLOCK

$BLOCK B_{name}_calibD
	E_{name}_uAbatet0[t,s,n]$(dqCO2[s,n] and t0[t])..					uAbate[t,s,n]		=E= sum(tech$(dTechS[t,s,tech]), techPot[t, s, tech] * @EOP_Tech(tauCO2[t,s,n], {cost}, techSmooth[t,s,tech]));
	E_{name}_uAbateCt0[t,s,n,tech]$(dTechSN[t,s,n,tech] and t0[t])..	uAbateC[t,s,n,tech] =E= techPot[t,s,tech] * @EOP_Cost(tauCO2[t,s,n], {cost}, techSmooth[t,s,tech]);
	E_{name}_qCO2calib[t,s,n]$(dqCO2[s,n] and txE[t])..					uCO2[t,s,n]	=E= uCO20[t,s,n] * (1+uCO2calib[s,n]);
$ENDBLOCK
"""

# Cost and supply of abatement capital:
def EOP_SqrAdjCosts(name):
	return f""" 
$BLOCK B_{name}_adjCost
	E_{name}_qKd[t,tech]$(dTech[t,tech] and tx0E[t])..			pKEOP[t,tech] * qKEOP[t,tech] =E= sum([s,n]$(dTechSN[t,s,n,tech]), uCO2[t,s,n]*qS[t,s,n]*uAbateC[t,s,n,tech]); # demand for abatement capital
	E_{name}_uEOP[t,s,tech]$(dTechS[t,s,tech] and txE[t])..		uEOP[t,s,tech]  =E= techPot[t,s,tech]*sum(n$(dTechSN[t,s,n,tech]), uCO2[t,s,n]*qS[t,s,n])/sum([ss,n]$(dTechSN[t,ss,n,tech]), uCO2[t,ss,n]*qS[t,ss,n]*techPot[t,ss,tech]); # share of abatement firm owned by sector s
	# E_{name}_uEOP[t,s,tech]$(dTechS[t,s,tech] and txE[t])..		uEOP[t,s,tech]  =E= sum(n$(dTechSN[t,s,n,tech]), uCO2[t,s,n]*qS[t,s,n]*uAbateC[t,s,n,tech]) / (pKEOP[t,tech] * qKEOP[t,tech]); # share of abatement firm owned by sector s
	E_{name}_techCost[t,s,tech]$(dTechS[t,s,tech] and txE[t])..	techCost[t,s,tech]	=E= uKEOP[t,tech] * pKEOP[t,tech]; # technology cost idx
	E_{name}_LOM[t,tech]$(dTech[t,tech] and txE[t])..			qKEOP[t+1,tech]		=E= (qKEOP[t,tech]*(1-rDeprEOP[tech])+qIEOP[t,tech])/(1+g_LR); # Law of motion for abatement capital
	E_{name}_pK[t,tech]$(dTech[t,tech] and tx02E[t])..			pKEOP[t,tech]		=E= Rrate[t]*(1+adjCostParEOP[tech]*( (qIEOP[t-1,tech]+qKmin[t-1,tech]*(rDeprEOP[tech]+g_LR))/(qKEOP[t-1,tech]+qKmin[t-1,tech])-(rDeprEOP[tech]+g_LR)))/(1+infl_LR)+adjCostParEOP[tech]*0.5*(sqr(rDeprEOP[tech]+g_LR)-sqr((qIEOP[t,tech]+qKmin[t,tech]*(rDeprEOP[tech]+g_LR))/(qKEOP[t,tech]+qKmin[t,tech])))-(1-rDeprEOP[tech])*(1+adjCostParEOP[tech]*((qIEOP[t,tech]+qKmin[t,tech]*(rDeprEOP[tech]+g_LR))/(qKEOP[t,tech]+qKmin[t,tech])-(rDeprEOP[tech]+g_LR))); # Tobin's Q for abatement capital
	E_{name}_pKT[t,tech]$(dTech[t,tech] and t2E[t])..			pKEOP[t,tech]		=E= Rrate[t]*(1+adjCostParEOP[tech]*( (qIEOP[t-1,tech]+qKmin[t-1,tech]*(rDeprEOP[tech]+g_LR))/(qKEOP[t-1,tech]+qKmin[t-1,tech])-(rDeprEOP[tech]+g_LR)))/(1+infl_LR)+rDeprEOP[tech]-1; # steady state approximation of Tobin's Q
	E_{name}_Ktvc[t,tech]$(dTech[t,tech] and tE[t])..			qKEOP[t,tech]	 	=E= (1+KtvcEOP[tech])*qKEOP[t-1,tech]/(1+g_LR); # TVC condition for abatement capital
	E_{name}_divd[t,tech]$(dTech[t,tech] and txE[t])..			divdEOP[t,tech]		=E= pKEOP[t,tech]*qKEOP[t,tech]-qIEOP[t,tech]-(qKEOP[t,tech]+qKmin[t,tech])*adjCostParEOP[tech]*0.5*sqr((qIEOP[t,tech]+qKmin[t,tech]*(rDeprEOP[tech]+g_LR))/(qKEOP[t,tech]+qKmin[t,tech])-(rDeprEOP[tech]+g_LR));
$ENDBLOCK

$BLOCK B_{name}_calibS
	E_{name}_pKEOPt0[t,tech]$(dTech[t,tech] and t0[t])..	pKEOP[t,tech]*qKEOP[t,tech]	=E= sum([s,n]$(dTechSN[t,s,n,tech]), uCO2[t,s,n]*qS[t,s,n]*uAbateC[t,s,n,tech]);
	E_{name}_qKEOPt0[t,tech]$(dTech[t,tech] and t0[t])..	pKEOP[t,tech]	=E= Rrate[t]+adjCostParEOP[tech]*0.5*(sqr(rDeprEOP[tech]+g_LR)-sqr((qIEOP[t,tech]+qKmin[t,tech]*(rDeprEOP[tech]+g_LR))/(qKEOP[t,tech]+qKmin[t,tech])))-(1-rDeprEOP[tech])*(1+adjCostParEOP[tech]*((qIEOP[t,tech]+qKmin[t,tech]*(rDeprEOP[tech]+g_LR))/(qKEOP[t,tech]+qKmin[t,tech])-(rDeprEOP[tech]+g_LR))); # Tobin's Q for abatement capital, t0
$ENDBLOCK
"""


EOP_CapIte = f"""
techCost.l[t,s,tech]$(dTechS[t,s,tech] and txE[t]) = uKEOP.l[t,tech] * pKEOP.l[t,tech];
uAbateC.l[t,s,n,tech]$(dTechSN[t,s,n,tech] and txE[t]) = techPot.l[t,s,tech] * @EOP_Cost(tauCO2.l[t,s,n], techCost.l[t,s,tech], techSmooth.l[t,s,tech]);
qKEOP.l[t,tech]$(dTech[t,tech] and txE[t]) = sum([s,n]$(dTechSN[t,s,n,tech]), uCO2.l[t,s,n]*qS.l[t,s,n]*uAbateC.l[t,s,n,tech])/pKEOP.l[t,tech];
qKEOP.l[t,tech]$(dTech[t,tech] and tE[t])  = (1+KtvcEOP.l[tech])*qKEOP.l[t-1,tech]/(1+g_LR);
qIEOP.l[t,tech]$(dTech[t,tech] and txE[t]) = (1+g_LR)*qKEOP.l[t+1,tech]+(rDeprEOP.l[tech]-1)*qKEOP.l[t,tech];
"""

EOP_PriceIte = f"""
pKEOP.l[t,tech]$(dTech[t,tech] and t2E[t])	= Rrate.l[t]*(1+adjCostParEOP.l[tech]*( (qIEOP.l[t-1,tech]+qKmin.l[t-1,tech]*(rDeprEOP.l[tech]+g_LR))/(qKEOP.l[t-1,tech]+qKmin.l[t-1,tech])-(rDeprEOP.l[tech]+g_LR)))/(1+infl_LR)+rDeprEOP.l[tech]-1;
pKEOP.l[t,tech]$(dTech[t,tech] and tx02E[t])= Rrate.l[t]*(1+adjCostParEOP.l[tech]*( (qIEOP.l[t-1,tech]+qKmin.l[t-1,tech]*(rDeprEOP.l[tech]+g_LR))/(qKEOP.l[t-1,tech]+qKmin.l[t-1,tech])-(rDeprEOP.l[tech]+g_LR)))/(1+infl_LR)+adjCostParEOP.l[tech]*0.5*(sqr(rDeprEOP.l[tech]+g_LR)-sqr((qIEOP.l[t,tech]+qKmin.l[t,tech]*(rDeprEOP.l[tech]+g_LR))/(qKEOP.l[t,tech]+qKmin.l[t,tech])))-(1-rDeprEOP.l[tech])*(1+adjCostParEOP.l[tech]*((qIEOP.l[t,tech]+qKmin.l[t,tech]*(rDeprEOP.l[tech]+g_LR))/(qKEOP.l[t,tech]+qKmin.l[t,tech])-(rDeprEOP.l[tech]+g_LR)));
pKEOP.l[t,tech]$(dTech[t,tech] and t0[t])	= Rrate.l[t]+adjCostParEOP.l[tech]*0.5*(sqr(rDeprEOP.l[tech]+g_LR)-sqr((qIEOP.l[t,tech]+qKmin.l[t,tech]*(rDeprEOP.l[tech]+g_LR))/(qKEOP.l[t,tech]+qKmin.l[t,tech])))-(1-rDeprEOP.l[tech])*(1+adjCostParEOP.l[tech]*((qIEOP.l[t,tech]+qKmin.l[t,tech]*(rDeprEOP.l[tech]+g_LR))/(qKEOP.l[t,tech]+qKmin.l[t,tech])-(rDeprEOP.l[tech]+g_LR)));
uEOP.l[t,s,tech]$(dTechS[t,s,tech] and txE[t]) = techPot.l[t,s,tech]*sum(n$(dTechSN[t,s,n,tech]), uCO2.l[t,s,n]*qS.l[t,s,n])/sum([ss,n]$(dTechSN[t,ss,n,tech]), uCO2.l[t,ss,n]*qS.l[t,ss,n]*techPot.l[t,ss,tech]);
"""


init_SqrAdjCosts = f"""
uAbateC.l[t,s,n,tech]$(dTechSN[t,s,n,tech]) = techPot.l[t,s,tech] * @EOP_Cost(tauCO2.l[t,s,n], techCost.l[t,s,tech], techSmooth.l[t,s,tech]);
pKEOP.l[t,tech]$(dTech[t,tech]) = Rrate.l[t]+rDeprEOP.l[tech]-1;
qKEOP.l[t,tech]$(dTech[t,tech]) = sum([s,n]$(dTechSN[t,s,n,tech]), uCO2.l[t,s,n]*qS.l[t,s,n]*uAbateC.l[t,s,n,tech])/pKEOP.l[t,tech];
qIEOP.l[t,tech]$(dTech[t,tech] and txE[t]) = (1+g_LR)*qKEOP.l[t+1,tech]+(rDeprEOP.l[tech]-1)*qKEOP.l[t,tech];
qKmin.l[t,tech]$(dTech[t,tech])  = qKminRate*sum([s,n]$(dTechSN[t,s,n,tech]), techPot.l[t,s,tech] * techCost.l[t,s,tech] * uCO2.l[t,s,n] * qS.l[t,s,n]) / pKEOP.l[t,tech];
# qKmin.l[t,tech]$(dTech[t,tech] and txE[t]) = qKminRate*sum([s,n]$(dTechSN[t+1,s,n,tech]), techPot.l[t+1,s,tech] * techCost.l[t+1,s,tech] * uCO2.l[t+1,s,n] * qS.l[t+1,s,n]) / pKEOP.l[t+1,tech];
# qKmin.l[t,tech]$(dTech[t,tech] and tE[t])  = qKminRate*sum([s,n]$(dTechSN[t,s,n,tech]), techPot.l[t,s,tech] * techCost.l[t,s,tech] * uCO2.l[t,s,n] * qS.l[t,s,n]) / pKEOP.l[t,tech];
{EOP_PriceIte}
"""

