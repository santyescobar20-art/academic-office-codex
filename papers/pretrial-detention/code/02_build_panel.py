"""Build the analysis files from the raw sources.

Outputs (data/processed):
  judge_year.csv      pretrial-detention orders, later outcomes and hearings by judge-court-year
  court_year.csv      the same aggregated to judicial unit
  province_year.csv   the same aggregated to province, plus SNAI prison stock
  snai_weekly.csv     national weekly prison population by legal status, 2017-2026
  snai_center_year.csv  unsentenced share by prison, annual, 2012-2025

Judge names appear in the official open data. They are replaced here by a
stable anonymous code; nothing in the paper depends on identity.
Run from the paper folder:  python code/02_build_panel.py
"""
import hashlib
import io
import re
import unicodedata
import warnings
from pathlib import Path

import libarchive
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

CRIMINAL = {"PENAL COIP", "TRANSITO COIP", "VIOLENCIA CONTRA LA MUJER Y FAMILIA COIP"}

# Release reasons that signal, after the fact, that detention was not followed
# by a conviction or was replaced by a milder measure.
NO_CONVICTION = {
    "SOBRESEIMIENTO",
    "SENTENCIA RATIFICATORIA DEL ESTADO DE INOCENCIA",
    "POR NO FORMULAR CARGOS",
    "PRESCRIPCION",
    "NULIDAD PROCESAL QUE AFECTE LA MEDIDA CAUTELAR",
}
SUBSTITUTED = {
    "SUSTITUCION DE LA PRISION PREVENTIVA",
    "POR DICTAR MEDIDA CAUTELAR NO PRIVATIVA DE LIBERTAD",
    "ARRESTO DOMICILIARIO",
}
COURT_ORDERED_RELEASE = {"HABEAS CORPUS", "CADUCIDAD DE LA PRISION PREVENTIVA"}


def norm(s: object) -> str:
    s = "" if pd.isna(s) else str(s)
    # the judiciary files carry "Ñ" as the literal escape sequence \\xd1
    s = s.replace("\\xd1", "Ñ").replace("\\xf1", "ñ")
    s = unicodedata.normalize("NFD", s.upper())
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", s).strip()


