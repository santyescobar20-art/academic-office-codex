"""Build the canton-month panel used in the paper.

Inputs  (data/raw, data/treatment)
  - Ministry of the Interior record-level intentional homicides, 2014-2026
  - INEC canton population estimates and projections (2024 revision)
  - geoBoundaries ADM2 polygons for Ecuador (topology-preserving simplification)
  - decrees.csv: hand-coded territorial and temporal scope of every state of exception

Outputs (data/processed)
  - cantons.csv        canton master (code, name, province, centroid, neighbours)
  - adjacency.csv      queen-contiguity pairs between cantons
  - treatment_daily.csv.gz  canton-day indicator of a security state of exception
  - panel.csv          canton-month panel, January 2019 to September 2026
"""
from __future__ import annotations

import unicodedata
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

START, END = "2019-01-01", "2026-09-30"
SHEET = "1. Homicidios Intencionales"

PROVINCES = {
    1: "Azuay", 2: "Bolivar", 3: "Canar", 4: "Carchi", 5: "Cotopaxi", 6: "Chimborazo",
    7: "El Oro", 8: "Esmeraldas", 9: "Guayas", 10: "Imbabura", 11: "Loja", 12: "Los Rios",
    13: "Manabi", 14: "Morona Santiago", 15: "Napo", 16: "Pastaza", 17: "Pichincha",
    18: "Tungurahua", 19: "Zamora Chinchipe", 20: "Galapagos", 21: "Sucumbios",
    22: "Orellana", 23: "Santo Domingo de los Tsachilas", 24: "Santa Elena",
}
COAST = {7, 8, 9, 12, 13, 23, 24}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", str(s).upper())
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return " ".join(s.replace(".", " ").replace("-", " ").split())


# Spelling variants across the three sources, mapped to one key.
ALIAS = {
    "CRNEL MARCELINO MARIDUENA": "CORONEL MARCELINO MARIDUENA",
    "GNRAL ANTONIO ELIZALDE": "GENERAL ANTONIO ELIZALDE",
    "GENERAL ANTONIO ELIZALDE (BUCAY)": "GENERAL ANTONIO ELIZALDE",
    "ALFREDO BAQUERIZO MORENO (JUJAN)": "ALFREDO BAQUERIZO MORENO",
    "EMPALME": "EL EMPALME",
    "ORELLANA": "FRANCISCO DE ORELLANA",
    "DISTRITO METROPOLITANO DE QUITO": "QUITO",
    "RUMINAHUI": "RUMINAHUI",
    "YAGUACHI": "SAN JACINTO DE YAGUACHI",
    "PLAYAS": "PLAYAS",
    "GENERAL VILLAMIL": "PLAYAS",
    "URBINA JADO": "SALITRE",
    "SALITRE (URBINA JADO)": "SALITRE",
    "PUEBLOVIEJO": "PUEBLOVIEJO",
    "PUEBLO VIEJO": "PUEBLOVIEJO",
    "BANOS": "BANOS DE AGUA SANTA",
    "PELILEO": "SAN PEDRO DE PELILEO",
    "PILLARO": "SANTIAGO DE PILLARO",
    "LOGRONO": "LOGRONO",
    "RIO VERDE": "RIOVERDE",
    "LA JOYA DE LOS SACHAS": "JOYA DE LOS SACHAS",
    "SANTO DOMINGO DE LOS TSACHILAS": "SANTO DOMINGO",
}


def key(s: str) -> str:
    k = norm(s)
    return ALIAS.get(k, k)


