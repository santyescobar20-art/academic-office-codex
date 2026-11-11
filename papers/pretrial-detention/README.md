# Can a Court Curb Pretrial Detention? Evidence from Ecuador

Working paper targeted at the *Journal of Empirical Legal Studies*.

Question: did Resolution 14-2021 of Ecuador's National Court of Justice
(15 December 2021), which requires prosecutors and judges to justify the
necessity of pretrial detention, reduce its use?

## Layout

```
data/raw/        official files exactly as published, with source manifests
data/processed/  panels built by code/02_build_panel.py
code/            numbered scripts; run in order
manuscript/      text, tables and figures
submission/      cover letter, title page, checklist
```

## Reproduce

```
pip install -r requirements.txt      # libarchive-c needs the system libarchive
python code/01_download.py           # only if data/raw is missing
python code/02_build_panel.py
```

## Sources

- Consejo de la Judicatura, Portal de Estadística Judicial: committal and
  release orders (*boletas*) and hearings, by judge and year, 2016-2026.
- SNAI: weekly prison population by legal status, 2017-2026, and yearly
  unsentenced share by prison and province, 2012-2025.

Every number in the manuscript is produced by the code in this folder.

## Full pipeline

```
python code/02_build_panel.py        # panels in data/processed
python code/03_estimate.py           # tables in manuscript/tables, results.json
python code/04_figures.py            # figures in manuscript/figures
python code/05_build_manuscript.py   # manuscript.md and manuscript.docx
```

## Main finding

Detention orders per hearing fell 21% in 2022, but the fall began before the
resolution, did not vary with prior reliance on detention, shows no break in
the weekly prison series at the resolution date, and was reversed by 2025.
