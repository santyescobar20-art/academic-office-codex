# Pre-submission checklist

## Done
- [x] Every figure and table is produced by the code in `code/` from public files stored with SHA-256 manifests.
- [x] References checked one by one against Crossref (authors, year, journal, volume, pages, DOI).
- [x] Structured replication package: `01_download.py` to `05_build_manuscript.py`.
- [x] Manuscript anonymised (no author names in the text or file properties to be checked on export).
- [x] Abstract: 213 words.
- [x] The two law-review articles without DOI confirmed (69 Stan. L. Rev. 711; 103 Minn. L. Rev. 303).
- [x] Content of Resolution 14-2021 and of judgment 8-20-CN/21 checked against an official source.

## To do by the author before submitting
- [ ] **Journal requirements.** The Wiley author-guidelines page and SCImago both refused automated access from this environment. Confirm by hand: current SJR quartile (aggregators report Q1 in Law, SJR 2025; JCR lists Q2), word and abstract limits, reference style, anonymisation and data policy. The manuscript uses author-date references in APA 7 style and can be reformatted.
- [ ] Optional: compare Section 2.2 with the full text of Resolution 14-2021. The description now follows the National Court's own summary of it, published in the Registro Oficial (Edición Jurídica No. 415, 31 May 2024); the Court's site with the original PDF returned errors.
- [ ] Check the document numbers of the 2013 and 2017 IACHR reports against the OAS site (it refused automated access). The 2022 report is cited by title and approval date.
- [ ] Complete the title page (author, affiliation, funding) and the repository link.

## Known limitations to keep in view during review
- Court data are annual; the weekly evidence comes from the prison stock.
- No arrest counts (the open-data portal blocks scripted downloads). If the arrests file can be downloaded manually, add orders per arrest as an outcome.
- The exposure design cannot exclude a uniform proportional effect on all courts.
