# Pre-submission review — FinalDraft_26082026.pdf

Consistency pass of the draft against the code that produced it, plus a referee-style read.
No model re-runs: figures compared by hash and by rendering, table values compared against
stored notebook outputs, parameters traced to the cells that set them, theory section checked
against its own appendix.

**Status.** Sections 1, 3, 4, the agreed items in section 2, and the "content" half of section 5
have been applied to the source; the document builds clean (biber + 2 passes: 0 undefined
references, 0 undefined citations, 62 pages). Three items in section 2 were declined by the
authors and are marked as such. Still open: the LaTeX/build-folder half of section 5, and
journal compliance for Energy Economics.

---

## 1. Verified errors — fix before submitting

### 1.1 Abatement-cost decline rate misstated (two places)

Baseline is **1 %/yr**, sensitivity is **2 %/yr**. The draft says 2 % and 3 %.

```
Main_1A_ModelData.ipynb  cell 200:  techCostTrend = g_LR/2
SENS2_1A_ModelData.ipynb cell 200:  techCostTrend = g_LR
g_LR = 2%   (Table 1: g = 2%; beta = 0.99 = 1.02^2/1.05 confirms)
  -> baseline 1%, SENS2 2%
```

| Location | Says | Should say |
|---|---|---|
| `Sections/4_Calibration.tex:20` | "a more modest rate of 2 percent per year" | 1 percent |
| `Sections/5_AlternativePathways.tex` | "fall in abatement costs of 2 percent … third row … 3 percent" | 1 percent … 2 percent |
| `Tables/welfareCosts_sensitivity.tex` note b | "2% instead of 1%" | correct as is |

Fix the two body passages, then add `techCostTrend` to Table 1 so the number has one home.

### 1.2 Inverted inequality, §2 Case B

Draft: "would prefer to borrow in period 0, formally because `nu_0/nu_1 > beta(1+r)`".

`Appendix/A_Theory.tex:73-77` has it right: `1/nu_t > beta(1+r)/nu_{t+1}` i.e.
`nu_{t+1} > beta(1+r) nu_t`. Same ordering is implied by eq (6)'s smoothing factor and by
eq (7)'s `1 - beta(1+r) C_0^c/C_1^c`.

Fix: `nu_1/nu_0 > beta(1+r)`. Surrounding argument and the back-loading conclusion unaffected.

### 1.3 Figures 5.2 and 5.3 are from a superseded run

The paper pulls these from legacy filenames that exist only in `local/refereeing/Figs/` —
nothing in the pipeline writes them any more. Figures 5.1, 5.4, 5.5 *are* byte-identical to
the current `results/` output.

```
paper includes                       pipeline writes (Main_4A_Plots)
  Figs/Figure51.pdf          ==      results/Figure51.pdf     identical
  Figs/GRH2M0_cons_EB.pdf    vs      results/Figure52.pdf     cell 49
  Figs/GRH2M0_priceAggCap_EB vs      results/Figure53.pdf     cell 57
  Figs/Figure54.pdf          ==      results/Figure54.pdf     identical
  Figs/Figure55.pdf          ==      results/Figure55.pdf     identical
```

Fig 5.3 left panel, average export price peak: **~1.081 in the paper vs ~1.089 in the current
run**. Fig 5.2 H2M panel settles at ~0.9035 vs ~0.9020, and the current version carries the
intended `ylim [0.875, 1.05]`.

Fix: copy `results/Figure52.pdf` and `results/Figure53.pdf` into `Figs/`, update the two
`\includegraphics`. No re-solving needed. Re-read the export-price paragraph afterwards — the
front-loading gap it describes is slightly larger in the new run.

---

## 2. Where a referee will push

- **[APPLIED] Terms-of-trade sign.** §2 Case C said "fundamentally ambiguous" one paragraph after
  "both favour a front loaded carbon tax", and §6 stated it as a finding. Now: §2 reads "both point
  towards a front loaded carbon tax" followed by "these asymmetries are suggestive rather than
  conclusive: the direction … cannot be established analytically"; §6 reads "could not be
  established analytically either, but in our simulations it likewise works in favour of
  front-loading". §5 already hedged correctly and was left alone.

- **[APPLIED] Intro overclaimed Case B.** "We show that, for empirically plausible parameter values,
  it will be optimal to front-load" replaced with the two-opposing-motives framing plus "we derive
  the condition determining which of the two dominates". §6 correspondingly softened to "has a
  motive to" plus "which of the two dominates is a quantitative question".
  Still open if wanted: eq (7) needs only `alpha`, `a_0` and `C_0^c/C_0^s`, all available from the
  calibrated CGE, so it could be evaluated to turn the condition into a result.

- **[DECLINED] Table 2 at two decimals.** 1.03 / 1.02 / 1.02 — the optimum ties the Hotelling rule.
  Authors' call: not important.

- **[DECLINED] Rank reversal in the zero-markup row.** Table 3: linear 1.25, Hotelling 1.26,
  optimal 1.23. Authors' call: "relative impacts" in the text refers mainly to distance from the
  optimal policy, so the sentence stands.

