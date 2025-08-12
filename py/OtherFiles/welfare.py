from auxfuncs import *
from gmsPython import Group, GModel
from gmsPython.gmsWrite import Syms

class HWPolicyRules(GModel):
	""" HouseholWelfare with some standard structures on policy. Currently two types of policy rules: Proportional and trends."""
	def __init__(self, name, CGE, active = True, **kwargs):
		super().__init__(name = name, database = CGE.db, **kwargs)
		self.CGE = CGE
		self.CGE.opt = active # If True --> use NLP solver to maximize welfare.
		self.db = self.CGE.db
		self.policy = {}
		self.instr = {}

	def initStuff(self, gdx = True):
		self.initData()
		self.initGroups()
		if gdx:
			self.db.mergeInternal()

	def initData(self):
		self.db.aom(0, name = 'Welfare', priority='first') # welfare objective
		self.db.aom(pd.Series(1, index = self.db('s_HH')), name = 'welWeights', priority='first')

	@property
	def equationText(self):
		return self.equationWelfare+self.equationPolicyRules

	@property
	def equationWelfare(self):
		return f"""
$BLOCK B_{self.name}
	E_{self.name}_obj..	Welfare =E= sum([t,s]$(t0[t] and s_HH[s]), welWeights[s]*vU[t,s]);
$ENDBLOCK
"""

	@property
	def equationPolicyRules(self):
		eqText = "\n\t".join([polDict['text'] for polDict in self.policy.values()])
		if eqText:
			return f"""
$BLOCK B_{self.name}_PolicyRules
	{eqText}
$ENDBLOCK
"""
		else:
			return f""

	@property
	def model_B(self):
		if self.policy and (self.CGE.opt):
			return OrdSet([f"B_{self.name}", f"B_{self.name}_PolicyRules"])
		else:
			return OrdSet([f"B_{self.name}"])
	@property
	def textBlocks(self):
		return {'main': self.equationText}

	@property
	def group_alwaysEndo(self):
		return Group(f'{self.name}_endo', v = ['Welfare'])
	@property
	def group_endoWhenActive(self):
		return Group(f'{self.name}_endoWhenActive', v = [(d['name'], d['cond']) for d in self.policy.values()]+[(d['name'], d['cond']) for d in self.instr.values()])
	@property
	def group_exo(self):
		return Group(f'{self.name}_exo',  v = [('welWeights', self.g('s_HH'))])
	def modelName(self, state = 'B'):
		return '_'.join(['M',self.name])


	def fixText(self, **kwargs):
		text = self.groups[f'{self.name}_exo'].fix(db = self.db)
		return text if self.CGE.opt else text+self.groups[f'{self.name}_endoWhenActive'].fix(db=self.db)
	def unfixText(self, **kwargs):
		text = self.groups[f'{self.name}_endo'].unfix(db = self.db)
		return text if not self.CGE.opt else text+self.groups[f'{self.name}_endoWhenActive'].unfix(db=self.db)

	def addRule_free(self, eqId, pol, cond = None, **kwargs):
		self.policy[eqId] = {'name': pol, 'cond': cond, 'type': 'free', 'text': ""}

	def addRule_addProp(self, eqId, pol, cond = None, instrDomains = None, **kwargs):
		self.policy[eqId] = {'name': pol, 'cond': cond, 'instr': [None]*len(instrDomains), 'type': 'addProp'}
		fInstrName = lambda instrDom: f"""{eqId}_flat""" if instrDom is None else f"""{eqId}_{''.join(instrDom)}"""
		for i in range(len(instrDomains)):
			instrId = fInstrName(instrDomains[i])
			self.addInstrFromDomains(instrId, pol, instrDomains[i], cond = cond)
			self.initLoadFactors(instrId, pol, instrDomains[i], cond = cond)
			self.policy[eqId]['instr'][i] = instrId
		self.policy[eqId]['text'] = self.eq_addProp(eqId)

	def addRule_AR1(self, eqId, pol, cond = None, **kwargs):
		self.policy[eqId] = {'name': pol, 'cond': cond, 'type': 'AR1'}
		self.initLoadFactors(eqId, pol, None, cond = cond)
		self.policy[eqId]['text'] = self.eq_AR1(eqId)

	def addInstrFromDomains(self, instrId, pol, domains, cond = None):
		self.instr[instrId] = {'name': instrId}
		dummy = self.instrIdxFromDomains(pol, domains, cond = cond) # dummy 
		if dummy is None:
			self.instr[instrId]['cond'] = None # if None --> the instrument is a scalar, no condition 
			self.db.aom(adj.rc_pd(self.get(pol), cond).mean(), name = instrId, priority = 'first') # If None --> initialize instrument value as mean over relevant policy
		else:
			self.db[f'd{instrId}'] = dummy # relevant domain for instrument
			self.instr[instrId]['cond'] = self.g(f'd{instrId}') # add as condition
			self.db.aom(adj.rc_pd(self.get(pol), cond).groupby(domains).mean(), name = instrId, priority = 'first')

	def initLoadFactors(self, instrId, pol, domains, cond = None):
		idx = adj.rc_pd(self.get(pol), cond).index # full index
		if domains is None:
			self.db.aom(pyDatabases.gpy(pd.Series(1, index = idx, name = f'LF{instrId}'), type = 'par'), priority='first')
		elif set(idx.names)-set(domains):
			self.db.aom(pyDatabases.gpy(pd.Series(1, index = idx.droplevel(domains).unique(), name = f'LF{instrId}'), type = 'par'), priority='first')
		else:
			self.db.aom(pyDatabases.gpy(1, name = f'LF{instrId}', type = 'par'), priority='first')

	def instrIdxFromDomains(self, pol, domains, cond = None):
		""" If domains is None --> instrument is a scalar policy """
		if domains is None:
			return None
		else:
			idx = adj.rc_pd(self.get(pol), cond).index
			return idx.droplevel([n for n in idx.names if n not in domains]).unique()

	def eq_addProp(self, eqId):
		polGpy, cond = self.g(self.policy[eqId]['name']), self.policy[eqId]['cond']
		iteInstr = self.policy[eqId]['instr'] # list of instrument ids 
		instrText = '+'.join([Syms.gpy(self.g(instr))+"*"+Syms.gpy(self.g(f'LF{instr}')) for instr in iteInstr])
		return f"""E_{self.name}_{eqId}{Syms.gpyDomains(polGpy)}{Syms.gpyCondition(cond)}..	{Syms.gpy(polGpy)} =E= {instrText};"""

	def eq_AR1(self, eqId):
		polGpy, cond = self.g(self.policy[eqId]['name']), self.policy[eqId]['cond']
		return f"""E_{self.name}_{eqId}{Syms.gpyDomains(polGpy)}{Syms.gpyCondition(cond)}.. {Syms.gpy(polGpy)} =E= {Syms.gpy(self.g(f'LF{eqId}'))}*{Syms.gpy(polGpy, lag = {'t':-1})};""" 

