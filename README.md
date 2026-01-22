Fire Science Agent (FSA)

This repository provides a research prototype of the Fire Science Agent (FSA),
a distributed multi-agent framework for intelligent fire-risk assessment in tunnel environments.
The system integrates physical and virtual sensing (soft sensors), fuzzy-logic inference, and
machine-learning models within a containerized, reproducible architecture.

1. Scope and Disclaimer

This code is provided exclusively for research, reproducibility, and technical auditing purposes.
It is not intended for direct operational deployment in safety-critical environments without
additional validation, certification, and regulatory approval.

The implementation prioritizes architectural transparency, traceability, and repeatability over
operational performance.

2. Related Publication

This repository supports the paper:

H. M. Tanoue and S. J. C. Almeida
Fire Science Agent: A Distributed Intelligent Sensing Framework for Tunnel Fire Detection Using Fuzzy Logic and Machine Learning
submitted to IEEE Sensors Journal, 2026.

The codebase reflects the architectural concepts, agent roles, and hybrid fuzzy–ML inference pipeline
described in the manuscript and is intended to serve as supplementary material for reproducibility.

3. System Overview

The Fire Science Agent is built upon:

CrewAI for multi-agent orchestration

Docker / Docker Compose for deterministic and reproducible execution

FastAPI for inference and reporting services

Offline-first data pipelines with optional online enrichment

Hybrid fuzzy-logic and machine-learning reasoning for fire-risk estimation

Conceptual Multi-Agent Workflow

The system is organized into the following logical roles:

Curator
Acquisition, preprocessing, normalization, and validation of heterogeneous sensor data.

Analyst
Hybrid fuzzy-logic and machine-learning inference to compute a continuous Fire Risk Index (FRI).

Researcher (optional, online)
Retrieval of metadata from scientific literature and technical standards to support contextual
interpretation.

Web Scraper (optional, online)
Extraction of publicly accessible abstracts and technical summaries for enrichment purposes.

Reporter
Compilation of human-readable decision-support reports in Markdown format.

By default, the edge pipeline (Curator + Analyst) is fully reproducible and operates
without external network access.
Cloud-based enrichment agents are disabled unless explicitly enabled.

4. Reproducibility Model

Reproducibility is enforced through:

Deterministic task orchestration (tasks.yaml)

Explicit agent role definitions (agents.yaml)

Offline-first execution (OFFLINE_MODE=true)

Fixed random seeds and run identifiers

Containerized execution without runtime dependency installation

Explicit persistence of all intermediate and final artifacts

All experiments reported in the paper can be reproduced using the production
Compose specification.

5. Repository Structure

fire-science-agent/
├── src/
│   ├── main.py            # Pipeline runner and FastAPI entry point
│   ├── agents.yaml        # Agent roles and tool bindings
│   ├── tasks.yaml         # Deterministic task pipeline
│   └── custom_tool.py     # Tool implementations (Python classes)
│
├── data/                  # Input datasets (e.g., sample sensor CSV)
├── output/                # Generated reports and results (not versioned)
├── artifacts/             # Intermediate artifacts for auditing
│
├── Dockerfile             # Deterministic container build
├── compose.prod.yml       # Paper-ready execution environment
├── requirements.txt       # Frozen Python dependencies
├── README.md
└── CITATION.cff


Note:
Directories such as output/ and artifacts/ are generated at runtime and are excluded from
version control.

6. Execution
Production / Paper-Ready Execution

cp .env.example .env
docker compose -f compose.prod.yml --profile edge --profile cloud up --build


Outputs:

Fire-risk report: output/report.md

Intermediate artifacts: artifacts/

Optional audit manifest (if enabled)

Offline Reproduction (Default)
OFFLINE_MODE=true docker compose -f compose.prod.yml --profile edge up

7. Citation

If you use this code or build upon it, please cite the associated paper and/or
the repository metadata provided in CITATION.cff.