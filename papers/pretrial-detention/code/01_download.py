"""Download every raw source and record provenance.

Sources are official open-data files of Ecuador's prison service (SNAI) and
Judicial Council (Consejo de la Judicatura). Files are stored exactly as
published; a manifest with URL, retrieval date, size and SHA-256 is written
next to them. Run from the paper folder:  python code/01_download.py
"""
import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

SNAI = "https://www.atencionintegral.gob.ec/wp-content/uploads/"
CJ = "https://fsweb.funcionjudicial.gob.ec/estadisticas/"

SOURCES = {
    "snai": [
        SNAI + "2022/02/Resumen-PPL-2017-27dic2017.xlsx",
        SNAI + "2022/02/Resumen-PPL-2018-26dic2018.xlsx",
        SNAI + "2022/02/Resumen-PPL-2019-31dic2019.xlsx",
        SNAI + "2022/02/Resumen-PPL-2020-30dic2020.xlsx",
        SNAI + "2022/02/Resumen-PPL-2021-29dic2021.xlsx",
        SNAI + "2023/01/Resumen-PPL-2022-30dic2022.xlsx",
        SNAI + "2025/01/Resumen-PPL-2023-29dic2023-1.xlsx",
        SNAI + "2025/01/Resumen-PPL-2024-27dic2024.xlsx",
        SNAI + "2026/01/Reporte-mensual-PPL-DICIEMBRE-2025.xlsx",
        SNAI + "2026/10/Reporte-mensual-PPL-SEPTIEMBRE-2026-9.xlsx",
        SNAI + "2026/02/Indicador-ODS-16.3.2.xlsx",
    ],
    "cj": [
        CJ + "Boletas.rar",
        CJ + "Audiencias.rar",
        CJ + "04 DV01_BOLETAS.xlsx",
        CJ + "04 DV01_AUDIENCIAS.xlsx",
    ],
}
# The national open-data portal rejects scripted downloads, so the homicide
# files come from a public mirror that keeps the official spreadsheets
# unchanged together with their checksums (github.com/jp1309/crimen).
MIRROR = "https://raw.githubusercontent.com/jp1309/crimen/main/data/"
SOURCES["mdi"] = [
    MIRROR + "raw/mdi_homicidios_intencionales_pm_historico.xlsx",
    MIRROR + "raw/mdi_homicidios_intencionales_pm_actual.xlsx",
    MIRROR + "source_manifest.json",
]

LANDING = {
    "mdi": "https://www.datosabiertos.gob.ec/dataset/homicidios-intencionales",
    "snai": "https://www.atencionintegral.gob.ec/estadisticas/",
    "cj": "https://fsweb.funcionjudicial.gob.ec/estadisticas/datoscj/portalestadistica.html",
}


def fetch(url: str, dest: Path, tries: int = 4) -> None:
    quoted = urllib.parse.quote(url, safe=":/")
    for k in range(tries):
        try:
            with urllib.request.urlopen(quoted, timeout=300) as r:
                dest.write_bytes(r.read())
            return
        except Exception as exc:  # network hiccup: back off and retry
            if k == tries - 1:
                raise
            print(f"  retry {k + 1} after error: {exc}", file=sys.stderr)
            time.sleep(2 ** (k + 1))


def main() -> None:
    force = "--force" in sys.argv
    for group, urls in SOURCES.items():
        folder = RAW / group
        folder.mkdir(parents=True, exist_ok=True)
        manifest_path = folder / "source_manifest.json"
        old = {}
        if manifest_path.exists():
            old = {e["file"]: e for e in json.loads(manifest_path.read_text())["files"]}
        entries = []
        for url in urls:
            name = url.rsplit("/", 1)[1].replace(" ", "_")
            if name == "source_manifest.json":
                name = "mirror_manifest.json"
            dest = folder / name
            if force or not dest.exists():
                print("downloading", name)
                fetch(url, dest)
                retrieved = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            else:
                retrieved = old.get(name, {}).get("retrieved", "unknown")
            data = dest.read_bytes()
            entries.append({
                "file": name,
                "url": url,
                "retrieved": retrieved,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            })
        manifest_path.write_text(json.dumps(
            {"landing_page": LANDING[group], "files": entries},
            indent=2, ensure_ascii=False) + "\n")
        print(group, len(entries), "files")


if __name__ == "__main__":
    main()
