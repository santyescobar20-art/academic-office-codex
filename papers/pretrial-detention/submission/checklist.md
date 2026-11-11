# Pre-submission checklist

## Done
- [x] Every figure and table is produced by the code in `code/` from public files stored with SHA-256 manifests.
- [x] References checked one by one against Crossref (authors, year, journal, volume, pages, DOI).
- [x] Structured replication package: `01_download.py` to `05_build_manuscript.py`.
- [x] Manuscript anonymised (no author names in the text or file properties to be checked on export).
- [x] Abstract: 213 words.

## To do by the author before submitting
- [ ] **Journal requirements.** The Wiley author-guidelines page and SCImago both refused automated access from this environment. Confirm by hand: current SJR quartile (aggregators report Q1 in Law, SJR 2025; JCR lists Q2), word and abstract limits, reference style, anonymisation and data policy. The manuscript uses author-date references in APA 7 style and can be reformatted.
- [ ] **Read the primary text of Resolution 14-2021** (Corte Nacional de Justicia, 15 December 2021) and check the description in Section 2.2 against it, including its publication in the Registro Oficial. The Court's site returned errors; the description relies on the press report cited and on secondary sources quoting the text.
- [ ] Check the three IACHR report citations (document numbers) against the OAS site, and the page ranges of the two law-review articles without DOI (Heaton et al., 2017; Stevenson, 2018b).
- [ ] Confirm the dates of the executive pardons of late 2021 and early 2022 if the editor asks for more detail on the decongestion policy.
- [ ] Complete the title page (author, affiliation, funding) and the repository link.

## Known limitations to keep in view during review
- Court data are annual; the weekly evidence comes from the prison stock.
- No arrest counts (the open-data portal blocks scripted downloads). If the arrests file can be downloaded manually, add orders per arrest as an outcome.
- The exposure design cannot exclude a uniform proportional effect on all courts.
