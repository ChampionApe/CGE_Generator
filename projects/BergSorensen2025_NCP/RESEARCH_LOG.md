## 2026-08-03
Researched elasticity of substitution between clean and dirty energy for CGE calibration. Wrote `notes/elasticity_clean_dirty_energy.md`: recommend σ ≈ 2 central (range 1–3 for sensitivity), based on Papageorgiou, Saam & Schulte (2017, ReStat) and a 2026 Groningen reconciliation paper. Next: decide whether to apply a single economy-wide σ or sector-specific values, and consider robustness checks at σ = 1 and σ = 3.

## 2026-08-26
Pre-submission review of `local/refereeing/FinalDraft_26082026.pdf` ahead of Energy Economics
submission. Checked every reported number against the notebooks and stored solution databases
without re-solving; read the draft adversarially. Findings in
`notes/presubmission_review_2026-08-26.md`, shareable version published as an artifact.

Three verified errors, all fixed: the abatement-cost decline rate was misstated in §4 and §5
(code sets `techCostTrend = g_LR/2`, so baseline is 1%/yr and SENS2 is 2%, not 2% and 3%); §2
Case B printed the borrowing condition inverted against its own Appendix A; and Figures 5.2/5.3
came from a superseded run via legacy filenames while 5.1/5.4/5.5 were current. Also renamed the
CGE-side H2M share from α to λ to match §2 and Appendix A, added three uncited attributions that
were already in the bib (GHH, GreenREFORM welfare note, Stöckl & Zerrahn + Jo), and applied the
content-level presentation fixes (Denmark in abstract/intro, Paris target wording, softened
front-loading claims in §1/§6, terms-of-trade ambiguity reconciled across §2/§5/§6, limitations
paragraph extended). Document builds clean: 0 undefined references, 0 undefined citations,
62 pages.

Reproduced exactly: all nine Table 2 welfare figures, all fifteen Table 3 sensitivity figures,
and every Table 1 parameter.

Next: LaTeX/build-folder hygiene (hardcoded cross-refs, 14 straight-quote pairs, "online
appendix" wording, dead files including the duplicate `\label{app:SimpleModel}`), and Energy
Economics submission compliance (highlights, abstract cap, declarations, data availability).
Optional strengthening: evaluate eq (7) at the calibrated α, a_0 and C_0^c/C_0^s to turn the
front-loading condition into a result. Known pre-existing issue: both `tabularx` tables throw a
recoverable `\TX@endtabularx` error caused by the `{\small ...}` wrapper.
