"""Figures for the manuscript. Reads data/processed and manuscript/tables."""
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
TAB, FIG = ROOT / "manuscript/tables", ROOT / "manuscript/figures"
FIG.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "Liberation Sans", "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 150, "savefig.dpi": 600})
C = {"core": "#8c2d04", "exp": "#f16913", "bord": "#6baed6", "int": "#d9d9d9"}

p = pd.read_csv(ROOT / "data/processed/panel.csv", dtype={"g": str, "g_nb": str})
p[["g", "g_nb"]] = p[["g", "g_nb"]].fillna("")
p["grp"] = np.where(p["g"] == "2024-05", "core", np.where(p["g"] != "", "exp",
                    np.where(p["g_nb"] != "", "bord", "int")))
LAB = {"core": "Coastal core (first covered May 2024)", "exp": "Expansion cohorts (Jul 2024–Jun 2026)",
       "bord": "Never covered, bordering a covered canton", "int": "Never covered, interior"}

# ---- Figure 1: map ----------------------------------------------------------------------
import importlib.util
spec = importlib.util.spec_from_file_location("b", ROOT / "code/01_build_panel.py")
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
hom = b.load_homicides(); pop = b.load_population(hom)
g = gpd.read_file(ROOT / "data/raw/geo/ecu_adm2_simplified.geojson")
g["geometry"] = g.geometry.buffer(0)
pts = hom[(hom["coordenada_x"].abs() > 1) & hom["coordenada_y"].notna()]
pts = gpd.GeoDataFrame(pts[["code"]], geometry=gpd.points_from_xy(pts["coordenada_x"], pts["coordenada_y"]), crs=4326)
j = gpd.sjoin(pts, g[["shapeID", "geometry"]], predicate="within")
vote = j.groupby(["shapeID", "code"]).size().rename("n").reset_index().sort_values("n", ascending=False).drop_duplicates("shapeID")
g = g.merge(vote[["shapeID", "code"]], on="shapeID", how="left")
g["k"] = g["shapeName"].map(b.key); pop["k"] = pop["canton"].map(b.key)
u = pop.groupby("k")["code"].agg(["first", "size"]); g["code"] = g["k"].map(u.loc[u["size"] == 1, "first"]).fillna(g["code"])
g = g.merge(p.drop_duplicates("code")[["code", "grp"]], on="code", how="left")
g = g[g.geometry.representative_point().x > -82.5]            # mainland only
fig, ax = plt.subplots(figsize=(5.2, 6))
for k, hatch in (("int", ""), ("bord", "///"), ("exp", ""), ("core", "")):
    g[g["grp"] == k].plot(ax=ax, color=C[k], edgecolor="white", linewidth=0.25, hatch=hatch)
ax.legend(handles=[Patch(facecolor=C[k], hatch="///" if k == "bord" else "", edgecolor="white", label=LAB[k])
                   for k in ("core", "exp", "bord", "int")], loc="lower left", frameon=False, fontsize=7.5,
          bbox_to_anchor=(0, -0.16))
ax.set_axis_off()
fig.savefig(FIG / "fig1_map.png", bbox_inches="tight"); plt.close(fig)

# ---- Figure 2: homicide rates by group --------------------------------------------------
m = p.groupby(["grp", "ym"]).agg(h=("hom", "sum"), pop=("pop", "sum")).reset_index()
m["rate"] = m["h"] / m["pop"] * 1.2e6
m["d"] = pd.to_datetime(m["ym"])
fig, axs = plt.subplots(2, 1, figsize=(6.5, 5.6), sharex=True, gridspec_kw={"height_ratios": [1.25, 1]})
for ax, keys in zip(axs, (("core", "exp"), ("bord", "int"))):
    for k in keys:
        s = m[m["grp"] == k].set_index("d")["rate"].rolling(3, center=True).mean()
        ax.plot(s.index, s.values, color=C[k] if k != "int" else "#636363", lw=1.6,
                ls="--" if k in ("exp", "int") else "-", label=LAB[k])
    ax.axvspan(pd.Timestamp("2024-01-08"), pd.Timestamp("2024-04-07"), color="#bdbdbd", alpha=0.35, lw=0)
    ax.axvline(pd.Timestamp("2024-04-30"), color="k", lw=0.7, ls=":")
    ax.set_ylabel("Homicides per 100,000\n(annualised, 3-month mean)")
    ax.legend(frameon=False, fontsize=7.5, loc="upper left")
axs[0].text(pd.Timestamp("2024-02-22"), axs[0].get_ylim()[1] * 0.04, "nationwide\ndecree", ha="center", fontsize=6.5)
fig.savefig(FIG / "fig2_rates.png", bbox_inches="tight"); plt.close(fig)

# ---- Figures 3 and 4: event studies -----------------------------------------------------
def es_plot(ax, f, title):
    e = pd.read_csv(TAB / f).sort_values("q")
    x = e["q"] * 3 + 1
    ax.axhline(1, color="k", lw=0.6); ax.axvline(-0.5, color="k", lw=0.7, ls=":")
    ax.errorbar(x, e["irr"], yerr=[e["irr"] - e["irr_lo"], e["irr_hi"] - e["irr"]], fmt="o-", color="#08519c",
                ms=4, lw=1.1, capsize=2.5)
    ax.set_yscale("log"); ax.set_yticks([0.4, 0.6, 0.8, 1, 1.5, 2, 2.5]); ax.set_yticklabels(["0.4", "0.6", "0.8", "1", "1.5", "2", "2.5"])
    ax.minorticks_off()
    ax.set_ylabel("Incidence rate ratio\n(reference: months −3 to −1)")

fig, axs = plt.subplots(2, 1, figsize=(6.5, 6))
cm = pd.read_csv(TAB / "direct_counts_by_month.csv")
axs[0].bar(cm["rel"], cm["treated"], color=C["exp"], width=0.8, label="Covered cantons")
axs[0].plot(cm["rel"], cm["control"], color="#636363", lw=1.4, marker="o", ms=2.5, label="Interior never-covered cantons")
axs[0].axvline(-0.5, color="k", lw=0.7, ls=":"); axs[0].set_ylabel("Homicides per month\n(summed over stacks)")
axs[0].legend(frameon=False, fontsize=7.5, loc="upper left"); axs[0].text(-0.13, 1.02, "a", transform=axs[0].transAxes, fontsize=11, fontweight="bold")
es_plot(axs[1], "event_direct.csv", "")
axs[1].text(-0.13, 1.02, "b", transform=axs[1].transAxes, fontsize=11, fontweight="bold")
axs[1].set_xlabel("Months relative to first coverage by a targeted decree")
fig.tight_layout(); fig.savefig(FIG / "fig3_direct.png", bbox_inches="tight"); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.5, 3.3))
es_plot(ax, "event_spillover.csv", "")
ax.set_xlabel("Months relative to first coverage of a bordering canton")
fig.savefig(FIG / "fig4_spillover.png", bbox_inches="tight"); plt.close(fig)
print("figures written:", sorted(x.name for x in FIG.glob("*.png")))
