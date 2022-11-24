# 1: Armington demand system:
def Armington(name):
	return f"""
$BLOCK B_{name}
	E_armington_{name}[t,s,n]$(sfor_ndom_{name}[s,n] and txE[t])..	qD[t,s,n]		=E= sum(nn$(dom2for[n,nn]), Fscale[s,n] * (p[t,nn]/pD[t,s,n]))**(sigma[s,n]);
	E_pwInp_{name}[t,s,n]$(sfor_ndom_{name}[s,n] and txE[t])..		pD[t,s,n]		=E= p[t,n] + tauD[t,s,n];
	E_TaxRev_{name}[t,s]$(s_{name}[s] and txE[t])..					TotalTax[t,s]	=E= tauLump[t,s]+sum(n$(sfor_ndom_{name}[s,n]), tauD[t,s,n]*qD[t,s,n]);
$ENDBLOCK
"""