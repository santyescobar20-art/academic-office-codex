"""Insert the tables produced by 03_estimate.py into the manuscript and export it.

Reads manuscript/manuscript_src.md, writes manuscript/manuscript.md and, when
pandoc is available, manuscript/manuscript.docx.
Run from the paper folder:  python code/05_build_manuscript.py
"""
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
TAB = MAN / "tables"


def md(df: pd.DataFrame, caption: str, note: str = "") -> str:
    head = "| " + " | ".join(df.columns) + " |"
    sep = "|" + "|".join([":--"] + ["--:"] * (len(df.columns) - 1)) + "|"
    body = ["| " + " | ".join(str(v) for v in row) + " |" for row in df.values]
    out = [f"**{caption}**", "", head, sep, *body, ""]
    if note:
        out += [f"*Note.* {note}", ""]
    return "\n".join(out)


def stars(p: float) -> str:
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""


def est(b: float, se: float, p: float) -> str:
    return f"{b:.3f}{stars(p)} ({se:.3f})"


def table1() -> str:
    t = pd.read_csv(TAB / "t1_national.csv")
    d = pd.DataFrame({
        "Year": t["year"].astype(str).replace({"2026": "2026ᵃ"}),
        "Detention orders": t["pp_orders"].map("{:,}".format),
        "Hearings held": t["hearings_held"].map(lambda v: "–" if v == 0 else f"{v:,}"),
        "Orders per 100 hearings": t["pp_per_100_hearings"].map(lambda v: "–" if np.isnan(v) else f"{v:.1f}"),
        "Homicides": t["homicides"].map("{:,}".format),
        "Later substituted (%)": (100 * t["subst_share"]).map("{:.1f}".format),
        "Unsentenced prisoners": t["prison_unsentenced"].map(lambda v: "–" if np.isnan(v) else f"{v:,.0f}"),
        "Overcrowding (%)": (100 * t["prison_overcrowding"]).map(lambda v: "–" if np.isnan(v) else f"{v:.1f}"),
    })
    return md(d, "Table 1. Pretrial detention, caseload, violence and prison population, 2016-2026",
              "Orders and hearings are from the Judicial Council (criminal, traffic and domestic-violence "
              "matters); hearings are available from 2017. Homicides refer to cantons with a criminal court. "
              "\"Later substituted\" is the share of each year's detention orders that ended with a "
              "non-custodial measure; recent cohorts are right-censored. Prison figures are annual means of "
              "weekly SNAI counts; the unsentenced series is redefined in January 2023. "
              "ᵃ January to September.")


def table2() -> str:
    t = pd.read_csv(TAB / "t2_year_effects.csv").sort_values("year")
    d = pd.DataFrame({
        "Year": t["year"],
        "Coefficient (SE)": [est(b, s, p) for b, s, p in zip(t["b"], t["se"], t["p"])],
        "Change vs. 2021 (%)": t["pct"].map("{:+.1f}".format),
        "95% CI (%)": [f"[{100 * np.expm1(lo):+.1f}, {100 * np.expm1(hi):+.1f}]" for lo, hi in zip(t["lo"], t["hi"])],
    })
    return md(d, "Table 2. Detention rate by year relative to 2021",
              "Poisson regression of detention orders on year indicators with canton fixed effects, "
              "log(1 + homicides) and log hearings held as offset; 129 cantons, 1,290 observations. "
              "Standard errors clustered by canton. * p < 0.10, ** p < 0.05, *** p < 0.01.")


def table3() -> str:
    t = pd.read_csv(TAB / "t3_event_study.csv")
    t = t[t["outcome"] == "pp_orders"]
    z = t[t["exposure"] == "z"].set_index("year")
    h = t[t["exposure"] == "high"].set_index("year")
    d = pd.DataFrame({
        "Year": z.index,
        "Continuous exposure (per SD)": [est(*r) for r in z[["b", "se", "p"]].values],
        "Above-median exposure": [est(*h.loc[y, ["b", "se", "p"]].values) for y in z.index],
    })
    extra = pd.DataFrame({"Year": ["Joint test, 2019-2020 (p)"],
                          "Continuous exposure (per SD)": [f"{z['pretrend_p'].iloc[0]:.3f}"],
                          "Above-median exposure": [f"{h['pretrend_p'].iloc[0]:.3f}"]})
    return md(pd.concat([d, extra]), "Table 3. Event-study estimates by pre-resolution reliance on detention",
              "Poisson regressions with canton and year fixed effects, log(1 + homicides) and log hearings "
              "as offset. Exposure is measured in 2017-2018; 2021 is the reference year. Standard errors "
              "clustered by canton. * p < 0.10, ** p < 0.05, *** p < 0.01.")


