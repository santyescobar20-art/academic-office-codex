"""Estimates for the pretrial-detention paper.

Identification. Resolution 14-2021 (15 December 2021) binds every criminal
judge at once, so there is no untreated court. We compare places according
to how heavily they relied on pretrial detention before the rule: a standard
that demands justification bites harder where detention was routine.
Exposure is measured in 2017-2018, which leaves 2019 and 2020 as clean
pre-periods (2021 is the reference year).

Outputs: manuscript/tables/*.csv and results.json.
Run from the paper folder:  python code/03_estimate.py
"""
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pyfixest as pf
import statsmodels.api as sm

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
TAB = ROOT / "manuscript" / "tables"
TAB.mkdir(parents=True, exist_ok=True)

BASE_YEARS = (2017, 2018)
REF = 2021
FIRST, LAST = 2017, 2026          # 2026 covers January-September only
RESOLUTION = pd.Timestamp("2021-12-15")
results: dict = {}


def tidy(fit, keep: str) -> pd.DataFrame:
    t = fit.tidy().reset_index()
    t = t[t["Coefficient"].str.contains(keep, regex=True)]
    return t.rename(columns={"Coefficient": "term", "Estimate": "b", "Std. Error": "se",
                             "Pr(>|t|)": "p", "2.5%": "lo", "97.5%": "hi"})[
        ["term", "b", "se", "p", "lo", "hi"]]


# ------------------------------------------------------------ canton panel
def load_canton() -> pd.DataFrame:
    k = pd.read_csv(PROC / "canton_year.csv")
    k["unit"] = k["province"] + " | " + k["canton"]
    base = (k[k["year"].between(*BASE_YEARS)].groupby("unit")[["pp_orders", "hearings_held"]].sum())
    base = base[base["hearings_held"] >= 200]
    base["base_rate"] = base["pp_orders"] / base["hearings_held"]
    base["z"] = (base["base_rate"] - base["base_rate"].mean()) / base["base_rate"].std()
    base["high"] = (base["base_rate"] > base["base_rate"].median()).astype(int)
    k = k.merge(base[["base_rate", "z", "high"]], left_on="unit", right_index=True)
    k = k[k["year"].between(FIRST, LAST) & (k["hearings_held"] > 0)].copy()
    k["log_hear"] = np.log(k["hearings_held"])
    k["log_hom"] = np.log1p(k["homicides"])
    k["post_early"] = k["year"].between(2022, 2023).astype(int)
    k["post_late"] = (k["year"] >= 2024).astype(int)
    for y in range(FIRST, LAST + 1):
        if y != REF:
            k[f"z_{y}"] = k["z"] * (k["year"] == y)
            k[f"high_{y}"] = k["high"] * (k["year"] == y)
    k["z_early"], k["z_late"] = k["z"] * k["post_early"], k["z"] * k["post_late"]
    k["high_early"], k["high_late"] = k["high"] * k["post_early"], k["high"] * k["post_late"]
    return k


def event_terms(prefix: str) -> str:
    return " + ".join(f"{prefix}_{y}" for y in range(FIRST, LAST + 1) if y != REF)


