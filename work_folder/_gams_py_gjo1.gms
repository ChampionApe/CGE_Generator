sets
	l1
;


sets
	tauS_shock_ss[t,s,n]
;

$GDXIN %grids%
$onMulti
$load l1
$load tauS_shock_ss
$GDXIN
$offMulti;

parameters
	tauS_shock[l1,t,s,n]
	sol_qS_shock[l1,t,s,n]
	sol_qD_shock[l1,t,s,n]
	sol_pD_shock[l1,t,s,n]
	sol_p_shock[l1,t,n]
;

$GDXIN %grids%
$onMulti
$load tauS_shock
$GDXIN
$offMulti;

loop(l1,
	tauS.fx[t,s,n]$(tauS_shock_ss[t,s,n]) = tauS_shock[l1,t,s,n];
	solve m_GE_2018_B using CNS;
	sol_qS_shock[l1,t,s,n] = qS.l[t,s,n];
	sol_qD_shock[l1,t,s,n] = qD.l[t,s,n];
	sol_pD_shock[l1,t,s,n] = pD.l[t,s,n];
	sol_p_shock[l1,t,n] = p.l[t,n];
);