def read_rar_csv(path: Path) -> pd.DataFrame:
    with libarchive.file_reader(str(path)) as archive:
        for entry in archive:
            if entry.pathname.lower().endswith(".csv"):
                raw = b"".join(entry.get_blocks())
                break
        else:
            raise FileNotFoundError(f"no csv inside {path}")
    for enc in ("utf-8", "latin-1"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    sep = ";" if text[:2000].count(";") > text[:2000].count(",") else ","
    df = pd.read_csv(io.StringIO(text), sep=sep, low_memory=False)
    df = df.rename(columns={df.columns[0]: "year"})
    return df


def judge_code(name: str) -> str:
    if name in ("", "N/D"):
        return "ND"
    return "J" + hashlib.sha256(name.encode("utf-8")).hexdigest()[:10]


def clean_keys(df: pd.DataFrame) -> pd.DataFrame:
    for col in ("Provincia", "Canton", "Judicatura", "Materia", "Juez"):
        df[col] = df[col].map(norm)
    df["judge"] = df["Juez"].map(judge_code)
    df["year"] = df["year"].astype(int)
    return df.rename(columns={"Provincia": "province", "Canton": "canton",
                              "Judicatura": "court", "Materia": "matter"})


# ---------------------------------------------------------------- judiciary
def build_orders() -> pd.DataFrame:
    b = clean_keys(read_rar_csv(RAW / "cj" / "Boletas.rar"))
    b["Motivo_EN"] = b["Motivo_EN"].map(norm)
    b["Motivo_EX"] = b["Motivo_EX"].map(norm)
    b = b[b["matter"].isin(CRIMINAL)]
    b["n"] = b["Contador"].fillna(0).astype(int)

    pp = b[b["Motivo_EN"] == "PRISION PREVENTIVA"].copy()
    pp["rel_noconv"] = np.where(pp["Motivo_EX"].isin(NO_CONVICTION), pp["n"], 0)
    pp["rel_subst"] = np.where(pp["Motivo_EX"].isin(SUBSTITUTED), pp["n"], 0)
    pp["rel_court"] = np.where(pp["Motivo_EX"].isin(COURT_ORDERED_RELEASE), pp["n"], 0)
    pp["rel_any"] = np.where(pp["Motivo_EX"] != "", pp["n"], 0)
    keys = ["province", "canton", "court", "judge", "year"]
    out = pp.groupby(keys, as_index=False).agg(
        pp_orders=("n", "sum"), pp_rel_any=("rel_any", "sum"),
        pp_rel_noconv=("rel_noconv", "sum"), pp_rel_subst=("rel_subst", "sum"),
        pp_rel_court=("rel_court", "sum"))
    conv = (b[b["Motivo_EN"] == "SENTENCIA CONDENATORIA"]
            .groupby(keys, as_index=False)["n"].sum()
            .rename(columns={"n": "conviction_committals"}))
    return out.merge(conv, on=keys, how="outer")


def build_hearings() -> pd.DataFrame:
    a = clean_keys(read_rar_csv(RAW / "cj" / "Audiencias.rar"))
    a = a[a["matter"].isin(CRIMINAL)]
    a["n"] = a["Contador"].fillna(0).astype(int)
    a["held"] = np.where(a["Estado"].map(norm) == "REALIZADA", a["n"], 0)
    keys = ["province", "canton", "court", "judge", "year"]
    return a.groupby(keys, as_index=False).agg(
        hearings_scheduled=("n", "sum"), hearings_held=("held", "sum"))


# --------------------------------------------------------------------- SNAI
def snai_weekly() -> pd.DataFrame:
    frames = []
    files = sorted((RAW / "snai").glob("Resumen-PPL-*.xlsx")) + \
        [RAW / "snai" / "Reporte-mensual-PPL-DICIEMBRE-2025.xlsx",
         RAW / "snai" / "Reporte-mensual-PPL-SEPTIEMBRE-2026-9.xlsx"]
    for f in files:
        x = pd.ExcelFile(f)
        sheet = [s for s in x.sheet_names if s.startswith("Resumen PPL")][0]
        d = x.parse(sheet, header=None)
        hdr = d.index[d.iloc[:, 0].astype(str).str.contains("FECHA DE REPORTE", na=False)][0]
        names = [norm(c) for c in d.iloc[hdr]]
        d = d.iloc[hdr + 1:].copy()
        d.columns = names

        def col(pattern: str) -> pd.Series:
            match = [c for c in names if re.search(pattern, c)]
            return pd.to_numeric(d[match[0]], errors="coerce")

        w = pd.DataFrame({
            "date": pd.to_datetime(d[names[0]], errors="coerce"),
            "sentenced": col(r"^PPL SENTENCIADOS"),
            "unsentenced": col(r"^PPL PROCESADOS"),
            "total": col(r"^TOTAL PPL"),
            "capacity": col(r"^CAPACIDAD INSTALADA"),
        })
        w["source_file"] = f.name
        frames.append(w.dropna(subset=["date", "total"]))
    w = pd.concat(frames).drop_duplicates("date").sort_values("date")
    w["unsentenced_share"] = w["unsentenced"] / (w["sentenced"] + w["unsentenced"])
    w["overcrowding"] = w["total"] / w["capacity"] - 1
    return w


def snai_center_year() -> tuple[pd.DataFrame, pd.DataFrame]:
    x = pd.ExcelFile(RAW / "snai" / "Indicador-ODS-16.3.2.xlsx")
    provinces = None
    prov_rows, center_rows = [], []
    for sheet in x.sheet_names:
        d = x.parse(sheet, header=None)
        label = d.iloc[:, 0].map(norm)
        starts = list(d.index[label == "NIVEL DE DESAGREGACION"])
        blocks = []
        for s in starts:
            rows = []
            for i in range(s + 1, len(d)):
                if label[i] in ("", "TOTALES") or pd.isna(d.iloc[i, 3]):
                    break
                rows.append((label[i], d.iloc[i, 3], d.iloc[i, 4]))
            blocks.append(rows)
        # blocks: national, sex, province, prison
        for name, proc, pop in blocks[2]:
            prov_rows.append((int(sheet), name, proc, pop))
        for name, proc, pop in blocks[3]:
            center_rows.append((int(sheet), name, proc, pop))
    cols = ["year", "unit", "unsentenced", "population"]
    prov = pd.DataFrame(prov_rows, columns=cols).rename(columns={"unit": "province"})
    cent = pd.DataFrame(center_rows, columns=cols).rename(columns={"unit": "prison"})
    for t in (prov, cent):
        t["unsentenced_share"] = t["unsentenced"] / t["population"]
    return prov, cent


def main() -> None:
    orders = build_orders()
    hearings = build_hearings()
    keys = ["province", "canton", "court", "judge", "year"]
    jy = orders.merge(hearings, on=keys, how="outer")
    num = [c for c in jy.columns if c not in keys]
    jy[num] = jy[num].fillna(0).astype(int)
    jy = jy.sort_values(keys)
    jy.to_csv(OUT / "judge_year.csv", index=False)

    cy = jy.groupby(["province", "canton", "court", "year"], as_index=False)[num].sum()
    cy.to_csv(OUT / "court_year.csv", index=False)

    prov_stock, center = snai_center_year()
    py = jy.groupby(["province", "year"], as_index=False)[num].sum()
    prov_stock = prov_stock.rename(columns={
        "unsentenced": "prison_unsentenced", "population": "prison_population",
        "unsentenced_share": "prison_unsentenced_share"})
    py = py.merge(prov_stock, on=["province", "year"], how="left")
    py.to_csv(OUT / "province_year.csv", index=False)
    center.to_csv(OUT / "snai_center_year.csv", index=False)

    weekly = snai_weekly()
    weekly.to_csv(OUT / "snai_weekly.csv", index=False)

    print("judge-court-years:", len(jy), "| judges:", jy["judge"].nunique() - 1,
          "| courts:", cy["court"].nunique())
    print(jy.groupby("year")[["pp_orders", "hearings_held"]].sum().T.to_string())
    print("weekly SNAI:", weekly["date"].min().date(), "to", weekly["date"].max().date(),
          len(weekly), "weeks")
    print("unmatched provinces in stock:",
          sorted(set(prov_stock["province"]) - set(py["province"])))


if __name__ == "__main__":
    main()
