def writeIdxFundExt_i(parentClass, name):
	return idxFundExt_text.replace('class IdxFund', f'class {name}({parentClass})')

idxFundExt_text = """
class IdxFund:
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def initData(self):
		super().initData()
		self.db.aom(pd.Series(1, index = self.get('t')), name ='vIdxFund', priority='first')
		self.db.aom(pd.Series(.1, index = self.get('sm')), name = 'uIdxFund', priority = 'first')
		self.db.aom(pd.Series(0, index = self.get('sm')), name = 'vA_F', priority='first')

	# Specify new blocks of equations (the self.nestingBlocks are the same)
	@property
	def model_B(self):
		return super().model_B+OrdSet([f"B_{self.name}_idxFund"])
	@property
	def model_C(self):
		return super().model_C+OrdSet([f"B_{self.name}_idxFund"])
	@property
	def textBlocks(self):
		return super().textBlocks | {'idxFund': self.idxFundBlocks}
	@property
	def idxFundBlocks(self):
		return gamsHouseholds.idxFund(f'{self.name}_idxFund', self.name)

	# Specify new groups of variables
	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.v += [('vA_F', self.g('sm')), ('uIdxFund', self.g('sm'))]
		g.sub_v += [('vA', ('and', [self.g('sm'), self.g('t0')]))]
		if self.partial:
			g.v += [('vIdxFund', self.g('t0'))]
		return g

	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		g.v += [('vA', ('and', [self.g('sm'), self.g('t0')]))]
		return g

"""

# Update idxFundExt.py: Defines class extensions for a number of parent classes
idxFundExt_parents = {k: f'{k}IdxFund' for k in ('StaticNCES','StaticGHH','Ramsey','RamseyGHH')}
idxFundExt_base = """from HouseholdFiles.ramsey import *"""
IdxFundExt = f"""
{idxFundExt_base}
{''.join([writeIdxFundExt_i(k,v) for k,v in idxFundExt_parents.items()])}
"""


writeMain = {'idxFundExt': {'text': IdxFundExt, 'classes': idxFundExt_parents.values()}}
