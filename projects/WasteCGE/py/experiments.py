import pyDatabases, pandas as pd, numpy as np
import warnings
from pyDatabases import OrdSet, noneInit, adj, adjMultiIndex
from functools import reduce

_stdOrder = OrdSet(['t','s','ss','n','nn','taxTypes','gc'])
def stdSort(symbol, order = None):
	if isinstance(pyDatabases.getIndex(symbol), pd.MultiIndex):
		return symbol.reorder_levels([x for x in noneInit(order, _stdOrder+OrdSet(pyDatabases.getDomains(symbol))) if x in pyDatabases.getDomains(symbol)])
	else:
		return symbol


def runIRR(Mi, Rep, d0, Δ = 0.1, m = None, solDict = None, **kwargs):
	di = experimentIRR(Mi, noneInit(solDict, {}), Δ = Δ, m = m)
	Mi.db.aom(di['shock'], priority = 'second') 
	Mi.db.mergeInternal()
	di['db'] = Mi.solve(state = 'B')
	di = Rep(di['db'], di, d0 = d0)
	Mi.db.aom(adj.rc_pd(d0['db'](di['shock'].name), di['shock']), priority = 'second')
	return di

def experimentIRR(Mi, solDict, Δ = 0.1, m = None):
	""" Add experiment with internal rate of recycling (IRR) to solution dictionary. 
		Δ is the size of the change, m is the type of material to apply the change to (m = None uses all)."""
	ξnew = adj.rc_pd(Mi.db('intRcEff'), m)+Δ
	μWP0 = (Mi.db('uWS_int') * (Mi.db('qWS')/(1-Mi.db('uWS_int') * Mi.db('intRcEff')))).dropna() # μint * W^P in baseline
	solDict['shock'] = ξnew
	solDict['Δexp'] = -((ξnew-Mi.db('intRcEff')) * μWP0).dropna().groupby(['t','m']).sum() # expected decrease in use of virgin materials
	return solDict

def runRCEff(Mi, Rep, d0, Δα = .1, m = None, solDict = None, **kwargs):
	di = experimentRCEff(Mi, noneInit(solDict, {}), Δα = Δα)
	Mi.db.aom(di['shock'], priority = 'second') 
	Mi.db.mergeInternal()
	di['db'] = Mi.solve(state = 'B')
	di = Rep(di['db'], di, d0 = d0)
	Mi.db.aom(adj.rc_pd(d0['db'](di['shock'].name), di['shock']), priority = 'second')
	return di

def experimentRCEff(Mi, solDict, Δα = 0.1):
	""" Add experiment with increased recycling efficiency. The lower bound on recycling quality is raised by Δα. """
	solDict['shock'] = Mi.db('WTD_alphal')+Δα # parameter shock
	# Local technology functions used to define 'expected' effect of shock:
	def f_intApprox(x, l = 0, u = 1, eps = 0.0001):
		return (l+np.sqrt(np.square(x-l)+eps)+u-np.sqrt(np.square(x-u)+eps))/2
	def f_techGInv(y, l = 0, u = 1, b = 2):
		return ((u-y)/(u-l)).pow(1/b)
	def f_techF(r, l = 0, u = 1, b = 2):
		return l+(u-l)*(1-r.pow(b)/(1+b))
	# Given prices and scale (amount of waste to be treated), how much extra recycling do we get out of this shock?
	l, u, b, eps = Mi.db('WTD_alphal')+Δα, Mi.db('WTD_alphau'), Mi.db('WTD_beta'), Mi.db('WTD_smooth')
	y = f_intApprox(Mi.db('WTD_zetaE'), l = l, u = u, eps = eps) 
	r = f_techGInv(y, l= l, u = u, b = b) # R/R̄
	a = f_techF(r, l = l, u = u, b = b) # A/R
	R = Mi.db('WTD_W') * r # R
	A = (a * R).dropna() # A
	qSR0 = adjMultiIndex.applyMult(Mi.db('qS').xs('Waste',level='s'), Mi.db('nr2m_D')).droplevel('n').dropna() # supply of recycled materials in baseline, mapped to 'm' index
	solDict['Δexp'] = -(A-qSR0).dropna()
	return solDict

def runTaxVirgin(Mi, Rep, d0, Δ = .1, solDict = None, **kwargs):
	di = experimentTaxVirgin(Mi, Rep, noneInit(solDict, {}), Δ=Δ)
	Mi.db.aom(di['shock'], priority = 'second')
	Mi.db.mergeInternal()
	di['db'] = Mi.solve(state = 'B')
	di = Rep(di['db'], di, d0 = d0)
	Mi.db.aom(adj.rc_pd(d0['db'](di['shock'].name), di['shock']), priority = 'second')
	return di

