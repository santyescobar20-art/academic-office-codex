"""Render manuscript tables (Markdown) from results.json and the CSV outputs."""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / "manuscript/tables"
R = json.loads((TAB / "results.json").read_text())


def cell(d):
    star = "***" if d["p"] < .001 else "**" if d["p"] < .01 else "*" if d["p"] < .05 else ""
    return f"{d['irr']:.2f}{star} [{d['irr_lo']:.2f}, {d['irr_hi']:.2f}]"


out = []
NAMES = {"Coastal core (May 2024)": "Coastal core (first covered May 2024)", "Expansion cohorts (Jul 2024-Jun 2026)": "Expansion cohorts (Jul 2024–Jun 2026)", "Never treated, bordering": "Never covered, bordering a covered canton", "Never treated, interior": "Never covered, interior"}
t1 = pd.read_csv(TAB / "table1_descriptives.csv")
out.append("**Table 1** Cantons, population and homicide by coverage group\n")
out.append("| Group | Cantons | Population 2024 (millions) | Rate 2019–20 | Rate 2023 | Rate 2024 | Rate 2025 | Rate 2026 (Jan–Sep) | Canton-months under decree since May 2024 | Firearm share |")
out.append("|---|---|---|---|---|---|---|---|---|---|")
tot = sum(t1[c].sum() for c in t1.columns if c.startswith("hom_"))
for _, r in t1.iterrows():
    h = sum(r[c] for c in t1.columns if c.startswith("hom_"))
    out.append(f"| {NAMES[r['group']]} | {int(r['cantons'])} | {r['population_2024']/1e6:.2f} | {r['rate_2019-2020']:.1f} | {r['rate_2023']:.1f} | "
               f"{r['rate_2024']:.1f} | {r['rate_2025']:.1f} | {r['rate_2026 Jan-Sep']:.1f} | {100*r['share_months_under_decree']:.0f}% | {100*r['firearm_share']:.0f}% |")
out.append("\nRates are homicides per 100,000 inhabitants per year. Source: authors' calculations from Ministry of the Interior records and INEC projections.\n")

out.append("**Table 2** Static fixed-effects Poisson models, full canton-month panel\n")
out.append("| Model | Under decree: IRR [95% CI] | Bordering a covered canton: IRR [95% CI] | N |")
out.append("|---|---|---|---|")
for k, v in R["static"].items():
    out.append(f"| {k} | {cell(v['D'])} | {cell(v['Nb'])} | {v['D']['n']:,} |")
out.append("\nStandard errors clustered by province (24 clusters). * p < .05, ** p < .01, *** p < .001.\n")

d, s = R["direct"], R["spill"]
out.append("**Table 3** Stacked difference-in-differences estimates\n")
out.append("| Specification | Covered cantons: IRR [95% CI] | Bordering cantons: IRR [95% CI] |")
out.append("|---|---|---|")
rows = [("Baseline (18 pre-entry months as comparison)", d["pooled"], s["pooled"]),
        ("Standard errors clustered by canton", d["pooled_canton_cluster"], s["pooled_canton_cluster"]),
        ("Region-by-month fixed effects", d["pooled_region_month"], s["pooled_region_month"]),
        ("Excluding months −3 to −1", d["donut3"], s["donut3"]),
        ("Excluding months −6 to −1", d["donut6"], None),
        ("Linear pre-entry trend extrapolated", d["trend_adjusted"], None),
        ("Firearm homicides only", d["pooled_firearm"], s["pooled_firearm"]),
        ("Non-firearm homicides", d["pooled_nonfirearm"], None),
        ("Femicide and family violence", d["pooled_family"], None),
        ("Controls include bordering cantons", d["pooled_all_never_controls"], None),
        ("Placebo entry 12 months early", d["placebo_minus12"], None),
        ("Excluding exposure cohort of May 2024", None, s["pooled_excl_core_onset"])]
for name, a, b in rows:
    out.append(f"| {name} | {cell(a) if a else '–'} | {cell(b) if b else '–'} |")
out.append(f"| Randomisation-inference p value (baseline) | {d['randomisation']['p']:.2f} | {s['randomisation']['p']:.2f} |")
out.append(f"| Joint test of pre-entry coefficients, p value | {d['pretrend']['p']:.4f} | {s['pretrend']['p']:.2f} |")
out.append(f"| Treated cantons / control cantons | {d['units']['cantons']} / {d['units']['controls']} | {s['units']['cantons']} / {s['units']['controls']} |")
out.append("\nIRR, incidence rate ratio. Standard errors clustered by province unless noted. * p < .05, ** p < .01, *** p < .001.\n")

out.append("**Table 4** Direct estimates by entry cohort\n")
out.append("| First month covered | Territory | Cantons | Homicides, 18 months before | Homicides, up to 9 months after | IRR [95% CI] |")
out.append("|---|---|---|---|---|---|")
terr = {"2024-07": "Orellana; Camilo Ponce Enríquez", "2024-10": "Quito", "2025-01": "Sucumbíos; La Troncal",
        "2025-09": "La Maná; Las Naves; Echeandía", "2026-01": "Esmeraldas; Santo Domingo; rest of Pichincha",
        "2026-06": "Rest of Azuay"}
for r in d["by_cohort"]:
    out.append(f"| {r['cohort']} | {terr[r['cohort']]} | {r['cantons']} | {r['hom_pre']} | {r['hom_post']} | {cell(r)} |")
(TAB / "tables.md").write_text("\n".join(out) + "\n")
print("\n".join(out))