def table4() -> str:
    t = pd.read_csv(TAB / "t4_did.csv")
    rows = []
    for spec, g in t.groupby("spec", sort=False):
        e = g[g["term"].str.contains("early")].iloc[0]
        l = g[g["term"].str.contains("late")].iloc[0]
        rows.append([spec[0].upper() + spec[1:], est(e["b"], e["se"], e["p"]),
                     f"[{e['pct_lo']:+.1f}, {e['pct_hi']:+.1f}]", est(l["b"], l["se"], l["p"]), int(e["n"])])
    d = pd.DataFrame(rows, columns=["Specification", "Exposure × 2022-2023", "95% CI (%)",
                                    "Exposure × 2024-2026", "N"])
    return md(d, "Table 4. Pooled difference-in-differences estimates",
              "Poisson regressions of detention orders (committals after conviction in the placebo row) with "
              "canton and year fixed effects unless stated, log hearings as offset. Exposure is standardised "
              "pre-resolution reliance, or an above-median indicator in the binary row. Standard errors "
              "clustered by canton unless stated. * p < 0.10, ** p < 0.05, *** p < 0.01.")


def table5() -> str:
    t = pd.read_csv(TAB / "t6_within_judge.csv")
    rows = []
    for spec, g in t.groupby("spec", sort=False):
        e, l = g.iloc[0], g.iloc[1]
        rows.append([spec[0].upper() + spec[1:], est(e["b"], e["se"], e["p"]), est(l["b"], l["se"], l["p"]),
                     f"{int(e['judges']):,}", f"{int(e['n']):,}"])
    d = pd.DataFrame(rows, columns=["Specification", "Exposure × 2022-2023", "Exposure × 2024-2026",
                                    "Judges", "Judge-years"])
    return md(d, "Table 5. Within-judge estimates, 2019-2026",
              "Poisson regressions of detention orders by judge-year with log hearings held as offset. "
              "Each judge carries the exposure of the canton where he or she held most hearings. Standard "
              "errors clustered by canton. * p < 0.10, ** p < 0.05, *** p < 0.01.")


def table6() -> str:
    t = pd.read_csv(TAB / "t7_stock_discontinuity.csv")
    lab = {"unsentenced": "Unsentenced prisoners", "sentenced": "Sentenced prisoners",
           "unsentenced_share": "Unsentenced share"}
    fmt = lambda v, o: f"{v:.4f}" if o == "unsentenced_share" else f"{v:,.0f}"
    d = pd.DataFrame({
        "Outcome": t["outcome"].map(lab),
        "Bandwidth (weeks)": t["bandwidth_weeks"],
        "Jump at 15 Dec 2021": [fmt(v, o) for v, o in zip(t["jump"], t["outcome"])],
        "HAC SE": [fmt(v, o) for v, o in zip(t["se"], t["outcome"])],
        "SD of placebo jumps": [fmt(v, o) for v, o in zip(t["placebo_sd"], t["outcome"])],
        "Placebo dates": t["placebo_dates"],
        "Share of placebos at least as large": t["placebo_p"].map("{:.2f}".format),
    })
    return md(d, "Table 6. Discontinuity in the weekly prison population at the resolution date",
              "Local linear regressions in time with separate slopes on each side of the cut-off. Placebo "
              "cut-offs are all weeks from January 2018 to June 2022 whose window overlaps neither the "
              "resolution nor the pandemic releases of 2020.")


def main() -> None:
    text = (MAN / "manuscript_src.md").read_text()
    for key, fn in {"{{TABLE1}}": table1, "{{TABLE2}}": table2, "{{TABLE3}}": table3,
                    "{{TABLE4}}": table4, "{{TABLE5}}": table5, "{{TABLE6}}": table6}.items():
        assert key in text, key
        text = text.replace(key, fn())
    (MAN / "manuscript.md").write_text(text)
    body = text.split("# References")[0]
    words = len([w for w in body.split() if any(ch.isalpha() for ch in w)])
    print("words before references (tables included):", words)
    if shutil.which("pandoc"):
        subprocess.run(["pandoc", "manuscript.md", "-o", "manuscript.docx", "--from",
                        "markdown+tex_math_dollars+pipe_tables", "--resource-path", "."],
                       cwd=MAN, check=True)
        print("wrote manuscript.docx")


if __name__ == "__main__":
    main()
