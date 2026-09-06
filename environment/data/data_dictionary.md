# Data Dictionary

## Data provenance and licensing

`gujarat_crop_stats.csv` and `gujarat_annual_rainfall.csv` are derived from a
public Kaggle dataset of Indian crop production statistics ("Crop Yield
Prediction Dataset" style data covering Crop, Crop_Year, Season, State, Area,
Production, Annual_Rainfall, Fertilizer, Pesticide, and Yield across Indian
states, 1997-2020). This subset keeps only the rows for Gujarat and four
crops (Cotton(lint), Wheat, Groundnut, Maize), and only the columns needed
for this task. The Fertilizer, Pesticide, and Yield columns from the source
dataset are not included here; Yield must be computed from Area and
Production if needed.

**License note:** `gujarat_crop_stats.csv` and `gujarat_annual_rainfall.csv`
are derived from the "Crop Yield in Indian States Dataset" by akshatgupta7 on
Kaggle (https://www.kaggle.com/datasets/akshatgupta7/crop-yield-in-indian-states-dataset),
licensed CC BY-SA 4.0. Under that license, redistribution of this derived
subset requires attribution to the original source and must be shared under
the same CC BY-SA 4.0 license. This attribution has not been independently
verified against the live Kaggle listing (this package was built without
internet access) -- confirm the listing is still current and the license
terms unchanged before relying on this note.

## gujarat_crop_stats.csv

- `Crop`: crop name, one of `Cotton(lint)`, `Wheat`, `Groundnut`, `Maize`
- `Crop_Year`: the agricultural year. Most rows use a plain year (e.g. `2005`);
  a small number of older rows use a fiscal-year label (e.g. `1997-98`)
  because that is how those particular records were originally logged.
- `Season`: the cropping season as recorded in the source system (values are
  not cleaned -- e.g. some contain trailing whitespace, and a small number of
  early records use `Whole Year` where later years use a specific season name
  for the same crop)
- `Area`: area harvested, in hectares
- `Production`: total production, in tonnes

Some crops appear more than once per year (grown in more than one season,
e.g. Groundnut in both Kharif and Summer) -- these are separate rows, not
duplicates.

## gujarat_annual_rainfall.csv

- `Year`: calendar year, as a plain integer in this file
- `Annual_Rainfall_mm`: total annual rainfall recorded for Gujarat that year,
  in millimeters

Note the year representation is not identical to `Crop_Year` in
gujarat_crop_stats.csv for the fiscal-year-labeled rows -- joining the two
files requires resolving that difference.

## crop_profiles.xlsx

General agronomic reference information about each crop's typical growing
season and water source in Gujarat. General background, not specific to any
particular year in this dataset.

## fund_committee_notes.txt

Informal notes from a fund committee meeting. Anecdotal opinions from
committee members, not verified analysis.