#### OLD version - kept to keep relevant notebooks intact
class HouseholdWelfare(GModel):
	""" Define welfare measure as convex sum of households utility in baseline year."""
	def __init__(self, name, CGE, policy = None, active = True, **kwargs):
		super().__init__(name = name, database = CGE.db, **kwargs)
		self.CGE = CGE
		self.CGE.opt = active # If True --> use NLP solver to maximize welfare.
		self.db = self.CGE.db
		self.policy = noneInit(policy, [])

	def initStuff(self, gdx = True):
		self.initData()
		self.initGroups()
		if gdx:
			self.db.mergeInternal()

	def initData(self):
		self.db.aom(0, name = 'Welfare', priority='first') # welfare objective
		self.db.aom(pd.Series(1, index = self.db('s_HH')), name = 'welWeights', priority='first')

	@property
	def equationText(self):
		return f"""
$BLOCK B_{self.name}
	E_{self.name}_obj..	Welfare =E= sum([t,s]$(t0[t] and s_HH[s]), welWeights[s]*vU[t,s]);
$ENDBLOCK
"""

	@property
	def group_alwaysEndo(self):
		return Group(f'{self.name}_endo', v = ['Welfare'])
	@property
	def group_endoWhenActive(self):
		return Group(f'{self.name}_endoWhenActive', v = self.policy.copy())
	@property
	def group_exo(self):
		return Group(f'{self.name}_exo',  v = [('welWeights', self.g('s_HH'))])
	def modelName(self, state = 'B'):
		return '_'.join(['M',self.name])
	@property
	def model_B(self):
		return OrdSet([f"B_{self.name}"])
	@property
	def textBlocks(self):
		return {'obj': self.equationText}
	def fixText(self, **kwargs):
		text = self.groups[f'{self.name}_exo'].fix(db = self.db)
		return text if self.CGE.opt else text+self.groups[f'{self.name}_endoWhenActive'].fix(db=self.db)
	def unfixText(self, **kwargs):
		text = self.groups[f'{self.name}_endo'].unfix(db = self.db)
		return text if not self.CGE.opt else text+self.groups[f'{self.name}_endoWhenActive'].unfix(db=self.db)