def canton_models(k: pd.DataFrame) -> None:
    results["canton_sample"] = {
        "cantons": int(k["unit"].nunique()), "obs": int(len(k)),
        "base_rate_mean": float(k.drop_duplicates("unit")["base_rate"].mean()),
        "base_rate_sd": float(k.drop_duplicates("unit")["base_rate"].std()),
        "base_rate_p25": float(k.drop_duplicates("unit")["base_rate"].quantile(.25)),
        "base_rate_p75": float(k.drop_duplicates("unit")["base_rate"].quantile(.75)),
    }
    # (1) aggregate before-after: year effects net of canton effects, caseload and violence
    k["year_f"] = k["year"].astype(str)
    fit = pf.fepois(f"pp_orders ~ i(year, ref={REF}) + log_hom | unit", data=k,
                    offset="log_hear", vcov={"CRV1": "unit"})
    yr = tidy(fit, r"year")
    yr["year"] = yr["term"].str.extract(r"(\d{4})").astype(int)
    yr["pct"] = np.expm1(yr["b"]) * 100
    yr.to_csv(TAB / "t2_year_effects.csv", index=False)

    # (2) event study in exposure
    out = []
    for outcome in ("pp_orders", "conviction_committals"):
        for prefix in ("z", "high"):
            f = pf.fepois(f"{outcome} ~ {event_terms(prefix)} + log_hom | unit + year",
                          data=k, offset="log_hear", vcov={"CRV1": "unit"})
            t = tidy(f, rf"^{prefix}_\d")
            t["year"] = t["term"].str[-4:].astype(int)
            t["outcome"], t["exposure"] = outcome, prefix
            pre = [f"{prefix}_{y}" for y in (2019, 2020)]
            try:
                w = f.wald_test(R=np.array([[1.0 if c == p else 0.0 for c in f._coefnames] for p in pre]))
                t["pretrend_p"] = float(w["pvalue"])
            except Exception:
                t["pretrend_p"] = np.nan
            out.append(t)
    pd.concat(out).to_csv(TAB / "t3_event_study.csv", index=False)

    # (3) pooled difference-in-differences with alternative specifications
    rows = []
    specs = {
        "baseline": dict(fml="pp_orders ~ z_early + z_late + log_hom | unit + year", data=k, vc="unit"),
        "province-year FE": dict(fml="pp_orders ~ z_early + z_late + log_hom | unit + province^year", data=k, vc="unit"),
        "cluster province": dict(fml="pp_orders ~ z_early + z_late + log_hom | unit + year", data=k, vc="province"),
        "no Guayaquil/Quito": dict(fml="pp_orders ~ z_early + z_late + log_hom | unit + year",
                                   data=k[~k["canton"].isin(["GUAYAQUIL", "QUITO"])], vc="unit"),
        "no homicide control": dict(fml="pp_orders ~ z_early + z_late | unit + year", data=k, vc="unit"),
        "binary exposure": dict(fml="pp_orders ~ high_early + high_late + log_hom | unit + year", data=k, vc="unit"),
        "placebo outcome: conviction committals": dict(
            fml="conviction_committals ~ z_early + z_late + log_hom | unit + year", data=k, vc="unit"),
        "drop 2020 (pandemic)": dict(fml="pp_orders ~ z_early + z_late + log_hom | unit + year",
                                     data=k[k["year"] != 2020], vc="unit"),
        "pre-period only 2019-2021": dict(fml="pp_orders ~ z_early + z_late + log_hom | unit + year",
                                          data=k[k["year"] >= 2019], vc="unit"),
    }
    for name, s in specs.items():
        f = pf.fepois(s["fml"], data=s["data"], offset="log_hear", vcov={"CRV1": s["vc"]})
        t = tidy(f, r"early|late")
        t["spec"], t["n"] = name, int(f._N)
        rows.append(t)
    did = pd.concat(rows)
    did["pct"] = np.expm1(did["b"]) * 100
    did["pct_lo"] = np.expm1(did["lo"]) * 100
    did["pct_hi"] = np.expm1(did["hi"]) * 100
    did.to_csv(TAB / "t4_did.csv", index=False)
    b0 = did[(did["spec"] == "baseline") & (did["term"] == "z_early")].iloc[0]
    iqr = (k.drop_duplicates("unit")["base_rate"].quantile(.75)
           - k.drop_duplicates("unit")["base_rate"].quantile(.25)) / k.drop_duplicates("unit")["base_rate"].std()
    results["bounds"] = {
        "early_pct_per_sd": float(b0["pct"]), "early_ci_lo": float(b0["pct_lo"]),
        "early_ci_hi": float(b0["pct_hi"]),
        "largest_relative_decline_ruled_out_per_sd": float(-b0["pct_lo"]),
        "iqr_in_sd": float(iqr),
        "largest_decline_ruled_out_p25_to_p75": float(-np.expm1(b0["lo"] * iqr) * 100),
        "mde_80_pct_per_sd": float(np.expm1(2.8 * b0["se"]) * 100),
    }

    # (4) placebo timing: pretend the rule arrived two years earlier, pre-data only
    pk = k[k["year"] <= 2021].copy()
    pk["z_fake"] = pk["z"] * (pk["year"] >= 2020)
    f = pf.fepois("pp_orders ~ z_fake + log_hom | unit + year", data=pk,
                  offset="log_hear", vcov={"CRV1": "unit"})
    tidy(f, "z_fake").assign(spec="placebo date 2020, sample 2017-2021").to_csv(
        TAB / "t5_placebo_timing.csv", index=False)

    # (5) permutation inference: reshuffle exposure across cantons
    rng = np.random.default_rng(20211215)
    units = k.drop_duplicates("unit")[["unit", "z"]]
    real = did[(did["spec"] == "baseline") & (did["term"] == "z_early")]["b"].iloc[0]
    draws = []
    for _ in range(500):
        perm = dict(zip(units["unit"], rng.permutation(units["z"].values)))
        kp = k.assign(zp=k["unit"].map(perm))
        kp["zp_early"], kp["zp_late"] = kp["zp"] * kp["post_early"], kp["zp"] * kp["post_late"]
        fp = pf.fepois("pp_orders ~ zp_early + zp_late + log_hom | unit + year", data=kp,
                       offset="log_hear", vcov="iid")
        draws.append(float(fp.coef()["zp_early"]))
    draws = np.array(draws)
    results["permutation"] = {"estimate": float(real), "draws": 500,
                              "p_two_sided": float((np.abs(draws) >= abs(real)).mean())}


