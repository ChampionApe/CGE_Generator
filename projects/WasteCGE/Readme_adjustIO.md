## adjustIO.CreateIOTargets class

Small note on this "data class":

**Set definitions:**

* ```s0```: IO sectors with one aggregate sector. 
* ```s```: IO sectors with foreign sector disaggregated into as many sectors as domestic IO ones.
* ```ns```: Set of IO goods. One-to-one correspondence with ```s``` set.
* ```nr```: "Raw" set of materials. This corredsponds to data as we receive it, where origin of a material is not included in the data.
* ```nm```: Set of materials. The set ```nr``` with added ```D/F``` suffix to indicate origin (domestic/foreign). 

**Data inputs:**

* ```vD0[s0,ns]```: Vector of demand. Here, we use domestic production sectors + aggregate foreign sector. Demand for domestic production goods + foreign goods.
    * Based on this, define ```vS0syn[s,ns]``` by summing over sectors' demand. *Note: This assumes that IO sectors and goods are originally named the same.*
    * Split up aggregate foreign sectors demand into synthetic subsectors. Use patterns from domestic demand to guide this (default to uniform distr. as neutral assumption). Store the full synthetic demand vector as ```vD0syn[s,ns]```.
* ```vDnRaw[s0,nr]```: Vector of demand. Domestic production sectors + aggregate foreign sector. Demand for materials does not distinguish between origin yet.
* ```vSnRaw[s0,nr]```: Vector of supply. Domestic production sectors + aggregate foreign sector. Supply of materials does not distinguish between origin yet.


**Outputs:**
* ```vD0syn[s,ns]```: Starts from ```vD0[s0,ns]``` and splits up foreign sector $F$ into synthetic sectors using demand patterns for domestic subsectors (backup --> uniform distr. if no other information is available).
* ```vS0syn[s,ns]```: Splits up foreign sector $F$ into synthetic sectors (diagonal assumption).
* ```vDnSyn[s,nm]```: Starts from ```vDnRaw[s0,nr]``` and splits up foreign sector $F$ into synthetic sectors (using domestic patterns). Splits up demand for ```nr``` into domestic/foreign splits based on output shares.
* ```vSnSyn[s,nm]```: Starts from ```vSnRaw[s0,nr]``` and splits up foreign sector $F$ into synthetic sectors (using dommestic pattenrs, backup --> uniform distr.). Splits up ```nr``` into domestic/foreign (trivial).
* ```vDsyn[s,ns]```: Starts from ```vD0syn[s,ns]``` and predicts how introduction of new materials vector (```vDnSyn[s,nm]```) reduces the original vector of demands for IO goods (```ns```). This is based on input structures, output intensities etc..
* ```vD[s_0,ns]```, ```vDn[s_0, nm]```, ```vS[s_0, ns]```, ```vSn[s_0, sm]```: Takes relevant ```xSyn``` vector and aggregates the synthetic foreign sector split into one $F$ sector again.