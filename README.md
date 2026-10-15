# RICMTECH ERP

Backlog maestro del ERP RICMTECH: 207 tareas, 6 fases, ~1.344 h estimadas.

## Estructura

| Ruta | Contenido |
|---|---|
| `data/backlog.csv` | Fuente maestra de tareas (no cambiar IDs una vez iniciado el sprint) |
| `data/labels.csv` | Labels de GitHub (módulo, tipo, prioridad) |
| `data/milestones.csv` | Milestones = fases del proyecto |
| `scripts/import_issues.py` | Crea labels, milestones, Issues y dependencias con `gh` |

## Fases

| Fase | Objetivo |
|---|---|
| 0 — Cierre técnico | OIDC productivo, CI seguridad, scheduler, restore y observabilidad |
| 1 — Piloto Perú | Primeros clientes pagados y SUNAT beta |
| 2 — Producto comercial | Onboarding, provisioning, cobro, soporte, importación |
| 3 — Restaurante | POS, turnos, comandas, cocina, recetas, merma |
| 4 — Integradores API | OAuth, cuotas, webhooks, catálogo API, SLA |
| 5 — Segundo país | Nuevo paquete fiscal e internacionalización |

## Flujo de trabajo

`BACKLOG → READY → IN PROGRESS → CODE REVIEW → QA → READY FOR RELEASE → DONE`

- Un Issue = un responsable principal (`justindev2004` o `rt-rcabrera`).
- Cada PR referencia su Issue y pasa Code Review + QA antes de DONE.
- No iniciar Fase 1 con bloqueantes críticos de Fase 0 abiertos, salvo decisión explícita del equipo.

## Importar el backlog a GitHub

```bash
gh auth login
gh auth refresh -s project          # solo si usarás --project
python scripts/import_issues.py --dry-run
python scripts/import_issues.py --project "RICMTECH ERP — Delivery"
```
