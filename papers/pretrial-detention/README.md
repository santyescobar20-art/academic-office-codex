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
