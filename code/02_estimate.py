"""Estimation: direct effects, spillovers, exits, robustness.

Reads  data/processed/panel.csv, cantons.csv
Writes manuscript/tables/*.csv and results.json (every number quoted in the text).
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pyfixest as pf
from scipy import stats

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / "manuscript" / "tables"
TAB.mkdir(parents=True, exist_ok=True)
RNG = np.random.default_rng(20261111)

CORE = "2024-05"                      # coastal core: entered straight after the nationwide decree
PRE, POST_DIRECT, POST_SPILL = 18, 9, 18   # months before / after onset kept in each stack
REGION = {**{k: "coast" for k in (7, 8, 9, 12, 13, 23, 24)},
          **{k: "amazon" for k in (14, 15, 16, 19, 21, 22)}, 20: "galapagos"}


def load():
    p = pd.read_csv(ROOT / "data/processed/panel.csv", dtype={"g": str, "g_nb": str})
    p[["g", "g_nb"]] = p[["g", "g_nb"]].fillna("")
    p["region"] = p["prov_code"].map(REGION).fillna("sierra")
    p["t"] = pd.PeriodIndex(p["ym"], freq="M").astype("int64")
    p["Nb"] = ((p["D"] == 0) & (p["nb_any"] == 1)).astype(int)
    p["reg_ym"] = p["region"] + "_" + p["ym"]
    return p


def mi(ym: str) -> int:
    return pd.Period(ym, freq="M").ordinal


def tidy(m, term):
    r = m.tidy().loc[term]
    b, se = float(r["Estimate"]), float(r["Std. Error"])
    return {"b": b, "se": se, "p": float(r["Pr(>|t|)"]), "lo": b - 1.96 * se, "hi": b + 1.96 * se,
            "irr": float(np.exp(b)), "irr_lo": float(np.exp(b - 1.96 * se)),
            "irr_hi": float(np.exp(b + 1.96 * se)), "n": int(m._N)}


def pois(formula, data, cluster="prov_code"):
    return pf.fepois(formula, data=data, vcov={"CRV1": cluster})


def wald(m, terms):
    """Joint Wald test that the listed coefficients are zero (cluster-robust vcov)."""
    names = list(m._coefnames)
    idx = [names.index(t) for t in terms]
    b = np.asarray(m._beta_hat)[idx]
    V = np.asarray(m._vcov)[np.ix_(idx, idx)]
    w = float(b @ np.linalg.solve(V, b))
    return {"chi2": w, "df": len(idx), "p": float(stats.chi2.sf(w, len(idx)))}


# --------------------------------------------------------------------------- stacks
def stack_direct(p, cohorts, clean_controls=True, post=POST_DIRECT):
    """One sub-panel per entry cohort: cohort cantons plus never-treated controls."""
    out = []
    never = p["g"] == ""
    for g in cohorts:
        g0 = mi(g)
        w = p[(p["t"] >= g0 - PRE) & (p["t"] < g0 + post)]
        ctrl = never & ((p["g_nb"] == "") if clean_controls else True)
        s = w[(w["g"] == g) | ctrl.reindex(w.index)].copy()
        s["stack"] = g
        s["treat"] = (s["g"] == g).astype(int)
        s["rel"] = s["t"] - g0
        out.append(s)
    return finish(pd.concat(out, ignore_index=True))


def stack_spill(p, post=POST_SPILL):
    """Exposed cantons: not under a decree themselves, bordering a canton that is."""
    out = []
    interior = (p["g"] == "") & (p["g_nb"] == "")
    for e in sorted(x for x in p["g_nb"].unique() if x):
        e0 = mi(e)
        exposed = (p["g_nb"] == e) & ((p["g"] == "") | (p["g"] > e))
        w = p[(p["t"] >= e0 - PRE) & (p["t"] < e0 + post)]
        s = w[exposed.reindex(w.index) | interior.reindex(w.index)].copy()
        own = s["g"].map(lambda x: mi(x) if x else 10 ** 9)
        s = s[s["t"] < own]                       # censor once the canton is itself treated
        s["stack"] = e
        s["treat"] = exposed.reindex(s.index).astype(int)
        s["rel"] = s["t"] - e0
        out.append(s)
    return finish(pd.concat(out, ignore_index=True))


def finish(s):
    s["post"] = (s["rel"] >= 0).astype(int)
    s["tp"] = s["treat"] * s["post"]
    s["q"] = np.floor(s["rel"] / 3).astype(int)          # quarters relative to onset
    s["cs"] = s["code"].astype(str) + "_" + s["stack"]
    s["ts"] = s["ym"] + "_" + s["stack"]
    s["rts"] = s["region"] + "_" + s["ts"]
    for q in sorted(s["q"].unique()):
        if q != -1:
            s[f"ev_{'p' if q >= 0 else 'm'}{abs(q)}"] = ((s["q"] == q) & (s["treat"] == 1)).astype(int)
    return s


def event_study(s, y="hom", fe="cs + ts", cluster="prov_code"):
    def qn(c):
        return int(c[4:]) * (-1 if c[3] == "m" else 1)
    terms = sorted([c for c in s.columns if c.startswith("ev_") and s[c].any()], key=qn)
    m = pois(f"{y} ~ {' + '.join(terms)} | {fe}", s, cluster)
    rows = [{"q": qn(t), **tidy(m, t)} for t in terms]
    rows.append({"q": -1, "b": 0.0, "se": 0.0, "p": np.nan, "lo": 0.0, "hi": 0.0, "irr": 1.0,
                 "irr_lo": 1.0, "irr_hi": 1.0, "n": int(m._N)})
    es = pd.DataFrame(rows).sort_values("q")
    pre = [t for t in terms if t[3] == "m"]
    return es, wald(m, pre)


def pooled(s, y="hom", fe="cs + ts", cluster="prov_code"):
    return tidy(pois(f"{y} ~ tp | {fe}", s, cluster), "tp")


def units(s):
    t = s[s["treat"] == 1]
    return {"cantons": int(t["code"].nunique()), "controls": int(s.loc[s["treat"] == 0, "code"].nunique()),
            "hom_pre": int(t.loc[t["post"] == 0, "hom"].sum()), "hom_post": int(t.loc[t["post"] == 1, "hom"].sum())}


def randomisation(s, y="hom", reps=499):
    """Permutation inference: reassign treated status across cantons within each stack."""
    obs = pooled(s, y)["b"]
    draws = []
    base = s.drop_duplicates(["stack", "code"])[["stack", "code", "treat"]]
    for _ in range(reps):
        perm = base.copy()
        perm["treat"] = perm.groupby("stack")["treat"].transform(lambda v: RNG.permutation(v.values))
        d = s.drop(columns=["treat", "tp"]).merge(perm, on=["stack", "code"])
        d["tp"] = d["treat"] * d["post"]
        try:
            draws.append(float(pf.fepois(f"{y} ~ tp | cs + ts", data=d, vcov="iid").coef()["tp"]))
        except Exception:
            continue
    draws = np.array(draws)
    return {"b": obs, "p": float((np.sum(np.abs(draws) >= abs(obs)) + 1) / (len(draws) + 1)),
            "reps": int(len(draws)), "q025": float(np.quantile(draws, .025)),
            "q975": float(np.quantile(draws, .975))}


# --------------------------------------------------------------------------- main
def main():
    p = load()
    R: dict = {}
    cohorts = sorted(x for x in p["g"].unique() if x)
    expansion = [c for c in cohorts if c != CORE]

    # ---- Table 1: descriptives by group -------------------------------------------------
    grp = np.where(p["g"] == CORE, "Coastal core (May 2024)",
          np.where(p["g"] != "", "Expansion cohorts (Jul 2024-Jun 2026)",
          np.where(p["g_nb"] != "", "Never treated, bordering", "Never treated, interior")))
    p["group"] = grp
    rows = []
    for name, d in p.groupby("group"):
        r = {"group": name, "cantons": d["code"].nunique(),
             "population_2024": d.loc[d["ym"] == "2024-06", "pop"].sum()}
        for lab, a, b in (("2019-2020", "2019-01", "2020-12"), ("2023", "2023-01", "2023-12"),
                          ("2024", "2024-01", "2024-12"), ("2025", "2025-01", "2025-12"),
                          ("2026 Jan-Sep", "2026-01", "2026-09")):
            w = d[(d["ym"] >= a) & (d["ym"] <= b)]
            py = w["pop"].sum() / 12
            r[f"hom_{lab}"] = int(w["hom"].sum())
            r[f"rate_{lab}"] = w["hom"].sum() / py * 1e5
        post = d[d["ym"] >= "2024-05"]
        r["share_months_under_decree"] = post["D"].mean()
        r["firearm_share"] = d["hom_firearm"].sum() / max(d["hom"].sum(), 1)
        rows.append(r)
    t1 = pd.DataFrame(rows)
    t1.to_csv(TAB / "table1_descriptives.csv", index=False)
    R["sample"] = {"cantons": int(p["code"].nunique()), "months": int(p["ym"].nunique()),
                   "obs": int(len(p)), "homicides": int(p["hom"].sum()),
                   "first_month": p["ym"].min(), "last_month": p["ym"].max(),
                   "cohort_sizes": p.drop_duplicates("code").groupby("g").size().to_dict(),
                   "core_share_homicides_2024_26": float(
                       p[(p["g"] == CORE) & (p["ym"] >= "2024-01")]["hom"].sum()
                       / p[p["ym"] >= "2024-01"]["hom"].sum())}

    # ---- Table 2: static models on the full panel ---------------------------------------
    specs = [
        ("(1) Canton and month FE", "hom ~ D + Nb | code + ym", p),
        ("(2) Region-by-month FE", "hom ~ D + Nb | code + reg_ym", p),
        ("(3) Excluding coastal core", "hom ~ D + Nb | code + reg_ym", p[p["g"] != CORE]),
        ("(4) Share of month under decree", "hom ~ soe_share + Nb | code + reg_ym", p[p["g"] != CORE]),
        ("(5) Excluding Quito and Guayaquil", "hom ~ D + Nb | code + reg_ym",
         p[(p["g"] != CORE) & ~p["code"].isin([1701, 901])]),
    ]
    rows = []
    for name, f, d in specs:
        m = pois(f, d)
        dterm = "soe_share" if "soe_share" in f else "D"
        mc = pois(f, d, "code")
        rows.append({"model": name, **{f"D_{k}": v for k, v in tidy(m, dterm).items()},
                     "D_se_canton": tidy(mc, dterm)["se"],
                     **{f"Nb_{k}": v for k, v in tidy(m, "Nb").items()},
                     "Nb_se_canton": tidy(mc, "Nb")["se"]})
    t2 = pd.DataFrame(rows)
    t2.to_csv(TAB / "table2_static.csv", index=False)
    R["static"] = {r["model"]: {"D": {k[2:]: r[k] for k in r if k.startswith("D_")},
                                "Nb": {k[3:]: r[k] for k in r if k.startswith("Nb_")}} for r in rows}

    # ---- Direct effect: stacked event study on expansion cohorts ------------------------
    sd = stack_direct(p, expansion)
    es_d, pre_d = event_study(sd)
    es_d.to_csv(TAB / "event_direct.csv", index=False)
    R["direct"] = {"pooled": pooled(sd), "pretrend": pre_d, "units": units(sd),
                   "pooled_canton_cluster": pooled(sd, cluster="code"),
                   "pooled_region_month": pooled(sd, fe="cs + rts"),
                   "pooled_all_never_controls": pooled(stack_direct(p, expansion, clean_controls=False)),
                   "pooled_firearm": pooled(sd, "hom_firearm"),
                   "pooled_nonfirearm": pooled(sd, "hom_other"),
                   "pooled_public": pooled(sd, "hom_public"),
                   "pooled_family": pooled(sd, "hom_family"),
                   "first6": pooled(sd[sd["rel"] < 6]),
                   "treated_post_share_under_decree": float(
                       sd[(sd["treat"] == 1) & (sd["post"] == 1)]["D"].mean())}
    by = []
    for g in expansion:
        s1 = sd[sd["stack"] == g]
        try:
            by.append({"cohort": g, **units(s1), **pooled(s1)})
        except Exception as e:                                   # pragma: no cover
            by.append({"cohort": g, **units(s1), "error": str(e)})
    pd.DataFrame(by).to_csv(TAB / "direct_by_cohort.csv", index=False)
    R["direct"]["by_cohort"] = by
    R["direct"]["randomisation"] = randomisation(sd)

    # Placebo in time: pretend each cohort entered 12 months earlier, using pre-entry data only.
    pl = p.copy()
    pl["g"] = pl["g"].map(lambda x: str(pd.Period(x, "M") - 12) if x and x != CORE else x)
    spl = stack_direct(pl, [str(pd.Period(g, "M") - 12) for g in expansion], post=9)
    R["direct"]["placebo_minus12"] = pooled(spl)

    # Decrees follow surges. Three readings of the same data:
    #  (a) donut: drop the months just before entry from the comparison period;
    #  (b) trend-adjusted: let the pre-entry divergence continue linearly;
    #  (c) raw ratios of treated to control counts by phase.
    R["direct"]["donut3"] = pooled(sd[(sd["rel"] >= 0) | (sd["rel"] < -3)])
    R["direct"]["donut6"] = pooled(sd[(sd["rel"] >= 0) | (sd["rel"] < -6)])
    sd["trend"] = sd["treat"] * sd["rel"]
    mt = pois("hom ~ tp + trend | cs + ts", sd)
    R["direct"]["trend_adjusted"] = tidy(mt, "tp")
    R["direct"]["trend_slope"] = tidy(mt, "trend")
    a = sd[sd["treat"] == 1].groupby("rel")["hom"].sum()
    b = sd[sd["treat"] == 0].groupby("rel")["hom"].sum()
    pd.DataFrame({"treated": a, "control": b}).to_csv(TAB / "direct_counts_by_month.csv")

    def phase(y, c, lo, hi):
        return (y.loc[lo:hi].mean() / y.loc[-PRE:-4].mean()) / (c.loc[lo:hi].mean() / c.loc[-PRE:-4].mean())
    R["direct"]["surge"] = {"baseline_monthly": float(a.loc[-PRE:-4].mean()),
                            "peak_monthly": float(a.loc[-3:-1].mean()),
                            "post_monthly": float(a.loc[0:POST_DIRECT - 1].mean()),
                            "peak_ratio": float(phase(a, b, -3, -1)),
                            "post_ratio": float(phase(a, b, 0, POST_DIRECT - 1))}

    # Benchmark: comparable province-level surges before 2024, when no targeted decree of
    # the Noboa period existed. How much of a surge was still there nine months later?
    pm = p.groupby(["prov_code", "t"])["hom"].sum().unstack(0).sort_index()
    ctrl = p[(p["g"] == "") & (p["g_nb"] == "")].groupby("t")["hom"].sum()
    cut, ev = mi("2024-01"), []
    for pc in pm.columns:
        y, last = pm[pc], -10 ** 6
        for m in y.index:
            if m - PRE < y.index.min() or m + POST_DIRECT - 1 >= cut:
                continue
            base = y.loc[m - PRE:m - 4].mean()
            if base < 4 or m - last < 12:
                continue
            peak = (y.loc[m - 3:m - 1].mean() / base) / (ctrl.loc[m - 3:m - 1].mean() / ctrl.loc[m - PRE:m - 4].mean())
            if peak >= 1.4:
                post = (y.loc[m:m + POST_DIRECT - 1].mean() / base) / (
                    ctrl.loc[m:m + POST_DIRECT - 1].mean() / ctrl.loc[m - PRE:m - 4].mean())
                ev.append({"prov_code": int(pc), "onset": str(pd.Period(ordinal=m, freq="M")),
                           "baseline_monthly": base, "peak_ratio": peak, "post_ratio": post})
                last = m
    bench = pd.DataFrame(ev)
    bench.to_csv(TAB / "surge_benchmark.csv", index=False)
    R["direct"]["surge_benchmark"] = {
        "episodes": int(len(bench)), "median_peak_ratio": float(bench["peak_ratio"].median()),
        "median_post_ratio": float(bench["post_ratio"].median()),
        "share_reverting_below_1_2": float((bench["post_ratio"] < 1.2).mean()),
        "min_post_ratio": float(bench["post_ratio"].min())}

    # ---- Spillover: exposed cantons vs interior never-treated ---------------------------
    ss = stack_spill(p)
    es_s, pre_s = event_study(ss)
    es_s.to_csv(TAB / "event_spillover.csv", index=False)
    late = ss[ss["stack"] != CORE]
    R["spill"] = {"pooled": pooled(ss), "pretrend": pre_s, "units": units(ss),
                  "pooled_canton_cluster": pooled(ss, cluster="code"),
                  "pooled_region_month": pooled(ss, fe="cs + rts"),
                  "pooled_firearm": pooled(ss, "hom_firearm"),
                  "pooled_first9": pooled(ss[ss["rel"] < 9]),
                  "pooled_excl_core_onset": pooled(late), "units_excl_core_onset": units(late),
                  "donut3": pooled(ss[(ss["rel"] >= 0) | (ss["rel"] < -3)]),
                  "dose": tidy(pois("hom ~ dose | cs + ts", ss.assign(dose=ss["tp"] * ss["nb_share"])), "dose"),
                  "randomisation": randomisation(ss)}
    # Second-order ring: never-treated cantons two steps away from a treated canton.
    c = pd.read_csv(ROOT / "data/processed/cantons.csv", dtype={"g": str, "g_nb": str}).fillna("")
    nb = {int(r.code): [int(x) for x in str(r.neighbours).split(";") if x and x != "nan"]
          for r in c.itertuples()}
    ever = set(c.loc[c["g"] != "", "code"])
    ring1 = set(c.loc[(c["g"] == "") & (c["g_nb"] != ""), "code"])
    ring2 = {k for k in nb if k not in ever and k not in ring1 and any(n in ring1 for n in nb[k])}
    R["rings"] = {"ring1": len(ring1), "ring2": len(ring2),
                  "interior_beyond_ring2": int(len(set(c["code"]) - ever - ring1 - ring2))}
    p["ring2_post"] = (p["code"].isin(ring2) & (p["ym"] >= CORE)).astype(int)
    p["ring1_post"] = (p["code"].isin(ring1) & (p["ym"] >= CORE)).astype(int)
    nv = p[(p["g"] == "") & (p["ym"] >= "2022-11") & (p["ym"] <= "2025-10")]
    m = pois("hom ~ ring1_post + ring2_post | code + ym", nv)
    R["rings"]["ring1"] = tidy(m, "ring1_post")
    R["rings"]["ring2_est"] = tidy(m, "ring2_post")

    # ---- Exits: cantons dropped from the regime in mid-2025 vs coastal cantons kept in --
    stay = p["prov_code"].isin([7, 9, 12, 13])               # El Oro, Guayas, Los Rios, Manabi
    leave = p["prov_code"].isin([21, 22, 24]) | p["code"].isin([1701, 115])
    ex = p[(stay | leave) & (p["ym"] >= "2024-08") & (p["ym"] <= "2025-12") & (p["ym"] != "2025-07")].copy()
    ex["leaver"] = leave.reindex(ex.index).astype(int)
    ex["after"] = (ex["ym"] >= "2025-08").astype(int)
    ex["la"] = ex["leaver"] * ex["after"]
    R["exit"] = {"pooled": tidy(pois("hom ~ la | code + ym", ex), "la"),
                 "canton_cluster": tidy(pois("hom ~ la | code + ym", ex, "code"), "la"),
                 "leavers": int(ex.loc[ex["leaver"] == 1, "code"].nunique()),
                 "stayers": int(ex.loc[ex["leaver"] == 0, "code"].nunique()),
                 "leaver_hom_before": int(ex[(ex["leaver"] == 1) & (ex["after"] == 0)]["hom"].sum()),
                 "leaver_hom_after": int(ex[(ex["leaver"] == 1) & (ex["after"] == 1)]["hom"].sum()),
                 "leaver_after_share_under_decree": float(
                     ex[(ex["leaver"] == 1) & (ex["after"] == 1)]["D"].mean())}

    # ---- Weighted displacement quotient and homicide accounting -------------------------
    def counterfactual(s, est):
        post = s[(s["treat"] == 1) & (s["post"] == 1)]
        obs = float(post["hom"].sum())
        cf = obs / np.exp(est["b"])
        return {"observed": obs, "expected_without": cf, "difference": obs - cf,
                "difference_lo": obs - obs / np.exp(est["lo"]), "difference_hi": obs - obs / np.exp(est["hi"])}
    R["accounting"] = {"direct": counterfactual(sd, R["direct"]["pooled"]),
                       "spill": counterfactual(ss[ss["rel"] < POST_DIRECT], R["spill"]["pooled_first9"])}
    a = R["accounting"]
    R["accounting"]["wdq"] = (a["spill"]["difference"] / a["direct"]["difference"]
                              if abs(a["direct"]["difference"]) > 1e-9 else None)

    # ---- Minimum detectable effects (80% power, two-sided 5%) --------------------------
    for k in ("direct", "spill"):
        se = R[k]["pooled"]["se"]
        R[k]["mde_log"] = 2.8 * se
        R[k]["mde_pct_reduction"] = float(1 - np.exp(-2.8 * se))
        R[k]["mde_pct_increase"] = float(np.exp(2.8 * se) - 1)

    (TAB / "results.json").write_text(json.dumps(R, indent=1, default=float))
    print(json.dumps({k: R[k] for k in ("sample", "direct", "spill", "exit", "rings", "accounting")},
                     indent=1, default=float)[:9000])


if __name__ == "__main__":
    main()
