
def basicArmington(name):
	return f"""
$BLOCK B_{name}
	E_{name}_qD[t,s,n]$({name}_dExport[s,n] and txE[t])..	qD[t,s,n]		=E= sum(nn$(dom2for[n,nn]), Fscale[s,n] * (p[t,nn]/pD[t,s,n])**(sigma[s,n]));
	E_{name}_pD[t,s,n]$({name}_dExport[s,n] and txE[t])..	pD[t,s,n]		=E= p[t,n]*(1+ tauD[t,s,n]);
	E_{name}_TotalTax[t,s]$({name}_sm[s] and txE[t])..	TotalTax[t,s]	=E= tauLump[t,s]+sum(n$({name}_dExport[s,n]), tauD[t,s,n]*qD[t,s,n]);
$ENDBLOCK
"""
