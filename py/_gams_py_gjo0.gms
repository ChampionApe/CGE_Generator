$ONEOLCOM
$EOLCOM #



;
OPTION SYSOUT=OFF, SOLPRINT=OFF, LIMROW=0, LIMCOL=0, DECIMALS=6;


# User defined functions:

# ----------------------------------------------------------------------------------------------------
#  Define function: SolveEmptyNLP
# ----------------------------------------------------------------------------------------------------


sets
	alias_set
	alias_map2
	s
	n
	t
;

alias(n,nn);

sets
	alias_[alias_set,alias_map2]
	mapOut[s,n,nn]
	knotOutTree[s,n]
	branchOut[s,n]
	branchNOut[s,n]
	mapInp[s,n,nn]
	knotOut[s,n]
	knotNOut[s,n]
	branch2Out[s,n]
	branch2NOut[s,n]
	map[s,n,nn]
	output[s,n]
	input[s,n]
	int[s,n]
;

variables
	mu[t,s,n,nn]
	vD[t,s,n]
	vS[t,s,n]
;
$GDXIN db
$onMulti
$load alias_set
$load alias_map2
$load s
$load n
$load t
$load alias_
$load mapOut
$load knotOutTree
$load branchOut
$load branchNOut
$load mapInp
$load knotOut
$load knotNOut
$load branch2Out
$load branch2NOut
$load map
$load output
$load input
$load int
$GDXIN
$offMulti;
$GDXIN db
$onMulti
$load mu
$load vD
$load vS
$GDXIN
$offMulti;




# --------------------------------------------B_ValueShares-------------------------------------------
#  Initialize B_ValueShares equation block
# ----------------------------------------------------------------------------------------------------
EQUATION E_Out_knot[t,s,n];
E_Out_knot[t,s,n]$(knotouttree[s,n]).. 								vD[t,s,n]	 =E=  sum(nn$(map[s,nn,n] and branchOut[s,nn]), vS[t,s,n])+sum(nn$(map[s,nn,n] and branchNOut[s,nn]), vD[t,s,n]);
EQUATION E_Out_shares_o[t,s,n,nn];
E_Out_shares_o[t,s,n,nn]$(mapout[s,n,nn] and branchout[s,n]).. 		mu[t,s,n,nn] =E=  vS[t,s,n]/vD[t,s,nn];
EQUATION E_Out_shares_no[t,s,n,nn];
E_Out_shares_no[t,s,n,nn]$(mapout[s,n,nn] and branchnout[s,n]).. 	mu[t,s,n,nn] =E=  vD[t,s,n]/vD[t,s,nn];
EQUATION E_Inp_knot_o[t,s,n];
E_Inp_knot_o[t,s,n]$(knotout[s,n]).. 								vS[t,s,n]	 =E=  sum(nn$(map[s,n,nn]), vD[t,s,nn]);
EQUATION E_Inp_knot_no[t,s,n];
E_Inp_knot_no[t,s,n]$(knotnout[s,n]).. 								vD[t,s,n]	 =E=  sum(nn$(map[s,n,nn]), vD[t,s,nn]);
EQUATION E_Inp_shares2o[t,s,n,nn];
E_Inp_shares2o[t,s,n,nn]$(mapinp[s,n,nn] and branch2out[s,nn]).. 	mu[t,s,n,nn] =E=  vD[t,s,nn]/vS[t,s,n];
EQUATION E_Inp_shares2no[t,s,n,nn];
E_Inp_shares2no[t,s,n,nn]$(mapinp[s,n,nn] and branch2nout[s,nn]).. 	mu[t,s,n,nn] =E=  vD[t,s,nn]/vD[t,s,n];

# ----------------------------------------------------------------------------------------------------
#  Define B_ValueShares model
# ----------------------------------------------------------------------------------------------------
Model B_ValueShares /
E_Out_knot, E_Out_shares_o, E_Out_shares_no, E_Inp_knot_o, E_Inp_knot_no, E_Inp_shares2o, E_Inp_shares2no
/;


vD.fx[t,s,n]$(input[s,n]) = vD.l[t,s,n]$(input[s,n]);
vS.fx[t,s,n]$(output[s,n]) = vS.l[t,s,n]$(output[s,n]);
mu.lo[t,s,n,nn]$(map[s,n,nn]) = -inf;
mu.up[t,s,n,nn]$(map[s,n,nn]) = inf;
vD.lo[t,s,n]$(int[s,n]) = -inf;
vD.up[t,s,n]$(int[s,n]) = inf;

variable randomnameobj;  
randomnameobj.L = 0;

EQUATION E_EmptyNLPObj;
E_EmptyNLPObj..    randomnameobj  =E=  0;

Model M_SolveEmptyNLP /
E_EmptyNLPObj, B_ValueShares
/;
solve M_SolveEmptyNLP using NLP min randomnameobj;
;
