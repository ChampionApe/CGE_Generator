from auxfuncs import *
from pyDatabases.gpyDB import gpy, GpyDB, AggDB
from gmsPython import gmsWrite, Model


class CreateIOTargets:
	""" Assume db contains IO with 1-to-1 correspondence: Sectors are uniquely associated with one output. """
	def __init__(self, dbIO, **kwargs):
		self.db = GpyDB(name = 'adjIO', ws = dbIO.ws, **kwargs)
		self.dbIO = dbIO

	def readFsets(self):
		self.db['F2n'] = pd.MultiIndex.from_product([self.dbIO('s_f'), self.dbIO('n_F')])
		self.db['F2synF'] = self.db('F2n').rename(['s','ss'])
		self.db['synF2F'] = self.db('F2synF').reorder_levels(['ss','s']).rename(['s','ss'])

	def add_vS0syn(self):
		vS0 = self.db('vD0').groupby('n').sum()
		vSfor = adjMultiIndex.bc(adj.rc_pd(vS0, self.dbIO('n_F')), self.dbIO('s_f')).reorder_levels(['s','n'])
		vSdom = adj.rc_pd(vS0, ('not', self.dbIO('n_F')))
		vSdom.index = pd.MultiIndex.from_arrays([vSdom.index.rename('s'), vSdom.index])
		self.db['vS0'] = vSfor.combine_first(vSdom)
		vS0.index = pd.MultiIndex.from_arrays([vS0.index.rename('s'), vS0.index])
		self.db['vS0syn'] = vS0

	def add_vD0syn(self):
		vD_DD = adj.rc_pd(self.db('vD0'), ('and', [self.dbIO('n_p'), self.dbIO('s_p')])) # domestic demand patterns 
		μD_DD = vD_DD/vD_DD.groupby('n').sum() # rewritten in shares.

		# If some goods are only exported (i.e. no domestic shares), use uniform distribution:
		vD_F = adj.rc_pd(self.db('vD0'), self.dbIO('s_f')).droplevel('s') # foreign sector's demand
		n_onlyToF = vD_F.index.difference(vD_DD.index.get_level_values('n').unique()) # what goods are only exported?
		v_nOnlyF = pd.Series(1, index = pd.MultiIndex.from_product([self.dbIO('n_p').rename('s'), n_onlyToF])) # create vector of ones for all combinations
		μD_DD_and_nOnlyF = μD_DD.combine_first((v_nOnlyF / v_nOnlyF.groupby('n').sum())) # add to shares

		# Multiply shares onto foreign demand:
		vD_F_mapped = (μD_DD_and_nOnlyF * vD_F).dropna() # use shares - dropna() if foreign sector does not have demand in a certain domain.
		vD_F_mapped = adjMultiIndex.applyMult(vD_F_mapped, self.dbIO('dom2for').rename(['s','ss'])).droplevel('s').rename_axis(['n','s']) # switch from domestic good names to synthetic foreign sector names
		vD_F_mapped.index = vD_F_mapped.index.reorder_levels(['s','n']) # reorder name order
		self.db['vD0syn'] = pd.concat([vD_DD, vD_F_mapped, adj.rc_pd(self.db('vD0'), self.dbIO('n_F'))], axis = 0)

	def add_vDnSyn_vSnSyn(self, vDnRaw, vSnRaw):
		self.db['vDnRaw'], self.db['vSnRaw'] = vDnRaw, vSnRaw
		# Split IO sectors demand for materials onto domestic/foreign based on output shares:
		dS_n = adj.rc_pd(vSnRaw, ('not', self.dbIO('s_f'))).groupby('n').sum() # domestic 
		dS_netOfExp = dS_n.add(-vDnRaw.xs('F'), fill_value=0) # all exports are domestic type goods
		fS_n = adj.rc_pd(vSnRaw, self.dbIO('s_f')).groupby('n').sum() # foreign supply
		tS_n = dS_n.add(fS_n, fill_value=0) # total supply
		tS_netOfExp = dS_netOfExp.add(fS_n, fill_value = 0)
		dS_shares = dS_netOfExp/tS_netOfExp
		fS_shares = 1-dS_shares
		vDn_DD = adj.rc_pd(vDnRaw, ('not', self.dbIO('s_f'))) * dS_shares # domestic demand for domestic goods
		vDn_DF = adj.rc_pd(vDnRaw, ('not', self.dbIO('s_f'))) * fS_shares # domestic demand for foreign goods
		demandShares = vDn_DD/vDn_DD.groupby('n').sum() 
		vDn_FD = (demandShares * vDnRaw.xs('F')).dropna()
		vDn_FD.index = vDn_FD.index.set_levels(vDn_FD.index.levels[0]+'_F', level = 's') 

		# If some materials are only exported, then domestic demand shares does provide any information here. In this case, instead, adjust by relative size of foreign synthetic sectors:
		predictedFD = vDn_FD.groupby('s').sum() # foreign demand for materials accounted for by "non-uniform mapping"
		forDemandRes = (self.db('vD0syn').groupby('s').sum()-predictedFD).dropna() # demand for IO goods net of predicted materials demands
		relSizes = forDemandRes/forDemandRes.sum() # relative sizes of the synthetic foreign sector's
		vDn_FD_NAF = vDnRaw.xs('F').add(-vDn_FD.groupby('n').sum(), fill_value=0) # part of foreign demand for domestic materials not accounted for above due to sparsity of domestic demand 
		vDn_FD = vDn_FD.combine_first(adjMultiIndex.bc(relSizes, vDn_FD_NAF) * vDn_FD_NAF) 

		# Update index names: Foreign sector definitions (add _F suffix) + goods definition (suffix D/F depending on country of origin)
		# vDn_DD.index = vDn_DD.index.set_levels(vDn_DD.index.levels[-1]+'D', level = 'n') # add suffix
		vDn_DF.index = vDn_DF.index.set_levels(vDn_DF.index.levels[-1]+'_F', level = 'n') # add suffix
		# vDn_FD.index = vDn_FD.index.set_levels(vDn_FD.index.levels[-1]+'D', level = 'n') # add suffix
		self.db['vDnSyn'] = pd.concat([vDn_DD, vDn_DF, vDn_FD], axis = 0)

		# Split IO sectors supply into domestic/foreign (trivial) + split up aggregate foreign sector into synthetic "subsectors" using domestic production patterns:
		vSn_D = adj.rc_pd(vSnRaw, ('not', self.dbIO('s_f'))) # domestic supply of materials
		μSn_D = vSn_D/vSn_D.groupby('n').sum() # sectors' shares of supply of materials 
			
		# Default to a uniform distribution if a material is only produced abroad:
		n_onlyFromF = vSnRaw.xs('F',level='s').index.difference(vSn_D.index.get_level_values('n').unique()) # goods only produced abroad
		v_onlyFromF = pd.Series(1, index = pd.MultiIndex.from_product([self.dbIO('n_F').rename('s'), n_onlyFromF]))
		μSn_D_and_nOnlyF = μSn_D.combine_first((v_onlyFromF/v_onlyFromF.groupby('s').sum())) # combine shares from domestic distributions + uniform distribution for goods without domestic supply		

		# Combine into one vector and add domestic/foreign origin:
		vSn_F = (μSn_D_and_nOnlyF * vSnRaw.xs('F',level='s')).dropna()
		# vSn_D.index = vSn_D.index.set_levels(vSn_D.index.levels[-1]+'D', level = 'n')
		vSn_F.index = vSn_F.index.set_levels([vSn_F.index.levels[0]+'_F', vSn_F.index.levels[1]+'_F'])
		self.db['vSnSyn'] = vSn_D.combine_first(vSn_F)

	def add_vDsyn(self):
		self.db['Δs'] = self.db('vDnSyn').groupby('s').sum() # total change in demand in each sector
		α_  = self.db('vDnSyn')/self.db('Δs') # input shares
		μ_  = self.db('vSnSyn')/self.db('vSnSyn').groupby('n').sum() # output intensities 
		# Map to common multiindices:
		self.db['α'] = adjMultiIndex.bc(α_, μ_).sort_index() # broadcast to common domains
		self.db['μ'] = adjMultiIndex.bc(μ_, α_).sort_index() # broadcast to common domains
		# Compute β:
		αMat, μMat = self.db('α').unstack('n').fillna(0), self.db('μ').unstack('n').fillna(0)
		β = np.matmul(αMat.values, μMat.values.T)
		self.db['β'] = pd.DataFrame(β, index = αMat.index, columns = αMat.index.rename('n'))
		self.db['vDsyn'] = self.db('vD0syn').add(-self.db('Δs').multiply(self.db('β').stack(), fill_value = 0), fill_value = 0)
		self.db['vDsyn'] = self.db('vDsyn')[self.db('vDsyn') != 0] # remove zeros

	def add_vD(self):
		self.db['vD'] = adjMultiIndex.applyMult(adj.rc_pd(self.db('vDsyn'), self.db('synF2F')), self.db('synF2F')).groupby(['ss','n']).sum().rename_axis(['s','n']).combine_first(adj.rc_pd(self.db('vDsyn'), self.dbIO('s_p')))

	def add_vDn(self):
		self.db['vDn'] = adjMultiIndex.applyMult(adj.rc_pd(self.db('vDnSyn'), self.db('synF2F')), self.db('synF2F')).groupby(['ss','n']).sum().rename_axis(['s','n']).combine_first(adj.rc_pd(self.db('vDnSyn'), self.dbIO('s_p')))

	def add_vS(self):
		vS = self.db('vS0syn').groupby('s').sum().add(-self.db('vSnSyn').groupby('s').sum(), fill_value=0)
		vS.index = pd.MultiIndex.from_arrays([vS.index, vS.index.rename('n')])
		vS = adjMultiIndex.applyMult(adj.rc_pd(vS, self.db('synF2F')), self.db('synF2F')).groupby(['ss','n']).sum().rename_axis(['s','n']).combine_first(adj.rc_pd(vS, self.dbIO('s_p')))
		self.db['vS'] = vS

	def add_vSn(self):
		self.db['vSn'] = adjMultiIndex.applyMult(adj.rc_pd(self.db('vSnSyn'), self.db('synF2F')), self.db('synF2F')).groupby(['ss','n']).sum().rename_axis(['s','n']).combine_first(adj.rc_pd(self.db('vSnSyn'), self.dbIO('s_p')))

	def __call__(self, vD0, vDnRaw, vSnRaw):
		""" Add initial vectors of demand and supply + new data on demand and supply. """
		self.db['vD0'] = vD0
		self.readFsets()
		self.add_vS0syn()
		self.add_vD0syn()
		self.add_vDnSyn_vSnSyn(vDnRaw, vSnRaw)
		self.add_vDsyn()
		self.add_vD()
		self.add_vDn()
		self.add_vS()
		self.add_vSn()
		return self


