# ml/: research, training and evaluation

ML code lives here. **ML never serves API routes and is never called by the frontend.** The backend reaches models only through an interface:

```text
backend domain service ──► backend/app/intelligence/<capability>.py (Protocol + DTOs)
                                   │
                                   └──► adapter (loads an artifact produced here, or a mock)
                                              │
                                              └──► model trained in ml/
```

Status: **no ML code yet** (workstream M06 has not started). Folders below are created when their first real code lands; don't add empty ones.

## Intended layout

```text
ml/
├── pyproject.toml     separate uv workspace member (add "ml" to [tool.uv.workspace] members in the root pyproject.toml)
├── features/          feature engineering shared by training and (via the backend adapter) inference
├── models/            one package per model family: anomaly/, task_time/, risk/, skill/
├── training/          reproducible, seeded training pipelines (read simulator datasets; no API calls)
├── inference/         pure predict functions the backend adapter imports (no FastAPI, no DB)
├── evaluation/        metrics, baselines (machine-only vs contextual), research evaluation (also M11)
├── experiments/       notebooks / experiment configs
├── federated/         federated learning prototype (M10), only after the core product works
└── tests/
```

## Rules

- Datasets come from the simulator: `python -m app.iot.simulator --sink stdout --start 2026-09-23T02:30:00Z --speed 0 > data.jsonl`. Data files are gitignored.
- Trained artifacts are **not** committed. When they exist, a top-level `models/` folder holds the registry/configs (see docs/architecture/decisions/ADR-0002).
- Every model output follows `docs/architecture/contracts/TOOL_AND_ML_CONTRACTS.md` Part B (model_version, confidence, contributors, fallback level).
- Report results on simulated data as simulated. Keep a machine-only baseline for every contextual model.
