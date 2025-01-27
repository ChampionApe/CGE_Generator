from auxfuncs import *
from gmsPython import Group, GModel, gmsWrite
from pyDatabases import cartesianProductIndex as cpi

class IndexFund(GModel):
	def __init__(self, name, database, sIdxFund, initFromGms = None, **kwargs):
		super().__init__(name = name, database = database, **kwargs)
		self.ns['sIdxFund'] = sIdxFund # the subset of sectors that are included in the "index fund"

	def initStuff(self, gdx = True):
		self.initData()
		self.initGroups()
		if gdx:
			self.db.mergeInternal()

	def initData(self):
		self.db.aom(pd.Series(0, index = self.db('t')), name = 'vIdxFund', priority='first')
		self.db.aom(pd.Series(1, index = cpi([self.db('t'), self.get('sIdxFund')])), name = 'uPortfolio', priority='first')

	@property
	def group_endo(self):
		return Group(f'{self.name}_endo', v = ['vIdxFund'])
	@property
	def group_exo(self):
		return Group(f'{self.name}_exo', v = [('uPortFolio', self.g('sIdxFund'))])
	def modelName(self, state = 'B'):
		return '_'.join(['M',self.name,'B'])
	@property
	def model_B(self):
		return OrdSet([f"B_{self.name}"])
	@property
	def textBlocks(self):
		return {'idxFund': self.equationText}
	@property
	def textInit(self):
		return "" if self.initFromGms is None else f"""vIdxFund.l[t] = sum(s$({gmsWrite.Syms.gpy(self.g('sIdxFund'))}), uPortfolio.l[t,s] * vA.l[t,s]);"""
	def fixText(self, **kwargs):
		return self.groups[f'{self.name}_exo'].fix(db = self.db)
	def unfixText(self, **kwargs):
		return self.groups[f'{self.name}_endo'].unfix(db = self.db)

	@property
	def equationText(self):
		return f"""
$BLOCK B_{self.name}
	E_{self.name}[t]$(txE[t])..	vIdxFund[t] =E= sum(s$({gmsWrite.Syms.gpy(self.g('sIdxFund'))}), uPortfolio[t,s]*vA[t,s]);
$ENDBLOCK
"""