class AdjustIO(Model):
	""" Adjust IO data with 1-to-1 correspondence between sectors and goods
		using supply-use data on 'other' goods for each sector. Requires the
		following inputs. """
	def __init__(self, name = 'adjIO', **kwargs):
		super().__init__(name = name, alias = [('n','nn'),('s','ss')], **kwargs)

	def initData(self, vD0, vD, vDn, vS0, vS, vSn):
		""" vD0::: Original demand over IO goods (parameter)
			vD:::  Target demand over IO goods (parameter)
			vDn::: Demand for new goods (parameter)
			vS::: Supply of IO goods after adj. (parameter) 
			vSn::: Supply of new goods adter adj. (parameter) """
		self.db['vD0'] = gpy(vD0, type = 'par')
		self.db['vD']  = gpy(vD, type = 'par')
		self.db['vDn'] = gpy(vDn, type = 'par')
		self.db['vS0'] = gpy(vS0, type = 'par')
		self.db['vS']  = gpy(vS, type = 'par')
		self.db['vSn'] = gpy(vSn, type = 'par')
		self.db['nm']  = self.db('vSn').index.levels[-1] # index of materials
		self.db['ns']  = self.db('vS0').index.levels[-1] # index of IO goods
		[self.db.__setitem__(f'd{k}', self.db(k).index) for k in ('vD0','vS0','vD','vS','vDn','vSn')];
		AggDB.readSets(self.db) # read set definitions from existing symbols
		self.db['vDsolve'] = self.db('vD0').copy().clip(0) # variable
		self.db['vSsolve'] = self.db('vS0').copy().clip(0) # variable
		self.db['obj'] = 0

	@property
	def text(self):
		return f"""
{gmsWrite.StdArgs.root()}
{gmsWrite.StdArgs.funcs()}
{gmsWrite.FromDB.declare(self.db)}
{gmsWrite.FromDB.load(self.db, gdx = self.db.name)}

$BLOCK B_adjustIO
	E_nBalance[n]$(ns[n])..	sum(s$(dvS0[s,n]), vSsolve[s,n])   =E= sum(s$(dvD0[s,n]), vDsolve[s,n]);
	E_vDsBalance[s]..		sum(n$(dvD0[s,n]), vD0[s,n]) =E= sum(n$(dvDn[s,n]), vDn[s,n])+sum(n$(dvD0[s,n]), vDsolve[s,n]);
	E_vSsBalance[s]..		sum(n$(dvS0[s,n]), vS0[s,n]) =E= sum(n$(dvSn[s,n]), vSn[s,n])+sum(n$(dvS0[s,n]), vSsolve[s,n]);
	E_obj..					obj =E= sum([s,n]$(dvD0[s,n]), sqr(vD0[s,n]-vDsolve[s,n]))+sum([s,n]$(dvS0[s,n]), sqr(vS0[s,n]-vSsolve[s,n]));
$ENDBLOCK

vDsolve.lo[s,n]$(dvD0[s,n]) = 0;
vDsolve.up[s,n]$(dvD0[s,n]) = inf;
vSsolve.lo[s,n]$(dvS0[s,n]) = 0;
vSsolve.up[s,n]$(dvS0[s,n]) = inf;
obj.lo = -inf;
obj.up = inf;

solve B_adjustIO  using NLP min obj;
"""

	def __call__(self, vD0, vD, vDn, vS0, vS, vSn):
		self.initData(vD0, vD, vDn, vS0, vS, vSn)
		self.db.mergeInternal()
		self.job = self.ws.add_job_from_string(self.compiler(self.text))
		self.job.run(databases = self.db.database)
		return GpyDB(self.job.out_db, ws = self.ws)

