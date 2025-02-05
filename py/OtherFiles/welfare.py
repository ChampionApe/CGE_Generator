from auxfuncs import *
from gmsPython import Group, GModel

class HouseholdWelfare(GModel):
	""" Define welfare measure as convex sum of households utility in baseline year."""
	def __init__(self, name, CGE, policy = None, active = True, **kwargs):
		super().__init__(name = name, database = CGE.db, **kwargs)
		self.CGE = CGE
		self.CGE.opt = active # If True --> use NLP solver to maximize welfare.
		self.db = self.CGE.db
		self.policy = policy 

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
		return Group(f'{self.name}_endoWhenActive', v = noneInit(self.policy, []))
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
Set {self.sn} /{', '.join(self.states)}/;
alias({self.sn}, {self.sa});

Variables
yInc[t,s,{self.sn}], HInc[t,s,{self.sn}], WInc[t,s,{self.sn}], ZInc[t,s,{self.sn}], TInc[t,s,{self.sn}], vAInc[t,s,{self.sn}], pV[t,s,{self.sn}]
EV_pV[t,s,{self.sn}], EV_vA[t,s,{self.sn}], EV_HInc[t,s,{self.sn}], EV_WInc[t,s,{self.sn}], EV_ZInc[t,s,{self.sn}], EV_TInc[t,s,{self.sn}], EV[t,s,{self.sn}];
"""

	def StaticNCES_Inc(self, m, state, GHH):
		qC = 'qC.l[t,s]' if GHH else """sum(n$({m}_C[s,n]), qD.l[t,s,n])"""
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