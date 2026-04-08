# Fire Science Agent

A compact, audit-oriented, and reproducible repository associated with the paper **“A Multi-Agent Intelligent Sensing Framework for Tunnel Fire Detection.”**

This repository contains the core workflow used to support the paper, including curated sensor data derived from processed *Fire Dynamics Simulator* (FDS) tunnel-fire outputs, a modular multi-agent pipeline, and the minimum configuration artifacts required for technical inspection and reproducibility.

## Overview

Tunnel fire detection and risk interpretation require the integration of heterogeneous sensing signals, scenario-aware data processing, and structured analytical reasoning. In this work, the repository supports a multi-agent workflow organized around four logical roles:

- **Curator** — validates and standardizes the input sensor dataset;
- **Researcher** — interprets scenario behavior and signal patterns;
- **Analyst** — performs hybrid risk-oriented inference using fuzzy logic and machine learning concepts;
- **Reporter** — produces a compact analytical report for inspection and audit.

The repository is intentionally lightweight. It is **not** a full archival mirror of the dissertation environment, nor a storage location for large raw FDS outputs. Instead, it provides a curated and traceable implementation aligned with the paper workflow.

## Repository Scope

This repository was designed to support:

- workflow reproducibility;
- inspection of the multi-agent sensing pipeline;
- auditability of curated sensor data used in the article;
- lightweight replication of the paper-oriented processing flow.

This repository was **not** designed to store:

- full dissertation chapters or thesis materials;
- large raw FDS output directories;
- Smokeview image/video collections;
- deprecated infrastructure not used in the final paper workflow;
- legacy cloud, scraper, MQTT, or overextended edge/cloud orchestration components.

## Main Components

```text
.
├── Dockerfile
├── LICENSE
├── README.md
├── docker-compose.yml
├── requirements.txt
├── data
│   └── curated
│       └── dataset_all_scenarios_long.csv
└── src
    ├── __init__.py
    ├── agents.yaml
    ├── custom_tool.py
    ├── main.py
    ├── tasks.yaml
    └── output/

Core files
src/main.py
Main entry point for the Fire Science Agent pipeline.
src/custom_tool.py
Auxiliary data processing and analytical logic used by the workflow.
src/agents.yaml
Definition of the logical agent roles used in the framework.
src/tasks.yaml
Definition of the pipeline task sequence.
data/curated/dataset_all_scenarios_long.csv
Curated dataset derived from processed FDS-based tunnel-fire outputs.
src/output/
Directory used for execution-generated outputs.
Dataset Description

The repository includes a curated dataset derived from processed FDS tunnel-fire simulation outputs representing a 50 m tunnel-fire segment and three representative scenarios:

S1
S2
S3

The data reflect the sensing logic described in the paper, using virtual sensors and the main physical variables considered in the framework:

temperature;
visibility;
carbon monoxide concentration (CO);
longitudinal smoke velocity.

The included dataset is processed and curated, not raw simulation output. Its purpose is to support reproducibility and auditability at repository level without inflating the project with heavy simulation artifacts.

Methodological Alignment with the Paper

The repository is aligned with the final paper design, which adopts:

an FDS-based tunnel-fire scenario;
three representative fire and ventilation scenarios;
ten virtual sensors;
hybrid analytical reasoning based on fuzzy logic and machine learning;
a modular multi-agent architecture centered on curation, interpretation, analysis, and reporting.

Legacy components from earlier exploratory stages were intentionally excluded from the final repository workflow when not required by the submitted manuscript.

Installation
Local environment

Create and activate a Python environment, then install the dependencies:

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Environment file

Copy the example environment file if needed:

cp .env.example .env

Then edit .env according to your local execution preferences.

Execution
Local execution

The repository uses src/main.py as the main entry point.

Run:

python src/main.py

The execution behavior is controlled by the repository configuration and environment variables defined in .env.example.

Docker execution

Build and run with Docker Compose:

docker compose up --build

The containerized execution uses the configuration declared in docker-compose.yml.

Generated Outputs

Runtime-generated artifacts may be written to src/output/ depending on the execution path configured in the local environment.

These files are considered execution outputs rather than primary repository assets.

Reproducibility Notes

This repository is intentionally compact. The guiding principle is paper-level reproducibility, not full-environment archival storage.

Accordingly:

the included dataset is curated and audit-ready;
large raw FDS outputs are excluded from version control;
the pipeline structure is kept readable and minimal;
the repository reflects the final scientific workflow described in the article.
Auditability

This repository supports technical audit in three complementary ways:

Traceable data origin
The included dataset is derived from processed FDS simulation outputs rather than synthetic placeholder data.
Explicit modular roles
Agent roles and task flow are defined in YAML files, improving readability and inspection.
Compact execution surface
The repository avoids unnecessary infrastructure, making the core logic easier to verify.
Limitations

This repository should not be interpreted as:

a complete CFD reproducibility package for rerunning all simulations from scratch;
a complete archive of the broader dissertation project;
a benchmark repository for exhaustive machine-learning model comparison;
a storage location for large-scale raw numerical outputs.

Its purpose is narrower and more practical: to provide a clean, inspectable, and reproducible companion repository for the submitted paper.

Citation

If you use this repository in academic or technical work, please cite the associated paper:

A Multi-Agent Intelligent Sensing Framework for Tunnel Fire Detection
Submitted to IEEE Sensors Journal.

License

This project is distributed under the terms specified in the LICENSE file.