class HW_propPolicy(HouseholdWelfare):
	def __init__(self, *args, policy = None, sumOuts = None, **kwargs):
		super().__init__(*args, **kwargs)
		self.resetPolicies(policy = policy, sumOuts = sumOuts)

	def resetPolicies(self, policy = None, sumOuts = None):
		""" Add policies as list of tuples (as it would be added to the group definition)"""
		self.policy, self.policy0, self.sumOuts = [], [], []
		if policy:
			sumOuts = noneInit(sumOuts, [None]*len(policy))
			[self.addPolIte(policy[i][0], condition = policy[i][1], sumOut = sumOuts[i]) for i in range(len(policy))];

	def addPolIte(self, pol, ite = None, condition = None, sumOut = None):
		""" If ite = None, add new condition. If sumOut = None, set policy0[ite] to None (don't use) """
		if ite is None:
			self.policy.insert(len(self.policy), (pol, condition))
			self.policy0.insert(len(self.policy0), self.addPol0Ite(pol, ite = len(self.policy0), condition = condition, sumOut = sumOut))
		else:
			self.policy[ite] = (pol, condition)
			self.policy0[ite] = self.addPol0Ite(pol, ite = ite, condition = condition, sumOut = sumOut)

	def addPol0Ite(self, pol, ite = None, condition = None, sumOut = None):
		if (pyDatabases.getIndex(self.g(pol)) is None) or (sumOut is None):
			return None
		else:
			subset = self.pol0subset(pol, condition = condition, sumOut = sumOut)
			if subset is None:
				self.db.aom(adj.rc_pd(self.get(pol), condition).mean(), name = f'{pol}_{ite}', priority = 'first')
				return (f'{pol}_{ite}', None)
			else:
				self.db[f'd{pol}_{ite}'] = subset # add relevant subset to database
				self.db.aom(adj.rc_pd(self.get(pol), condition).groupby(subset.names).mean(), name = f'{pol}_{ite}', priority='first')
				return (f'{pol}_{ite}', self.g(f'd{pol}_{ite}'))

	def pol0subset(self, pol, condition = None, sumOut = None):
		idx = adj.rc_pd(self.get(pol), condition).index
		if sumOut is None:
			return idx
		else:
			if set(idx.names)-set(sumOut):
				return idx.droplevel(sumOut).unique()
			else:
				return None

	@property
	def model_B(self):
		if (any(self.policy0)) and (self.CGE.opt):
			return OrdSet([f"B_{self.name}", f"B_{self.name}_propPolicy"])
		else:
			return OrdSet([f"B_{self.name}"])

	def addPolEq(self, i):
		if self.policy0[i] is None:
			return ""
		else:
			pol, cond = self.g(self.policy[i][0]), self.policy[i][1]
			pol0 = self.g(self.policy0[i][0])
			return f"""E_{self.name}_{i}{Syms.gpyDomains(pol)}{Syms.gpyCondition(cond)}..	{Syms.gpy(pol0)} =E= {Syms.gpy(pol)};"""

	@property
	def addPolEqs(self):
		eqText = "\n\t".join([self.addPolEq(i) for i in range(len(self.policy))])
		if eqText:
			return f"""
$BLOCK B_{self.name}_propPolicy
	{eqText}
$ENDBLOCK
"""
		else:
			return f""

	@property
	def equationText(self):
		return f"""
{super().equationText}
{self.addPolEqs}
"""

	@property
	def group_endoWhenActive(self):
		g = super().group_endoWhenActive
		g.v += [tup for tup in self.policy0 if tup is not None];
		return g


