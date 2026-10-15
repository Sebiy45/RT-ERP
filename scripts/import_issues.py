#!/usr/bin/env python3
"""Importa el backlog de RICMTECH ERP a GitHub (labels, milestones, issues y dependencias).

Uso (desde la raíz del repo, con `gh` autenticado):
    python scripts/import_issues.py --dry-run            # simula, no crea nada
    python scripts/import_issues.py                      # crea todo
    python scripts/import_issues.py --project "RICMTECH ERP — Delivery"

Es reanudable: guarda IDs -> nº de Issue en data/issues_map.json y omite lo ya creado.
"""
import argparse, csv, json, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
MAP_FILE = DATA / "issues_map.json"


def gh(*args, dry=False, check=True):
    cmd = ["gh", *args]
    if dry:
        print("  [dry-run]", " ".join(cmd[:6]), "...")
        return ""
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"ERROR: {' '.join(cmd[:5])}\n{r.stderr}")
    return r.stdout.strip()


def read_csv(name):
    with open(DATA / name, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def body(row, deps_text):
    return (
        f"**ID:** {row['ID']}  \n"
        f"**Fase:** {row['Fase']} · **Épica:** {row['Épica']} · **Módulo:** {row['Módulo']}  \n"
        f"**Tipo:** {row['Tipo']} · **Prioridad:** {row['Prioridad']} · **Estimación:** {row['Estimación_h']} h  \n"
        f"**Base:** {row['Base']}  \n"
        f"**Responsable:** @{row['Responsable']}\n\n"
        f"### Criterios de aceptación\n{row['Criterios_de_aceptación']}\n\n"
        f"### Dependencias\n{deps_text}\n"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--project", default="")
    ap.add_argument("--skip-setup", action="store_true", help="no crear labels/milestones")
    ap.add_argument("--sleep", type=float, default=1.0)
    a = ap.parse_args()
    dry = a.dry_run

    rows = read_csv("backlog.csv")
    mapping = json.loads(MAP_FILE.read_text()) if MAP_FILE.exists() else {}

    if not a.skip_setup:
        print("== Labels")
        for l in read_csv("labels.csv"):
            gh("label", "create", l["Label"], "--description", l["Descripción"], "--force", dry=dry)
        print("== Milestones")
        existing = set()
        if not dry:
            out = gh("api", "repos/{owner}/{repo}/milestones?state=all&per_page=100", "--jq", ".[].title")
            existing = set(out.splitlines())
        for m in read_csv("milestones.csv"):
            if m["Milestone"] in existing:
                continue
            gh("api", "repos/{owner}/{repo}/milestones", "-f", f"title={m['Milestone']}",
               "-f", f"description={m['Objetivo']}", dry=dry)

    print("== Issues")
    for i, r in enumerate(rows, 1):
        if r["ID"] in mapping:
            continue
        deps = "—" if r["Dependencias"].strip() in ("", "—") else r["Dependencias"]
        args = ["issue", "create", "--title", r["GitHub Title"], "--body", body(r, deps),
                "--assignee", r["Responsable"], "--milestone", r["Milestone"]]
        for lab in r["GitHub Labels"].split(";"):
            args += ["--label", lab.strip()]
        if a.project:
            args += ["--project", a.project]
        url = gh(*args, dry=dry)
        if not dry:
            mapping[r["ID"]] = int(url.rstrip("/").split("/")[-1])
            MAP_FILE.write_text(json.dumps(mapping, indent=2, ensure_ascii=False))
            time.sleep(a.sleep)
        print(f"  {i}/{len(rows)} {r['ID']}")

    print("== Dependencias (se agregan al cuerpo del Issue como #n)")
    for r in rows:
        d = r["Dependencias"].strip()
        if d in ("", "—") or r["ID"] not in mapping:
            continue
        refs = []
        for dep in [x.strip() for x in d.replace(";", ",").split(",") if x.strip()]:
            refs.append(f"#{mapping[dep]} ({dep})" if dep in mapping else dep)
        gh("issue", "edit", str(mapping[r["ID"]]), "--body", body(r, ", ".join(refs)), dry=dry)
        if not dry:
            time.sleep(a.sleep)
    print("Listo.")


if __name__ == "__main__":
    main()
