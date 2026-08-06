# Elasticity of substitution between clean and dirty energy

*Note for calibration of the NCP CGE model. 2026-08-03.*

## Recommended value

For the central/reference calibration, use **σ ≈ 2** for the elasticity of substitution between clean and dirty energy inputs, treated as a long-run parameter (consistent with the model's dynamic structure and installation-cost adjustment). For sensitivity analysis, use a range of **1 to 3**, with the low end reflecting short-run/putty-clay rigidity and the high end reflecting econometric estimates for the electricity sector specifically.

Given the model has explicit installation costs and dynamic technology adoption, it is defensible to treat σ as a long-run elasticity even though most econometric estimates in this range come from panel data with limited ability to fully capture long-run adjustment — the model's own dynamics already generate short-run "stickiness" through adjustment costs, so the CES elasticity itself should represent the frictionless (long-run) substitution possibility.

## Why not lower or higher

Values below 1 (near-complementarity) are estimated when technology and infrastructure are held fixed — i.e., short-run responses to relative price changes. Since our model already has a separate mechanism (installation costs) generating short-run rigidity, using a low σ in the CES nest as well would double-count that friction. Values above 3–4 are typically drawn from bottom-up engineering/dispatch models of the electricity sector alone, which capture technical substitutability (e.g., storage-enabled substitution between renewables and fossil generation) rather than economy-wide macro substitution across all "dirty" (fossil) and "clean" (renewable/low-carbon) energy uses. Since our model spans multiple sectors, not just electricity generation, an economy-wide estimate is the more appropriate anchor.

## Key references and their estimates

**Papageorgiou, Saam & Schulte (2017)**, "Substitution between Clean and Dirty Energy Inputs: A Macroeconomic Perspective," *Review of Economics and Statistics* 99(2): 281–290 (working paper version: ZEW Discussion Paper No. 13-087, 2013). Using a panel of nested CES production functions across 26 countries, they estimate a macroeconomic elasticity significantly above 1, with a cross-country estimate of about **1.8** for the electricity-generating sector specifically. This is the most widely cited estimate in the CGE/IAM literature and the natural benchmark for our central case.

**Reconciling empirical estimates (2026 working paper, University of Groningen)**, "On the Elasticity of Substitution between Clean and Dirty Energy: Reconciling Empirical Estimates and Their Implications for Model Calibration." Using an encompassing specification on 13 OECD countries, 1980–2020, they show that estimates depend critically on whether technology/infrastructure is held fixed (short run, σ well below 1) or allowed to adjust (long run, σ between **2 and 3**). This paper is useful precisely because it reconciles the wide range of prior estimates (< 0.5 to 10) by showing much of the disagreement is a short-run/long-run distinction rather than a genuine empirical contradiction.

**Stöckl & Zerrahn (2023)**, "Substituting Clean for Dirty Energy: A Bottom-Up Analysis," *Journal of the Association of Environmental and Resource Economists* 10(3). A bottom-up numerical dispatch model of electricity generation finds σ **above 1** whenever some energy storage is available, with no single clean technology indispensable, though substitution becomes harder at higher clean-energy shares (i.e., the elasticity is not strictly constant — it falls as decarbonization progresses). Useful as a caution: if the model is used to simulate deep decarbonization paths, a constant σ may overstate substitutability at high abatement rates.

**Jo (2025)**, "Substitution between Clean and Dirty Energy with Biased Technical Change," *International Economic Review*. Extends the Papageorgiou et al. approach by allowing for directed technical change, generally supporting elasticities above unity once endogenous technology bias is accounted for.

## Typical values used in other CGE/IAM models (for context)

- EPPA (MIT): σ ≈ 0.5 for the electricity/non-electricity energy nest (values differ by nest — not directly comparable to the clean/dirty split used here).
- GTAP-E: σ = 1 in the relevant energy nest.
- Bottom-up/hybrid models (GEM-E3, IMACLIM-R, ENV-Linkages) typically use higher, technology-specific substitution possibilities informed by engineering data rather than a single macro elasticity.

These illustrate that modeling conventions vary substantially by model structure and nest definition; they are included for context rather than as a direct source for our value, since our clean/dirty nest is not defined identically to these models' energy nests.

## Practical range for sensitivity analysis

| Case | σ | Basis |
|---|---|---|
| Low | 1.0 | Short-run/rigid estimates from panel data; conservative bound |
| Central | 1.8–2.0 | Papageorgiou et al. (2017) cross-country electricity estimate; consistent with long-run range in Reconciling Empirical Estimates (2026) |
| High | 3.0 | Upper end of long-run OECD estimates |

## Caveats

- All estimates above pertain primarily to electricity generation or aggregate energy use; econometric identification of a clean/dirty elasticity for non-electricity sectors (e.g., industrial process heat, transport fuels) is much sparser, so applying a single economy-wide σ to all sectors is a simplification worth flagging in the paper.
- The elasticity is likely not constant over the transition path (Stöckl & Zerrahn), which is a limitation of the CES structure generally; this is worth a robustness check (e.g., re-running key results with σ = 1 and σ = 3) rather than a reason to abandon CES.
- If the paper is challenged on this parameter in review, cite Papageorgiou et al. (2017) as the primary source and the 2026 Groningen paper as the reconciliation of the wider range, and report the 1–3 sensitivity band.

## References

- Papageorgiou, C., Saam, M., & Schulte, P. (2017). Substitution between Clean and Dirty Energy Inputs: A Macroeconomic Perspective. *Review of Economics and Statistics*, 99(2), 281–290.
- [On the elasticity of substitution between clean and dirty energy: Reconciling empirical estimates and their implications for model calibration](https://wps-feb.ugent.be/Papers/wp_26_1140.pdf), University of Ghent/Groningen working paper, 2026.
- Stöckl, F., & Zerrahn, A. (2023). Substituting Clean for Dirty Energy: A Bottom-Up Analysis. *Journal of the Association of Environmental and Resource Economists*, 10(3). https://doi.org/10.1086/722612
- Jo, A. (2025). Substitution between Clean and Dirty Energy with Biased Technical Change. *International Economic Review*. https://onlinelibrary.wiley.com/doi/full/10.1111/iere.12743