class ReportEV:
	""" Reporting module - does not require model structure"""
	def __init__(self, model, states, base, sn = 'state', sa = 'stateAls'):
		self.model = model # CGE model with households
		self.db = model.db 
		self.sn = sn
		self.sa = sa
		self.states = states # list
		self.base = base # string
		self.declared = False
		self.init = False

	@property
	def declSclr(self):
		if self.declared:
			return ""
		else:
			self.declared = True
			return f"""Scalar tempSclr;"""
	@property
	def writeInit(self):
		if self.init:
			return ""
		else:
			self.init = True
			return self.initText

	def Ramsey(self, m, state, GHH):
		return self.writeInit + self.Ramsey_EV(m, state, GHH)
	def StaticNCES(self, m, state, GHH):
		return self.writeInit + self.StaticNCES_EV(m, state, GHH)

	@property
	def initText(self):
		return f"""
$onMultiR
Set {self.sn} /{', '.join(self.states)}/;
alias({self.sn}, {self.sa});

Variables
yInc[t,s,{self.sn}], HInc[t,s,{self.sn}], WInc[t,s,{self.sn}], ZInc[t,s,{self.sn}], TInc[t,s,{self.sn}], vAInc[t,s,{self.sn}], pV[t,s,{self.sn}]
EV_pV[t,s,{self.sn}], EV_vA[t,s,{self.sn}], EV_HInc[t,s,{self.sn}], EV_WInc[t,s,{self.sn}], EV_ZInc[t,s,{self.sn}], EV_TInc[t,s,{self.sn}], EV[t,s,{self.sn}];
"""

	def StaticNCES_Inc(self, m, state, GHH):
		qC = 'qC.l[t,s]' if GHH else f"""sum(n$({m}_C[s,n]), qD.l[t,s,n])"""
		text = f"""
yInc.l[t,s,{self.sn}]$({m}_sm[s] and txE[t] and sameAs({self.sn}, '{state}')) = vA.l[t+1,s]*(1+g_LR)-vA.l[t,s]*Rrate.l[t]+{qC};
HInc.l[t,s,{self.sn}]$({m}_sm[s] and tE[t] and sameAs({self.sn}, '{state}'))  = yInc.l[t-1,s,{self.sn}]/(1-(1+g_LR)/R_LR);
WInc.l[t,s,{self.sn}]$({m}_sm[s] and tE[t] and sameAs({self.sn}, '{state}'))  = sum(n$({m}_L[s,n]), pS.l[t-1,s,n]*qS.l[t-1,s,n])/(1-(1+g_LR)/R_LR);
TInc.l[t,s,{self.sn}]$({m}_sm[s] and tE[t] and sameAs({self.sn}, '{state}'))  = tauLump.l[t-1,s]/(1-(1+g_LR)/R_LR);
vAInc.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = vA.l[t,s];
pV.l[t,s,{self.sn}]$({m}_sm[s] and txE[t] and sameAs({self.sn}, '{state}')) = sum(n$({m}_C[s,n]), pD.l[t,s,n]);
pV.l[t,s,{self.sn}]$({m}_sm[s] and tE[t] and sameAs({self.sn}, '{state}')) = sum(n$({m}_C[s,n]), pD.l[t-1,s,n]);

{self.declSclr}

tempSclr = card(t)-1;
While(tempSclr >= 1,
	Hinc.l[t,s,{self.sn}]$({m}_sm[s] and (ord(t) = tempSclr) and sameAs({self.sn}, '{state}')) = HInc.l[t+1,s,{self.sn}]*(1+g_LR)/Rrate.l[t]+yInc.l[t,s,{self.sn}];
	WInc.l[t,s,{self.sn}]$({m}_sm[s] and (ord(t) = tempSclr) and sameAs({self.sn}, '{state}')) = WInc.l[t+1,s,{self.sn}]*(1+g_LR)/Rrate.l[t]+sum(n$({m}_L[s,n]), pS.l[t,s,n]*qS.l[t,s,n]);
	TInc.l[t,s,{self.sn}]$({m}_sm[s] and (ord(t) = tempSclr) and sameAs({self.sn}, '{state}')) = TInc.l[t+1,s,{self.sn}]*(1+g_LR)/Rrate.l[t]+tauLump.l[t,s];
	tempSclr = tempSclr-1;
);
"""
		if GHH:
			text += f"""ZInc.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = frisch.l[s]*WInc.l[t,s,{self.sn}]/(1+frisch.l[s]);"""
		return text

	def Ramsey_Inc(self, m, state, GHH):
		text = self.StaticNCES_Inc(m, state, GHH)
		return text+f"""
pV.l[t,s,{self.sn}]$({m}_sm[s] and tE[t] and sameAs({self.sn}, '{state}')) = pV.l[t,s,{self.sn}]/( (1-discF.l[s]**(1/crra.l[s])/(R_LR**((crra.l[s]-1)/crra.l[s])))**(crra.l[s]/(crra.l[s]-1)) );

tempSclr = card(t)-1;
While(tempSclr >= 1,
	pV.l[t,s,{self.sn}]$({m}_sm[s] and (ord(t) = tempSclr) and sameAs({self.sn}, '{state}')) = (pV.l[t,s,{self.sn}]**((crra.l[s]-1)/crra.l[s])+discF.l[s]**(1/crra.l[s])*(pV.l[t+1,s,{self.sn}]/Rrate.l[t])**((crra.l[s]-1)/crra.l[s]))**(crra.l[s]/(crra.l[s]-1));
	tempSclr = tempSclr-1;
);
"""

	def StaticNCES_EV(self, m, state, GHH):
		relPrices = f"""((sum({self.sa}$(sameAs({self.sa}, '{self.base}')), pV.l[t,s,{self.sa}])-pV.l[t,s,{self.sn}])/pV.l[t,s,{self.sn}])"""
		text = f"""
{self.StaticNCES_Inc(m,state,GHH)}

EV_pV.l[t,s,{self.sn}]$({m}_sm[s] and tE[t] and sameAs({self.sn}, '{state}')) = {relPrices}*yInc.l[t-1,s,{self.sn}]/(1-(1+g_LR)/R_LR);

tempSclr = card(t)-1;
While(tempSclr >= 1,
	EV_pV.l[t,s,{self.sn}]$({m}_sm[s] and (ord(t) = tempSclr) and sameAs({self.sn}, '{state}')) = EV_pV.l[t+1,s,{self.sn}]*(1+g_LR)/Rrate.l[t]+{relPrices}*yInc.l[t,s,{self.sn}];
	tempSclr = tempSclr-1;
);

EV_vA.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = vAInc.l[t,s,{self.sn}]-sum({self.sa}$(sameAs({self.sa}, '{self.base}')), vAInc.l[t,s,{self.sa}]);
EV_HInc.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = HInc.l[t,s,{self.sn}]-sum({self.sa}$(sameAs({self.sa}, '{self.base}')), HInc.l[t,s,{self.sa}]);
EV_WInc.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = WInc.l[t,s,{self.sn}]-sum({self.sa}$(sameAs({self.sa}, '{self.base}')), WInc.l[t,s,{self.sa}]);
EV_TInc.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = -TInc.l[t,s,{self.sn}]+sum({self.sa}$(sameAs({self.sa}, '{self.base}')), TInc.l[t,s,{self.sa}]);
EV.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = EV_pV.l[t,s,{self.sn}]+EV_vA.l[t,s,{self.sn}]+EV_HInc.l[t,s,{self.sn}];
"""
		if GHH:
			text += f"""EV_ZInc.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = sum({self.sa}$(sameAs({self.sa}, '{self.base}')), ZInc.l[t,s,{self.sa}])-ZInc.l[t,s,{self.sn}];"""
		return text

	def Ramsey_EV(self, m, state, GHH):
		text = f"""
{self.Ramsey_Inc(m,state,GHH)}

EV_pV.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = (sum({self.sa}$(sameAs({self.sa}, '{self.base}')), pV.l[t,s,{self.sa}])-pV.l[t,s,{self.sn}])*(vAInc.l[t,s,{self.sn}]+HInc.l[t,s,{self.sn}])/pV.l[t,s,{self.sn}];	
EV_vA.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = vAInc.l[t,s,{self.sn}]-sum({self.sa}$(sameAs({self.sa}, '{self.base}')), vAInc.l[t,s,{self.sa}]);
EV_HInc.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = HInc.l[t,s,{self.sn}]-sum({self.sa}$(sameAs({self.sa}, '{self.base}')), HInc.l[t,s,{self.sa}]);
EV_WInc.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = WInc.l[t,s,{self.sn}]-sum({self.sa}$(sameAs({self.sa}, '{self.base}')), WInc.l[t,s,{self.sa}]);
EV_TInc.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = sum({self.sa}$(sameAs({self.sa}, '{self.base}')), TInc.l[t,s,{self.sa}])-TInc.l[t,s,{self.sn}];
EV.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = EV_pV.l[t,s,{self.sn}]+EV_vA.l[t,s,{self.sn}]+EV_HInc.l[t,s,{self.sn}];
"""
		if GHH:
			text += f"""EV_ZInc.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = sum({self.sa}$(sameAs({self.sa}, '{self.base}')), ZInc.l[t,s,{self.sa}])-ZInc.l[t,s,{self.sn}];"""
		return text