def experimentTaxVirgin(Mi, Rep, solDict, Δ = .1):
	solDict['shock'] = adj.rc_pd(Mi.db('tauD'), Rep.vm)+Δ
	return solDict

def runRCMandate(Mi, Rep, d0, targetRate = .5, solDict = None, m = None, sIdx = None, **kwargs):
	di = experimentRCMandate(Mi, noneInit(solDict, {}), targetRate=targetRate, m = m, sIdx = sIdx)
	Mi.db.aom(di['shock'], priority = 'second')
	Mi.db.mergeInternal()
	di['db'] = Mi.solve(state = 'B')
	di = Rep(di['db'], di, d0 = d0)
	Mi.db.aom(adj.rc_pd(d0['db'](di['shock'].name), di['shock']), priority = 'second')
	return di

def experimentRCMandate(Mi, solDict, targetRate = .5, m = None, sIdx = None):
	mi = noneInit(m, Mi.db('m')) # relevant materials to target
	sIdx = noneInit(sIdx, pd.Index(['Waste'],name='s')) # relevant industry
	ni = adjMultiIndex.applyMult(mi, Mi.db('nr2m_D')) # map to relevant n index 
	R̄ = adj.rc_pd((Mi.db('WTD_W')*(1-Mi.db('WTD_dmin'))).dropna(), mi) 
	Rtarget = R̄ * targetRate
	solDict['Δexp'] = (R̄ * adj.rc_pd(Mi.db('WTD_r'), mi)).dropna()-Rtarget
	# Compute subsidy that results in this with partial equilibrium assumptions:
	pzw = adj.rc_pd(Mi.db('pD'), Mi.get('n_ZW',m='W')).droplevel(('s','n'))
	pmr = adj.rc_pd(Mi.db('p'), ni)
	pwe = adj.rc_pd(Mi.db('pS'), Mi.db('n_wasteE')).droplevel(('s','n'))
	Δγ  = adj.rc_pd(Mi.db('WTD_gr'), mi)-adj.rc_pd(Mi.db('WTD_ge'), mi)
	ζtarget = adj.rc_pd(Mi.db('WTD_alphau') - (Mi.db('WTD_alphau')-Mi.db('WTD_alphal'))*(targetRate**(Mi.db('WTD_beta'))), mi).dropna()
	τ = adjMultiIndex.bc(adj.rc_pd(1/(1+Mi.db('markup')), sIdx), mi)-(pzw*Δγ+adj.rc_pd(Mi.db('WTD_gwe'), mi) * adjMultiIndex.bc(pwe, mi))/(pmr*ζtarget)
	τ = stdSort(τ.dropna()).droplevel('m').rename('tauS')
	solDict['shock'] = τ
	return solDict

def runTaxWasteGen(Mi, Rep, d0, Δ = .1, solDict = None, **kwargs):
	di = experimentTaxWasteGen(Mi, noneInit(solDict, {}), Δ=Δ)
	Mi.db.aom(di['shock'], priority = 'second')
	Mi.db.mergeInternal()
	di['db'] = Mi.solve(state = 'B')
	di = Rep(di['db'], di, d0 = d0)
	Mi.db.aom(adj.rc_pd(d0['db'](di['shock'].name), di['shock']), priority = 'second')
	return di

def experimentTaxWasteGen(Mi, solDict, Δ = .1):
	uWS_adValorem = (Mi.db('uWS').groupby(['t','s','n']).sum() / Mi.db('p')).dropna() # unit tax per ton of waste across m types
	solDict['shock'] = Mi.db('tauD').add(uWS_adValorem * Δ, fill_value = 0).rename('tauD') # add on top of existing taxes
	return solDict

def runSubsidyRecycledInputs(Mi, Rep, d0, Δ = .1, solDict = None, **kwargs):
	di = experimentSubsidyRecycledInputs(Mi, Rep, noneInit(solDict, {}), Δ=Δ)
	Mi.db.aom(di['shock'], priority = 'second')
	Mi.db.mergeInternal()
	di['db'] = Mi.solve(state = 'B')
	di = Rep(di['db'], di, d0 = d0)
	Mi.db.aom(adj.rc_pd(d0['db'](di['shock'].name), di['shock']), priority = 'second')
	return di

def experimentSubsidyRecycledInputs(Mi, Rep, solDict, Δ = .1):
	solDict['shock'] = adj.rc_pd(Mi.db('tauD'), Rep.rm)-Δ
	return solDict