# Task Description

The attempt acts as an analyst for a Gujarat agricultural investment fund
running a drought-resilience program (irrigation subsidies + drought-tolerant
seed R&D) across four crops: Cotton(lint), Wheat, Groundnut, and Maize. A
budget cut forces the fund to drop exactly one crop from the program. The
attempt must recommend which crop to drop based on 1997-2019 crop production
and rainfall records, and produce two deliverables:
`output/crop_rainfall_sensitivity.csv` (a Pearson correlation between annual
yield and annual rainfall, per crop) and `output/recommendation.md` (an
Exclude line, Key Findings, Rationale, and Risks and Caveats).

# Data Provenance

`gujarat_crop_stats.csv` and `gujarat_annual_rainfall.csv` are a real subset
(Gujarat state, four crops) of the "Crop Yield in Indian States Dataset" by
akshatgupta7 on Kaggle
(https://www.kaggle.com/datasets/akshatgupta7/crop-yield-in-indian-states-dataset),
licensed CC BY-SA 4.0 -- attribution to the original source is required, and
this derived subset must be shared under the same license. The ground truth
below was discovered by direct analysis of the real data, not engineered --
see the verification notes at the end of this card. `crop_profiles.xlsx` and
`fund_committee_notes.txt` were authored for this task and are not sourced
from the Kaggle dataset. This attribution has not been independently
verified against the live listing (this package was built without internet
access); confirm the listing and license are still current before
submission.

# Complexity Justification

1. **Rainfall-sensitivity vs. surface plausibility (the crux).** Cotton,
   Wheat, and Groundnut all show a strong, robust positive correlation
   between annual yield and annual rainfall in Gujarat (r = 0.67-0.69, and
   still r = 0.61-0.71 after removing any shared linear time trend). Maize
   shows essentially no such relationship (r = 0.163, dropping to r = 0.07
   after detrending). A correct attempt must compute this per-crop
   correlation to find that Maize is the one crop that would gain the least
   protection from a drought-resilience investment. The fund committee notes
   explicitly pressure the reader toward keeping Maize (rising prices,
   cooperative demand) and toward dropping Cotton (optics) or Groundnut (a
   pest-year anecdote) instead -- a correct attempt has to recognize these as
   not answering the stated question (which crop's yield history shows the
   least rainfall dependence) and hold to the data-driven mandate stated in
   the committee's own notes.

2. **Inconsistent year formats across files.** A subset of
   gujarat_crop_stats.csv (1997-99) uses a fiscal-year label (`1997-98`)
   while the rest use a plain year, and gujarat_annual_rainfall.csv uses
   plain years throughout. A correct attempt must resolve this before
   joining the two files; a naive numeric coercion silently drops three
   years of data for every crop instead.

3. **Multi-season aggregation.** Some crops (Groundnut, Maize) are grown in
   more than one season per year and appear as multiple rows per crop-year.
   A correct attempt must aggregate Area and Production across seasons
   before computing that year's yield, rather than treating each season row
   as an independent year-crop observation or arbitrarily picking one
   season.

# Taxonomy Tags

agriculture, public-policy, climate-risk, data-cleaning, decision-analysis,
correlation-analysis

# Expected Difficulty

Target: strong model mean reward at or under 0.6, weak model mean reward at
or under 0.35 over 4 sweep trials. A strong attempt is expected to miss
primarily by reasoning from the committee notes (price trends, optics, the
pest-year anecdote) rather than computing the per-crop correlation, or by
losing years to the fiscal-year label mismatch. Verified: a naive attempt
that drops the fiscal-year-labeled rows and follows the committee's pest-year
anecdote (excluding Groundnut) scored 30/65 on the automated test suite
versus 65/65 for the correct analysis, and its own reported numbers
contradicted its stated decision.

# Ground-Truth Recommendation

**Exclude Maize; retain Cotton(lint), Wheat, and Groundnut.**

Pearson correlation between annual yield (Production/Area, summed across
seasons) and annual rainfall, 1997-2019, recomputed independently in the
verifier from the shipped source files:

- Cotton(lint): r = 0.691 (23 years)
- Wheat: r = 0.687 (23 years)
- Groundnut: r = 0.668 (23 years)
- Maize: r = 0.163 (23 years)

This gap (0.668 vs 0.163, a 0.50 spread) is large and holds up after
removing any shared linear time trend from both series (detrended: Cotton
0.640, Wheat 0.705, Groundnut 0.610, Maize 0.070), so it is not an artifact
of both series happening to trend upward over 1997-2019.

Plausible wrong answers and why they're wrong:
- "Exclude Cotton(lint)" (reasoning from its large area/production, as one
  committee member suggests) -- Cotton is in fact one of the three most
  rainfall-sensitive crops in the data; dropping it would remove protection
  from the crop that has among the most to lose from a poor monsoon.
- "Exclude Groundnut" (reasoning from the committee's 2015 pest-year
  anecdote) -- a single pest-related bad year is a different risk from
  rainfall dependence, and Groundnut's multi-year correlation with rainfall
  is nearly as strong as Cotton's and Wheat's.
- "Exclude Wheat" -- Wheat has the single highest correlation with rainfall
  of the four crops even after detrending, making it the strongest case for
  keeping the program, not dropping it.