class ReportCV(ReportEV):
	def Ramsey(self, m, state, GHH):
		return self.writeInit + self.Ramsey_CV(m, state, GHH)
	def StaticNCES(self, m, state, GHH):
		return self.writeInit + self.StaticNCES_CV(m, state, GHH)

	@property
	def initText(self):
		return f"""
$onMultiR
Set {self.sn} /{', '.join(self.states)}/;
alias({self.sn}, {self.sa});

Variables
yInc[t,s,{self.sn}], HInc[t,s,{self.sn}], WInc[t,s,{self.sn}], ZInc[t,s,{self.sn}], TInc[t,s,{self.sn}], vAInc[t,s,{self.sn}], pV[t,s,{self.sn}]
CV_pV[t,s,{self.sn}], CV_vA[t,s,{self.sn}], CV_HInc[t,s,{self.sn}], CV[t,s,{self.sn}];
"""


	def StaticNCES_CV(self, m, state, GHH):
		relPrices = f"""(pV.l[t,s,{self.sn}]/pV.l[t,s,{self.sa}]-1)"""
		text = f"""
{self.StaticNCES_Inc(m,state,GHH)}

CV_pV.l[t,s,{self.sn}]$({m}_sm[s] and tE[t] and sameAs({self.sn}, '{state}')) = sum({self.sa}$(sameAs({self.sa}, '{self.base}')), {relPrices}*yInc.l[t-1,s,{self.sa}])/(1-(1+g_LR)/R_LR);

tempSclr = card(t)-1;
While(tempSclr >= 1,
	CV_pV.l[t,s,{self.sn}]$({m}_sm[s] and (ord(t) = tempSclr) and sameAs({self.sn}, '{state}')) = CV_pV.l[t+1,s,{self.sn}]*(1+g_LR)/Rrate.l[t]+sum({self.sa}$(sameAs({self.sa}, '{self.base}')), {relPrices}*yInc.l[t,s,{self.sa}]);
	tempSclr = tempSclr-1;
);

CV_vA.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = sum({self.sa}$(sameAs({self.sa}, '{self.base}')), vAInc.l[t,s,{self.sa}]-vAInc.l[t,s,{self.sn}]);
CV_HInc.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = sum({self.sa}$(sameAs({self.sa}, '{self.base}')), HInc.l[t,s,{self.sa}]-HInc.l[t,s,{self.sn}]);
CV.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = CV_pV.l[t,s,{self.sn}]+CV_vA.l[t,s,{self.sn}]+CV_HInc.l[t,s,{self.sn}];
"""
		return text

	def Ramsey_CV(self, m, state, GHH):
		text = f"""
{self.Ramsey_Inc(m,state,GHH)}

CV_pV.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = sum({self.sa}$(sameAs({self.sa}, '{self.base}')), (pV.l[t,s,{self.sn}]/pV.l[t,s,{self.sa}]-1) * (vAInc.l[t,s,{self.sa}]+HInc.l[t,s,{self.sa}]));
CV_vA.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = sum({self.sa}$(sameAs({self.sa}, '{self.base}')), vAInc.l[t,s,{self.sa}]-vAInc.l[t,s,{self.sn}]);
CV_HInc.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = sum({self.sa}$(sameAs({self.sa}, '{self.base}')), HInc.l[t,s,{self.sa}]-HInc.l[t,s,{self.sn}]);
CV.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = CV_pV.l[t,s,{self.sn}]+CV_vA.l[t,s,{self.sn}]+CV_HInc.l[t,s,{self.sn}];
"""
		return text