- **[DECLINED] §5 explanation for the lambda=0 row covers only one column.** Authors' call:
  not important.

- **[APPLIED] "The same carbon budget" is calibration-specific.** Added to the Table 3 note: "The
  budget is recomputed within each calibration, so it is common to the three policies within a row
  but differs across rows."

---

## 3. Notation collisions

| Symbol | §2 theory | §3–§5 CGE |
|---|---|---|
| `alpha` | capital share in `Y = A K^alpha L^(1-alpha)`; appears in eq (7) | population share of H2M consumers (Table 1: 0.4; Table 3 row "No credit constraints (alpha = 0)") |
| `epsilon` | export demand elasticity, `X_t = k_t p_t^-epsilon`, `epsilon -> inf` in Case A | CRRA parameter = 2 (§3, Table 1) |
| `tau_t` | the carbon tax | labour income tax rate (§3); carbon tax becomes `tau_t^CO2` |

`alpha` is the one to actually fix. §2 already uses `lambda` for the H2M share, so renaming the
CGE share to `lambda` through §3–§5 and the two tables is a find-and-replace.

---

## 4. Missing attributions (all already in References.bib, uncited)

- `GHH:1998` — §3's consumer block is Greenwood–Hercowitz–Huffman preferences ("leisure-adjusted
  consumption", labour supply from `dy_t/dL_t = 0`). Readers in this literature will recognise it.
  Note the bib key says 1998 but the entry year is 1988 (AER 78(3)) — rename the key.
- `StocklZerrahn:2023` (JAERE) and `Jo:2025` (IER) — both on clean/dirty energy substitution.
  `sigma_EM = sigma_ED = 1.8` is the most contestable parameter in the paper and Table 1 note c
  currently rests on one published paper plus a 2026 Ghent working paper.
- `GR:welfare` — GreenREFORM technical note on the welfare measure; cite where the CV is defined.

---

## 5. Presentation and hygiene

Content:
- Denmark appears nowhere in the abstract or introduction; first substantive mention is §4.
- Scenario (iii) defined two ways: intro "minimizes the (non-climate) welfare cost" vs
  abstract/§5 "maximizes average household welfare".
- Intro's Hotelling rule omits "at the world interest rate", which abstract and §5 specify.
- §6 "constrained only by the carbon budget" in the same sentence as "all attaining net zero by 2050".
- Paris target given as "below 2 degrees"; the text is "well below 2 °C, pursuing efforts to
  limit to 1.5 °C".
- Footnote 1 speculating that a future US government will rejoin — adds nothing, dates badly.
- Only uncertainty listed as a limitation; add a line each on absent climate damages in the
  welfare measure, leakage, and external validity of a single small open economy.

LaTeX and build folder:
- Hardcoded cross-refs: "Table 2 reports" (§5), "As shown in Appendix A" (§2), "Section 5
  investigates" (§4). All resolve correctly today; all break silently on insertion.
- Eleven straight `"` quotes (§2 ×1, §6 ×2, Appendix C ×8). Under T1 fontenc these render as
  vertical marks against the paper's `` `` … '' `` elsewhere.
- Ten "online appendix" references to appendices bound into the same 61-page PDF.
- Dead files: `Sections/2_Theory.tex`, `Appendix/A_SimpleModel.tex` (duplicate
  `\label{app:SimpleModel}` shared with `A_Theory.tex`), `Appendix/E_Robustness.tex`, ~20 unused
  figures, `JEEM_submission/`.
- `Tables/welfareCosts_ramsey.tex` reports 0.95 / 0.94 / 0.92 for the no-H2M case against Table 3's
  1.16 / 1.16 / 1.14, under a different budget (739 vs 681 Mt). Harmless while Appendix E is
  commented out; contradictory the moment it is re-enabled.

---

## 6. Reproduced cleanly

- Table 2, all nine welfare figures: 0.62/0.61/0.28, 1.25/1.25/1.43, 1.03/1.02/1.02 — exact match
  to cells 29 and 31 of `Main_4A_Plots.ipynb`.
- Table 3, all fifteen sensitivity figures — exact match to cell 33 of `Main_5_SENS.ipynb`, and
  row order matches the order the text describes them in.
- Table 1: `epsilon = 2`, `xi = 0.1`, H2M share 0.4 all match `Main_1A` (cells 143, 113);
  `beta = 0.99 = 1.02^2/1.05`; BAU intensity decline 1.25 % = 25 % of the stated 5 % historical
  rate and matches `shareTrend_uCO2 = 0.25`, with SENS1 setting it to 0.5 as the text says.
- Figures 5.1, 5.4, 5.5 byte-identical to current `results/`.
- No undefined references in 61 pages; every `\cite` key resolves in `References.bib`.
- No leftovers from the previous submission target in any compiled source.

## 7. Not verifiable without a re-run

Table 2's EUR/ton column (47.2 / 47.0 / 46.7) and the 681 Mt budget are computed in cells 33 and
35 of `Main_4A_Plots.ipynb`, but neither `EuroPerTon` nor `reductions2050_pretty` is displayed, so
there is no stored output to compare against. Adding a display line for both would make them
auditable without re-solving.
