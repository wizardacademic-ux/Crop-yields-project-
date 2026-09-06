"""
Verifier for gujarat-drought-resilience-v1. Reads ONLY the attempt's output
files plus the source data (to independently recompute ground truth) --
never the reference solution's output.
"""
import os
import re
import pandas as pd

DATA_DIR = os.environ.get("DATA_DIR", "/workspace/environment/data")
OUT_DIR = os.environ.get("OUT_DIR", "/workspace/output")

CROPS = {"Cotton(lint)", "Wheat", "Groundnut", "Maize"}
EXPECTED_COLUMNS = ["crop", "n_years", "yield_rainfall_correlation"]


def _resolve_year(raw):
    s = str(raw).strip()
    m = re.match(r"^(\d{4})-\d{2}$", s)
    if m:
        return int(m.group(1))
    return int(float(s))


def _recompute_ground_truth():
    stats = pd.read_csv(os.path.join(DATA_DIR, "gujarat_crop_stats.csv"))
    rain = pd.read_csv(os.path.join(DATA_DIR, "gujarat_annual_rainfall.csv"))

    stats["Year"] = stats["Crop_Year"].apply(_resolve_year)
    stats["Crop"] = stats["Crop"].str.strip()

    agg = stats.groupby(["Crop", "Year"]).agg(Area=("Area", "sum"),
                                               Production=("Production", "sum")).reset_index()
    agg["yield"] = agg["Production"] / agg["Area"]
    merged = agg.merge(rain, on="Year", how="inner")

    gt = {}
    for crop in CROPS:
        sub = merged[merged["Crop"] == crop]
        corr = sub["yield"].corr(sub["Annual_Rainfall_mm"])
        gt[crop] = {"n_years": len(sub), "corr": float(corr)}
    return gt


GT = _recompute_ground_truth()
EXPECTED_EXCLUDE = min(GT, key=lambda c: GT[c]["corr"])
# sanity: the gap must be large enough that this is a robust, non-fragile answer
_sorted = sorted(GT.values(), key=lambda v: v["corr"])
assert _sorted[1]["corr"] - _sorted[0]["corr"] > 0.25, "generator invariant broken: gap too small"


def _load_csv():
    path = os.path.join(OUT_DIR, "crop_rainfall_sensitivity.csv")
    if not os.path.exists(path):
        return None
    try:
        return pd.read_csv(path)
    except Exception:
        return None


def _load_md():
    path = os.path.join(OUT_DIR, "recommendation.md")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return f.read()


def _extract_decision(md_text):
    if md_text is None:
        return None
    m = re.search(r"\*\*Exclude:\*\*\s*(.+)", md_text)
    if not m:
        return None
    return m.group(1).strip().split("\n")[0].strip()


# ---------- file presence / structure ----------

def test_sensitivity_file_exists():
    assert os.path.exists(os.path.join(OUT_DIR, "crop_rainfall_sensitivity.csv"))


def test_recommendation_file_exists():
    assert os.path.exists(os.path.join(OUT_DIR, "recommendation.md"))


def test_sensitivity_columns_exact():
    df = _load_csv()
    assert df is not None
    assert list(df.columns) == EXPECTED_COLUMNS


def test_sensitivity_row_count():
    df = _load_csv()
    assert df is not None
    assert len(df) == 4


def test_sensitivity_crop_values_valid():
    df = _load_csv()
    assert df is not None
    assert set(df["crop"].unique()) == CROPS


# ---------- numeric correctness ----------

def test_n_years_reasonable():
    df = _load_csv()
    assert df is not None
    for _, row in df.iterrows():
        crop = row["crop"]
        if crop in GT:
            assert abs(int(row["n_years"]) - GT[crop]["n_years"]) <= 1


def test_correlations_match_recomputed_ground_truth():
    df = _load_csv()
    assert df is not None
    ok, total = 0, 0
    for _, row in df.iterrows():
        crop = row["crop"]
        if crop not in GT:
            continue
        total += 1
        # generous absolute tolerance: defensible methodological variation
        # (e.g. mean-of-seasonal-yields vs pooled production/area) should not
        # fail this, only a materially wrong computation should
        if abs(row["yield_rainfall_correlation"] - GT[crop]["corr"]) <= 0.08:
            ok += 1
    assert total > 0
    assert ok / total >= 0.75


# ---------- decision correctness (the crux) ----------

def test_decision_line_present_and_valid_token():
    md = _load_md()
    decision = _extract_decision(md)
    assert decision in CROPS


def test_decision_matches_ground_truth():
    md = _load_md()
    decision = _extract_decision(md)
    assert decision == EXPECTED_EXCLUDE


def test_excluded_crop_correlation_clearly_lowest():
    """The excluded crop's own reported correlation must actually be the
    lowest of the four in the attempt's own CSV -- catches a right-sounding
    decision paired with numbers that don't actually support it."""
    df = _load_csv()
    md = _load_md()
    assert df is not None
    decision = _extract_decision(md)
    if decision not in set(df["crop"]):
        assert False
    idx_min = df["yield_rainfall_correlation"].idxmin()
    assert df.loc[idx_min, "crop"] == decision