class ReportCVcostMin(ReportCV):

	def Ramsey(self, m, state, GHH):
		return self.writeInit + self.getCV(m, state, GHH)
	def StaticNCES(self, m, state, GHH):
		return self.writeInit + self.getCV(m, state, GHH)

	@property
	def initText(self):
		return f"""
$onMultiR
Set {self.sn} /{', '.join(self.states)}/;
alias({self.sn}, {self.sa});

Variables
yInc[t,s,{self.sn}], HInc[t,s,{self.sn}], WInc[t,s,{self.sn}], ZInc[t,s,{self.sn}], TInc[t,s,{self.sn}], vAInc[t,s,{self.sn}], pV[t,s,{self.sn}],
CV[t,s,{self.sn}], CV_shadowVal[s,{self.sn}], CV_vU[s,{self.sn}], CV_Delta[t,s,{self.sn}];
"""

	def getCV(self, m, state, GHH):
		qC = 'qC.l[t,s]' if GHH else f"""sum(n$({m}_C[s,n]), qD.l[t,s,n])"""
		qC_ = 'qC.l[t-1,s]' if GHH else f"""sum(n$({m}_C[s,n]), qD.l[t-1,s,n])"""
		pC = f"sum(n$({m}_C[s,n]), pD.l[t,s,n])"
		pC_ = f"sum(n$({m}_C[s,n]), pD.l[t-1,s,n])"
		text = f"""
{self.Ramsey_Inc(m,state,GHH)}

# Store lifetime utility across states to access and compare
CV_vU.l[s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = sum(t$(t0[t]), vU.l[t,s]);

# Compute lambda the shadow value on the constraint that lifetime utility equals baseline levels
CV_shadowVal.l[s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}')) = sum({self.sa}$(sameAs({self.sa}, '{self.base}')), ((1-crra.l[s])*CV_vU.l[s,{self.sa}])**(crra.l[s]/(1-crra.l[s])) * sum(t$(t0[t]), pV.l[t,s,{self.sn}]));

# Compute Delta:
CV_Delta.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}') and txE[t]) = (CV_shadowVal.l[s,{self.sn}]/{pC})**(1/crra.l[s])-{qC};
CV_Delta.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}') and tE[t]) = CV_Delta.l[t-1,s,{self.sn}];

# Compute CV recursively:
CV.l[t,s,{self.sn}]$({m}_sm[s] and sameAs({self.sn}, '{state}') and tE[t]) = {pC_}*CV_Delta.l[t,s,{self.sn}]/(1-(1+g_LR)/R_LR);

tempSclr = card(t)-1;
While(tempSclr >= 1,
	CV.l[t,s,{self.sn}]$({m}_sm[s] and (ord(t) = tempSclr) and sameAs({self.sn}, '{state}')) = 	CV.l[t+1,s,{self.sn}] * (1+g_LR)/Rrate.l[t]+{pC}*CV_Delta.l[t,s,{self.sn}];
	tempSclr = tempSclr-1;
);
"""
		return text
