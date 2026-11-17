"""Insert the tables produced by 03_estimate.py into the manuscript and export it.

English: reads manuscript/manuscript_src.md, writes manuscript.md (+ .docx).
Spanish: reads manuscript/manuscript_src_es.md, writes manuscript_es.md (+ .docx).
Politica Criminal: reads manuscript/manuscript_src_pc.md (Spanish, footnote citations,
ISO 690), writes manuscript_pc.md and a .docx formatted to the journal's norms.
Run from the paper folder:  python code/05_build_manuscript.py [en|es|pc|all]
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
TAB = MAN / "tables"

TEXT = {
    "en": {
        "note": "Note.", "stars": "* p < 0.10, ** p < 0.05, *** p < 0.01.",
        "t1_cap": "Table 1. Pretrial detention, caseload, violence and prison population, 2016-2026",
        "t1_cols": ["Year", "Detention orders", "Hearings held", "Orders per 100 hearings", "Homicides",
                    "Later substituted (%)", "Unsentenced prisoners", "Overcrowding (%)"],
        "t1_note": ("Orders and hearings are from the Judicial Council (criminal, traffic and domestic-violence "
                    "matters); hearings are available from 2017. Homicides refer to cantons with a criminal court. "
                    "\"Later substituted\" is the share of each year's detention orders that ended with a "
                    "non-custodial measure; recent cohorts are right-censored. Prison figures are annual means of "
                    "weekly SNAI counts; the unsentenced series is redefined in January 2023. ᵃ January to September."),
        "t2_cap": "Table 2. Detention rate by year relative to 2021",
        "t2_cols": ["Year", "Coefficient (SE)", "Change vs. 2021 (%)", "95% CI (%)"],
        "t2_note": ("Poisson regression of detention orders on year indicators with canton fixed effects, "
                    "log(1 + homicides) and log hearings held as offset; 129 cantons, 1,290 observations. "
                    "Standard errors clustered by canton."),
        "t3_cap": "Table 3. Event-study estimates by pre-resolution reliance on detention",
        "t3_cols": ["Year", "Continuous exposure (per SD)", "Above-median exposure"],
        "t3_joint": "Joint test, 2019-2020 (p)",
        "t3_note": ("Poisson regressions with canton and year fixed effects, log(1 + homicides) and log hearings "
                    "as offset. Exposure is measured in 2017-2018; 2021 is the reference year. Standard errors "
                    "clustered by canton."),
        "t4_cap": "Table 4. Pooled difference-in-differences estimates",
        "t4_cols": ["Specification", "Exposure × 2022-2023", "95% CI (%)", "Exposure × 2024-2026", "N"],
        "t4_note": ("Poisson regressions of detention orders (committals after conviction in the placebo row) with "
                    "canton and year fixed effects unless stated, log hearings as offset. Exposure is standardised "
                    "pre-resolution reliance, or an above-median indicator in the binary row. Standard errors "
                    "clustered by canton unless stated."),
        "spec": {},
        "t5_cap": "Table 5. Within-judge estimates, 2019-2026",
        "t5_cols": ["Specification", "Exposure × 2022-2023", "Exposure × 2024-2026", "Judges", "Judge-years"],
        "t5_note": ("Poisson regressions of detention orders by judge-year with log hearings held as offset. "
                    "Each judge carries the exposure of the canton where he or she held most hearings. Standard "
                    "errors clustered by canton."),
        "t6_cap": "Table 6. Discontinuity in the weekly prison population at the resolution date",
        "t6_cols": ["Outcome", "Bandwidth (weeks)", "Jump at 15 Dec 2021", "HAC SE", "SD of placebo jumps",
                    "Placebo dates", "Share of placebos at least as large"],
        "t6_out": {"unsentenced": "Unsentenced prisoners", "sentenced": "Sentenced prisoners",
                   "unsentenced_share": "Unsentenced share"},
        "t6_note": ("Local linear regressions in time with separate slopes on each side of the cut-off. Placebo "
                    "cut-offs are all weeks from January 2018 to June 2022 whose window overlaps neither the "
                    "resolution nor the pandemic releases of 2020."),
    },
    "es": {
        "note": "Nota.", "stars": "* p < 0,10; ** p < 0,05; *** p < 0,01.",
        "t1_cap": "Tabla 1. Prisión preventiva, carga procesal, violencia y población penitenciaria, 2016-2026",
        "t1_cols": ["Año", "Órdenes de prisión preventiva", "Audiencias realizadas", "Órdenes por cada 100 audiencias",
                    "Homicidios", "Sustituidas después (%)", "Presos sin sentencia", "Hacinamiento (%)"],
        "t1_note": ("Órdenes y audiencias provienen del Consejo de la Judicatura (materias penal, de tránsito y de "
                    "violencia contra la mujer o miembros del núcleo familiar); las audiencias están disponibles "
                    "desde 2017. Los homicidios corresponden a cantones con unidad judicial penal. \"Sustituidas "
                    "después\" es la proporción de órdenes de cada año que terminó con una medida no privativa de "
                    "libertad; las cohortes recientes están censuradas por la derecha. Las cifras penitenciarias son "
                    "promedios anuales de los conteos semanales del SNAI; la serie de presos sin sentencia cambia de "
                    "definición en enero de 2023. ᵃ Enero a septiembre."),
        "t2_cap": "Tabla 2. Tasa de prisión preventiva por año, respecto de 2021",
        "t2_cols": ["Año", "Coeficiente (EE)", "Cambio respecto de 2021 (%)", "IC 95 % (%)"],
        "t2_note": ("Regresión de Poisson de las órdenes de prisión preventiva sobre indicadores de año, con "
                    "efectos fijos de cantón, log(1 + homicidios) y el logaritmo de las audiencias realizadas como "
                    "término de exposición; 129 cantones, 1.290 observaciones. Errores estándar agrupados por cantón."),
        "t3_cap": "Tabla 3. Estudio de eventos según la dependencia previa de la prisión preventiva",
        "t3_cols": ["Año", "Exposición continua (por DE)", "Exposición sobre la mediana"],
        "t3_joint": "Prueba conjunta, 2019-2020 (p)",
        "t3_note": ("Regresiones de Poisson con efectos fijos de cantón y de año, log(1 + homicidios) y el logaritmo "
                    "de las audiencias como término de exposición. La exposición se mide en 2017-2018; 2021 es el año "
                    "de referencia. Errores estándar agrupados por cantón."),
        "t4_cap": "Tabla 4. Estimaciones agregadas de diferencias en diferencias",
        "t4_cols": ["Especificación", "Exposición × 2022-2023", "IC 95 % (%)", "Exposición × 2024-2026", "N"],
        "t4_note": ("Regresiones de Poisson de las órdenes de prisión preventiva (boletas por sentencia condenatoria "
                    "en la fila placebo) con efectos fijos de cantón y de año salvo indicación, y el logaritmo de las "
                    "audiencias como término de exposición. La exposición es la dependencia previa estandarizada, o un "
                    "indicador de estar sobre la mediana en la fila binaria. Errores estándar agrupados por cantón "
                    "salvo indicación."),
        "spec": {
            "baseline": "Principal",
            "province-year FE": "Efectos fijos provincia-año",
            "cluster province": "Errores agrupados por provincia",
            "no Guayaquil/Quito": "Sin Guayaquil ni Quito",
            "no homicide control": "Sin control por homicidios",
            "binary exposure": "Exposición binaria",
            "placebo outcome: conviction committals": "Placebo: boletas por sentencia condenatoria",
            "drop 2020 (pandemic)": "Sin 2020 (pandemia)",
            "pre-period only 2019-2021": "Periodo previo solo 2019-2021",
            "judge FE + year FE": "Efectos fijos de juez y de año",
            "judge FE + province-year FE": "Efectos fijos de juez y de provincia-año",
        },
        "t5_cap": "Tabla 5. Estimaciones dentro de cada juez, 2019-2026",
        "t5_cols": ["Especificación", "Exposición × 2022-2023", "Exposición × 2024-2026", "Jueces", "Juez-año"],
        "t5_note": ("Regresiones de Poisson de las órdenes de prisión preventiva por juez y año, con el logaritmo de "
                    "las audiencias realizadas como término de exposición. Cada juez recibe la exposición del cantón "
                    "donde celebró más audiencias. Errores estándar agrupados por cantón."),
        "t6_cap": "Tabla 6. Discontinuidad en la población penitenciaria semanal en la fecha de la resolución",
        "t6_cols": ["Resultado", "Ancho de banda (semanas)", "Salto al 15 dic. 2021", "EE (HAC)",
                    "DE de los saltos placebo", "Fechas placebo", "Proporción de placebos iguales o mayores"],
        "t6_out": {"unsentenced": "Presos sin sentencia", "sentenced": "Presos sentenciados",
                   "unsentenced_share": "Proporción sin sentencia"},
        "t6_note": ("Regresiones lineales locales en el tiempo, con pendientes distintas a cada lado del punto de "
                    "corte. Las fechas placebo son todas las semanas entre enero de 2018 y junio de 2022 cuya ventana "
                    "no se superpone con la resolución ni con las excarcelaciones de la pandemia en 2020."),
    },
}


TEXT["pc"] = dict(TEXT["es"], note="Nota:", plain=True, sources={
    "{{TABLE1}}": "Consejo de la Judicatura, Ministerio del Interior y SNAI",
    "{{TABLE2}}": "Consejo de la Judicatura y Ministerio del Interior",
    "{{TABLE3}}": "Consejo de la Judicatura y Ministerio del Interior",
    "{{TABLE4}}": "Consejo de la Judicatura y Ministerio del Interior",
    "{{TABLE5}}": "Consejo de la Judicatura",
    "{{TABLE6}}": "SNAI",
})


class Fmt:
    """Number formatting for each language (thousands and decimal marks)."""

    def __init__(self, lang: str):
        self.lang = lang
        self.sep = ", " if lang == "en" else "; "

    def loc(self, s: str) -> str:
        if self.lang == "en":
            return s
        s = s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")
        return s.replace("-", "−") if re.match(r"^[\[\-+0-9]", s) else s

    def num(self, v: float, spec: str) -> str:
        return self.loc(format(v, spec))

    def ci(self, lo: float, hi: float) -> str:
        return "[" + self.loc(f"{lo:+.1f}") + self.sep + self.loc(f"{hi:+.1f}") + "]"


def md(df: pd.DataFrame, caption: str, note: str, T: dict) -> str:
    head = "| " + " | ".join(df.columns) + " |"
    sep = "|" + "|".join([":--"] + ["--:"] * (len(df.columns) - 1)) + "|"
    body = ["| " + " | ".join(str(v) for v in row) + " |" for row in df.values]
    if T.get("plain"):   # Politica Criminal: no bold or italics outside the allowed uses
        cap = f'::: {{custom-style="PC Tabla"}}\n{caption}\n:::'
        nota = f'::: {{custom-style="PC Nota"}}\n{T["note"]} {note}\n:::'
        return "\n".join([cap, "", head, sep, *body, "", nota, ""])
    return "\n".join([f"**{caption}**", "", head, sep, *body, "", f"*{T['note']}* {note}", ""])


def stars(p: float) -> str:
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""


def build_tables(lang: str) -> dict:
    T, F = TEXT[lang], Fmt("es" if lang == "pc" else lang)
    est = lambda b, se, p: F.num(b, ".3f") + stars(p) + " (" + F.num(se, ".3f") + ")"
    spec = lambda s: T["spec"].get(s, s[0].upper() + s[1:])
    out = {}

    t = pd.read_csv(TAB / "t1_national.csv")
    dash = "–"
    cols = T["t1_cols"]
    out["{{TABLE1}}"] = md(pd.DataFrame({
        cols[0]: t["year"].astype(str).replace({"2026": "2026ᵃ"}),
        cols[1]: t["pp_orders"].map(lambda v: F.num(v, ",")),
        cols[2]: t["hearings_held"].map(lambda v: dash if v == 0 else F.num(v, ",")),
        cols[3]: t["pp_per_100_hearings"].map(lambda v: dash if np.isnan(v) else F.num(v, ".1f")),
        cols[4]: t["homicides"].map(lambda v: F.num(v, ",")),
        cols[5]: (100 * t["subst_share"]).map(lambda v: F.num(v, ".1f")),
        cols[6]: t["prison_unsentenced"].map(lambda v: dash if np.isnan(v) else F.num(v, ",.0f")),
        cols[7]: (100 * t["prison_overcrowding"]).map(lambda v: dash if np.isnan(v) else F.num(v, ".1f")),
    }), T["t1_cap"], T["t1_note"], T)

    t = pd.read_csv(TAB / "t2_year_effects.csv").sort_values("year")
    cols = T["t2_cols"]
    out["{{TABLE2}}"] = md(pd.DataFrame({
        cols[0]: t["year"],
        cols[1]: [est(b, s, p) for b, s, p in zip(t["b"], t["se"], t["p"])],
        cols[2]: t["pct"].map(lambda v: F.num(v, "+.1f")),
        cols[3]: [F.ci(100 * np.expm1(lo), 100 * np.expm1(hi)) for lo, hi in zip(t["lo"], t["hi"])],
    }), T["t2_cap"], T["t2_note"] + " " + T["stars"], T)

    t = pd.read_csv(TAB / "t3_event_study.csv")
    t = t[t["outcome"] == "pp_orders"]
    z = t[t["exposure"] == "z"].set_index("year")
    h = t[t["exposure"] == "high"].set_index("year")
    cols = T["t3_cols"]
    d = pd.DataFrame({cols[0]: z.index,
                      cols[1]: [est(*r) for r in z[["b", "se", "p"]].values],
                      cols[2]: [est(*h.loc[y, ["b", "se", "p"]].values) for y in z.index]})
    d = pd.concat([d, pd.DataFrame({cols[0]: [T["t3_joint"]],
                                    cols[1]: [F.num(z["pretrend_p"].iloc[0], ".3f")],
                                    cols[2]: [F.num(h["pretrend_p"].iloc[0], ".3f")]})])
    out["{{TABLE3}}"] = md(d, T["t3_cap"], T["t3_note"] + " " + T["stars"], T)

    t = pd.read_csv(TAB / "t4_did.csv")
    rows = []
    for s, g in t.groupby("spec", sort=False):
        e = g[g["term"].str.contains("early")].iloc[0]
        l = g[g["term"].str.contains("late")].iloc[0]
        rows.append([spec(s), est(e["b"], e["se"], e["p"]), F.ci(e["pct_lo"], e["pct_hi"]),
                     est(l["b"], l["se"], l["p"]), F.num(int(e["n"]), ",")])
    out["{{TABLE4}}"] = md(pd.DataFrame(rows, columns=T["t4_cols"]), T["t4_cap"],
                           T["t4_note"] + " " + T["stars"], T)

    t = pd.read_csv(TAB / "t6_within_judge.csv")
    rows = []
    for s, g in t.groupby("spec", sort=False):
        e, l = g.iloc[0], g.iloc[1]
        rows.append([spec(s), est(e["b"], e["se"], e["p"]), est(l["b"], l["se"], l["p"]),
                     F.num(int(e["judges"]), ","), F.num(int(e["n"]), ",")])
    out["{{TABLE5}}"] = md(pd.DataFrame(rows, columns=T["t5_cols"]), T["t5_cap"],
                           T["t5_note"] + " " + T["stars"], T)

    t = pd.read_csv(TAB / "t7_stock_discontinuity.csv")
    f = lambda v, o: F.num(v, ".4f") if o == "unsentenced_share" else F.num(v, ",.0f")
    cols = T["t6_cols"]
    out["{{TABLE6}}"] = md(pd.DataFrame({
        cols[0]: t["outcome"].map(T["t6_out"]),
        cols[1]: t["bandwidth_weeks"],
        cols[2]: [f(v, o) for v, o in zip(t["jump"], t["outcome"])],
        cols[3]: [f(v, o) for v, o in zip(t["se"], t["outcome"])],
        cols[4]: [f(v, o) for v, o in zip(t["placebo_sd"], t["outcome"])],
        cols[5]: t["placebo_dates"],
        cols[6]: t["placebo_p"].map(lambda v: F.num(v, ".2f")),
    }), T["t6_cap"], T["t6_note"], T)
    if "sources" in T:
        for key, src in T["sources"].items():
            out[key] = _add_source(out[key], src)
    return out


def _add_source(block: str, src: str) -> str:
    """Append the data source to the table note (last fenced div)."""
    head, sep, tail = block.rpartition("\n:::")
    fuente = f" Fuente: elaboración propia con datos del {src}." if not src.startswith("SNAI") \
        else " Fuente: elaboración propia con datos del SNAI."
    return head + fuente + sep + tail


def pc_reference_docx() -> Path:
    """Word template for Politica Criminal: Times New Roman, justified, single spacing."""
    from docx import Document
    from docx.enum.style import WD_STYLE_TYPE
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.shared import Pt, RGBColor

    ref = MAN / "pc_reference.docx"
    raw = subprocess.run(["pandoc", "--print-default-data-file", "reference.docx"],
                         capture_output=True, check=True).stdout
    ref.write_bytes(raw)
    doc = Document(str(ref))

    def font(style, size, bold=False, italic=False, superscript=False):
        f = style.font
        f.name, f.size, f.bold, f.italic = "Times New Roman", Pt(size), bold, italic
        f.color.rgb = RGBColor(0, 0, 0)
        if superscript:
            f.superscript = True
        rpr = style.element.get_or_add_rPr()
        fonts = rpr.find(qn("w:rFonts"))
        if fonts is None:
            fonts = rpr.makeelement(qn("w:rFonts"), {})
            rpr.append(fonts)
        for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
            fonts.attrib.pop(qn(a), None)
        for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
            fonts.set(qn(a), "Times New Roman")

    def para(style, align=WD_ALIGN_PARAGRAPH.JUSTIFY, before=0, after=12, keep=False):
        pf = style.paragraph_format
        pf.alignment, pf.line_spacing = align, 1.0
        pf.space_before, pf.space_after = Pt(before), Pt(after)
        pf.first_line_indent, pf.left_indent = Pt(0), Pt(0)
        pf.keep_with_next = keep

    styles = doc.styles
    def get(name, kind=WD_STYLE_TYPE.PARAGRAPH):
        # pandoc's template stores "Heading 1" capitalised, which styles[...] cannot look up
        found = [st for st in styles if st.name == name or st.style_id == name.replace(" ", "")]
        return found[0] if found else styles.add_style(name, kind)
    for name in ("Normal", "Body Text", "First Paragraph", "Block Text"):
        font(get(name), 12); para(get(name))
    for name, size, bold, italic in (("Heading 1", 12, True, False), ("Heading 2", 11, True, False),
                                     ("Heading 3", 11, False, False)):
        font(get(name), size, bold, italic); para(get(name), WD_ALIGN_PARAGRAPH.LEFT, 6, 12, keep=True)
    font(get("Compact"), 10); para(get("Compact"), WD_ALIGN_PARAGRAPH.LEFT, 0, 0)
    font(get("Footnote Text"), 10); para(get("Footnote Text"), after=0)
    font(get("Footnote Reference", WD_STYLE_TYPE.CHARACTER), 11, superscript=True)
    for name in ("Image Caption", "Caption", "Table Caption"):
        font(get(name), 11); para(get(name))
    for name in ("Hyperlink",):
        font(get(name, WD_STYLE_TYPE.CHARACTER), 12)
    font(get("PC Titulo"), 12, bold=True); para(get("PC Titulo"), WD_ALIGN_PARAGRAPH.CENTER, 0, 6)
    font(get("PC Centro"), 12); para(get("PC Centro"), WD_ALIGN_PARAGRAPH.CENTER, 0, 6)
    font(get("PC Tabla"), 11); para(get("PC Tabla"), WD_ALIGN_PARAGRAPH.LEFT, 6, 6, keep=True)
    font(get("PC Nota"), 10); para(get("PC Nota"))
    doc.save(str(ref))
    return ref


def build(lang: str) -> None:
    src, dst = {"en": ("manuscript_src.md", "manuscript"), "es": ("manuscript_src_es.md", "manuscript_es"),
                "pc": ("manuscript_src_pc.md", "manuscript_pc")}[lang]
    text = (MAN / src).read_text()
    for key, table in build_tables(lang).items():
        assert key in text, key
        text = text.replace(key, table)
    (MAN / f"{dst}.md").write_text(text)
    marker = {"en": "# References", "es": "# Referencias", "pc": "# Bibliografía citada"}[lang]
    words = len([w for w in text.split(marker)[0].split() if any(ch.isalpha() for ch in w)])
    print(f"[{lang}] words before references (tables included): {words}")
    if shutil.which("pandoc"):
        cmd = ["pandoc", f"{dst}.md", "-o", f"{dst}.docx", "--from",
               "markdown+tex_math_dollars+pipe_tables+fenced_divs", "--resource-path", "."]
        if lang == "pc":
            cmd += ["--reference-doc", str(pc_reference_docx())]
        subprocess.run(cmd, cwd=MAN, check=True)
        print(f"[{lang}] wrote {dst}.docx")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    for lang in (["en", "es", "pc"] if arg == "all" else [arg]):
        build(lang)
