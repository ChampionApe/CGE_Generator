from auxfuncs import *
from pyDatabases.gpyDB import MergeDbs
from gmsPython import Group, GModel
import mEmissions, mGovernment, mHousehold, mOther, mProduction, mTrade

class Base(GModel):
	def __init__(self, name = None, database = None, **kwargs):
		super().__init__(name = name, database = database, **kwargs)

	@property
	def groups(self):
		return {k:v for d in [m.groups for m in self.m.values()] for k,v in d.items()}

	### WRITING METHODS:
	def fixText(self, state = 'B'):
		return '\n'.join([m.fixText(state=state) for m in self.m.values()])
	def unfixText(self, state = 'B'):
		return '\n'.join([m.unfixText(state=state) for m in self.m.values()])

	@property
	def model_B(self):
		return OrdSet.union(*[m.getModel(state='B') for m in self.m.values()])
	@property
	def model_C(self):
		return OrdSet.union(*[m.getModel(state='C') for m in self.m.values()])
	@property
	def writeBlocks(self):
		return '\n'.join([''.join(m.textBlocks.values()) for m in self.m.values()])
	@property
	def writeInit(self):
		return '\n'.join([m.writeInit for m in self.m.values() if hasattr(m, 'writeInit')])
	@property
	def writeFuncs(self):
		return '\n'.join([m.writeFuncs for m in self.m.values() if hasattr(m, 'writeFuncs')])


class CGE_base(Base):
	# Standard load procedures for main modules:
	def addFromNest(self, module, cl, tree, *args, **kwargs):
		self.addModule(getattr(module, cl)(tree, *args, **kwargs))
		m = self.m[tree.name]
		MergeDbs.merge(self.db, tree.db)
		m.db = self.db 
		m.initStuff(db = None, gdx = False)
		return m

	def addProduction(self, cl, tree, *args, **kwargs):
		return self.addFromNest(mProduction, cl, tree, *args, **kwargs)

	def addHousehold(self, cl, tree, *args, **kwargs):
		return self.addFromNest(mHousehold, cl, tree, *args, **kwargs)

	def addGovernment(self, cl, tree, *args, **kwargs):
		return self.addFromNest(mGovernment, cl, tree, *args, **kwargs)

	def addTrade(self, cl, name, *args, **kwargs):
		self.addModule(getattr(mTrade, cl)(name, self.db, *args, **kwargs))
		self.m[name].initStuff(db = None, gdx = False)
		return self.m[name]

	def addEquilibriumModule(self, cl, name, *args, **kwargs):
		self.addModule(getattr(mOther, cl)(name, self.db, *args, **kwargs))
		self.m[name].initStuff(gdx = False)
		return self.m[name]

