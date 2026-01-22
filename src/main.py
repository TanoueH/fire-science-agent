import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from custom_tool import (
    LoadCSVTool,
    NormalizeSensorsTool,
    FetchLiteratureTool,
    WebScraperTool,
    PredictFireTool,
    CompileReportTool,
)

app = FastAPI(title="FireScience Agent", version="1.0")


# ----------------------------
# Configuration
# ----------------------------

@dataclass(frozen=True)
class Settings:
    project_root: Path
    tasks_file: Path
    output_dir: Path
    input_csv: str
    report_file: str
    model: str
    offline_mode: bool
    seed: int
    run_id: str

    @staticmethod
    def from_env() -> "Settings":
        project_root = Path(os.getenv("PROJECT_ROOT", "/app")).resolve()
        tasks_file = Path(os.getenv("TASKS_FILE", str(project_root / "src" / "tasks.yaml"))).resolve()
        output_dir = Path(os.getenv("OUTPUT_DIR", str(project_root / "output"))).resolve()

        input_csv = os.getenv("INPUT_CSV", "./sample_sensors.csv")
        report_file = os.getenv("REPORT_FILE", str(output_dir / "report.md"))

        model = os.getenv("MODEL", "gpt-4o")
        offline_mode = os.getenv("OFFLINE_MODE", "true").lower() in ("1", "true", "yes", "y")
        seed = int(os.getenv("SEED", "42"))
        run_id = os.getenv("RUN_ID", "paper-run")

        return Settings(
            project_root=project_root,
            tasks_file=tasks_file,
            output_dir=output_dir,
            input_csv=input_csv,
            report_file=report_file,
            model=model,
            offline_mode=offline_mode,
            seed=seed,
            run_id=run_id,
        )


SETTINGS = Settings.from_env()


# ----------------------------
# Tools registry
# ----------------------------

TOOLS = {
    "LoadCSVTool": LoadCSVTool(),
    "NormalizeSensorsTool": NormalizeSensorsTool(),
    "FetchLiteratureTool": FetchLiteratureTool(),
    "WebScraperTool": WebScraperTool(),
    "PredictFireTool": PredictFireTool(),
    "CompileReportTool": CompileReportTool(),
}


# ----------------------------
# Helpers
# ----------------------------

def _substitute_vars(obj: Any, variables: Dict[str, str]) -> Any:
    """Recursively substitute ${VARNAME} in strings for YAML-loaded structures."""
    if isinstance(obj, str):
        out = obj
        for k, v in variables.items():
            out = out.replace("${" + k + "}", v)
        return out
    if isinstance(obj, dict):
        return {k: _substitute_vars(v, variables) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_substitute_vars(v, variables) for v in obj]
    return obj


def _load_tasks() -> Dict[str, Any]:
    if not SETTINGS.tasks_file.exists():
        raise FileNotFoundError(f"Tasks file not found: {SETTINGS.tasks_file}")

    with SETTINGS.tasks_file.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    variables = {
        "INPUT_CSV": SETTINGS.input_csv,
        "REPORT_FILE": SETTINGS.report_file,
        "MODEL": SETTINGS.model,
        "OFFLINE_MODE": str(SETTINGS.offline_mode).lower(),
        "SEED": str(SETTINGS.seed),
        "RUN_ID": SETTINGS.run_id,
        "OUTPUT_DIR": str(SETTINGS.output_dir),
    }
    cfg = _substitute_vars(cfg, variables)
    return cfg