# -------------------------------------------------------- within-judge check
def judge_models(k: pd.DataFrame) -> None:
    j = pd.read_csv(PROC / "judge_year.csv")
    j = j[j["judge"] != "ND"]
    j["unit"] = j["province"] + " | " + j["canton"]
    # each judge is assigned to the canton where he or she held most hearings
    home = (j.groupby(["judge", "unit"])["hearings_held"].sum().reset_index()
            .sort_values("hearings_held").drop_duplicates("judge", keep="last")[["judge", "unit"]])
    jy = j.groupby(["judge", "year"], as_index=False)[["pp_orders", "hearings_held"]].sum()
    jy = jy.merge(home, on="judge").merge(k.drop_duplicates("unit")[["unit", "z", "province"]], on="unit")
    jy = jy[jy["year"].between(2019, LAST) & (jy["hearings_held"] >= 20)].copy()
    ever = jy.groupby("judge")["pp_orders"].sum()
    jy = jy[jy["judge"].isin(ever[ever > 0].index)]
    jy["log_hear"] = np.log(jy["hearings_held"])
    jy["z_early"] = jy["z"] * jy["year"].between(2022, 2023)
    jy["z_late"] = jy["z"] * (jy["year"] >= 2024)
    rows = []
    for name, fml in {
        "judge FE + year FE": "pp_orders ~ z_early + z_late | judge + year",
        "judge FE + province-year FE": "pp_orders ~ z_early + z_late | judge + province^year",
    }.items():
        f = pf.fepois(fml, data=jy, offset="log_hear", vcov={"CRV1": "unit"})
        t = tidy(f, "early|late")
        t["spec"], t["n"], t["judges"] = name, int(f._N), int(jy["judge"].nunique())
        rows.append(t)
    t = pd.concat(rows)
    t["pct"] = np.expm1(t["b"]) * 100
    t.to_csv(TAB / "t6_within_judge.csv", index=False)


# ---------------------------------------- prison stock: discontinuity in time
def local_jump(w: pd.DataFrame, cut: pd.Timestamp, y: str, bw: int) -> tuple[float, float]:
    """Local-linear jump in y at `cut`, using `bw` weeks on each side."""
    d = w[(w["date"] >= cut - pd.Timedelta(weeks=bw)) & (w["date"] < cut + pd.Timedelta(weeks=bw))].copy()
    d["t"] = (d["date"] - cut).dt.days / 7.0
    d["post"] = (d["t"] >= 0).astype(int)
    d["t_post"] = d["t"] * d["post"]
    f = sm.OLS(d[y], sm.add_constant(d[["t", "post", "t_post"]])).fit(
        cov_type="HAC", cov_kwds={"maxlags": 4})
    return float(f.params["post"]), float(f.bse["post"])


