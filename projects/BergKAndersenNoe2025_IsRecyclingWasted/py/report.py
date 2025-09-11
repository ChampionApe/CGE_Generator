import pyDatabases, pandas as pd, numpy as np
import warnings
from pyDatabases import OrdSet, noneInit, adj, adjMultiIndex
from functools import reduce

class Standard:
	def __init__(self, db, vm = None, rm = None, si = None, cpi = None):
		self.db = db
		self.vm = noneInit(vm, adj.rc_pd(self.db('n2m2k2o'), pd.Index(['V'], name = 'k')).get_level_values('n'))
		self.rm = noneInit(rm, adj.rc_pd(self.db('n2m2k2o'), pd.Index(['R'], name = 'k')).get_level_values('n')) # recycled materials
		self.si = noneInit(si, self.db('s').difference(self.db('s_f')))
		self.n2m = self.db('n2m2k2o').droplevel(['k','o'])
		self.cpi = noneInit(cpi, ('HH','C')) # consumer price index element in price vector

	def __call__(self, dbi, solDict, d0 = None, Δexp = None, **kwargs):
		solDict.update({k:getattr(self,f'get{k}')(dbi, **kwargs) for k in self.listOfSymbols})
		solDict.update({k:getattr(self,f'get{k}')(solDict) for k in ('QvTot','QrTot','QtTot')})
		solDict.update({k:getattr(self,f'get{k}')(solDict) for k in ('CircularRate','CircularRateTot')})
		if d0 is not None:
			if 'Δexp' not in solDict:
				solDict['Δexp'] = noneInit(Δexp, pd.Series(1, index = self.db('t'))) # if the shock does not have an expected effect --> insert 1 to avoid errors in reporting functions
			solDict.update({k: getattr(self,f'get{k}')(solDict, d0) for k in ('Rbv','Rbr','Rbt','RbvTot','RbrTot','RbtTot','ΔQv_Qv','ΔQr_Qr','ΔQt_Qt','ΔQvTot_QvTot','ΔQrTot_QrTot','ΔQtTot_QtTot')})
		return solDict

	@property
	def listOfSymbols(self):
		return ['Qv','Vv','Qr','Vr','Qt','Vv','Cpi','RealGDPi','RealGDP','MaterialPrices','MaterialIntensityi','MaterialIntensity']

	def getQv(self, dbi = None, vmi = None, si = None, **kwargs):
		""" Quantity of virgin materials"""
		return adjMultiIndex.applyMult(adj.rc_pd(dbi('qD'), ('and', [noneInit(vmi, self.vm), noneInit(si, self.si)])).groupby(['t','n']).sum(), self.n2m).groupby(['t','m']).sum()

	def getVv(self, dbi = None, vmi = None, si = None, **kwargs):
		""" Value of virgin materials"""
		return adjMultiIndex.applyMult(adj.rc_pd((dbi('qD') * dbi('p')).dropna(), ('and', [noneInit(vmi, self.vm), noneInit(si, self.si)])).groupby(['t','n']).sum(), self.n2m).groupby(['t','m']).sum()

	def getQr(self, dbi, rmi = None, si = None, **kwargs):
		""" Quantity of recycled materials"""
		return adjMultiIndex.applyMult(adj.rc_pd(dbi('qD'), ('and', [noneInit(rmi, self.rm), noneInit(si, self.si)])).groupby(['t','n']).sum(), self.n2m).groupby(['t','m']).sum()

	def getVr(self, dbi = None, vmi = None, si = None, **kwargs):
		""" Value of recycled materials"""
		return adjMultiIndex.applyMult(adj.rc_pd((dbi('qD') * dbi('p')).dropna(), ('and', [noneInit(vmi, self.vm), noneInit(si, self.si)])).groupby(['t','n']).sum(), self.n2m).groupby(['t','m']).sum()

	def getQt(self, dbi, vmi = None, rmi = None, si = None, **kwargs):
		""" Quantity of recycled+virgin materials"""
		return self.getQv(dbi, vmi = vmi, si = si).add(self.getQr(dbi, rmi = rmi, si = si), fill_value=0)

	def getVt(self, dbi, vmi = None, rmi = None, si = None, **kwargs):
		""" Quantity of recycled+virgin materials"""
		return self.getVv(dbi, vmi = vmi, si = si).add(self.getVr(dbi, rmi = rmi, si = si), fill_value=0)

	def getCpi(self, dbi, **kwargs):
		""" Consumer price index """
		return dbi('pD').xs(self.cpi,level=('s','n'))

	def getRealGDPi(self, dbi, sGDP = None, **kwargs):
		return adj.rc_pd((dbi('qS') * dbi('p')).dropna(), noneInit(sGDP, dbi('s_p').union(dbi('s_i')))).groupby(['t','s']).sum()/self.getCpi(dbi)

	def getRealGDP(self, dbi, sGDP = None, **kwargs):
		return self.getRealGDPi(dbi, sGDP = sGDP).groupby('t').sum()

	def getMaterialPrices(self, dbi, vmi = None, rmi = None, **kwargs):
		return adjMultiIndex.applyMult(adj.rc_pd(dbi('p'), noneInit(vmi, self.vm).union(noneInit(rmi, self.rm))), dbi('n2m2k2o')).droplevel('n') / self.getCpi(dbi)

	def getMaterialIntensityi(self, dbi, sGDP = None, **kwargs):
		sGDP = noneInit(sGDP, dbi('s_p').union(dbi('s_i')))
		return (self.getVt(dbi, si = sGDP, **kwargs) / self.getCpi(dbi)) / self.getRealGDP(dbi, sGDP = sGDP)

	def getMaterialIntensity(self, dbi, sGDP = None, **kwargs):
		return self.getMaterialIntensityi(dbi, sGDP = sGDP, **kwargs).groupby('t').sum()

	# Aux computations:
	def getQvTot(self, di, **kwargs):
		""" Quantity of virgin materials, sum over m"""
		return di['Qv'].groupby('t').sum()
	def getQrTot(self, di, **kwargs):
		""" Quantity of recycled materials, sum over m"""
		return di['Qr'].groupby('t').sum()
	def getQtTot(self, di, **kwargs):
		""" Quantity of total materials, sum over m"""
		return di['Qt'].groupby('t').sum()
	def getCircularRate(self, di, **kwargs):
		return di['Qr']/di['Qt']
	def getCircularRateTot(self, di, **kwargs):
		return di['QrTot']/di['QtTot']

	# Changes compared to a baseline:
	def getRbv(self, di, d0, **kwargs):
		""" Rebound effect, virgin materials"""
		return ((di['Δexp']-(di['Qv']-d0['Qv']))/di['Δexp']).dropna()
	def getRbr(self, di,d0,**kwargs):
		""" ΔRecycled materials/mechanical effect of shock"""
		return ((di['Δexp']-(di['Qr']-d0['Qr']))/di['Δexp']).dropna()
	def getRbt(self, di,d0,**kwargs):
		""" ΔMaterials/mechanical effect of shock"""
		return ((di['Δexp']-(di['Qt']-d0['Qt']))/di['Δexp']).dropna()

	def getRbvTot(self, di, d0, **kwargs):
		""" Rebound effect, virgin materials"""
		return ((di['Δexp'].groupby('t').sum()-(di['QvTot']-d0['QvTot']))/di['Δexp'].groupby('t').sum()).dropna()
	def getRbrTot(self,di,d0,**kwargs):
		""" ΔRecycled materials/mechanical effect of shock"""
		return ((di['Δexp'].groupby('t').sum()-(di['QrTot']-d0['QrTot']))/di['Δexp'].groupby('t').sum()).dropna()
	def getRbtTot(self,di,d0,**kwargs):
		""" ΔMaterials/mechanical effect of shock"""
		return ((di['Δexp'].groupby('t').sum()-(di['QtTot']-d0['QtTot']))/di['Δexp'].groupby('t').sum()).dropna()

	def getΔQv_Qv(self, di,d0,**kwargs):
		""" Percentage change in virgin material use"""		
		return ((di['Qv']-d0['Qv'])/d0['Qv']).dropna()
	def getΔQr_Qr(self, di,d0,**kwargs):
		""" Percentage change in recycled material use"""		
		return ((di['Qr']-d0['Qr'])/d0['Qr']).dropna()
	def getΔQt_Qt(self, di,d0,**kwargs):
		""" Percentage change in total material use"""		
		return ((di['Qt']-d0['Qt'])/d0['Qt']).dropna()
	def getΔQvTot_QvTot(self, di,d0,**kwargs):
		""" Percentage change in virgin material use, sum over m"""		
		return ((di['QvTot']-d0['QvTot'])/d0['QvTot']).dropna()
	def getΔQrTot_QrTot(self, di,d0,**kwargs):
		""" Percentage change in recycled material use, sum over m"""		
		return ((di['QrTot']-d0['QrTot'])/d0['QrTot']).dropna()
	def getΔQtTot_QtTot(self, di,d0,**kwargs):
		""" Percentage change in total material use, sum over m"""		
		return ((di['QtTot']-d0['QtTot'])/d0['QtTot']).dropna()
