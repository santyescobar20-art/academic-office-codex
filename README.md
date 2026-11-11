# academic-office-codex

Replication files and manuscript for *Crackdown or Relocation? Targeted States of Exception and the Geography of Lethal Violence in Ecuador, 2024–2026*.

```
data/raw/          homicide records, INEC population projections, canton polygons
data/treatment/    decrees.csv: hand-coded scope of every state of exception, with sources
data/processed/    canton master, adjacency, canton-month panel
code/              01_build_panel.py  02_estimate.py  03_figures.py  04_tables.py
manuscript/        manuscript.md/.docx, supplement, tables/, figures/
submission/        title page, cover letter, pre-submission checklist
```

Reproduce everything with:

```
pip install -r requirements.txt
python code/01_build_panel.py && python code/02_estimate.py && python code/03_figures.py && python code/04_tables.py
```

Sources: Ministerio del Interior (homicidios intencionales, release of 20 October 2026, via the public mirror jp1309/crimen); INEC population projections, 2024 revision; geoBoundaries ADM2.
