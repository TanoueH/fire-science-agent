# Fire Science Agent and tunnel-fire research materials

This repository now also contains the author-approved revision of the manuscript **“Scenario-wise assessment of sparse virtual sensing and interpretable severity screening in simulated tunnel fires.”** Its current target is *Engineering Applications of Artificial Intelligence (EAAI)*. The manuscript has not yet been resubmitted or accepted.

## Current manuscript and reproducibility package

- `paper/manuscript.tex`, `paper/references.bib`, `paper/tables/`, and `paper/figures/` contain the manuscript source and the files needed alongside it.
- `releases/eaai-2026-11-14/` contains the manuscript bundle and separate nine-scenario reproducibility archive.
- `docs/reproducibility.md` gives the reproduction sequence and the study's limits.
- `paper/STATUS_EAAI_2026-11-14.md` records the manuscript and deposit status.

## Zenodo archive

The reproducibility package is publicly archived on Zenodo:

- Current deposited version (version 2): [DOI 10.5281/zenodo.24231837](https://doi.org/10.5281/zenodo.24231837) ([record](https://zenodo.org/records/24231837)).
- Concept DOI for the record across versions: [10.5281/zenodo.24229182](https://doi.org/10.5281/zenodo.24229182).

Cite the version DOI above when referring to the exact archived package. The Zenodo deposit is an archival record; it does not submit the manuscript to EAAI.

The current study evaluates contemporaneous reconstruction of temperature, visibility, and carbon monoxide at six omitted virtual measurement sites using four observed sites. It compares nearest-site and spatial-linear baselines with Ridge and random-forest regression across nine CFD cases: six development cases and three reserved cases evaluated once after the protocol was frozen.

The results do **not** establish general machine-learning superiority or a novel inference algorithm. The four-band severity rule is a local research criterion; it has not been validated as a human-safety limit, alarm threshold, or operational risk level. The study does not include physical fire-test validation, mesh-convergence analysis, a second geometry, or operational evaluation.

## Earlier multi-agent materials retained for provenance

The existing `src/`, `analysis/`, and earlier three-scenario data files document a previous multi-agent tunnel-fire project stage. They are preserved, but **they are not the method or results of the current nine-scenario manuscript**. The current manuscript does not claim that the multi-agent pipeline produced its results. Do not use the earlier three-scenario artifacts as a substitute for the current reproducibility archive.

## Funding

This work was carried out with support from the National Council for Scientific and Technological Development (CNPq), Brazil, under Funding Code 131754/2025-4.

## Status

Prof. Saulo approved the revised manuscript modifications on 14 November 2026. The reproducibility package is publicly archived on Zenodo under the version DOI [10.5281/zenodo.24231837](https://doi.org/10.5281/zenodo.24231837); the concept DOI is [10.5281/zenodo.24229182](https://doi.org/10.5281/zenodo.24229182). The manuscript has not yet been resubmitted to EAAI.