# --------------------------------------------------------------------------- homicides
def load_homicides() -> pd.DataFrame:
    parts = []
    for f in ("mdi_homicidios_intencionales_pm_historico.xlsx",
              "mdi_homicidios_intencionales_pm_actual.xlsx"):
        parts.append(pd.read_excel(RAW / "homicides" / f, sheet_name=SHEET, header=0))
    d = pd.concat(parts, ignore_index=True)
    d.columns = [c.strip() for c in d.columns]
    d["date"] = pd.to_datetime(d["fecha_infraccion"])
    d["code"] = d["codigo_canton"].astype(int)
    for c in ("coordenada_x", "coordenada_y"):
        d[c] = pd.to_numeric(d[c].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    d["firearm"] = (d["arma"].map(norm) == "ARMA DE FUEGO").astype(int)
    d["public_place"] = (d["tipo_lugar"].map(norm) == "PUBLICO").astype(int)
    d["femicide_or_family"] = (
        (d["tipo_muerte"].map(norm) == "FEMICIDIO")
        | (d["presunta_motivacion"].map(norm) == "VIOLENCIA INTRAFAMILIAR")
    ).astype(int)
    return d


# --------------------------------------------------------------------------- population
def load_population(hom: pd.DataFrame) -> pd.DataFrame:
    x = pd.ExcelFile(RAW / "population" / "Tabulado_cantonal_2010-2035_rev2024.xlsx")
    rows = []
    for prov, sheet in enumerate(x.sheet_names[1:], start=1):
        p = x.parse(sheet, header=None)
        years = [int(float(v)) for v in p.iloc[13, 2:28]]
        for k in range(15, len(p)):
            r = p.iloc[k]
            name = r.iloc[1]
            if isinstance(name, str) and pd.notna(r.iloc[2]) and not name.lower().startswith(
                    ("nota", "fuente", "elabor")):
                rows.append([prov, name.strip()] + [float(v) for v in r.iloc[2:28]])
    pop = pd.DataFrame(rows, columns=["prov_code", "canton"] + years)
    pop["k"] = pop["canton"].map(key)

    # Official canton codes come from the homicide file; match on province + name.
    ref = hom[["code", "canton"]].drop_duplicates()
    ref["prov_code"] = ref["code"] // 100
    ref["k"] = ref["canton"].map(key)
    ref = ref.drop_duplicates(["prov_code", "k"])
    pop = pop.merge(ref[["prov_code", "k", "code"]], on=["prov_code", "k"], how="left")

    # Cantons with no recorded homicide in 2014-2026 never appear in the homicide file.
    manual = {(1, "ONA"): 110, (7, "MARCABELI"): 708, (19, "YACUAMBI"): 1904,
              (20, "SAN CRISTOBAL"): 2001, (20, "ISABELA"): 2002}
    miss = pop["code"].isna()
    pop.loc[miss, "code"] = [manual.get((a, b), np.nan) for a, b in
                             zip(pop.loc[miss, "prov_code"], pop.loc[miss, "k"])]
    if pop["code"].isna().any():
        raise SystemExit("Unmatched cantons in population file:\n"
                         + pop.loc[pop["code"].isna(), ["prov_code", "canton"]].to_string())
    pop["code"] = pop["code"].astype(int)
    assert pop["code"].is_unique and len(pop) == 221
    unknown = set(hom["code"]) - set(pop["code"])
    if unknown:
        print("Homicide records with canton codes outside the INEC list:",
              hom[hom["code"].isin(unknown)].groupby(["code", "canton"]).size().to_dict())
    return pop


# --------------------------------------------------------------------------- geography
def load_geo(hom: pd.DataFrame, pop: pd.DataFrame):
    g = gpd.read_file(RAW / "geo" / "ecu_adm2_simplified.geojson")
    g["geometry"] = g.geometry.buffer(0)
    g["k"] = g["shapeName"].map(key)

    # Assign each polygon the canton code most frequent among the homicides located in it.
    pts = hom[(hom["coordenada_x"].abs() > 1) & hom["coordenada_y"].notna()]
    pts = gpd.GeoDataFrame(pts[["code"]], geometry=gpd.points_from_xy(
        pts["coordenada_x"], pts["coordenada_y"]), crs=4326)
    j = gpd.sjoin(pts, g[["shapeID", "geometry"]], predicate="within")
    vote = (j.groupby(["shapeID", "code"]).size().rename("n").reset_index()
            .sort_values("n", ascending=False).drop_duplicates("shapeID"))
    g = g.merge(vote[["shapeID", "code"]], on="shapeID", how="left")

    # Name match as a cross-check and as fallback where a polygon holds no geocoded record.
    uniq = pop.groupby("k")["code"].agg(["first", "size"])
    by_name = uniq.loc[uniq["size"] == 1, "first"]
    g["code_name"] = g["k"].map(by_name)
    disagree = g[g["code"].notna() & g["code_name"].notna() & (g["code"] != g["code_name"])]
    g.loc[disagree.index, "code"] = disagree["code_name"]
    g["code"] = g["code"].fillna(g["code_name"])
    g = g[g["code"].notna()].copy()
    g["code"] = g["code"].astype(int)
    # Non-delimited zones and stray duplicates: keep the largest polygon per canton.
    g["area"] = g.to_crs(32717).area
    g = g.sort_values("area", ascending=False).drop_duplicates("code")
    missing = set(pop["code"]) - set(g["code"])
    if missing:
        print("Cantons without a polygon:", pop[pop["code"].isin(missing)][["code", "canton"]].values.tolist())

    gm = g.to_crs(32717).set_index("code")
    # Queen contiguity; a 250 m tolerance absorbs slivers left by simplification.
    buf = gm.geometry.buffer(250)
    sidx = buf.sindex
    pairs = set()
    for i, geom in enumerate(buf.values):
        for jx in sidx.query(geom, predicate="intersects"):
            if jx != i:
                a, b = buf.index[i], buf.index[jx]
                pairs.add((min(a, b), max(a, b)))
    adj = pd.DataFrame(sorted(pairs), columns=["code_a", "code_b"])
    cen = gm.geometry.representative_point().to_crs(4326)
    geo = pd.DataFrame({"code": gm.index, "lon": cen.x.values, "lat": cen.y.values,
                        "area_km2": (gm["area"].values / 1e6).round(1)})
    return geo, adj


# --------------------------------------------------------------------------- treatment
def build_treatment(cantons: pd.DataFrame) -> pd.DataFrame:
    dec = pd.read_csv(ROOT / "data" / "treatment" / "decrees.csv", dtype=str).fillna("")
    prov_by_name = {norm(v): k for k, v in PROVINCES.items()}
    cant_by_name = cantons.groupby("k")["code"].agg(list)
    days = pd.date_range("2024-01-01", END, freq="D")
    codes = cantons["code"].to_numpy()
    sec = pd.DataFrame(0, index=days, columns=codes, dtype="int8")
    nat = pd.Series(0, index=days, dtype="int8")
    oth = sec.copy()
    for _, r in dec.iterrows():
        span = (days >= r["date_start"]) & (days <= r["date_end"])
        if r["national"] == "1":
            nat[span] = 1
            continue
        hit = []
        for p in filter(None, r["provinces"].split(";")):
            pc = prov_by_name[norm(p)]
            hit += cantons.loc[cantons["prov_code"] == pc, "code"].tolist()
        for c in filter(None, r["cantons"].split(";")):
            found = cant_by_name.get(key(c))
            if found is None or len(found) != 1:
                raise SystemExit(f"Ambiguous or unknown canton in decrees.csv: {c}")
            hit += found
        target = sec if r["ground"] == "security" else oth
        target.loc[span, sorted(set(hit))] = 1
    daily = (sec.rename_axis("date").reset_index().melt("date", var_name="code", value_name="soe")
             .merge(oth.rename_axis("date").reset_index().melt("date", var_name="code",
                                                               value_name="soe_other"),
                    on=["date", "code"]))
    daily["soe_national"] = daily["date"].map(nat)
    return daily


# --------------------------------------------------------------------------- panel
def main() -> None:
    hom = load_homicides()
    pop = load_population(hom)
    geo, adj = load_geo(hom, pop)

    cantons = pop[["code", "canton", "prov_code", "k"]].merge(geo, on="code", how="left")
    cantons["province"] = cantons["prov_code"].map(PROVINCES)
    cantons["coast"] = cantons["prov_code"].isin(COAST).astype(int)

    daily = build_treatment(cantons)
    daily.to_csv(OUT / "treatment_daily.csv.gz", index=False)
    daily["month"] = daily["date"].dt.to_period("M")
    tm = daily.groupby(["code", "month"]).agg(
        soe_share=("soe", "mean"), soe_other_share=("soe_other", "mean"),
        soe_national_share=("soe_national", "mean")).reset_index()

    months = pd.period_range(START, END, freq="M")
    panel = pd.MultiIndex.from_product([cantons["code"], months],
                                       names=["code", "month"]).to_frame(index=False)
    h = hom[(hom["date"] >= START) & (hom["date"] <= END) & hom["code"].isin(cantons["code"])].copy()
    h["month"] = h["date"].dt.to_period("M")
    agg = h.groupby(["code", "month"]).agg(
        hom=("code", "size"), hom_firearm=("firearm", "sum"), hom_public=("public_place", "sum"),
        hom_family=("femicide_or_family", "sum")).reset_index()
    panel = panel.merge(agg, on=["code", "month"], how="left").merge(tm, on=["code", "month"], how="left")
    cnt = ["hom", "hom_firearm", "hom_public", "hom_family"]
    panel[cnt] = panel[cnt].fillna(0).astype(int)
    panel["hom_other"] = panel["hom"] - panel["hom_firearm"]
    sh = ["soe_share", "soe_other_share", "soe_national_share"]
    panel[sh] = panel[sh].fillna(0.0)

    # Mid-year population, linearly interpolated to months.
    yrs = [c for c in pop.columns if isinstance(c, int)]
    pl = pop.melt(id_vars="code", value_vars=yrs, var_name="year", value_name="pop")
    pl["t"] = pl["year"] + 0.5
    panel["t"] = panel["month"].dt.year + (panel["month"].dt.month - 0.5) / 12
    panel["pop"] = np.nan
    for code, grp in pl.groupby("code"):
        m = panel["code"] == code
        panel.loc[m, "pop"] = np.interp(panel.loc[m, "t"], grp["t"], grp["pop"])
    panel["rate"] = panel["hom"] / panel["pop"] * 1e5 * 12  # annualised, per 100,000

    # Monthly treatment status: under a security decree for at least half of the month.
    panel["D"] = (panel["soe_share"] >= 0.5).astype(int)
    first = panel[panel["D"] == 1].groupby("code")["month"].min().rename("g")
    panel = panel.merge(first, on="code", how="left")

    # Exposure of each canton-month to treated neighbours.
    nb = pd.concat([adj, adj.rename(columns={"code_a": "code_b", "code_b": "code_a"})])
    dn = nb.merge(panel[["code", "month", "D"]].rename(columns={"code": "code_b", "D": "D_nb"}),
                  on="code_b")
    ex = dn.groupby(["code_a", "month"])["D_nb"].agg(["max", "mean"]).reset_index()
    ex.columns = ["code", "month", "nb_any", "nb_share"]
    panel = panel.merge(ex, on=["code", "month"], how="left").fillna({"nb_any": 0, "nb_share": 0})
    panel["nb_any"] = panel["nb_any"].astype(int)
    first_nb = panel[(panel["nb_any"] == 1)].groupby("code")["month"].min().rename("g_nb")
    panel = panel.merge(first_nb, on="code", how="left")

    panel = panel.merge(cantons[["code", "canton", "prov_code", "province", "coast"]], on="code")
    panel["ym"] = panel["month"].astype(str)
    panel["g"] = panel["g"].astype(str).replace("NaT", "")
    panel["g_nb"] = panel["g_nb"].astype(str).replace("NaT", "")
    panel = panel.drop(columns=["month", "t"]).sort_values(["code", "ym"])

    nbl = nb.groupby("code_a")["code_b"].agg(lambda s: ";".join(map(str, sorted(s)))).rename("neighbours")
    cantons = cantons.merge(nbl, left_on="code", right_index=True, how="left").drop(columns="k")
    cantons = cantons.merge(panel.drop_duplicates("code")[["code", "g", "g_nb"]], on="code")

    cantons.to_csv(OUT / "cantons.csv", index=False)
    adj.to_csv(OUT / "adjacency.csv", index=False)
    panel.to_csv(OUT / "panel.csv", index=False)

    # ---- integrity report
    tot = hom.groupby(hom["date"].dt.year).size()
    in_panel = panel.groupby(panel["ym"].str[:4].astype(int))["hom"].sum()
    rep = pd.DataFrame({"source_records": tot, "panel": in_panel}).dropna()
    print(rep.astype(int).to_string())
    print("cantons:", len(cantons), "| adjacency pairs:", len(adj),
          "| isolated:", int(cantons["neighbours"].isna().sum()))
    print(cantons.groupby("g").size().to_string())


if __name__ == "__main__":
    main()
