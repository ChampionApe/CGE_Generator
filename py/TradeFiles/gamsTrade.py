def basicArmington(name):
	return f"""
$BLOCK B_{name}
	E_{name}_qD[t,s,n]$({name}_dExport[s,n] and txE[t])..	qD[t,s,n]		=E= sum(nn$(dom2for[n,nn]), Fscale[s,n] * (p[t,nn]/pD[t,s,n])**(sigma[s,n]));
	E_{name}_pD[t,s,n]$({name}_dExport[s,n] and txE[t])..	pD[t,s,n]		=E= p[t,n]*(1+ tauD[t,s,n]);
	E_{name}_TotalTax[t,s]$({name}_sm[s] and txE[t])..	TotalTax[t,s]	=E= tauLump[t,s]+sum(n$({name}_dExport[s,n]), tauD[t,s,n]*qD[t,s,n]);
$ENDBLOCK
"""

def wasteImports(name, m):
	return f"""
$BLOCK B_{name}
	E_{name}_qWS[t,s,m]$({m}_sm[s] and dWS[s,m] and txE[t])..	qWS[t,s,m]	=E= Fscale_WI[s,m] * sum([n,nn]$(n2m_D[n,m] and dom2for[n,nn]), (p[t,nn]/pD[t,s,n])**(sigma[s,n]));
$ENDBLOCK
"""

def initArmingtonParams(m):
	return f"""
	Fscale.l[s,n]$({m}_dExport[s,n]) = sum(t$(t0[t]), qD.l[t,s,n] * sum(nn$(dom2for[n,nn]), (pD.l[t,s,n]/p.l[t,nn])**(sigma.l[s,n])));
"""


def initArmingtonWasteParams(m):
	return f"""
	Fscale.l[s,n]$({m}_dExport[s,n]) = sum(t$(t0[t]), qD.l[t,s,n] * sum(nn$(dom2for[n,nn]), (pD.l[t,s,n]/p.l[t,nn])**(sigma.l[s,n])));
	Fscale_WI.l[s,m]$({m}_sm[s] and dWS[s,m]) = sum(t$(t0[t]), qWS.l[t,s,m] * sum([n,nn]$(n2m_D[n,m] and dom2for[n,nn]), (pD.l[t,s,n]/p.l[t,nn])**(sigma.l[s,n])));
"""
