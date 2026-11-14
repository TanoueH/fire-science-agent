# Reproducibility of the nine-scenario manuscript

## Materials

Download and extract `releases/eaai-2026-11-14/EAAI_Development_6_Scenarios_2026-11-07.zip`. It contains the corrected CFD inputs and outputs, consolidated datasets, analysis scripts, frozen protocols, audit records, and results. The companion manuscript ZIP contains the LaTeX source, bibliography, table fragments, layout figure, compiled PDF, changelog, manifest, and a copy of the data archive.

SHA-256 checksums for both ZIP files are in `releases/eaai-2026-11-14/SHA256SUMS.txt`.

## Development reproduction

Use Python 3.11.9 and install the pinned dependencies from `requirements-lock.txt` at the root of the extracted data archive. From that archive's root, run in order:

```text
python build_development_dataset.py
python run_development_benchmark.py
python diagnose_development.py
python evaluate_support_screen.py
```

These commands reproduce the development analysis only, using six scenarios and scenario-wise validation.

## Reserved evaluation

P05V03, P10V01, and P20V02 were evaluated once after the protocol was frozen. Their results and audit record are included. Do not rerun `run_reserved_benchmark.py` as a new confirmatory evaluation: the reserved results have already been examined.

## Limits and separation from earlier project files

The current manuscript uses nine corrected CFD scenarios, six development and three reserved. The older `src/`, `analysis/`, and three-scenario materials in this repository belong to the earlier multi-agent project stage; they do not reproduce the current manuscript.

All nine current cases share one idealized geometry and the study's numerical setup. The results do not establish physical fire-test validity, mesh convergence, transfer to another geometry, operational readiness, human-safety limits, alarm performance, or general machine-learning superiority. The local severity rule is a research screen only.
