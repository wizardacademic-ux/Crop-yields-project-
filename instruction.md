# Drought-Resilience Program — Crop Prioritization Review

You are an analyst supporting a state agricultural investment fund that runs a
multi-year drought-resilience program for farmers in Gujarat: subsidized drip
irrigation and drought-tolerant seed R&D grants. The program currently covers
four major Gujarat crops: **Cotton(lint)**, **Wheat**, **Groundnut**, and
**Maize**.

A mid-year budget cut means the fund can only continue support for **three**
of the four crops this cycle. The programme lead has asked you to recommend
which **one** crop should be **dropped** from the program, using the
historical crop and weather data provided, and to show the analysis behind
the recommendation.

You have been given the fund's records: multi-year crop production
statistics, an annual rainfall record, general agronomic reference notes on
each crop, and informal notes from a recent committee meeting. The data
comes from different internal sources and has not been reconciled for you.

## Deliverables

Write your output to the `output/` directory. Both files below are required.

### 1. `output/crop_rainfall_sensitivity.csv`

One row per crop (4 data rows plus a header). Exact columns, in this order:

```
crop,n_years,yield_rainfall_correlation
```

- `crop`: exactly one of `Cotton(lint)`, `Wheat`, `Groundnut`, `Maize`
- `n_years`: the number of distinct crop-years of data used for that crop
- `yield_rainfall_correlation`: the Pearson correlation coefficient, rounded
  to 3 decimal places, between that crop's annual yield (total Production
  divided by total Area for that crop-year, summed across every season the
  crop was grown in that year) and that year's `Annual_Rainfall_mm`,
  computed across every crop-year for which the crop has data

### 2. `output/recommendation.md`

A Markdown report containing, at minimum, these sections:

- A line beginning exactly with `**Exclude:**` followed by exactly one of
  these four tokens (verbatim): `Cotton(lint)`, `Wheat`, `Groundnut`, `Maize`
- A `## Key Findings` section reporting all four crops'
  `yield_rainfall_correlation` values from the CSV
- A `## Rationale` section of at least 150 words explaining the
  recommendation
- A `## Risks and Caveats` section noting at least one specific limitation
  of the analysis

## Requirements and prohibitions

- Base your analysis only on the data provided in `environment/data/`. Do not
  fabricate figures.
- The year fields are not formatted consistently across the two data files;
  resolve this yourself before joining them. Do not drop a crop-year from the
  analysis solely because its year label doesn't match the other file's
  format at face value.
- All numeric values in `output/crop_rainfall_sensitivity.csv` must use the
  precision specified above.
