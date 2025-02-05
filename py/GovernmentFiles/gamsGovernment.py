from gamsSnippets_noOut import *

############################################################
################		1. GovNCES			################
############################################################

# 1.1. Price/tax blocks: 
def priceBlock(name, m, addInc_tx0 = '', addInc_t0 = ''):
	return f"""
$BLOCK B_{name}
	E_{name}_pD[t,s,n]$({m}_input[s,n] and txE[t])..	pD[t,s,n]		=E= p[t,n]*(1+tauD[t,s,n]); # effective input prices
	E_{name}_TotalTax[t,s]$({m}_sm[s] and txE[t])..		TotalTax[t,s]	=E= tauLump[t,s]+sum(n$({m}_input[s,n]), tauD[t,s,n] * p[t,n] * qD[t,s,n]); # total tax transfers
	E_{name}_vA0[t,s]$({m}_sm[s] and t0[t])..			vA[t+1,s]		=E= (vA[t,s] * Rrate[t]+sum(ss$(d_TotalTax[ss]), TotalTax[t,ss])-sum(n$({m}_input[s,n]), p[t,n]*qD[t,s,n])-TotalTax[t,s]{addInc_t0})/(1+g_LR); # law of motion for government assets, initial year
	E_{name}_vA[t,s]$({m}_sm[s] and tx0E[t])..			vA[t+1,s]		=E= (vA[t,s] * Rrate[t]+sum(ss$(d_TotalTax[ss]), TotalTax[t,ss])-sum(n$({m}_input[s,n]), p[t,n]*qD[t,s,n])-TotalTax[t,s]{addInc_tx0})/(1+g_LR); # law of motion for government assets
$ENDBLOCK
"""

# 1.2. Block for calibration of taxes using permannet adjustments. Can accept different tax instruments.
def taxCalibBlock(name, m, taxInstr, taxCond):
	""" taxInstr is a gpy symbol, taxCond is a condition"""
	return f"""
$BLOCK B_{name}
	E_{name}_taxRevPar{Syms.gpyDomains(taxInstr)}{Syms.gpyCondition(taxCond)}..	{Syms.gpy(taxInstr)} =E= {Syms.gpy(taxInstr).replace(taxInstr.name, taxInstr.name+'0')}+taxRevPar[s];
$ENDBLOCK
"""

############################################################
################		2. GovPolicy		################
############################################################

# 2.1. Proportional Tax Changes: Adjust the same type of tax with distributional impact taxDistr.
def distrTauLump(name):
	return f"""
$BLOCK B_{name}_tauLS
	E_{name}_tauLump[t,s]$({name}_sTax[s] and txE[t])..	tauLump[t,s] =E= uDistTauLump[t,s] * diffTauLump[t] + tauLump0[t,s];
$ENDBLOCK
"""


# Block of equations for stand alone, baseline model:
def balancedBudget(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_pw[t,s,n]$({m}_input[s,n] and txE[t])..	pD[t,s,n]	=E= p[t,n]*(1+tauD[t,s,n]);
	E_{name}_taxRev[t,s]$({m}_sm[s] and txE[t])..	TotalTax[t,s]	=E= sum(n$({m}_input[s,n]), tauD[t,s,n] * p[t,n]*qD[t,s,n]);
	E_{name}_bb[t,s]$({m}_sm[s] and txE[t])..			jTerm[s]	=E= sum(ss$(d_TotalTax[ss]), TotalTax[t,ss])-sum(n$({m}_input[s,n]), p[t,n]*qD[t,s,n]);
$ENDBLOCK
"""

def taxCalibration(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_taxCal[t,s,n]$({m}_input[s,n] and txE[t])..	tauD[t,s,n]	=E= tauD0[t,s,n]+taxRevPar[s];
$ENDBLOCK
"""
