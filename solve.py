"""
Reference solution for gujarat-drought-resilience-v1.
Joins the crop stats and rainfall files (resolving the fiscal-year label
mismatch), computes annual yield per crop-year, correlates it against
rainfall per crop, and writes the two required deliverable files.
"""
import os
import re
import pandas as pd

DATA_DIR = os.environ.get("DATA_DIR", "/workspace/environment/data")
OUT_DIR = os.environ.get("OUT_DIR", "/workspace/output")
os.makedirs(OUT_DIR, exist_ok=True)

CROPS = ["Cotton(lint)", "Wheat", "Groundnut", "Maize"]


def resolve_year(raw):
    """'1997-98' -> 1997 (agricultural year convention); plain years pass through."""
    s = str(raw).strip()
    m = re.match(r"^(\d{4})-\d{2}$", s)
    if m:
        return int(m.group(1))
    return int(float(s))


def main():
    stats = pd.read_csv(os.path.join(DATA_DIR, "gujarat_crop_stats.csv"))
    rain = pd.read_csv(os.path.join(DATA_DIR, "gujarat_annual_rainfall.csv"))

    stats["Year"] = stats["Crop_Year"].apply(resolve_year)
    stats["Crop"] = stats["Crop"].str.strip()
    stats["Season"] = stats["Season"].str.strip()

    # aggregate to crop-year level, summing across seasons
    agg = stats.groupby(["Crop", "Year"]).agg(Area=("Area", "sum"),
                                               Production=("Production", "sum")).reset_index()
    agg["yield"] = agg["Production"] / agg["Area"]

    merged = agg.merge(rain, on="Year", how="inner")

    rows = []
    for crop in CROPS:
        sub = merged[merged["Crop"] == crop]
        corr = sub["yield"].corr(sub["Annual_Rainfall_mm"])
        rows.append({
            "crop": crop,
            "n_years": len(sub),
            "yield_rainfall_correlation": round(float(corr), 3),
        })

    sens = pd.DataFrame(rows)
    sens.to_csv(os.path.join(OUT_DIR, "crop_rainfall_sensitivity.csv"), index=False)

    lowest = sens.loc[sens["yield_rainfall_correlation"].idxmin()]
    exclude_crop = lowest["crop"]

    lines = []
    lines.append(f"**Exclude:** {exclude_crop}")
    lines.append("")
    lines.append("## Key Findings")
    lines.append("")
    lines.append("Correlation between annual yield and annual rainfall, by crop:")
    lines.append("")
    for _, r in sens.sort_values("yield_rainfall_correlation", ascending=False).iterrows():
        lines.append(f"- {r['crop']}: {r['yield_rainfall_correlation']:.3f} "
                      f"({int(r['n_years'])} years of data)")
    lines.append("")
    lines.append("## Rationale")
    lines.append("")
    others = sens[sens["crop"] != exclude_crop].sort_values(
        "yield_rainfall_correlation", ascending=False)
    other_summary = ", ".join(
        f"{r['crop']} ({r['yield_rainfall_correlation']:.2f})" for _, r in others.iterrows()
    )
    lines.append(
        f"{exclude_crop}'s yield shows a correlation of only "
        f"{lowest['yield_rainfall_correlation']:.3f} with annual rainfall over "
        f"{int(lowest['n_years'])} years of data, far below the other three "
        f"candidates: {other_summary}. All three of the other crops show a "
        f"strong, consistent positive relationship between rainfall and yield "
        f"-- in years with less monsoon rainfall, their yields drop "
        f"noticeably, which is exactly the vulnerability the drought-resilience "
        f"program (irrigation subsidies and drought-tolerant seed R&D) is "
        f"designed to protect against. {exclude_crop}, by contrast, shows "
        f"essentially no such relationship in the historical record: its "
        f"yield does not reliably move with rainfall one way or the other, "
        f"which suggests its production is already comparatively insulated "
        f"from monsoon variability, whether due to irrigation access, "
        f"growing-season timing, or other factors not captured directly in "
        f"this dataset. Given a forced choice to drop exactly one crop from "
        f"the program, {exclude_crop} is the crop where a drought-resilience "
        f"investment would have the smallest expected protective payoff, "
        f"since its yield history does not show it being meaningfully at risk "
        f"from rainfall shortfalls in the first place. The other three crops "
        f"should retain funding precisely because their yield histories show "
        f"they have the most to lose from a poor monsoon."
    )
    lines.append("")
    lines.append("## Risks and Caveats")
    lines.append("")
    lines.append(
        "This analysis uses a simple year-level correlation between rainfall "
        "and yield; it does not control for other factors that changed over "
        "the same 1997-2019 period (input costs, seed varieties, market "
        "prices) that could also affect yield and happen to move together "
        "with rainfall in some years. A committee member also noted a 2015 "
        "pest outbreak affecting Groundnut that was unrelated to rainfall; "
        "isolated shocks like that can add noise to a single crop's "
        "correlation without changing its underlying rainfall sensitivity. "
        "A longer time series or a model that controls for input use over "
        "time would give a more robust estimate."
    )

    with open(os.path.join(OUT_DIR, "recommendation.md"), "w") as f:
        f.write("\n".join(lines) + "\n")

    print(sens)
    print("Exclude:", exclude_crop)


if __name__ == "__main__":
    main()
