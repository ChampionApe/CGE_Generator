# Method for adding MultOut extensions to parent classes
def writeMultOutExt_i(parentClass, name):
	return MultOutExt_text.replace('class MultOut', f'class {name}({parentClass})')

ConvenienceFunctions = """
def _getExt(extension):
	if extension is None:
		return ''
	elif type(extension) is str:
		return f'_{extension}'
	else:
		return '_'+'_'.join(list(extension))

def getStaticNCES(tree, *args, extension = None, **kwargs):
	return globals()[f'StaticNCES{_getExt(extension)}'](tree, *args, **kwargs)

def getDynamicNCES(tree, *args, extension = None, **kwargs):
	return globals()[f'DynamicNCES{_getExt(extension)}'](tree, *args, **kwargs)

"""

MultOutExt_text = """
class MultOut:
	def __init__(self, *args, exoP = None, exoQS = None, **kwargs):
		self.exoP = exoP # prices that are exogenous in partial equilibrium
		self.exoQS = exoQS # supply quantities that are exogenous in partial equilibrium 
		super().__init__(*args, **kwargs)

	def calibrationSubsets(self, tree):
		self.ns.update({k: f'{self.name}_{k}' for k in ['endoMu','exoQS','exoP']})
		self.db[self.n('exoQS')] = self.exoQS 
		self.db[self.n('exoP')] = self.exoP 
		self.db[self.n('endoP')] = adj.rc_pd(self.get('endoP'), ('not', self.exoP))
		self.db[self.n('endoMu')] = self.getEndoMu(tree)

	def getEndoMu(self, tree):
		# Output part:
		mOutputs = adj.rc_pd(self.get('map'), ('and', [self.get('output'), ('not', self.get('exoQS'))])) # output part of nesting 
		mOutFromInpTree = adj.rc_pd(mOutputs, tree.mapInp) # split into outputs that come from CES/input-like trees
		mOutFromOutTree = adj.rc_pd(mOutputs, tree.mapOut) # ... and outputs that come from CET/output-like trees
		endoMu_out = mOutFromOutTree.union(pd.MultiIndex.from_frame(mOutFromInpTree.to_frame(index=False).groupby(['s','n']).first().reset_index())) # share parameters to endogenize

		# Input part:		
		mInputs = adj.rc_pd(self.get('map'), self.get('input').rename({'n':'nn'})) # input part of nesting
		mInputs = adj.rc_pd(mInputs, ('not', endoMu_out.droplevel('n').unique().rename(['s','n']))) # We cannot endogenize a share parameter that is ultimately controlled in endoMu for outputs
		mInpFromInpTree = adj.rc_pd(mInputs, tree.mapInp) # split into inputs that are nodes in CES/input-like trees
		mInpFromOutTree = adj.rc_pd(mInputs, tree.mapOut) # ... and inputs that branch directly into CET/output-like trees
		endoMu_inp = mInpFromInpTree.union(pd.MultiIndex.from_frame(mInpFromOutTree.to_frame(index=False).groupby(['s','nn']).first().reset_index()[['s','n','nn']])) # share parameters to endogenize
		return endoMu_out.union(endoMu_inp)

	@property
	def group_alwaysExo(self):
		g = super().group_alwaysExo
		g.v += [('eta', self.g('knout'))]
		if not self.partial:
			return g
		else:
			g.sub_v += [('qS', self.g('output'))]
			g.v += [('qS', ('and', [self.g('output'), self.g('exoQS')])), ('p', self.g('exoP'))]
			return g

	@property
	def group_alwaysEndo(self):
		g = super().group_alwaysEndo
		g.v += [('qS', ('and', [self.g('output'), ('not', self.g('exoQS')), self.db['tx0']]))]
		return g

	@property
	def group_exoInCalib(self):
		g = super().group_exoInCalib
		g.v += [('qS', ('and', [self.g('output'), ('not', self.g('exoQS')), self.db['t0']]))]
		return g

"""

# Update MultOutExt.py: Defines class extensions for a number of parent classes
multOutExt_parents = {k: f'{k}_multOut' for k in ('StaticNCES','StaticNCES_emission', 'StaticNCES_emission','DynamicNCES','DynamicNCES_emission','DynamicNCES_emission')}
multOutExt_base = """from ProductionFiles.dynamicNCES import *"""
MultOutExt = f"""
{multOutExt_base}
{''.join([writeMultOutExt_i(k,v) for k,v in multOutExt_parents.items()])}

{ConvenienceFunctions}
"""

writeMain = {'multOutExt': {'text': MultOutExt, 'classes': list(multOutExt_parents.keys())+list(multOutExt_parents.values())+['getStaticNCES','getDynamicNCES']}}