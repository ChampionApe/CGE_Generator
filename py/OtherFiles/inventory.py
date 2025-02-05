from auxfuncs import *
from gmsPython import Group, GModel

class InventoryAR(GModel):
	def __init__(self, name, database, sInventory, **kwargs):
		super().__init__(name = name, database = database, **kwargs)
		self.ns['sInventory'] = sInventory # Subset of inventory sectors (should just be one specific sector)

	# initialize
	def initStuff(self, gdx = True):
		self.initData()
		self.initGroups()
		if gdx:
			self.db.mergeInternal()

	def initData(self):
		self.db.aom(adj.rc_pd(self.db('qD'), self.get('sInventory')).index.droplevel('t').unique(), name = 'dInventory')
		self.db.aom(pd.Series(.05, index = self.get('dInventory')), name = 'inventoryAR', type = 'par')

	@property
	def group_endo(self):
		return Group(f'{self.name}_endo', v = [('qD', ('and', [self.g('dInventory'), self.g('tx0E')]))])
	@property
	def group_exo(self):
		return Group(f'{self.name}_exo',  v = [('qD', ('and', [self.g('dInventory'), self.g('t0')]))])

	def modelName(self, state = 'B'):
		return '_'.join(['M',self.name,'B'])
	@property
	def model_B(self):
		return OrdSet([f"B_{self.name}"])
	@property
	def textBlocks(self):
		return {'invtory': self.equationText}

	def fixText(self, **kwargs):
		return self.groups[f'{self.name}_exo'].fix(db = self.db)
	def unfixText(self, **kwargs):
		return self.groups[f'{self.name}_endo'].unfix(db = self.db)

	@property
	def equationText(self):
		return f"""
$BLOCK B_{self.name}
	E_{self.name}[t,s,n]$(dInventory[s,n] and tx0E[t])..	qD[t,s,n] =E= inventoryAR[s,n] * qD[t-1,s,n]/(1+g_LR);
$ENDBLOCK
"""