def _resolve_output_path(p: str) -> Path:
    path = Path(p)
    if path.is_absolute():
        return path
    # Treat relative paths as relative to project root (paper-friendly)
    return (SETTINGS.project_root / path).resolve()


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_output(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".json":
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    elif path.suffix.lower() == ".md":
        with path.open("w", encoding="utf-8") as f:
            f.write(str(data))
    else:
        # Default: write as text for unknown extensions
        with path.open("w", encoding="utf-8") as f:
            f.write(str(data))


def run_pipeline() -> Dict[str, Any]:
    cfg = _load_tasks()
    tasks = cfg.get("tasks", [])
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("No tasks found in tasks.yaml")

    SETTINGS.output_dir.mkdir(parents=True, exist_ok=True)

    # Optional: keep in-memory map of outputs keyed by task id
    results: Dict[str, Any] = {}

    for task in tasks:
        task_id = task.get("id", "<no-id>")
        tool_name = task.get("tool")
        if tool_name not in TOOLS:
            raise ValueError(f"Tool not found: {tool_name} (task: {task_id})")

        tool = TOOLS[tool_name]
        desc = task.get("description", "")

        # Offline guardrail for networked tasks (paper-reproducible by default)
        if SETTINGS.offline_mode and tool_name in ("FetchLiteratureTool", "WebScraperTool"):
            # Produce deterministic empty output rather than failing
            output_path = _resolve_output_path(task.get("output", str(SETTINGS.output_dir / f"{task_id}.json")))
            _write_output(output_path, {"skipped": True, "reason": "OFFLINE_MODE=true"})
            results[task_id] = {"skipped": True}
            continue

        # Resolve input
        input_data: Optional[Any] = None
        if "input" in task:
            inp = task["input"]
            if isinstance(inp, str):
                in_path = _resolve_output_path(inp)
                if in_path.exists():
                    input_data = _read_json(in_path) if in_path.suffix.lower() == ".json" else in_path.read_text(encoding="utf-8")
                elif inp in results:
                    input_data = results[inp]
            elif isinstance(inp, list):
                # Support list of inputs (files or task ids)
                assembled = []
                for item in inp:
                    if isinstance(item, str) and item in results:
                        assembled.append(results[item])
                        continue
                    p = _resolve_output_path(str(item))
                    if p.exists():
                        assembled.append(_read_json(p) if p.suffix.lower() == ".json" else p.read_text(encoding="utf-8"))
                input_data = assembled

        params = task.get("params", {}) or {}
        # Inject reproducibility params consistently if tools accept them
        params.setdefault("model", SETTINGS.model)
        params.setdefault("seed", SETTINGS.seed)
        params.setdefault("run_id", SETTINGS.run_id)
        params.setdefault("offline", SETTINGS.offline_mode)

        # Execute
        try:
            output_data = tool.run(input_data, **params)
        except Exception as e:
            raise RuntimeError(f"Task failed: {task_id} ({tool_name}) - {desc}. Error: {e}") from e

        # Persist output deterministically
        out = task.get("output")
        if not out:
            out = str(SETTINGS.output_dir / f"{task_id}.json")
        out_path = _resolve_output_path(out)
        _write_output(out_path, output_data)

        results[task_id] = output_data

    return results


# ----------------------------
# API endpoints
# ----------------------------

class RunResponse(BaseModel):
    run_id: str
    offline_mode: bool
    output_dir: str
    report_file: str
    tasks_executed: int


@app.get("/")
async def root():
    return {"message": "FireScience Agent active"}


@app.get("/health")
async def health():
    # Minimal deterministic checks (safe for Compose healthcheck)
    ok = True
    details: Dict[str, Union[str, bool]] = {}

    details["tasks_file_exists"] = SETTINGS.tasks_file.exists()
    if not SETTINGS.tasks_file.exists():
        ok = False

    try:
        SETTINGS.output_dir.mkdir(parents=True, exist_ok=True)
        details["output_dir_writable"] = True
    except Exception:
        ok = False
        details["output_dir_writable"] = False

    return {"ok": ok, "details": details}


@app.post("/run", response_model=RunResponse)
async def run():
    try:
        results = run_pipeline()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return RunResponse(
        run_id=SETTINGS.run_id,
        offline_mode=SETTINGS.offline_mode,
        output_dir=str(SETTINGS.output_dir),
        report_file=SETTINGS.report_file,
        tasks_executed=len(results),
    )


if __name__ == "__main__":
    # For local execution only; in container prefer: uvicorn ... (no --reload in prod)
    run_pipeline()
