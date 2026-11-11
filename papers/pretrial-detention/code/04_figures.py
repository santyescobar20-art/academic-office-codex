"""Figures for the manuscript. Run after 03_estimate.py:  python code/04_figures.py"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / "manuscript" / "tables"
FIG = ROOT / "manuscript" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
RES = pd.Timestamp("2021-12-15")
INK, ACCENT, MUTED = "#1f2933", "#b3541e", "#7b8794"
plt.rcParams.update({"font.family": "DejaVu Serif", "font.size": 9.5, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.edgecolor": INK, "figure.dpi": 200})


def save(fig, name: str) -> None:
    fig.tight_layout()
    fig.savefig(FIG / f"{name}.png", dpi=300)
    fig.savefig(FIG / f"{name}.pdf")
    plt.close(fig)


def fig1() -> None:
    n = pd.read_csv(TAB / "t1_national.csv").set_index("year")
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0))
    ax[0].plot(n.index, n["pp_orders"] / 1000, color=INK, marker="o", ms=3.5)
    ax[0].plot([2025, 2026], n.loc[[2025, 2026], "pp_orders"] / 1000, color="white", lw=2.2)
    ax[0].plot([2025, 2026], n.loc[[2025, 2026], "pp_orders"] / 1000, color=INK, ls=":", marker="o", ms=3.5)
    ax[0].set_ylabel("Pretrial detention orders (thousands)")
    ax[0].set_ylim(0, 20)
    ax[0].annotate("2026: Jan-Sep", (2026, n.loc[2026, "pp_orders"] / 1000), xytext=(-52, -14),
                   textcoords="offset points", fontsize=8, color=MUTED)
    r = n.loc[2017:]
    ax[1].plot(r.index, r["pp_per_100_hearings"], color=INK, marker="o", ms=3.5)
    ax[1].set_ylabel("Orders per 100 criminal hearings held")
    ax[1].set_ylim(0, 16)
    for a in ax:
        a.axvline(2021.5, color=ACCENT, lw=1)
        a.set_xticks(range(2016, 2027, 2))
    ax[0].text(2021.65, 19.6, "Resolution 14-2021", color=ACCENT, fontsize=8, va="top")
    save(fig, "fig1_national")


def fig2() -> None:
    e = pd.read_csv(TAB / "t3_event_study.csv")
    e = e[(e["outcome"] == "pp_orders") & (e["exposure"] == "z")].sort_values("year")
    ref = pd.DataFrame({"year": [2021], "b": [0.0], "lo": [0.0], "hi": [0.0]})
    e = pd.concat([e, ref]).sort_values("year")
    fig, ax = plt.subplots(figsize=(5.2, 3.1))
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.axvline(2021.5, color=ACCENT, lw=1)
    ax.errorbar(e["year"], e["b"], yerr=[e["b"] - e["lo"], e["hi"] - e["b"]], fmt="o", color=INK,
                ms=4, capsize=2.5, lw=1)
    ax.axvspan(2016.6, 2018.4, color=MUTED, alpha=0.12, lw=0)
    ax.text(2017.5, ax.get_ylim()[1] * 0.93, "exposure\nmeasured", ha="center", va="top", fontsize=7.5, color=MUTED)
    ax.set_xticks(range(2017, 2027))
    ax.set_ylabel("Log-point difference per SD of exposure")
    save(fig, "fig2_event_study")


def fig3() -> None:
    w = pd.read_csv(ROOT / "data" / "processed" / "snai_weekly.csv", parse_dates=["date"])
    w = w[(w["date"] >= "2019-01-01") & (w["date"] < "2023-01-01")]
    fig, ax = plt.subplots(figsize=(6.4, 3.1))
    ax.plot(w["date"], w["unsentenced"] / 1000, color=INK, lw=1.3, label="Unsentenced")
    ax.plot(w["date"], w["sentenced"] / 1000, color=MUTED, lw=1.3, label="Sentenced")
    events = [("2020-03-16", "Pandemic"), ("2021-08-18", "Const. Court\n8-20-CN/21"),
              ("2021-09-28", "Litoral\nmassacre"), ("2021-12-15", "Res. 14-2021")]
    top = ax.get_ylim()[1]
    for (d, lab), y in zip(events, (27.2, 27.2, 24.6, 27.2)):
        d = pd.Timestamp(d)
        ax.axvline(d, color=ACCENT if "Res." in lab else MUTED, lw=1 if "Res." in lab else 0.7,
                   ls="-" if "Res." in lab else "--")
        ax.text(d, y, lab, fontsize=7, ha="right" if "Res." not in lab else "left", va="top",
                color=ACCENT if "Res." in lab else MUTED)
    ax.set_ylim(10, 27.5)
    ax.set_ylabel("People in prison (thousands)")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(frameon=False, loc=(0.03, 0.40), fontsize=8)
    save(fig, "fig3_prison_stock")


def fig4() -> None:
    g = pd.read_csv(TAB / "t1b_rate_by_exposure.csv")
    fig, ax = plt.subplots(figsize=(5.2, 3.1))
    for h, lab, c in ((1, "High-exposure cantons", INK), (0, "Low-exposure cantons", MUTED)):
        d = g[g["high"] == h]
        ax.plot(d["year"], 100 * d["rate"] / d.loc[d["year"] == 2021, "rate"].iloc[0], color=c,
                marker="o", ms=3.5, label=lab)
    ax.axvline(2021.5, color=ACCENT, lw=1)
    ax.axhline(100, color=MUTED, lw=0.6)
    ax.set_xticks(range(2017, 2027))
    ax.set_ylabel("Orders per hearing (2021 = 100)")
    ax.legend(frameon=False, fontsize=8)
    save(fig, "fig4_by_exposure")


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
    print(sorted(p.name for p in FIG.glob("*.png")))