def stock_its() -> None:
    w = pd.read_csv(PROC / "snai_weekly.csv", parse_dates=["date"])
    # the series is redefined in January 2023 (about 3,600 people move from
    # "unsentenced" to "sentenced" in a single week), so the test stops in 2022
    pre = w[w["date"] < "2023-01-01"]
    rows = []
    for y in ("unsentenced", "sentenced", "unsentenced_share"):
        for bw in (8, 12, 20):
            b, se = local_jump(pre, RESOLUTION, y, bw)
            placebo = []
            for cut in pd.date_range("2018-01-03", "2022-06-29", freq="W-WED"):
                if abs((cut - RESOLUTION).days) < 7 * bw:
                    continue
                if pd.Timestamp("2020-03-01") - pd.Timedelta(weeks=bw) < cut < pd.Timestamp("2020-10-01") + pd.Timedelta(weeks=bw):
                    continue          # pandemic releases
                placebo.append(local_jump(pre, cut, y, bw)[0])
            placebo = np.array(placebo)
            rows.append({"outcome": y, "bandwidth_weeks": bw, "jump": b, "se": se,
                         "placebo_dates": len(placebo),
                         "placebo_p": float((np.abs(placebo) >= abs(b)).mean()),
                         "placebo_sd": float(placebo.std())})
    pd.DataFrame(rows).to_csv(TAB / "t7_stock_discontinuity.csv", index=False)

    def avg(a: str, b: str, col: str) -> float:
        return float(w[(w["date"] >= a) & (w["date"] <= b)][col].mean())
    results["stock"] = {
        "unsentenced_12w_before": avg("2021-09-22", "2021-12-14", "unsentenced"),
        "unsentenced_12w_after": avg("2021-12-15", "2022-03-08", "unsentenced"),
        "unsentenced_2022H2": avg("2022-07-01", "2022-12-31", "unsentenced"),
        "sentenced_12w_before": avg("2021-09-22", "2021-12-14", "sentenced"),
        "sentenced_2022H2": avg("2022-07-01", "2022-12-31", "sentenced"),
        "share_2021": avg("2021-01-01", "2021-12-14", "unsentenced_share"),
        "share_2022": avg("2022-01-01", "2022-12-31", "unsentenced_share"),
        "share_2026": avg("2026-01-01", "2026-12-31", "unsentenced_share"),
        "overcrowding_2026": avg("2026-07-01", "2026-12-31", "overcrowding"),
    }


# ------------------------------------------------------------- descriptives
def descriptives(k: pd.DataFrame) -> None:
    c = pd.read_csv(PROC / "canton_year.csv")
    nat = c.groupby("year")[["pp_orders", "pp_rel_any", "pp_rel_noconv", "pp_rel_subst",
                             "pp_rel_court", "conviction_committals", "hearings_held",
                             "homicides"]].sum()
    nat["pp_per_100_hearings"] = 100 * nat["pp_orders"] / nat["hearings_held"].replace(0, np.nan)
    nat["pp_per_homicide"] = nat["pp_orders"] / nat["homicides"]
    nat["subst_share"] = nat["pp_rel_subst"] / nat["pp_orders"]
    nat["noconv_share"] = nat["pp_rel_noconv"] / nat["pp_orders"]
    nat["released_share"] = nat["pp_rel_any"] / nat["pp_orders"]
    nat["subst_share_of_released"] = nat["pp_rel_subst"] / nat["pp_rel_any"]
    nat["noconv_share_of_released"] = nat["pp_rel_noconv"] / nat["pp_rel_any"]
    w = pd.read_csv(PROC / "snai_weekly.csv", parse_dates=["date"])
    ann = w.groupby(w["date"].dt.year)[["unsentenced", "total", "unsentenced_share", "overcrowding"]].mean()
    nat = nat.join(ann.add_prefix("prison_"))
    nat.to_csv(TAB / "t1_national.csv")
    g = k.groupby(["high", "year"])[["pp_orders", "hearings_held"]].sum()
    g["rate"] = 100 * g["pp_orders"] / g["hearings_held"]
    g.reset_index().to_csv(TAB / "t1b_rate_by_exposure.csv", index=False)
    results["national"] = {
        "pp_2021": int(nat.loc[2021, "pp_orders"]), "pp_2022": int(nat.loc[2022, "pp_orders"]),
        "pp_2025": int(nat.loc[2025, "pp_orders"]),
        "pct_change_21_22": float(100 * (nat.loc[2022, "pp_orders"] / nat.loc[2021, "pp_orders"] - 1)),
        "hom_2021": int(nat.loc[2021, "homicides"]), "hom_2022": int(nat.loc[2022, "homicides"]),
    }


def main() -> None:
    k = load_canton()
    descriptives(k)
    canton_models(k)
    judge_models(k)
    stock_its()
    (ROOT / "manuscript" / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    pd.set_option("display.width", 200)
    for f in sorted(TAB.glob("t*.csv")):
        print("\n==", f.name)
        print(pd.read_csv(f).round(4).to_string(index=False, max_rows=60))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
